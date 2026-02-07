# 🚀 QuickStart Guide - PromptOptimizer Pro

## ✅ All Errors Fixed!

All deprecation warnings and errors have been resolved. The system is ready to use.

---

## 📋 Prerequisites

1. **Python 3.12** installed
2. **Virtual environment** activated (you're already in `.venv`)
3. **API Key** - At least ONE of:
   - `ANTHROPIC_API_KEY` (recommended)
   - `GROQ_API_KEY` (free alternative)

---

## 🔧 Setup (If Not Done)

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-...
# OR
# GROQ_API_KEY=gsk_...
```

---

## 🎯 Three Ways to Use the System

### **Option 1: Interactive CLI Tool** ⭐ RECOMMENDED

The easiest way to test everything!

```bash
python cli.py
```

**Features:**
- Interactive menu system
- Colorful terminal output
- Analyze prompts for defects
- Optimize prompts automatically
- View all techniques
- Save results to files

**Example Session:**
```
1. Choose "3. Analyze + Optimize"
2. Enter your prompt (press Enter twice when done)
3. System analyzes with 4 agents in parallel
4. Shows defects found with evidence
5. Applies techniques to fix defects
6. Shows before/after comparison
7. Option to save optimized prompt
```

---

### **Option 2: Run API Server**

For testing API endpoints or building clients.

**Start Server:**
```bash
# Method 1: Direct (simplest)
python -m backend.app

# Method 2: With hot reload (best for development)
uvicorn backend.app:app --reload --port 8000

# Method 3: Production mode
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

**Access:**
- **Interactive API Docs**: http://localhost:8000/docs
- **API Info**: http://localhost:8000/
- **Health Check**: http://localhost:8000/api/health

**Test with curl:**
```bash
# Health check
curl http://localhost:8000/api/health

# Analyze a prompt
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a sorting function"}'

# Optimize a prompt
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write code",
    "optimization_level": "balanced",
    "max_techniques": 3
  }'

# List all techniques
curl http://localhost:8000/api/techniques
```

---

### **Option 3: Python Code**

For programmatic usage or custom scripts.

```python
import asyncio
from backend.services.agent_orchestrator import get_orchestrator
from backend.services.optimizer_service import get_optimizer

async def main():
    # Analyze a prompt
    orchestrator = get_orchestrator()
    analysis = await orchestrator.analyze_with_agents(
        prompt="Write a function to sort numbers",
        context={"task_type": "code_generation"}
    )

    print(f"Score: {analysis['overall_score']}/10")
    print(f"Defects: {len(analysis['defects'])}")

    # Optimize it
    optimizer = get_optimizer()
    result = await optimizer.optimize(
        prompt="Write a function to sort numbers",
        optimization_level="balanced",
        max_techniques=3,
        analysis=analysis  # Reuse analysis to save API calls
    )

    print(f"Improvement: {result['improvement_score']:+.1f}")
    print(f"Optimized: {result['optimized_prompt'][:100]}...")

asyncio.run(main())
```

---

## 🧪 Quick Test

**Test the CLI:**
```bash
python cli.py
```
Choose option 5 (System Information) to verify everything is configured.

**Test the API:**
```bash
# Terminal 1: Start server
python -m backend.app

# Terminal 2: Test health
curl http://localhost:8000/api/health
```

---

## 📊 Current System Status

### ✅ Completed Backend Components

1. **Core Infrastructure** (100%)
   - Configuration management
   - Logging & error handling
   - Token counting & validation
   - LLM service (Anthropic + Groq)

2. **Data Models** (100%)
   - 28 defect definitions
   - 15 technique definitions
   - Request/response schemas
   - Enums and validators

3. **Multi-Agent System** (100%)
   - 4 specialized agents (Clarity, Structure, Context, Security)
   - Parallel execution with asyncio
   - Consensus voting mechanism
   - Agent orchestrator

4. **Optimization Engine** (100%)
   - Technique selection algorithm
   - Category-based application
   - Verification loop (analyze → optimize → re-analyze)
   - Improvement scoring

5. **REST API** (100%)
   - FastAPI application
   - 5 endpoints (analyze, optimize, techniques, health, root)
   - Auto-generated OpenAPI docs
   - CORS support
   - Global exception handling

6. **Testing Tools** (100%)
   - Interactive CLI
   - Test scripts (test_optimizer.py)
   - Demo scripts (demo.py)

---

## 🎯 Next Steps Before Frontend

Before building the React frontend, consider these optional backend enhancements:

### **Priority 1: Add More Techniques** (Optional)
Currently: 15 techniques
Target: 25-30 techniques from the research paper

**Why:** Better optimization coverage for different defect types

**Effort:** 2-3 hours

---

### **Priority 2: Improve Agent Prompts** (Optional)
Enhance detection accuracy with better meta-prompts.

**Why:** More accurate defect detection = better optimizations

**Effort:** 1-2 hours

---

### **Priority 3: Add Batch Processing** (Optional)
Process multiple prompts at once from a file.

**Why:** Useful for testing and evaluation

**File:** `batch_processor.py`

**Effort:** 1 hour

---

### **Priority 4: Add Prompt History** (Optional)
Save optimization history to local JSON files.

**Why:** Track improvements over time, compare strategies

**Effort:** 2 hours

---

### **Priority 5: Add Export Formats** (Optional)
Export results to CSV, JSON, Markdown.

**Why:** Easier reporting and documentation

**Effort:** 1 hour

---

## 🎨 Moving to Frontend (React)

Once you're happy with the backend, the frontend will need:

### **Essential Features:**
1. **Prompt Input Form**
   - Textarea for prompt
   - Task type & domain dropdowns
   - Optimization level selector

2. **Analysis Display**
   - Overall score visualization (gauge/progress bar)
   - Defect list with severity badges
   - Agent breakdown
   - Evidence highlighting

3. **Optimization Display**
   - Before/after comparison (side-by-side)
   - Techniques applied (expandable cards)
   - Improvement metrics
   - Export/save buttons

4. **Techniques Browser**
   - Searchable/filterable list
   - Category grouping
   - Effectiveness ratings
   - Examples

### **Tech Stack Recommendations:**
- **Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS or Material-UI
- **State:** React Query for API calls
- **Charts:** Recharts or Chart.js
- **Routing:** React Router
- **Deployment:** Vercel or Netlify

### **API Integration:**
All endpoints are ready at `http://localhost:8000/api/*`

---

## 📝 Summary

### **How to Run Right Now:**

```bash
# Option 1: Interactive CLI (easiest)
python cli.py

# Option 2: API Server
python -m backend.app
# Then visit: http://localhost:8000/docs

# Option 3: Demo script
python demo.py
```

### **What Works:**
✅ Analyze prompts for defects
✅ Optimize prompts with techniques
✅ Multi-agent consensus voting
✅ REST API with 5 endpoints
✅ Interactive CLI tool
✅ Auto-generated API docs

### **What's Next:**
1. **Now:** Test the CLI and API, explore the system
2. **Optional:** Add more techniques/features if needed
3. **Then:** Build React frontend for better UX

---

## 🐛 Troubleshooting

### **No API keys configured**
- Edit `.env` file
- Add `ANTHROPIC_API_KEY=sk-ant-...` or `GROQ_API_KEY=gsk_...`

### **Import errors**
- Activate virtual environment: `.venv\Scripts\activate`
- Reinstall: `pip install -r backend/requirements.txt`

### **Port 8000 already in use**
- Change port: `uvicorn backend.app:app --port 8001`

### **Rate limits (Groq)**
- Use Anthropic API key instead
- Or add delays between requests

---

## 📚 Documentation

- **API Docs:** http://localhost:8000/docs (when server is running)
- **Architecture:** See `SESSION_SUMMARY.md`
- **Research Paper:** See `CLAUDE.md` for references
- **Implementation:** See `IMPLEMENTATION_COMPLETE.md`

---

**You're all set! Try running `python cli.py` now! 🚀**
