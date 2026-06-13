# CompilerX – Installation Guide
## Phase 10 – Windows 10 + VS Code

### 1. Prerequisites – Verify
Open PowerShell in VS Code (`Ctrl + ``):

```
python --version
# Expected: Python 3.12.x
# If 'python' not found, try: py --version

pip --version
# Expected: pip 24.x

git --version
# Expected: git version 2.xx

code --version
# Expected: 1.8x.x
```
If Python is not 3.12, download from python.org – check "Add Python to PATH".

---

### 2. Clone / Download Project

**Option A – Git Clone (recommended)**
```
cd $HOME\Desktop
git clone https://github.com/YOUR_USERNAME/compiler-project.git
cd compiler_project
```

**Option B – Download ZIP**
Download `compiler_project.zip` from the release / workspace → Extract to `D:\compiler_project`

Verify folder structure – you must see:
```
compiler_project/
├── app.py
├── requirements.txt
├── lexer/
├── parser/
├── analyzer/
├── tests/
├── static/
├── templates/
└── docs/
```

⚠️ Common mistake: you extract and get `compiler_project/compiler_project/` double nested. Move the inner folder to `D:\compiler_project`.

---

### 3. Virtual Environment – Windows

```powershell
cd D:\compiler_project
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Prompt changes to: `(venv) PS D:\compiler_project>`

If PowerShell blocks scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then activate again.

**Every time you open a new terminal, activate venv again.** If you forget, `pip install` goes to global Python – bad.

To deactivate: `deactivate`

---

### 4. Install Dependencies

With `(venv)` active:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Expected output ends with:
```
Successfully installed Flask-3.0.3 gunicorn-21.2.0 pytest-8.2.2 pytest-cov-5.0.0 reportlab-4.2.0 groq-0.11.0 httpx-0.27.2 python-dotenv-1.0.1 ...
```

**Groq API – version conflict fix**
If you get: `Client.__init__() got an unexpected keyword argument 'proxies'`
Fix:
```
pip install httpx==0.27.2 groq==0.11.0 --force-reinstall
```
This is a known httpx 0.28 / groq compatibility issue – pinning fixes it. The app still works 100% offline without Groq.

---

### 5. Environment Variables – Optional AI

For AI explanations (Phase 8.2 – optional):

1. Copy `.env.example` → `.env`
   ```
   copy .env.example .env
   ```
2. Get a FREE Groq API key:
   - Go to https://console.groq.com/keys
   - Login with Google/GitHub – no credit card
   - Create API Key → Copy key `gsk_...`
3. Edit `.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   LLM_PROVIDER=auto
   ```
4. Save.

No key? Leave blank. App runs in **Rule-Based Offline Mode** – suggestions + auto-fix still work to 100% Health.

**Never commit `.env` to Git** – it's already in `.gitignore`.

---

### 6. Run Locally

```powershell
# venv must be active – check for (venv) in prompt
python app.py
```

Console output:
```
============================================================
  CompilerX - Advanced Compiler Front-End
  Phase 8.1: Suggestion Engine | Phase 8.2: LLM Advisor
  LLM Mode: Groq Llama 3.1
  Local URL: http://127.0.0.1:5000
============================================================
```

Open browser:
- Landing: http://127.0.0.1:5000
- Workspace: http://127.0.0.1:5000/workspace
- Health: http://127.0.0.1:5000/health

Stop server: `Ctrl+C`

---

### 7. Run Tests

```powershell
python -m pytest tests/ -v
# Expected: 56 passed

# With coverage HTML report
python -m pytest tests/ --cov --cov-report=html
start htmlcov/index.html
```
Expected coverage: Core modules 80%

---

### 8. GitHub – Push Your Project

```powershell
cd D:\compiler_project
git init
git add .
git commit -m "Initial commit: Complete compiler front-end project - Phase 1-10"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/compiler-project.git
git push -u origin main
```
Replace `YOUR_USERNAME` with your GitHub username.

If pushing fails with authentication: GitHub → Settings → Developer settings → Personal access tokens → Generate classic token with `repo` scope → use token as password when git asks.

---

### 9. Deploy to Render.com – Free

1. Go to https://render.com → Sign up with **GitHub**
2. Dashboard → **New +** → **Web Service**
3. **Connect GitHub repository**: select `compiler-project`
4. Configure:
   - Name: `compiler-project`
   - Region: Singapore (closest to India)
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: **Free**
5. **Advanced → Add Environment Variable** (optional):
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_key_here`
   - Leave blank for offline mode – app still works
6. Click **Create Web Service**
7. Wait 3-5 minutes – logs show: `Build successful`, `Starting gunicorn`
8. Visit your live URL: `https://compiler-project-xxxx.onrender.com`
9. Test: open `/workspace`, Analyze Sample Code, check Suggestions tab

**Free tier notes:**
- Sleeps after 15 min inactivity – first request wakes in ~30 sec – normal
- 750 hours/month free – enough for 1 app 24/7
- Logs available in Render dashboard

**render.yaml** is already in repo – Render auto-detects it, you can skip manual config if you want – just Connect Repo → Deploy.

---

### 10. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'flask'` | venv not activated | `.\venv\Scripts\Activate.ps1` – check for `(venv)` prompt |
| `SyntaxError: source code string cannot contain null bytes` | Files saved as UTF-16 (Windows Notepad copy-paste bug) | Delete project, download clean ZIP from GitHub / workspace – all files must be UTF-8 |
| `invalid character '�' (U+FFFD)` | Same – encoding corruption in `__init__.py` | Re-download clean ZIP – `__init__.py` files are 0-byte in the repo |
| `Port 5000 already in use` | Old Flask server still running | Close old terminal / `Ctrl+C` / reboot |
| CSS looks broken / buttons don't click | Static files 404 / browser extension blocking CDN | 1. Run from project root (`cd D:\compiler_project`), 2. Disable MetaMask/adblock for localhost, 3. Hard refresh `Ctrl+Shift+R`, 4. Try Edge/Firefox Incognito |
| `Load Sample` does nothing / Analyze says "Please enter source code" | JavaScript failed to load – usually extension interference or wrong file paths | Check browser console F12 – should see `CompilerX editor.js initialized` – disable extensions, ensure `static/js/editor.js` exists |
| Groq: `Client.__init__() got an unexpected keyword argument 'proxies'` | httpx version mismatch – httpx 0.28 removed `proxies` arg | `pip install httpx==0.27.2 groq==0.11.0 --force-reinstall` – then restart `python app.py` – app falls back to offline mode automatically if this fails |
| Tests fail – `assert False` in parser test | Old test file expecting old error message capitalization | Pull latest from GitHub – test suite was updated for Parser v2 – run `git pull` |
| Render deploy fails – `gunicorn: command not found` | `gunicorn` not in requirements.txt | It is – verify `requirements.txt` includes `gunicorn==21.2.0` – then redeploy with Clear Build Cache |
| Render app sleeps / slow first load | Free tier sleeps after 15 min | Normal – first request wakes in ~30 sec |

**Still stuck?** Open an Issue on GitHub with:
- OS version
- `python --version` output
- Full traceback
- Screenshot of `dir` / `ls` in project root

---

### 11. Folder Structure After Install

```
compiler_project/
├── venv/                  # virtual environment – DO NOT commit
├── .env                   # your local API keys – DO NOT commit (copy from .env.example)
├── app.py
├── requirements.txt
├── pytest.ini
├── .coveragerc
├── render.yaml
├── gunicorn_config.py
├── README.md
│
├── lexer/
├── parser/
├── analyzer/
├── exporter/
├── tests/                 # 56 tests
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
└── docs/
    ├── installation_guide.md  ← you are here
    ├── user_manual.md
    ├── architecture.md
    ├── flowchart.md
    ├── project_report.md
    └── viva_qa.md
```

---

**Next:** See `docs/user_manual.md` – How to use the Compiler Workspace, all 9 tabs explained with screenshots.
