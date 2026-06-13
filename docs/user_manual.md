# CompilerX – User Manual

## 1. Opening the Workspace

1. Start server: `python app.py`
2. Open http://127.0.0.1:5000
3. Click **"Launch Compiler"** → `/workspace`

Layout: Left = Source Code Editor, Right = Analysis Results (9 tabs).

---

## 2. Source Code Editor – Left Panel

- **Monospace editor** with live line numbers (left gutter)
- **Character count / Line count** – updates live, bottom-left
- **Language selector** – C / C++ / Java – cosmetic, parser handles all 3 C-style syntaxes
- **Load Sample** – loads 1 of 5 samples (including 1 intentionally broken sample – ID 5 – perfect for testing the Fix-It engine)
- **Clear Editor** – clears code + resets results panel
- **Analyze Code** – blue full-width button – sends code to `/analyze`

**Character limit:** 5000 characters – enforced server-side, editor shows "Too long" warning.

**Supported language constructs:**
`int, float, double, char, string, bool, if, else, elif, while, for, do, return, void, break, continue, true, false, null, class, public, private, ...`
Operators: `+ - * / % == != < > <= >= = += -= *= /= %= && || ! & | ^ ~ << >>`
Delimiters: `( ) { } [ ] ; , . :`
Literals: integers `42`, floats `3.14`, strings `"hello"` / `'world'`

Comments: `// line comment`, `/* block comment */`, `# python style`

---

## 3. Analysis Results – Right Panel – 9 Tabs

After clicking **Analyze Code**, wait 50-200ms, results appear.

### Tab 1 – Overview
- **Health Score Circle** – 0-100, color coded: Green 90-100, Blue 70-89, Yellow 50-69, Orange 30-49, Red 0-29
- **4 Stat boxes:** Tokens, Errors, Warnings, Symbols
- **Health summary text**
- **Analysis time ms**
- **💡 Suggestions pill** – if issues found, click to jump to Suggestions tab

### Tab 2 – Tokens
- Table: `# | Token Value | Token Type | Line | Col`
- **Filter buttons:** All / Keywords / Identifiers / Operators / Delimiters / Integers / Floats / Strings
- **Search box:** filter by token value live
- Color-coded type badges: KEYWORD=blue, IDENTIFIER=purple, OPERATOR=yellow, DELIMITER=cyan, INTEGER=green, FLOAT=orange, STRING=red

### Tab 3 – Syntax
- Green success card: "Syntax looks correct!" if 0 errors
- Red error cards if errors found – each shows: Line number badge, Error type, Full message
- Example: `Line 4: Missing ';' after variable declaration of 'a'`

### Tab 4 – Symbol Table
- Columns: `# | Name | Type | Category | Scope | Scope Level | Line Declared`
- Filter: All scopes / Global only / Local only
- Click column headers to sort ascending/descending

### Tab 5 – Scope
- Visual nested scope tree cards
- Global scope at top, child scopes indented
- Variables shown as badge chips inside each scope
- Scope violations (if any) shown in red below

### Tab 6 – Errors & Warnings
- Top section – Warnings – yellow cards – Duplicate declarations
  - Example: `Warning Line 6: Variable 'a' already declared in same scope at Line 3`
- Bottom section – Errors – red cards – Undeclared variables
  - Example: `Error Line 8: Variable 'x' used but never declared`
- Count badges at section headers

### Tab 7 – Metrics
12 metric cards in responsive grid:
Total Lines, Keywords, Identifiers, Operators, Functions, Variables, Loops, Conditionals, Max Nesting, String Literals, Blank Lines, Comments

Numbers count up with animation on tab open.

### Tab 8 – Report
- Full text summary of analysis
- Buttons:
  - **Copy** – copies report to clipboard
  - **Download .txt** – downloads `compilerx_report.txt`
  - **Download PDF** – downloads `compilerx_report.pdf` (ReportLab)

### Tab 9 – 💡 Suggestions – Phase 8.1 / 8.2
**This is the star feature.**

Left column – Issues Found:
- Each suggestion card shows: Severity badge (ERROR/WARNING), Line number, Issue text, Fix text, Health impact `+5`
- Buttons per card: **[Apply]** – apply this single fix, **[✨ AI Explain]** – get LLM explanation (requires GROQ_API_KEY, otherwise shows offline message)

Right column – Fixed Code Preview:
- Read-only textarea – shows code after auto-fix, syntax highlighted green
- Buttons:
  - **Replace in Editor & Re-analyze** – copies fixed code back to left editor and auto-runs Analyze again – Health Score jumps!
  - **Copy Fixed Code** – copy to clipboard

Top banner:
```
Found 3 issues – Apply fixes to improve Health 68 → 100
[Apply All Fixes] [Refresh]
```

**Typical Fix-It workflow:**
1. Analyze broken code → Health 45, 3 errors
2. Open Suggestions tab → see 3 cards
3. Click **Apply All Fixes**
4. Fixed code appears on right
5. Click **Replace in Editor & Re-analyze**
6. Health Score: **100 – Excellent** ✅
7. Export PDF – report shows Health 100

**AI Explain – Phase 8.2 (optional)**
- Click ✨ AI Explain on any suggestion
- If `GROQ_API_KEY` is set in `.env`: 1-2 sec, friendly 2-3 sentence explanation appears below the card – e.g.:
  > "In C, every statement must end with a semicolon. Without it, the compiler doesn't know where the variable declaration ends, so it gets confused when it sees `return` next. Adding `;` tells the compiler 'this statement is finished' – a good habit is to type the semicolon immediately after the variable name."
- No API key / offline / quota exceeded: shows: *"AI explain unavailable – using offline rule-based suggestion. Set GROQ_API_KEY to enable AI."* – the Fix button still works 100%, no functionality loss.

---

## 4. Exporting Reports

Top-right navbar → **Export ▼**
- **PDF Report** – `compilerx_report.pdf` – includes Health Score, token summary, syntax errors, symbol table – generated with ReportLab
- **Text Report** – `compilerx_report.txt` – plain text, same content

Also available in Tab 8 – Report – with Copy to Clipboard button.

**Requirement:** You must run Analyze at least once in the current server session – export reads from `LAST_ANALYSIS` memory store. If you restart the Flask server, run Analyze again before exporting.

---

## 5. Sample Codes

Click **Load Sample** – cycles through 5 samples:

1. **Simple Variables** – `int a = 10; float pi = 3.14; string name = "CompilerX";`
2. **If-Else Example** – `if (x > y) { ... } else { ... }`
3. **Loop Example** – `for (int i=0; i<10; i++)` + `while`
4. **Function Example** – `int add(int a, int b) { return result; }`
5. **Broken Code (Test Fix-It)** – intentionally broken: missing semicolons, duplicate variable, undeclared variable – perfect for testing the Suggestion Engine → Health 35 → Apply All → Health 100

You can also append `?id=5` to the API directly: `GET /api/sample?id=5`

---

## 6. Keyboard Shortcuts

- Editor: **Tab** → inserts 4 spaces (not focus change)
- Analyze: No default hotkey – click the blue button
- Browser: **Ctrl+Shift+R** – hard refresh (fix CSS cache issues)

---

## 7. Troubleshooting – User Side

| Symptom | Fix |
|---------|-----|
| Analyze button shows "Please enter some source code first" even with code | Hard refresh `Ctrl+Shift+R`, check browser console F12 – should see `CompilerX editor.js initialized` and `analyzer.js initialized` – if not, clear browser cache, disable extensions (MetaMask breaks fetch) |
| Load Sample does nothing | Check Network tab F12 – GET `/api/sample` should return 200 + JSON – if 404, Flask server not running – run `python app.py` |
| Token table empty after Analyze | Check Response in Network tab – POST `/analyze` – should return JSON with `success:true` and `lexer.tokens` array – if `success:false`, read the `error` field – usually "source_code exceeds 5000 character limit" |
| Export PDF says "No analysis to export" | Run Analyze first – export reads from server memory `LAST_ANALYSIS`, which is cleared on server restart |
| AI Explain says "LLM call failed ... proxies" | `pip install httpx==0.27.2 groq==0.11.0 --force-reinstall` then restart server – see `docs/installation_guide.md §4` |
| Health Score seems too harsh (e.g. `ww` = 35 not 96) | This is intentional – Health Score v2 is stricter for academic rigor – see `analyzer/diagnostics.py` – you can tune penalties if needed for your viva requirements – original spec was 100-5*errors, v2 is 100-12*errors with density penalty |

---

Next: `architecture.md` – How the Flask backend, lexer, parser, and 7 analysis modules interact.
