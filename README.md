# CompilerX – Advanced Compiler Front-End with Interactive Source Code Analysis

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask)
![Tests](https://img.shields.io/badge/tests-56_passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-80%25-green)
![License](https://img.shields.io/badge/license-Academic-lightgrey)

> A production-quality, web-based compiler front-end that visually demonstrates all major compiler design phases – with an AI-powered Fix-It engine that takes code to 100% Health.

**Live Demo:** `https://compiler-project-xxxx.onrender.com` ← Replace with your Render URL after Phase 10 deploy  
**Course:** Compiler Design – Semester End Project – 2026

---

### Screenshot
```
┌─────────────────────────────────────────────────────────────┐
│  CompilerX  |  Compiler Workspace    [Load Sample][Clear][Export▼] │
├──────────────────────────┬──────────────────────────────────┤
│  Source Code Editor      │  Analysis Results                │
│  int a = 10;             │  ● Overview | Tokens | Syntax …  │
│  int b = 20;             │  Health Score: 100  Excellent    │
│  int sum = a + b;        │  Tokens: 18  Errors: 0  Symbols:3│
│  return sum;             │                                  │
│                          │  💡 Suggestions Tab →            │
│  [Analyze Code]          │  0 issues – Code is clean!       │
└──────────────────────────┴──────────────────────────────────┘
```
Dark VS Code / GitHub inspired UI. Fully responsive.

---

### Features

- ✅ **Lexical Analyzer** – Tokenizes keywords, identifiers, operators, integers, floats, strings – with exact line/column tracking – supports `//` and `/* */` comments
- ✅ **Syntax Analyzer (Advanced v2)** – 10+ grammar rules, missing semicolon detection before statement starters, orphan identifier detection, unmatched braces/parens – C/C++/Java robust
- ✅ **Symbol Table Generator** – type, category, scope_level, line_declared, line_used
- ✅ **Scope Analyzer** – Visual scope tree, global / function / block scopes, parent-child hierarchy
- ✅ **Error Detector** – Duplicate declaration warnings, undeclared variable errors, **type mismatch detection** (`int x = "hello"`)
- ✅ **Code Metrics** – 18 metrics: lines, keywords, identifiers, operators, functions, variables, loops, conditionals, max nesting depth, avg line length, longest line
- ✅ **Diagnostics Dashboard** – Health Score 0-100 with Advanced v2 scoring: error density penalty, syntax validity cap, short-file penalty
- ✅ **Suggestion Engine – Phase 8.1** – Rule-based auto-fix: missing semicolons, undeclared variables → `int x = 0;`, duplicate removal, orphan identifier fix – **Health 35 → 100 in one click**
- ✅ **LLM Advisor – Phase 8.2** – Optional Groq Llama 3.1 / Gemini 1.5 Flash explanations – graceful offline fallback, $0 cost
- ✅ **Export System** – PDF report (ReportLab) + Plain Text report – one click download
- ✅ **Test Suite – Phase 9** – 56 pytest tests, 80% core coverage
- ✅ **Modern SaaS UI** – Bootstrap 5, dark theme, 9-tab analysis workspace, token filtering, sortable tables, diff viewer

---

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, Flask 3.0.3 |
| Frontend | HTML5, CSS3, Vanilla JS, Bootstrap 5.3, Font Awesome 6, Inter + Fira Code |
| Testing | pytest 8.2.2, pytest-cov 5.0.0 – 56 tests, 80% coverage |
| AI (optional) | Groq Llama 3.1 8B – free tier, 30 req/min – falls back to offline |
| PDF Export | ReportLab 4.2.0 |
| Deployment | Gunicorn 21.2.0, Render.com Free Tier |
| No | React/Vue, Docker, Database, Paid services |

---

### Quick Start – Local

```powershell
# 1. Clone
git clone https://github.com/YOUR_USERNAME/compiler-project.git
cd compiler_project

# 2. Virtual env (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install
pip install -r requirements.txt

# 4. (Optional) AI explanations – create .env
copy .env.example .env
# Edit .env, add: GROQ_API_KEY=gsk_xxxxxxxx
# No key? App works 100% offline – Rule-Based mode

# 5. Run
python app.py

# 6. Open
http://127.0.0.1:5000
http://127.0.0.1:5000/workspace
```

---

### Running Tests

```powershell
# All tests
python -m pytest tests/ -v

# With coverage HTML report
python -m pytest tests/ --cov --cov-report=html
start htmlcov/index.html

# Expected: 56 passed, Core coverage 80%
```

---

### Project Structure

```
compiler_project/
├── app.py                      # Flask – 7 routes + /suggest + /autofix + /ai_explain
├── requirements.txt
├── pytest.ini
├── .coveragerc
├── .env.example
├── render.yaml
├── gunicorn_config.py
│
├── lexer/
│   └── lexer.py                # Lexical Analyzer – C/C++/Java comments
├── parser/
│   └── parser.py               # Syntax Analyzer – Advanced v2
├── analyzer/
│   ├── symbol_table.py
│   ├── scope_analyzer.py
│   ├── error_detector.py       # + type mismatch
│   ├── metrics.py
│   ├── diagnostics.py          # Health Score v2
│   ├── suggestion_engine.py    # Phase 8.1 – Auto-fix
│   └── llm_advisor.py          # Phase 8.2 – Groq/Gemini
├── exporter/
│   ├── pdf_exporter.py
│   └── text_exporter.py
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_symbol_table.py
│   ├── test_scope_analyzer.py
│   ├── test_metrics.py
│   ├── test_error_detector.py
│   ├── test_diagnostics.py
│   └── test_suggestions.py
├── static/
│   ├── css/main.css
│   ├── css/landing.css
│   ├── css/workspace.css
│   ├── js/main.js
│   ├── js/editor.js
│   ├── js/analyzer.js
│   ├── js/export.js
│   └── js/suggestions.js
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── workspace.html
│   └── error.html
└── docs/
    ├── installation_guide.md
    ├── user_manual.md
    ├── architecture.md
    ├── flowchart.md
    ├── project_report.md
    └── viva_qa.md
```

---

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/workspace` | Compiler workspace |
| POST | `/analyze` | Run full compiler pipeline – returns tokens, parser errors, symbols, scope, metrics, diagnostics |
| POST | `/suggest` | Generate fix suggestions – Health gain prediction |
| POST | `/autofix` | Apply auto-fixes – returns fixed_code + new_health_score |
| POST | `/ai_explain` | LLM explanation for a suggestion (Groq/Gemini – optional) |
| GET | `/api/sample?id=1..5` | Sample code – includes broken code sample for testing Fix-It |
| GET | `/export/pdf` | Download PDF report |
| GET | `/export/text` | Download text report |
| GET | `/health` | Health check – `{"status":"ok","version":"1.1.0"}` |

---

### Health Score Formula – v2 Advanced

```
Start = 100
-12 per syntax_error
-8  per undeclared_variable
-5  per warning
if not parser.is_valid: score = min(score, 65)
error_density = errors / tokens
  if >0.30: -25
  elif >0.15: -12
  elif >0.05: -5
if tokens < 5 and errors > 0: -20
score = clamp(0, 100)
if zero errors: score = 100, label = "Excellent"
```

Labels: 90-100 Excellent, 70-89 Good, 50-69 Fair, 30-49 Poor, 0-29 Critical

---

### Screenshots

*Add 3 screenshots to `docs/screenshots/` after deployment:*
1. `landing.png` – Landing page hero
2. `workspace_analysis.png` – Workspace with 8 tabs open
3. `suggestions.png` – Suggestions tab showing Health 68 → 100 auto-fix

---

### Deployment – Render.com Free

1. Push to GitHub (see `docs/installation_guide.md`)
2. https://render.com → New → Web Service → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Add Environment Variable (optional): `GROQ_API_KEY=gsk_xxx`
6. Deploy – 3 min – Live URL provided

Full step-by-step with screenshots: `docs/installation_guide.md`

---

### Testing

```
56 tests – all passing
Core coverage: 80%
analyzer/metrics.py               100%
analyzer/scope_analyzer.py        100%
analyzer/symbol_table.py          100%
analyzer/error_detector.py         98%
lexer/lexer.py                     87%
analyzer/diagnostics.py            84%
parser/parser.py                   80%
```
Run: `python -m pytest tests/ -v --cov`

---

### Documentation

- `docs/installation_guide.md` – Windows 10 + VS Code setup, GitHub, Render
- `docs/user_manual.md` – How to use every tab, export reports
- `docs/architecture.md` – System architecture, Flask request flow, module interaction
- `docs/flowchart.md` – Compiler phases flowchart (Mermaid)
- `docs/project_report.md` – Full academic project report – Abstract, Introduction, Literature, Design, Implementation, Testing, Results, Conclusion, References
- `docs/viva_qa.md` – 30 viva questions & detailed answers – compiler theory + Flask + testing + your implementation

---

### License

Academic Project – Compiler Design Course – 2026  
Free for educational use.

---

### Author

Built with ❤️ using Python + Flask  
Mentor-guided – Senior Compiler Engineer / Python / UI/UX / QA – Arena.ai Agent Mode

**CompilerX – Analyze Your Code. Understand Your Compiler.**
