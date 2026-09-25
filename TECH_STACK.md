# 🛠️ Tech Stack Summary

## Legal AI Platform - Complete Technology Stack

---

## 🔷 **Backend Frameworks**

### Django Application (Legal AI Core)
- **Django 5.2.10** - Main web framework for case management
- **Django REST Framework** - API endpoints for case/document management
- **SQLite3** - Database for cases, documents, drafts, timeline
- **Python 3.11** - Core programming language

### Flask Application (MedCompliance Agents)
- **Flask 3.0+** - Lightweight web framework for agent orchestration
- **Flask Sessions** - User session management
- **Gunicorn** - Production WSGI server

---

## 🤖 **AI & Machine Learning**

### LLM & Generative AI
- **Google Gemini API** - Primary LLM for all AI operations
  - Models: `gemini-2.5-flash-lite`, `gemini-2.0-flash-lite`, `gemini-2.0-flash`
  - Fallback chain for quota management
- **google-generativeai SDK** - Python client for Gemini

### Agent Framework
- **LangGraph 0.2+** - Agent workflow orchestration
  - State management for multi-agent systems
  - Sequential agent execution with fallback
  - 4-agent pipeline: Intake → Compliance → Risk → Audit

### RAG (Retrieval-Augmented Generation)
- **FAISS** - Vector database for semantic search
- **LangChain** - RAG pipeline and document processing
- **Sentence Transformers** - Text embeddings
- Knowledge base with medical rules, laws, judgments

---

## 📄 **Document Processing**

- **PyMuPDF (fitz)** - PDF text extraction and parsing
- **python-docx** - DOCX file handling
- **FPDF** - PDF generation for reports and drafts
- **ReportLab** - Advanced PDF creation

---

## 🎨 **Frontend Technologies**

### UI Framework
- **HTML5** - Semantic markup
- **CSS3** - Custom styling with animations
- **JavaScript (Vanilla)** - Interactive components
- **Bootstrap 5** - Responsive grid and components

### Templates
- **Django Templates** - Server-side rendering for Legal AI
- **Jinja2** - Flask templating for MedCompliance

### Design Elements
- **Custom CSS Animations** - Hover effects, transitions
- **Maroon Theme (#7B2C2C)** - Consistent branding
- **Responsive Design** - Mobile-friendly layouts

---

## 🗄️ **Database & Storage**

- **SQLite3** - Relational database
  - Cases, Documents, Drafts, Timeline models
  - Django ORM for queries
- **File System Storage** - Media uploads
  - Medical records
  - Legal documents
  - Generated reports

---

## 🔐 **Security & Configuration**

- **python-dotenv** - Environment variable management
- **.env** - Secure API key storage
- **.gitignore** - Prevents secret exposure
- **GitHub Secret Scanning** - Repository security
- **Input Validation** - Secure file uploads

---

## 🚀 **Deployment & DevOps**

### Local Development
- **Python Virtual Environments** - Dependency isolation
- **Django Development Server** - Port 8000
- **Flask Development Server** - Port 7000

### Production Ready
- **Render.com** - Cloud deployment platform
- **Gunicorn** - WSGI production server
- **render.yaml** - Infrastructure as code
- **requirements.txt** - Dependency management

### Version Control
- **Git** - Source control
- **GitHub** - Repository hosting
- Remote: `https://github.com/Ajinkya-Ghuge/LEGAL-AI-.git`

---

## 📦 **Key Python Libraries**

### Core Dependencies
```
Django==5.2.10
djangorestframework==3.15.2
Flask==3.0+
google-generativeai==0.8.3
langgraph==0.2.45
langchain==0.3.7
python-dotenv==1.0.1
```

### Document Processing
```
PyMuPDF==1.24.13
python-docx==1.1.2
fpdf==1.7.2
reportlab==4.2.5
```

### ML & AI
```
faiss-cpu==1.9.0
sentence-transformers==3.3.1
```

---

## 🏗️ **Architecture Patterns**

### Design Patterns
- **MVC (Model-View-Controller)** - Django apps structure
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic separation
- **Multi-Agent System** - LangGraph workflow

### API Architecture
- **RESTful APIs** - Django REST endpoints
- **JSON Responses** - Standard data format
- **File Upload APIs** - Multipart form data

---

## 📊 **Data Flow**

### Legal AI Flow
```
User Upload → Django View → PyMuPDF Parser → Gemini AI → 
RAG Vault Search → AI Analysis → Template Render → User
```

### MedCompliance Flow
```
Upload → Flask Route → Intake Agent → Compliance Agent (RAG) → 
Risk Agent → Audit Agent → Report Generation → Dashboard
```

---

## 🧪 **Testing & Quality**

- **Manual Testing** - Both applications tested with real medical records
- **Error Handling** - Try-catch blocks, fallback mechanisms
- **API Quota Management** - Multiple model fallback chain
- **Logging** - Flask debug mode, Django development server logs

---

## 📱 **Features by Tech**

### Django Features
- ✅ Case management system
- ✅ Document upload & parsing
- ✅ Medical record analysis
- ✅ Draft generation (Legal Notice, Affidavit, Claim Petition)
- ✅ Timeline tracking
- ✅ Compensation calculation

### Flask + LangGraph Features
- ✅ 4-agent workflow orchestration
- ✅ Real-time agent progress display
- ✅ RAG-powered compliance checking
- ✅ Risk assessment (Clinical, Legal, Financial)
- ✅ Comprehensive audit reports
- ✅ Professional landing page & dashboard

---

## 🌐 **API Integrations**

- **Google Gemini API** - All LLM operations
- **FAISS Vector Store** - Local embeddings (no external API)

---

## 📈 **Scalability Features**

- **Modular Architecture** - Separate Django apps
- **Agent Isolation** - Each agent independent
- **Model Fallback** - Handles quota limits automatically
- **Session Management** - Multi-user support
- **Cloud Ready** - Render deployment configured

---

## 🎯 **Summary Statistics**

- **Languages**: Python (Backend), HTML/CSS/JS (Frontend)
- **Frameworks**: Django + Flask
- **AI Models**: Google Gemini (3 variants)
- **Agents**: 4 specialized LangGraph agents
- **Database**: SQLite with Django ORM
- **PDF Libraries**: PyMuPDF, FPDF, ReportLab
- **Deployment**: Local + Render.com ready
- **Security**: .env + .gitignore + GitHub protection

---

**Built for**: Legal AI + Medical Compliance Analysis  
**Deployment Status**: ✅ Production Ready  
**GitHub**: https://github.com/Ajinkya-Ghuge/LEGAL-AI-.git
