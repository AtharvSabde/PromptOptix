# 🎯 PromptOptimizer Pro

**Automated Prompt Engineering Tool with Multi-Agent Defect Detection**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📚 Research Background

This project implements the findings from our published survey paper:

**"A Comprehensive Survey of Prompt Engineering Techniques and Defect Taxonomies"**  
*Nagpure et al., 2025, International Journal of Fundamental & Applied Research*

### Key Research Gaps Addressed

Our survey identified that:
- ✅ **60-80% of developer time** is spent in trial-and-error prompt engineering
- ✅ **No automated defect detection tools exist** for systematic prompt analysis
- ✅ **28 defect types** were cataloged from literature (Tian et al.'s taxonomy)
- ✅ **41 prompting techniques** were documented but lack automated application

**PromptOptimizer Pro fills this gap** by being the first tool to automate defect detection and technique application based on peer-reviewed research.

---

## 🚀 Features

### 1. **Multi-Agent Defect Detection**
- **4 Specialized Agents** working in parallel:
  - 🔍 **Clarity Agent** → Detects specification & intent defects
  - 📋 **Structure Agent** → Detects formatting & organization issues
  - 🧠 **Context Agent** → Detects memory & relevance problems
  - 🛡️ **Security Agent** → Detects injection & safety vulnerabilities
- **Consensus Mechanism** → Agents vote on severity, system aggregates results

### 2. **Adaptive Optimization**
- Maps detected defects to appropriate techniques from the 41-technique catalog
- Rule-based + LLM-guided technique selection
- Generates optimized prompts with detailed change logs

### 3. **A/B Testing & Evaluation**
- Side-by-side comparison of original vs. optimized prompts
- Quality metrics: clarity, completeness, structure, coherence
- Statistical significance testing
- Token count reduction tracking

### 4. **Research-Backed Taxonomy**
- Implements **Tian et al.'s 28 defects** across 6 dimensions:
  1. Specification & Intent (4 defects)
  2. Structure & Formatting (5 defects)
  3. Context & Memory (5 defects)
  4. Output Guidance (4 defects)
  5. Examples & Demonstrations (4 defects)
  6. Security & Safety (6 defects)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Future React Frontend)                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Flask API Layer                         │
│  /api/analyze  |  /api/optimize  |  /api/test           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Multi-Agent Orchestrator                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Clarity  │ │Structure │ │ Context  │ │ Security │  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                  Consensus Mechanism                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Optimization Engine                         │
│  Defect→Technique Mapper  |  Adaptive Selector          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                LLM Service Layer                         │
│      Anthropic Claude API  |  Groq API (Fallback)       │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- API keys from [Anthropic](https://console.anthropic.com/) and/or [Groq](https://console.groq.com/)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/promptoptimizer-pro.git
cd promptoptimizer-pro
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp ../.env.example ../.env
# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_key_here
# GROQ_API_KEY=your_key_here
```

5. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

---

## 🧪 Usage

### API Endpoints

#### 1. Analyze Prompt
**POST** `/api/analyze`

Detect defects in a prompt using multi-agent analysis.

```json
{
  "prompt": "Write a function to sort numbers",
  "task_type": "code_generation",
  "domain": "software_engineering"
}
```

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "defects": [
      {
        "type": "underspecification",
        "severity": "high",
        "confidence": 0.85,
        "description": "Missing algorithm specification",
        "agent": "clarity",
        "remediation": "Specify sorting algorithm (quicksort, mergesort, etc.)"
      }
    ],
    "overall_score": 6.2,
    "agent_consensus": 0.78
  }
}
```

#### 2. Optimize Prompt
**POST** `/api/optimize`

Apply techniques to fix detected defects.

```json
{
  "prompt": "Write a function to sort numbers",
  "analysis": { /* from /analyze endpoint */ },
  "optimization_level": "balanced"
}
```

**Response:**
```json
{
  "status": "success",
  "original_prompt": "Write a function to sort numbers",
  "optimized_prompt": "Write a Python function that implements the quicksort algorithm to sort a list of integers in ascending order. Include docstrings and handle edge cases.",
  "techniques_applied": [
    "specification_enhancement",
    "example_inclusion",
    "constraint_addition"
  ],
  "change_log": [
    "Added language specification (Python)",
    "Specified algorithm (quicksort)",
    "Added output format requirement (ascending order)"
  ],
  "improvement_score": 8.7
}
```

#### 3. A/B Test
**POST** `/api/test`

Compare original vs. optimized prompts.

```json
{
  "original_prompt": "Write a function to sort numbers",
  "optimized_prompt": "Write a Python function...",
  "test_input": "Sample test case",
  "iterations": 5
}
```

---

## 🎓 Research Alignment

This implementation directly maps to our published survey:

| Survey Section | Implementation Component |
|----------------|--------------------------|
| Section 4: 41 Techniques | `models/technique_registry.py` |
| Section 5: Tian et al.'s 28 Defects | `models/defect_taxonomy.py` |
| Section 6: Evaluation Frameworks | `evaluation/automated_metrics.py` |
| Multi-Agent Systems (Citation 47-52) | `agents/` directory |
| Adaptive Optimization (Citation 28-35) | `services/optimizer_service.py` |

**Full citation mapping:** See [docs/SURVEY_ALIGNMENT.md](docs/SURVEY_ALIGNMENT.md)

---

## 📊 Evaluation

### Test Dataset
- 50+ prompts from public datasets
- Self-annotated with defect types
- Covers 9 task types across 8 domains

### Metrics
- **Defect Detection Accuracy:** % of correctly identified defects
- **Optimization Effectiveness:** Quality score improvement
- **Token Reduction:** % decrease in prompt length
- **Statistical Significance:** p-value < 0.05

### Running Evaluation
```bash
python scripts/evaluate_system.py
```

---

## 🗂️ Project Structure

```
promptoptimizer-pro/
├── backend/
│   ├── app.py                    # Flask application entry point
│   ├── config.py                 # Configuration management
│   ├── agents/                   # Multi-agent system
│   │   ├── clarity_agent.py
│   │   ├── structure_agent.py
│   │   ├── context_agent.py
│   │   └── security_agent.py
│   ├── services/                 # Business logic
│   │   ├── llm_service.py
│   │   ├── analyzer_service.py
│   │   ├── optimizer_service.py
│   │   └── agent_orchestrator.py
│   ├── models/                   # Data models
│   │   ├── defect_taxonomy.py    # 28 defects
│   │   └── technique_registry.py # 41 techniques
│   └── routes/                   # API endpoints
├── data/
│   └── test_prompts/             # Evaluation dataset
├── docs/
│   ├── SURVEY_ALIGNMENT.md       # Research mapping
│   ├── DEFECT_TAXONOMY.md        # Complete defect list
│   └── API.md                    # API documentation
└── README.md
```

---

## 🔬 Key Innovations

1. **First Automated Implementation** of Tian et al.'s taxonomy
2. **Multi-Agent Architecture** with consensus mechanism
3. **Adaptive Technique Selection** based on defect types
4. **Research-Backed** - every feature maps to published literature

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📖 Citation

If you use this tool in your research, please cite our survey paper:

```bibtex
@article{nagpure2025promptsurvey,
  title={A Comprehensive Survey of Prompt Engineering Techniques and Defect Taxonomies},
  author={Nagpure, [Your Name] and [Co-authors]},
  journal={International Journal of Fundamental \& Applied Research},
  year={2025},
  publisher={IJFMR}
}
```

---

## 👥 Authors

- **[Your Name]** - *Lead Developer & Researcher*
- **[Team Members]** - *Co-authors*

**Institution:** [Your University]  
**Program:** Final Year Computer Engineering Project

---

## 🙏 Acknowledgments

- **Tian et al.** for the comprehensive defect taxonomy
- **Anthropic** for Claude API access
- **Groq** for fast inference capabilities
- All authors cited in our survey paper

---

## 📞 Contact

For questions or collaboration:
- **Email:** your.email@university.edu
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/promptoptimizer-pro/issues)
- **Research Paper:** [Link to IJFMR publication]

---

**Built with ❤️ for the prompt engineering research community**