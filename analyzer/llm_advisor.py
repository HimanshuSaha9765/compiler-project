# CompilerX - LLM Advisor (Optional AI Explanations)
# Phase 8.2 - Groq / Gemini integration
# 100% optional - app works fully offline without this

import os
import json

# Try to load .env if present (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_llm_provider():
    """Detect which LLM provider is configured"""
    groq_key = os.getenv('GROQ_API_KEY', '').strip()
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    provider = os.getenv('LLM_PROVIDER', 'auto').lower()
    
    if provider == 'off':
        return None, None
    if (provider == 'groq' or provider == 'auto') and groq_key:
        return 'groq', groq_key
    if (provider == 'gemini' or provider == 'auto') and gemini_key:
        return 'gemini', gemini_key
    return None, None

def ai_explain_suggestion(source_code, suggestion, diagnostics):
    """
    Get a friendly AI explanation for a compiler suggestion
    Falls back gracefully if no API key / no internet / version mismatch
    """
    provider, api_key = get_llm_provider()
    if not provider:
        return {
            'success': False,
            'explanation': '',
            'provider': 'offline',
            'reason': 'No LLM API key configured. Set GROQ_API_KEY in .env to enable AI explanations. Rule-based fix is still available.'
        }
    
    prompt = f"""You are a friendly Compiler Design tutor helping a beginner student.

Source code:
```
{source_code[:1200]}
```

Compiler found an issue:
Line {suggestion['line_number']}: {suggestion['issue']}
Suggested fix: {suggestion['fix']}

Explain in 2-3 short sentences, simple English:
1. Why is this an error?
2. How does the fix help?
3. One tip to avoid it next time.

Be encouraging, no jargon. Max 80 words.
"""
    
    try:
        if provider == 'groq':
            return _call_groq(prompt, api_key)
        elif provider == 'gemini':
            return _call_gemini(prompt, api_key)
    except Exception as e:
        return {
            'success': False,
            'explanation': '',
            'provider': provider,
            'reason': f'LLM call failed: {str(e)[:120]}. Using offline rule-based suggestion.'
        }
    
    return {'success': False, 'explanation': '', 'provider': 'none'}

def _call_groq(prompt, api_key):
    try:
        from groq import Groq
    except ImportError as e:
        return {'success': False, 'explanation': '', 'provider': 'groq', 'reason': f'groq package not installed. Run: pip install groq httpx==0.27.2 --force-reinstall. Error: {e}'}
    
    # Groq client init – handle httpx version incompatibility (proxies arg removed in httpx 0.28)
    try:
        client = Groq(api_key=api_key)
    except TypeError as e:
        if 'proxies' in str(e):
            return {'success': False, 'explanation': '', 'provider': 'groq',
                    'reason': 'Groq client / httpx version mismatch. Fix: pip install httpx==0.27.2 groq==0.11.0 --force-reinstall – then restart server. Using offline suggestions meanwhile.'}
        return {'success': False, 'explanation': '', 'provider': 'groq', 'reason': str(e)[:200]}
    except Exception as e:
        return {'success': False, 'explanation': '', 'provider': 'groq', 'reason': str(e)[:200]}
    
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a patient Compiler Design tutor. Explain errors simply, be encouraging."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=220,
        )
        text = resp.choices[0].message.content.strip()
        return {'success': True, 'explanation': text, 'provider': 'groq_llama3.1-8b'}
    except Exception as e:
        return {'success': False, 'explanation': '', 'provider': 'groq', 'reason': str(e)[:200]}

def _call_gemini(prompt, api_key):
    try:
        import google.generativeai as genai
    except ImportError:
        return {'success': False, 'explanation': '', 'provider': 'gemini', 'reason': 'google-generativeai not installed. Run: pip install google-generativeai'}
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content(prompt, generation_config={'temperature': 0.4, 'max_output_tokens': 220})
        text = resp.text.strip() if hasattr(resp, 'text') else str(resp)
        return {'success': True, 'explanation': text, 'provider': 'gemini-1.5-flash'}
    except Exception as e:
        return {'success': False, 'explanation': '', 'provider': 'gemini', 'reason': str(e)[:200]}

def llm_status():
    provider, key = get_llm_provider()
    if provider == 'groq':
        return {'enabled': True, 'provider': 'Groq Llama 3.1', 'mode': 'ai'}
    if provider == 'gemini':
        return {'enabled': True, 'provider': 'Gemini 1.5 Flash', 'mode': 'ai'}
    return {'enabled': False, 'provider': 'Rule-Based (Offline)', 'mode': 'offline'}
