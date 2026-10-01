"""
Case-Specific RAG (Retrieval-Augmented Generation) System
Enables intelligent Q&A about case documents and general legal knowledge
"""
import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class CaseRAGSystem:
    """
    RAG system for answering questions about case documents and legal matters
    """
    
    def __init__(self, case_id: int):
        self.case_id = case_id
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, accurate embeddings
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=f"./chroma_db/case_{case_id}",
            anonymized_telemetry=False
        ))
        
        # Get or create collection for this case
        try:
            self.collection = self.chroma_client.get_collection(f"case_{case_id}_docs")
        except:
            self.collection = self.chroma_client.create_collection(
                name=f"case_{case_id}_docs",
                metadata={"description": f"Document chunks for case {case_id}"}
            )
        
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.llm = genai.GenerativeModel('gemini-pro')
    
    def ingest_pdf(self, pdf_path: str, doc_id: int, doc_name: str):
        """
        Ingest a PDF document into the RAG system
        Chunks it intelligently and stores embeddings
        """
        try:
            logger.info(f"Ingesting PDF: {doc_name} from {pdf_path}")
            
            # Extract text from PDF
            doc = fitz.open(pdf_path)
            chunks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # Split page into paragraphs/chunks
                paragraphs = text.split('\n\n')
                
                for para_idx, para in enumerate(paragraphs):
                    if len(para.strip()) < 50:  # Skip very short paragraphs
                        continue
                    
                    chunks.append({
                        'text': para.strip(),
                        'doc_id': doc_id,
                        'doc_name': doc_name,
                        'page': page_num + 1,
                        'chunk_id': f"{doc_id}_p{page_num + 1}_c{para_idx}"
                    })
            
            doc.close()
            
            if not chunks:
                logger.warning(f"No text chunks extracted from {doc_name}")
                return False
            
            # Generate embeddings and store in ChromaDB
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedder.encode(texts).tolist()
            
            ids = [chunk['chunk_id'] for chunk in chunks]
            metadatas = [{
                'doc_id': str(chunk['doc_id']),
                'doc_name': chunk['doc_name'],
                'page': chunk['page'],
                'case_id': str(self.case_id)
            } for chunk in chunks]
            
            # Add to vector database
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully ingested {len(chunks)} chunks from {doc_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting PDF {doc_name}: {str(e)}")
            return False
    
    def ingest_case_data(self, case_data: Dict[str, Any]):
        """
        Ingest structured case data (injuries, timeline, treatments, etc.)
        """
        try:
            chunks = []
            
            # Injuries
            if case_data.get('injuries'):
                injuries_text = "Documented Injuries:\n" + "\n".join([
                    f"- {injury}" for injury in case_data['injuries']
                ])
                chunks.append({
                    'text': injuries_text,
                    'type': 'injuries',
                    'chunk_id': f"case_{self.case_id}_injuries"
                })
            
            # Timeline events
            if case_data.get('timeline'):
                timeline_text = "Medical Timeline:\n" + "\n".join([
                    f"[{event['date']}] {event['facility']}: {event['description']}"
                    for event in case_data['timeline']
                ])
                chunks.append({
                    'text': timeline_text,
                    'type': 'timeline',
                    'chunk_id': f"case_{self.case_id}_timeline"
                })
            
            # Case details
            case_details = f"""
Case Information:
- Case Number: {case_data.get('case_no', 'N/A')}
- Client Name: {case_data.get('client_name', 'N/A')}
- Accident Date: {case_data.get('accident_date', 'N/A')}
- Accident Place: {case_data.get('accident_place', 'N/A')}
- FIR Number: {case_data.get('fir_no', 'N/A')}
- Claim Amount: {case_data.get('claim_amount', 'N/A')}
            """.strip()
            
            chunks.append({
                'text': case_details,
                'type': 'case_details',
                'chunk_id': f"case_{self.case_id}_details"
            })
            
            # Store in vector DB
            if chunks:
                texts = [chunk['text'] for chunk in chunks]
                embeddings = self.embedder.encode(texts).tolist()
                ids = [chunk['chunk_id'] for chunk in chunks]
                metadatas = [{
                    'type': chunk['type'],
                    'case_id': str(self.case_id),
                    'doc_name': 'Case Data'
                } for chunk in chunks]
                
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"Ingested {len(chunks)} case data chunks")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error ingesting case data: {str(e)}")
            return False
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant chunks for a query using vector similarity
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode([query])[0].tolist()
            
            # Search in vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            chunks = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    chunks.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def answer_question(self, question: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Answer a question using RAG
        Returns answer with source citations
        """
        try:
            # Retrieve relevant context
            relevant_chunks = self.retrieve_relevant_chunks(question, n_results=5)
            
            if not relevant_chunks:
                return {
                    'answer': "I don't have enough information in the case documents to answer that question. Could you try rephrasing or asking about something specific from the medical records?",
                    'sources': [],
                    'confidence': 'low'
                }
            
            # Build context from retrieved chunks
            context = "\n\n".join([
                f"[Source: {chunk['metadata'].get('doc_name', 'Case Data')}, Page {chunk['metadata'].get('page', 'N/A')}]\n{chunk['text']}"
                for chunk in relevant_chunks
            ])
            
            # Build conversation context
            conv_context = ""
            if conversation_history:
                conv_context = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in conversation_history[-3:]  # Last 3 messages
                ])
            
            # Create prompt for LLM
            prompt = f"""You are an expert legal AI assistant helping a lawyer with a motor accident case. Answer the user's question based ONLY on the provided case documents and context.

Case Documents Context:
{context}

{f'Recent Conversation:{conv_context}' if conv_context else ''}

User Question: {question}

Instructions:
- Answer clearly and concisely based on the provided context
- If the question asks about a specific page, focus on that page's content
- Cite sources with page numbers when possible
- If the information is not in the context, say so honestly
- For legal strategy questions, provide practical advice based on case facts
- Use bullet points for lists and clear formatting

Answer:"""
            
            # Generate answer using Gemini
            response = self.llm.generate_content(prompt)
            answer = response.text
            
            # Extract sources with page numbers
            sources = []
            seen_sources = set()
            for chunk in relevant_chunks:
                doc_name = chunk['metadata'].get('doc_name', 'Case Data')
                page = chunk['metadata'].get('page', 'N/A')
                source_key = f"{doc_name}_{page}"
                
                if source_key not in seen_sources:
                    sources.append({
                        'document': doc_name,
                        'page': page,
                        'excerpt': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                    })
                    seen_sources.add(source_key)
            
            return {
                'answer': answer,
                'sources': sources[:3],  # Top 3 sources
                'confidence': 'high' if len(relevant_chunks) >= 3 else 'medium',
                'chunks_found': len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 'error'
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed documents"""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'case_id': self.case_id,
                'status': 'ready' if count > 0 else 'empty'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
