# RAG Chatbot Testing Guide 🧪

## Quick Start Testing

### Prerequisites
✅ Django server running (`python backend/manage.py runserver`)
✅ GEMINI_API_KEY configured in `.env`
✅ All dependencies installed (`pip install -r requirements.txt`)

---

## Test Scenario 1: Basic Chat Functionality

### Step 1: Navigate to Case
1. Go to Dashboard
2. Click on any case (or create a new one)
3. You should see the chat panel on the right side

### Step 2: Test Without Documents
**Action:** Type a question like "What are the main injuries?"

**Expected Result:**
```
"I don't have any case documents ingested yet. 
Please upload case documents and try again."
```

### Step 3: Upload a PDF
1. Go to "Expense & Bills" tab
2. Click "Upload Document"
3. Select a medical record PDF
4. Wait for "Processing complete" message

**Behind the scenes:**
- PDF text extracted
- Document chunked into paragraphs
- Embeddings generated
- Stored in ChromaDB at `./chroma_db/case_{case_id}/`

### Step 4: Ask Questions
Try these questions:

**Q1:** "What are the main injuries documented?"
**Expected:** List of injuries with page sources

**Q2:** "Summarize page 4"
**Expected:** Summary of page 4 content with source citation

**Q3:** "What medications were prescribed?"
**Expected:** List of medications with source pages

**Q4:** "When was the accident?"
**Expected:** Accident date from case data or documents

**Q5:** "Calculate compensation under Section 166"
**Expected:** Breakdown of compensation heads with reasoning

---

## Test Scenario 2: Source Citations

### Check Every Answer
Every response should include sources like:
```
Sources: Page 4 of Medical Records, Page 12 of Discharge Summary
```

### Verify Sources Are Accurate
1. Click "View in PDF" button for an injury
2. Note the page number
3. Ask chatbot about that specific injury
4. Verify chatbot cites the same page

---

## Test Scenario 3: Conversation Context

### Multi-Turn Conversation
**Turn 1:** "What injuries did the patient sustain?"
**Turn 2:** "Which one was the most severe?"
**Turn 3:** "What treatment was given for that?"

**Expected:** Bot remembers previous context (last 3 messages)

---

## Test Scenario 4: Page-Specific Questions

### Direct Page Query
**Q:** "What is written on page 7?"
**Expected:** Content from page 7 specifically

### Range Query
**Q:** "Summarize pages 5 to 8"
**Expected:** Summary of that page range

---

## Test Scenario 5: Error Handling

### Case 1: No Documents
- Ask question before uploading PDF
- Should get friendly "no documents" message

### Case 2: Question Out of Scope
**Q:** "What's the weather today?"
**Expected:** "I don't have enough information in the case documents..."

### Case 3: Empty Question
- Send empty message
- Should handle gracefully

---

## Test Scenario 6: Multiple Documents

### Upload Second PDF
1. Upload another medical document
2. Wait for processing
3. Ask questions spanning both documents

**Q:** "What treatments are mentioned across all documents?"
**Expected:** Aggregated list from all uploaded PDFs with sources from each

---

## Verification Checklist

### Functional Tests
- [ ] Chat UI loads without errors
- [ ] Messages send successfully
- [ ] Typing indicator shows while processing
- [ ] Responses appear in chat bubble
- [ ] Sources are displayed at bottom of answer
- [ ] Shift+Enter adds new line (doesn't send)
- [ ] Clear chat button works
- [ ] Suggested questions work when clicked

### Accuracy Tests
- [ ] Answers are relevant to questions
- [ ] Sources cited are accurate (match PDF page)
- [ ] No hallucinations (all info from documents)
- [ ] Handles "I don't know" gracefully
- [ ] Conversation context maintained

### Performance Tests
- [ ] Response time < 5 seconds per query
- [ ] PDF ingestion completes within 10 seconds
- [ ] No memory leaks with multiple queries
- [ ] ChromaDB persists across server restarts

### UI/UX Tests
- [ ] Professional appearance
- [ ] Readable font and spacing
- [ ] Smooth animations
- [ ] Mobile responsive (if applicable)
- [ ] Error messages are user-friendly

---

## Debugging

### If Chat Doesn't Respond
1. Check browser console for JavaScript errors
2. Check Django logs for Python errors:
   ```bash
   tail -f backend/django.log
   ```
3. Verify `/api/chat/` endpoint in Network tab

### If Sources Are Wrong
1. Check PDF extraction quality:
   - Open document in admin panel
   - Verify `extracted_text` field has content
2. Check RAG ingestion logs:
   - Look for "✅ RAG ingestion complete" messages

### If Answers Are Poor Quality
1. Check ChromaDB collection:
   ```python
   from apps.web.case_rag import CaseRAGSystem
   rag = CaseRAGSystem(case_id=1)
   stats = rag.get_collection_stats()
   print(stats)  # Should show total_chunks > 0
   ```

2. Check retrieval results:
   ```python
   chunks = rag.retrieve_relevant_chunks("injuries", n_results=5)
   print(len(chunks))  # Should return relevant chunks
   ```

---

## Common Issues & Solutions

### Issue: "GEMINI_API_KEY not set"
**Solution:** Add to `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### Issue: "chromadb module not found"
**Solution:** Install dependencies:
```bash
pip install chromadb sentence-transformers
```

### Issue: PDF text not extracted
**Solution:** Check PDF is not:
- Password protected
- Scanned image (needs OCR)
- Corrupted

### Issue: Slow responses
**Possible causes:**
- Large PDFs (split into smaller chunks)
- Too many chunks retrieved (reduce n_results)
- Slow Gemini API (check API limits)

---

## Advanced Testing

### Test RAG Quality
**Precision Test:** Ask very specific questions
- "What was prescribed on January 15th?"
- "What did Dr. Smith say about the fracture?"

**Recall Test:** Ask broad questions
- "What are ALL injuries mentioned?"
- "List every medication prescribed"

**Accuracy Test:** Cross-verify answers
- Compare chatbot answers with actual PDF content
- Check if page numbers are correct

### Test Edge Cases
- Very long questions (>500 words)
- Questions in different languages
- Medical terminology queries
- Legal jargon questions

---

## Success Criteria

### Must Pass:
✅ Basic Q&A works for uploaded PDFs
✅ Sources are cited accurately
✅ Conversation context maintained
✅ Error handling is graceful
✅ Performance is acceptable (<5s per query)

### Nice to Have:
🎯 Answers are professional and legally sound
🎯 Can handle complex multi-document queries
🎯 Provides legal strategy suggestions
🎯 Sources link to PDF viewer (future enhancement)

---

## Reporting Issues

If you find bugs, note:
1. **Question asked**
2. **Expected answer**
3. **Actual answer received**
4. **Error messages (if any)**
5. **Browser console logs**
6. **Django server logs**

---

## Next Steps After Testing

Once basic tests pass:
1. Test with REAL medical records (not sample PDFs)
2. Test with multiple documents per case
3. Test conversation history persistence
4. Test with different case types (not just MACT)
5. Load test with many concurrent users
6. Security test for injection attacks

---

**Happy Testing! 🚀**

If all tests pass, Phase 3 is production-ready! ✅
