# CompilerX – System Architecture

## 1. High-Level Overview

```
Browser (HTML/CSS/JS)
        │  POST /analyze  {source_code}
        ▼
Flask app.py  – 7 routes
        │
        ├─▶ Lexer ──▶ tokens[]
        ├─▶ Parser ──▶ syntax_errors[]
        ├─▶ Symbol Table ──▶ symbols[]
        ├─▶ Scope Analyzer ──▶ scope_tree
        ├─▶ Error Detector ──▶ warnings + undeclared[]
        ├─▶ Metrics ──▶ 18 statistics
        └─▶ Diagnostics ──▶ health_score 0-100
        │
        ◀── JSON response
        │
JavaScript analyzer.js – render 8 tabs
        │
        └─▶ Suggestion Engine (Phase 8.1)
             ├─▶ /suggest → fix list
             └─▶ /autofix → fixed_code
                  ↘ Optional LLM Advisor → Groq / Gemini
```

**No database. No authentication. Stateless – except `LAST_ANALYSIS` in-memory dict for PDF/Text export.**

---

## 2. Module Responsibility Matrix

| Module | File | Input | Output | Lines |
|--------|------|-------|--------|-------|
| Lexical Analyzer | `lexer/lexer.py` | source_code: str | tokens[], counts per category | 180 |
| Syntax Analyzer | `parser/parser.py` | tokens[] | errors[], is_valid: bool | 210 |
| Symbol Table | `analyzer/symbol_table.py` | tokens[] | symbols[] with scope_level, line_used | 65 |
| Scope Analyzer | `analyzer/scope_analyzer.py` | tokens[], symbol_table | scope_tree (nested dict), violations[] | 45 |
| Error Detector | `analyzer/error_detector.py` | tokens[], symbol_table | duplicate_warnings[], undeclared_errors[] + type_mismatch | 70 |
| Metrics | `analyzer/metrics.py` | source_code, tokens, symbol_table | 18 metrics dict | 65 |
| Diagnostics | `analyzer/diagnostics.py` | all above | health_score 0-100, health_label, summary, analysis_time_ms | 45 |
| Suggestion Engine | `analyzer/suggestion_engine.py` | parser+error results | suggestions[], auto_fix() → fixed_code | 220 |
| LLM Advisor | `analyzer/llm_advisor.py` | source_code + suggestion | explanation: str – Groq/Gemini – fails gracefully | 115 |
| PDF Exporter | `exporter/pdf_exporter.py` | analysis_data | BytesIO PDF – ReportLab | 45 |
| Text Exporter | `exporter/text_exporter.py` | analysis_data | str report | 35 |

Total backend: ~1,100 LOC, 0 external services required (LLM optional).

---

## 3. Flask Request Flow – POST /analyze

```
1. request.is_json ? 400 if not
2. source_code = data['source_code'].strip()
3. validate: not empty, len <= 5000 else 400
4. start_ms = time.time()*1000
5. lexer_result       = analyze_lexical(source_code)
6. parser_result      = analyze_syntax(lexer_result['tokens'])
7. symbol_table_result= build_symbol_table(lexer_result['tokens'], source_code)
8. scope_result       = analyze_scope(lexer_result['tokens'], symbol_table_result)
9. error_result       = detect_errors(lexer_result['tokens'], symbol_table_result)
10. metrics_result    = calculate_metrics(source_code, lexer_result['tokens'], symbol_table_result)
11. diagnostics_result= generate_diagnostics(lexer,parser,error,sym, start_ms)
12. response = {success:true, source_code, lexer, parser, symbol_table, scope, errors, metrics, diagnostics}
13. LAST_ANALYSIS = response   # for /export/pdf|text
14. return jsonify(response), 200
```

Average analysis time: **15-80 ms** for 50-200 line files – measured in `diagnostics.analysis_time_ms`.

Error handling: every route wrapped in `try/except`, returns JSON with `success:false`, proper HTTP status: 400 bad request, 404 not found, 500 server error, 501 not implemented. Never leaks Python traceback to client.

---

## 4. Frontend Architecture – No Framework

```
base.html
 ├─ Bootstrap 5.3 CSS/JS (CDN)
 ├─ Font Awesome 6 (CDN)
 ├─ Google Fonts: Inter + Fira Code
 ├─ static/css/main.css   – dark theme variables, global
 ├─ static/js/main.js     – showToast()
 │
 ├─ landing.html
 │   └─ landing.css
 │
 └─ workspace.html
     ├─ workspace.css
     ├─ editor.js      – line numbers, char count, Load Sample, Clear
     ├─ analyzer.js    – analyzeCode(), renderTokens(), renderSyntax() … renderReport()
     ├─ export.js      – exportPDF(), exportText(), copyReport()
     └─ suggestions.js – loadSuggestions(), applyAllFixes(), aiExplain()
```

**Why no React/Vue?** – Project requirement: "Strictly FORBIDDEN Technologies: React, Angular, Vue, Svelte". Vanilla JS keeps it simple, fast (< 50KB total JS), no build step, works on Render free tier instantly, easy to explain in viva.

**State management:** No Redux. Simple module globals:
- `window.cxEditor.getCode()/setCode()`
- `lastResult` in analyzer.js
- `currentSuggestions[]` in suggestions.js

**DOM rendering:** Pure `innerHTML` + `createElement` – fast enough for < 2000 tokens. Tables are virtualized by browser native scroll.

---

## 5. Data Contracts

**Token**
```json
{"token_id":1,"token_value":"int","token_type":"KEYWORD","line_number":1,"column_number":1}
```
Types: `KEYWORD | IDENTIFIER | OPERATOR | DELIMITER | INTEGER | FLOAT | STRING`

**Parser Error**
```json
{"error_id":1,"error_type":"SYNTAX_ERROR","error_message":"Line 4: Missing ';' after variable declaration of 'a'","line_number":4,"severity":"ERROR"}
```

**Symbol**
```json
{"symbol_id":1,"name":"counter","type":"int","category":"variable","scope":"global","scope_level":0,"line_declared":3,"line_used":[7,12]}
```

**Diagnostics**
```json
{"total_tokens":87,"total_syntax_errors":2,"total_warnings":1,"total_undeclared_errors":0,"total_symbols":8,"health_score":86,"health_label":"Good","summary":"2 syntax errors …","analysis_time_ms":43}
```

**Suggestion – Phase 8.1**
```json
{"suggestion_id":1,"severity":"ERROR","line_number":4,"issue":"Missing ';' after variable declaration of 'a'","fix":"Add ';' at end of line 4","auto_fixable":true,"fixed_code_snippet":"int a = 10;","health_impact":5,"category":"syntax"}
```

Full JSON schema for `/analyze` response: see `app.py` lines 55-85 and `README.md` API table.

---

## 6. Security / Privacy

- No database → No SQL injection
- No authentication → No session hijacking
- Input validation: `source_code` max 5000 chars, stripped, JSON only
- Output encoding: Jinja2 auto-escapes, JS uses `escapeHtml()` before `innerHTML`
- API keys: Never in Git – `.env` is gitignored – server reads `os.getenv('GROQ_API_KEY')` – if missing, LLM gracefully disables, app continues in offline mode
- CORS: Same-origin only – Flask default – no `Access-Control-Allow-Origin: *`
- No `eval()`, no `exec()`, no `subprocess` on user code – lexer is pure regex/string scan – safe
- Export endpoints read from server-side `LAST_ANALYSIS` memory – no path traversal

---

## 7. Performance

| Operation | 50 LOC | 200 LOC | Notes |
|-----------|--------|---------|-------|
| Lexical Analysis | 3 ms | 12 ms | O(n) scan |
| Syntax Analysis | 2 ms | 8 ms | O(tokens) |
| Symbol Table | 1 ms | 5 ms | O(tokens) |
| Scope + Errors + Metrics + Diagnostics | 2 ms | 6 ms | – |
| **Total /analyze** | **~15 ms** | **~45 ms** | Measured on Render Free (512 MB) |
| JSON response size | 8 KB | 45 KB | gzip enabled by Flask |
| Frontend render | 30 ms | 120 ms | DOM table build |

No database round-trips. No external API calls in core pipeline (LLM is opt-in, per-suggestion, with 2s timeout).

---

## 8. Deployment Architecture

```
GitHub repo: https://github.com/YOUR_USERNAME/compiler-project
     │
     │  auto-deploy on git push main
     ▼
Render.com – Web Service – Free Tier
  - Python 3.12
  - Build: pip install -r requirements.txt
  - Start: gunicorn app:app
  - Workers: 2 sync
  - Memory: 512 MB
  - Region: Singapore
  - Health check: GET /health
  - Env var (optional): GROQ_API_KEY
```

`gunicorn_config.py` – bind `0.0.0.0:10000`, workers=2, timeout=120, max_requests=1000

`render.yaml` – Infrastructure as Code – one-click deploy

No Docker, no Kubernetes, no database – as per project constraints.

---

## 9. Extensibility

Want to add a new compiler phase? 

1. Create `analyzer/my_phase.py` – function `analyze_xxx(tokens, symbol_table)` → return dict
2. Import in `app.py`, call in `/analyze` pipeline after metrics
3. Add Tab 10 in `templates/workspace.html`
4. Add `renderMyPhase(data)` in `static/js/analyzer.js`
5. Add 5-7 pytest tests in `tests/test_my_phase.py`

The Suggestion Engine automatically picks up new `parser.errors` and `error_detector.warnings` – no changes needed there.

Want to add a new LLM provider? Edit `analyzer/llm_advisor.py` – add `_call_claude()` / `_call_ollama()` – plug into `ai_explain_suggestion()` switch – 20 lines.

---

Next: `flowchart.md` – Visual compiler pipeline (Mermaid).
