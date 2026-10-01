"""
Simple RAG System - No TensorFlow, No sentence-transformers
Uses Gemini embeddings API for lightweight vector search
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class SimpleCaseRAG:
    """
    Lightweight RAG system using only Gemini (no heavy dependencies)
    """
    
    def __init__(self, case_id: int):
        self.case_id = case_id
        self.storage_dir = f"./rag_storage/case_{case_id}"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Configure Gemini - use Flash models (same as views.py)
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            # Try Flash models in order of preference
            self.models_to_try = [
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash-lite", 
                "gemini-2.0-flash",
                "gemini-flash-lite-latest",
                "gemini-2.5-flash",
                "gemini-1.5-flash",
            ]
        else:
            logger.error("GEMINI_API_KEY not set")
            self.models_to_try = []
        
        # Load existing chunks
        self.chunks = self._load_chunks()
    
    def _load_chunks(self) -> List[Dict]:
        """Load chunks from JSON file"""
        chunks_file = os.path.join(self.storage_dir, "chunks.json")
        if os.path.exists(chunks_file):
            try:
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading chunks: {e}")
        return []
    
    def _save_chunks(self):
        """Save chunks to JSON file"""
        chunks_file = os.path.join(self.storage_dir, "chunks.json")
        try:
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving chunks: {e}")
    
    def ingest_pdf(self, pdf_path: str, doc_id: int, doc_name: str):
        """Ingest PDF into simple text storage"""
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # Split into paragraphs
                paragraphs = text.split('\n\n')
                
                for para_idx, para in enumerate(paragraphs):
                    if len(para.strip()) < 50:
                        continue
                    
                    self.chunks.append({
                        'text': para.strip(),
                        'doc_id': doc_id,
                        'doc_name': doc_name,
                        'page': page_num + 1,
                        'chunk_id': f"{doc_id}_p{page_num + 1}_c{para_idx}",
                        'type': 'pdf'
                    })
            
            doc.close()
            self._save_chunks()
            logger.info(f"✅ Ingested {doc_name} for case {self.case_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting PDF: {e}")
            return False
    
    def ingest_case_data(self, case_data: Dict[str, Any]):
        """Ingest structured case data"""
        try:
            # Injuries
            if case_data.get('injuries'):
                injuries_text = "Documented Injuries:\n" + "\n".join([
                    f"- {injury}" for injury in case_data['injuries']
                ])
                self.chunks.append({
                    'text': injuries_text,
                    'type': 'injuries',
                    'doc_name': 'Case Data',
                    'page': 'N/A',
                    'chunk_id': f"case_{self.case_id}_injuries"
                })
            
            # Timeline
            if case_data.get('timeline'):
                timeline_text = "Medical Timeline:\n" + "\n".join([
                    f"[{event['date']}] {event['facility']}: {event['description']}"
                    for event in case_data['timeline']
                ])
                self.chunks.append({
                    'text': timeline_text,
                    'type': 'timeline',
                    'doc_name': 'Case Data',
                    'page': 'N/A',
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
            
            self.chunks.append({
                'text': case_details,
                'type': 'case_details',
                'doc_name': 'Case Data',
                'page': 'N/A',
                'chunk_id': f"case_{self.case_id}_details"
            })
            
            self._save_chunks()
            logger.info(f"✅ Ingested case data for case {self.case_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting case data: {e}")
            return False
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Simple keyword-based retrieval (no vectors needed)
        Ranks chunks by keyword overlap
        """
        if not self.chunks:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each chunk
        scored_chunks = []
        for chunk in self.chunks:
            text_lower = chunk['text'].lower()
            chunk_words = set(text_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words & chunk_words)
            
            # Bonus for exact phrase match
            if query_lower in text_lower:
                overlap += 10
            
            # Bonus for page-specific queries
            if 'page' in query_lower:
                import re
                page_match = re.search(r'page\s+(\d+)', query_lower)
                if page_match and str(chunk.get('page')) == page_match.group(1):
                    overlap += 20
            
            if overlap > 0:
                scored_chunks.append({
                    'chunk': chunk,
                    'score': overlap
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N
        return [item['chunk'] for item in scored_chunks[:n_results]]
    
    def answer_question(self, question: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Answer question using retrieved context"""
        try:
            if not self.models_to_try:
                return {
                    'answer': 'AI service not configured. Please set GEMINI_API_KEY.',
                    'sources': [],
                    'confidence': 'error'
                }
            
            # Retrieve relevant chunks
            relevant_chunks = self.retrieve_relevant_chunks(question, n_results=5)
            
            if not relevant_chunks:
                return {
                    'answer': "I don't have enough information in the case documents to answer that question. Could you try rephrasing or asking about something specific from the medical records?",
                    'sources': [],
                    'confidence': 'low'
                }
            
            # Build context
            context = "\n\n".join([
                f"[Source: {chunk.get('doc_name', 'Unknown')}, Page {chunk.get('page', 'N/A')}]\n{chunk['text']}"
                for chunk in relevant_chunks
            ])
            
            # Build conversation context
            conv_context = ""
            if conversation_history:
                conv_lines = []
                for msg in conversation_history[-3:]:
                    role = 'User' if msg['role'] == 'user' else 'Assistant'
                    conv_lines.append(f"{role}: {msg['content']}")
                conv_context = "\n".join(conv_lines)
            
            # Create prompt
            recent_conv = f'Recent Conversation:\n{conv_context}' if conv_context else ''
            
            prompt = f"""You are an expert legal AI assistant helping a lawyer with a motor accident case. Answer the user's question based ONLY on the provided case documents and context.

Case Documents Context:
{context}

{recent_conv}

User Question: {question}

Instructions:
- Answer clearly and concisely based on the provided context
- If the question asks about a specific page, focus on that page's content
- Cite sources with page numbers when possible
- If the information is not in the context, say so honestly
- For legal strategy questions, provide practical advice based on case facts
- Use bullet points for lists and clear formatting

Answer:"""
            
            # Try models in order until one works
            answer = None
            last_error = None
            
            for model_name in self.models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    answer = response.text
                    if answer:
                        logger.info(f"✅ Chat answer generated with {model_name}")
                        break
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Model {model_name} failed: {str(e)[:100]}")
                    continue
            
            if not answer:
                logger.error(f"All models failed. Last error: {last_error}")
                return {
                    'answer': "I couldn't generate an answer due to an AI service issue. Please try again.",
                    'sources': [],
                    'confidence': 'error'
                }
            
            # Extract sources
            sources = []
            seen_sources = set()
            for chunk in relevant_chunks:
                doc_name = chunk.get('doc_name', 'Case Data')
                page = chunk.get('page', 'N/A')
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
                'sources': sources[:3],
                'confidence': 'high' if len(relevant_chunks) >= 3 else 'medium',
                'chunks_found': len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': f"I encountered an error: {str(e)}",
                'sources': [],
                'confidence': 'error'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'total_chunks': len(self.chunks),
            'case_id': self.case_id,
            'status': 'ready' if len(self.chunks) > 0 else 'empty'
        }
