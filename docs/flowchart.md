# CompilerX – Compiler Phases Flowchart

## 1. Full Compiler Front-End Pipeline

```mermaid
flowchart TD
    A[Source Code<br/>editor textarea<br/>C/C++/Java style] --> B[Lexical Analyzer<br/>lexer/lexer.py]
    B --> C{Tokens[]<br/>keyword / identifier / operator<br/>delimiter / integer / float / string}
    C --> D[Syntax Analyzer<br/>parser/parser.py]
    D --> E{Syntax Errors[]<br/>is_valid: true/false}
    C --> F[Symbol Table Generator<br/>analyzer/symbol_table.py]
    F --> G{Symbols[]<br/>name, type, scope_level,<br/>line_declared, line_used}
    G --> H[Scope Analyzer<br/>analyzer/scope_analyzer.py]
    H --> I{Scope Tree<br/>global → function → block}
    G --> J[Error Detector<br/>analyzer/error_detector.py]
    C --> J
    J --> K{Duplicate Warnings[]<br/>Undeclared Errors[]}
    C --> L[Metrics Calculator<br/>analyzer/metrics.py]
    G --> L
    L --> M{18 Metrics<br/>lines, tokens, functions,<br/>loops, nesting depth…}
    E --> N[Diagnostics<br/>analyzer/diagnostics.py]
    K --> N
    G --> N
    C --> N
    N --> O{Health Score 0-100<br/>Excellent / Good / Fair / Poor / Critical}
    O --> P[Suggestion Engine<br/>analyzer/suggestion_engine.py]
    E --> P
    K --> P
    P --> Q{Fix Suggestions[]<br/>auto_fixable: true/false<br/>health_impact: +5}
    Q --> R[Auto-Fix<br/>apply_autofix()]
    R --> S[Fixed Code<br/>Health → 100]
    Q --> T[LLM Advisor – Optional<br/>analyzer/llm_advisor.py<br/>Groq Llama 3.1 / Gemini]
    T --> U[AI Explanation<br/>2-3 sentences, beginner friendly]
    O --> V[Report Exporter<br/>exporter/pdf_exporter.py<br/>exporter/text_exporter.py]
    M --> V
    V --> W[PDF / TXT Download]
    S --> B
    classDef phase fill:#1e293b,stroke:#3b82f6,color:#f1f5f9
    class B,D,F,H,J,L,N,P,R,T,V phase
```

---

## 2. Flask Request Flow – POST /analyze

```mermaid
sequenceDiagram
    participant Browser as Browser<br/>analyzer.js
    participant Flask as Flask<br/>app.py /analyze
    participant Lex as Lexer
    participant Par as Parser
    participant Sym as Symbol Table
    participant Err as Error Detector
    participant Met as Metrics
    participant Diag as Diagnostics

    Browser->>Flask: POST /analyze {source_code}
    Flask->>Flask: validate: not empty, len <= 5000
    Flask->>Lex: analyze_lexical(source_code)
    Lex-->>Flask: tokens[], counts
    Flask->>Par: analyze_syntax(tokens)
    Par-->>Flask: errors[], is_valid
    Flask->>Sym: build_symbol_table(tokens)
    Sym-->>Flask: symbols[]
    Flask->>Err: detect_errors(tokens, symbols)
    Err-->>Flask: warnings[], undeclared[]
    Flask->>Met: calculate_metrics(source, tokens, symbols)
    Met-->>Flask: 18 metrics
    Flask->>Diag: generate_diagnostics(...)
    Diag-->>Flask: health_score, health_label
    Flask->>Browser: JSON {lexer, parser, symbol_table, scope, errors, metrics, diagnostics}
    Browser->>Browser: renderResults() → 8 tabs update
    Note over Browser: User clicks Suggestions tab
    Browser->>Flask: POST /suggest
    Flask-->>Browser: suggestions[], health_gain
    Browser->>Browser: render suggestion cards + diff viewer
```

---

## 3. Suggestion Engine – Auto-Fix Flow

```mermaid
flowchart LR
    A[Parser Errors<br/>+ Error Detector Warnings] --> B[Suggestion Engine<br/>generate_suggestions()]
    B --> C{For each error:<br/>- Map to fix_template<br/>- Compute health_impact<br/>- Set auto_fixable flag}
    C --> D[Suggestions List<br/>sorted by severity<br/>then health_impact DESC]
    D --> E[Frontend: Render cards<br/>Apply / AI Explain buttons]
    E --> F{User clicks<br/>Apply All Fixes}
    F --> G[POST /autofix<br/>apply_autofix(source, suggestions)]
    G --> H[Fixed Code String<br/>- Insert missing ;<br/>- Add int x = 0;<br/>- Comment duplicates]
    H --> I[Re-analyze fixed code<br/>parser → diagnostics]
    I --> J{New Health Score}
    J -->|95-100| K[✅ Excellent – Export Report]
    J -->|<90| E
```

**Auto-fixable transformations:**
1. Missing semicolon → insert `;` at EOL
2. Unmatched `{` / `(` → append `}` / `)`
3. Undeclared variable `x` → prepend `int x = 0; // Auto-declared`
4. Duplicate variable → comment out: `// FIXED DUPLICATE: int a = 5;`
5. Orphan identifier `ww` → convert to `int ww = 0;`
6. Invalid assignment `x = ;` → complete to `x = 0;`
7. Missing `(` after `if/while/for` → insert `(`, close `)` if missing
8. Missing `;` after `return` → append `;`

Type mismatch (`int x = "hello"`) → flagged as WARNING, **NOT auto-fixed** – requires human review – correct behavior.

---

## 4. Frontend Component Tree

```
base.html
├── <head> Bootstrap 5, Font Awesome 6, Inter + Fira Code, main.css
├── {% block content %}
│   ├── landing.html
│   │   ├── navbar
│   │   ├── hero – "Analyze Your Code. Understand Your Compiler."
│   │   ├── features grid – 6 cards
│   │   ├── pipeline diagram – Source → Lexer → … → Diagnostics
│   │   ├── sample code preview
│   │   └── footer
│   │
│   └── workspace.html
│       ├── workspace navbar – Load Sample / Clear / Export
│       ├── LEFT: editor panel
│       │   ├── line_numbers gutter (JS synced)
│       │   ├── <textarea id="sourceEditor">
│       │   ├── char/line counter
│       │   └── [Analyze Code] button
│       └── RIGHT: results panel – 9 tabs
│           ├── Tab 1 Overview – score circle, 4 stats
│           ├── Tab 2 Tokens – filterable table
│           ├── Tab 3 Syntax – error cards
│           ├── Tab 4 Symbol Table – sortable
│           ├── Tab 5 Scope – nested tree
│           ├── Tab 6 Errors – warnings + undeclared
│           ├── Tab 7 Metrics – 12 cards
│           ├── Tab 8 Report – copy / download txt / pdf
│           └── Tab 9 Suggestions – Phase 8.1/8.2
│               ├── left: suggestion cards – Apply / AI Explain
│               └── right: Fixed Code diff + Replace in Editor
└── <script> main.js, editor.js, analyzer.js, export.js, suggestions.js
```

---

## 5. Health Score – v2 – Decision Flow

```mermaid
flowchart TD
    Start([Start: 100]) --> A[syntax_errors * 12]
    A --> B[undeclared * 8]
    B --> C[warnings * 5]
    C --> D{parser.is_valid?}
    D -->|No| E[score = min(score, 65)]
    D -->|Yes| F
    E --> F[error_density = errors / tokens]
    F --> G{density > 0.3?}
    G -->|Yes| H[-25]
    G -->|No| I{density > 0.15?}
    I -->|Yes| J[-12]
    I -->|No| K{density > 0.05?}
    K -->|Yes| L[-5]
    K -->|No| M
    H --> M
    J --> M
    L --> M[tokens < 5 and errors > 0?]
    M -->|Yes| N[-20]
    M -->|No| O
    N --> O[clamp 0-100]
    O --> P{errors == 0 ?}
    P -->|Yes| Q[Score = 100<br/>Label = Excellent]
    P -->|No| R{score >= 90? Excellent<br/>>=70 Good<br/>>=50 Fair<br/>>=30 Poor<br/>else Critical}
    Q --> S[Return diagnostics]
    R --> S
```

---

*All diagrams render in GitHub / VS Code Markdown preview – Mermaid is natively supported.*

Next: `project_report.md` – Full academic report.
