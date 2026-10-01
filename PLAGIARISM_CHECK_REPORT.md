# Plagiarism Check Report - LegalAI Paper

## Date: February 2026

## Summary
Initial web-based plagiarism check conducted. Overall assessment: **LOW TO MODERATE RISK** with recommended actions below.

## Potential Overlaps Found

### 1. IIT Delhi MACT RAG System (HIGH PRIORITY)
- **Source**: https://home.iitd.ac.in/public/storage/viva_abstracts/viva/abstracts/2020MEZ8831_abstract.pdf
- **Overlap**: Similar domain (MACT) + approach (RAG system)
- **Risk Level**: HIGH - Must cite if they published first
- **Action Required**: 
  - Download and review the IIT Delhi abstract/thesis
  - Cite it in Related Work section
  - Clearly differentiate your contributions (page classification algorithm, specific tech stack, pilot evaluation)

### 2. General Legal RAG Systems
Multiple papers exist on RAG for legal domains:
- arXiv paper on Indian legal RAG systems
- Harvard JOLT article on RAG for legal work
- Multiple GitHub projects on legal document RAG

**Action**: Add these to Related Work section and differentiate your MACT-specific focus

## Unique Contributions (Safe from Plagiarism)

✅ **Your Algorithm 1**: Intelligent page selection with priority-based + relevance-based phases
✅ **Specific Tech Stack**: Django + Gemini 2.5 Flash + PyMuPDF + FAISS combination
✅ **Pilot Evaluation**: 18 cases, 7 lawyers, Maharashtra-specific
✅ **Sarla Verma Formula Implementation**: Specific compensation calculator
✅ **Deployment Details**: Render + Supabase architecture at $7/month

## Professional Plagiarism Check Recommendations

### Free Tools (Basic Check)
1. **Turnitin** (if your institution provides access)
2. **Grammarly Plagiarism Checker** (limited free version)
3. **Quetext** (https://www.quetext.com/) - 500 words free
4. **Duplichecker** (https://www.duplichecker.com/) - 1000 words free
5. **Plagiarism Detector** (https://plagiarismdetector.net/) - 1000 words free

### Paid Tools (Comprehensive)
1. **iThenticate** - Industry standard for academic papers ($50-100)
2. **Copyscape Premium** - Good for web content ($0.03-0.05 per search)
3. **Plagscan** - Academic-focused (€5-20)

### IEEE Specific
- **IEEE CrossCheck** - Available through IEEE submission portal (uses iThenticate)
- IEEE will run plagiarism check during peer review

## Immediate Actions Required

### 1. Download and Review IIT Delhi Work (URGENT)
```bash
# Download the PDF
wget https://home.iitd.ac.in/public/storage/viva_abstracts/viva/abstracts/2020MEZ8831_abstract.pdf -O iitd_mact_rag.pdf
```

### 2. Update Related Work Section
Add proper citations for:
- IIT Delhi MACT RAG work (if relevant)
- Recent legal RAG papers from arXiv
- Indian legal AI systems

### 3. Strengthen Your Differentiation
Emphasize what makes YOUR work unique:
- Novel page-classification algorithm (Algorithm 1)
- Specific evaluation on real MACT cases
- Production deployment with cost analysis
- Lawyer feedback and SUS scores
- Open-source, API-first design

### 4. Run Professional Check
Before submission:
- Use at least one paid tool (iThenticate recommended)
- Target: <15% similarity (excluding references)
- Investigate any match >2% carefully

## Citation Fixes Needed

Review your references [1-20] and ensure:
- All factual claims about Indian legal system have citations
- All technical approaches (RAG, FAISS, PyMuPDF) properly cited
- Related legal AI systems properly cited
- No verbatim text from sources without quotation marks

## Self-Check Questions

Before submission, verify:
- [ ] Downloaded and reviewed IIT Delhi MACT work
- [ ] Added differentiation paragraph in Introduction
- [ ] Cited all similar RAG legal systems in Related Work
- [ ] Ran professional plagiarism check (target <15%)
- [ ] All technical definitions properly attributed
- [ ] No copied text without quotation marks + citation
- [ ] Paraphrased all background information
- [ ] Algorithm 1 is your original work (or cited if adapted)

## Risk Assessment

**Overall Risk Level**: MODERATE
- High overlap in domain/approach with IIT Delhi work
- Must carefully differentiate your contributions
- With proper citations and differentiation: LOW RISK

**Recommendation**: PROCEED WITH CAUTIONS ABOVE

## Next Steps

1. **Today**: Download IIT Delhi abstract, review for overlap
2. **Tomorrow**: Run paper through Quetext/Duplichecker for initial check
3. **Before submission**: Purchase iThenticate check ($50-100)
4. **Before submission**: Add 2-3 sentences in intro clearly stating what's novel vs. prior work
5. **Before submission**: Update Related Work section with proper differentiation

---

**Report Generated**: February 2026
**Reviewer**: Automated Web Search + Manual Analysis
**Status**: REQUIRES ACTION BEFORE SUBMISSION
