from flask import Flask, render_template, request, jsonify, send_file
import os
import time

from lexer.lexer import analyze_lexical
from parser.parser import analyze_syntax
from analyzer.symbol_table import build_symbol_table
from analyzer.scope_analyzer import analyze_scope
from analyzer.error_detector import detect_errors
from analyzer.metrics import calculate_metrics
from analyzer.diagnostics import generate_diagnostics
from exporter.text_exporter import generate_text_report
from exporter.pdf_exporter import generate_pdf_report

from analyzer.suggestion_engine import generate_suggestions, apply_autofix, predict_health_gain

try:
    from analyzer.llm_advisor import ai_explain_suggestion, llm_status
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False
    def ai_explain_suggestion(*args, **kwargs):
        return {'success': False, 'explanation': '', 'provider': 'offline', 'reason': 'LLM module not available'}
    def llm_status():
        return {'enabled': False, 'provider': 'Rule-Based (Offline)', 'mode': 'offline'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'compilerx-dev-key-2026'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

LAST_ANALYSIS = {}
LAST_SUGGESTIONS = []

@app.route('/')
def landing():
    try:
        return render_template('landing.html')
    except Exception as e:
        app.logger.error(f"Landing page error: {str(e)}")
        return render_template('error.html', error_code=500, error_message="Internal Server Error"), 500

@app.route('/workspace')
def workspace():
    try:
        llm = llm_status() if LLM_AVAILABLE else {'enabled': False, 'provider': 'Rule-Based', 'mode': 'offline'}
        return render_template('workspace.html', llm_status=llm)
    except Exception as e:
        app.logger.error(f"Workspace error: {str(e)}")
        return render_template('error.html', error_code=500, error_message="Internal Server Error"), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    start_ms = time.time() * 1000
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        data = request.get_json()
        if 'source_code' not in data:
            return jsonify({"success": False, "error": "Missing 'source_code' field"}), 400
        source_code = data.get('source_code', '').strip()
        if not source_code:
            return jsonify({"success": False, "error": "source_code cannot be empty"}), 400
        if len(source_code) > 5000:
            return jsonify({"success": False, "error": "source_code exceeds 5000 character limit"}), 400

        lexer_result = analyze_lexical(source_code)
        parser_result = analyze_syntax(lexer_result['tokens'])
        symbol_table_result = build_symbol_table(lexer_result['tokens'], source_code)
        scope_result = analyze_scope(lexer_result['tokens'], symbol_table_result)
        error_result = detect_errors(lexer_result['tokens'], symbol_table_result)
        metrics_result = calculate_metrics(source_code, lexer_result['tokens'], symbol_table_result)
        diagnostics_result = generate_diagnostics(
            lexer_result, parser_result, error_result, symbol_table_result, start_ms
        )

        response = {
            "success": True,
            "source_code": source_code,
            "lexer": lexer_result,
            "parser": parser_result,
            "symbol_table": symbol_table_result,
            "scope": scope_result,
            "errors": error_result,
            "metrics": metrics_result,
            "diagnostics": diagnostics_result
        }
        global LAST_ANALYSIS, LAST_SUGGESTIONS
        LAST_ANALYSIS = response
        LAST_SUGGESTIONS = []
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Analyze error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error during analysis"}), 500

@app.route('/suggest', methods=['POST'])
def suggest():
    """Generate fix suggestions for the last analysis, or for provided source"""
    try:
        global LAST_ANALYSIS, LAST_SUGGESTIONS

        if request.is_json:
            data = request.get_json(silent=True) or {}
            source_code = data.get('source_code')
        else:
            source_code = None
        
        if source_code:
            lexer_result = analyze_lexical(source_code)
            parser_result = analyze_syntax(lexer_result['tokens'])
            symbol_table_result = build_symbol_table(lexer_result['tokens'], source_code)
            error_result = detect_errors(lexer_result['tokens'], symbol_table_result)
        elif LAST_ANALYSIS:
            source_code = LAST_ANALYSIS.get('source_code', '')
            parser_result = LAST_ANALYSIS['parser']
            error_result = LAST_ANALYSIS['errors']
            symbol_table_result = LAST_ANALYSIS['symbol_table']
            lexer_result = LAST_ANALYSIS['lexer']
        else:
            return jsonify({"success": False, "error": "No analysis found. Run /analyze first or provide source_code"}), 400
        
        suggestions = generate_suggestions(parser_result, error_result, symbol_table_result, source_code, lexer_result)
        health_gain = predict_health_gain(suggestions)

        current_health = 0
        if LAST_ANALYSIS and 'diagnostics' in LAST_ANALYSIS:
            current_health = LAST_ANALYSIS['diagnostics'].get('health_score', 0)
        
        predicted_health = min(100, current_health + health_gain)
        
        LAST_SUGGESTIONS = suggestions
        
        return jsonify({
            "success": True,
            "suggestions": suggestions,
            "total_count": len(suggestions),
            "auto_fixable_count": sum(1 for s in suggestions if s['auto_fixable']),
            "health_gain": health_gain,
            "current_health": current_health,
            "predicted_health": predicted_health,
            "llm": llm_status() if LLM_AVAILABLE else {'enabled': False}
        })
    except Exception as e:
        app.logger.error(f"Suggest error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Suggestion engine failed"}), 500

@app.route('/autofix', methods=['POST'])
def autofix():
    """Apply auto-fixes and return fixed code + re-analyze"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "JSON body required"}), 400
        
        source_code = data.get('source_code', '')
        if not source_code and LAST_ANALYSIS:
            source_code = LAST_ANALYSIS.get('source_code', '')
        
        if not source_code:
            return jsonify({"success": False, "error": "No source_code provided and no last analysis"}), 400
        
        selected_ids = data.get('suggestion_ids')

        global LAST_SUGGESTIONS
        suggestions = LAST_SUGGESTIONS
        if not suggestions:
            lexer_result = analyze_lexical(source_code)
            parser_result = analyze_syntax(lexer_result['tokens'])
            symbol_table_result = build_symbol_table(lexer_result['tokens'], source_code)
            error_result = detect_errors(lexer_result['tokens'], symbol_table_result)
            suggestions = generate_suggestions(parser_result, error_result, symbol_table_result, source_code, lexer_result)
        
        fixed_code, applied_count = apply_autofix(source_code, suggestions, selected_ids)
        
        start_ms = time.time() * 1000
        lexer2 = analyze_lexical(fixed_code)
        parser2 = analyze_syntax(lexer2['tokens'])
        sym2 = build_symbol_table(lexer2['tokens'], fixed_code)
        err2 = detect_errors(lexer2['tokens'], sym2)
        metrics2 = calculate_metrics(fixed_code, lexer2['tokens'], sym2)
        diag2 = generate_diagnostics(lexer2, parser2, err2, sym2, start_ms)
        
        return jsonify({
            "success": True,
            "fixed_code": fixed_code,
            "applied_count": applied_count,
            "new_health_score": diag2['health_score'],
            "new_diagnostics": diag2,
            "improvement": diag2['health_score']
        })
    except Exception as e:
        app.logger.error(f"Autofix error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Auto-fix failed"}), 500

@app.route('/ai_explain', methods=['POST'])
def ai_explain():
    """Get AI explanation for a specific suggestion"""
    if not LLM_AVAILABLE:
        return jsonify({"success": False, "error": "LLM advisor not installed. pip install groq / google-generativeai and set GROQ_API_KEY"}), 501
    try:
        data = request.get_json()
        suggestion = data.get('suggestion')
        source_code = data.get('source_code', '')
        if not suggestion:
            return jsonify({"success": False, "error": "Missing suggestion object"}), 400
        diagnostics = LAST_ANALYSIS.get('diagnostics', {}) if LAST_ANALYSIS else {}
        result = ai_explain_suggestion(source_code, suggestion, diagnostics)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"AI explain error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "AI explain failed"}), 500

@app.route('/api/llm_status')
def api_llm_status():
    status = llm_status() if LLM_AVAILABLE else {'enabled': False, 'provider': 'Rule-Based (Offline)', 'mode': 'offline'}
    return jsonify({"success": True, "llm": status})

@app.route('/export/text')
def export_text():
    try:
        if not LAST_ANALYSIS:
            return jsonify({"success": False, "error": "No analysis to export. Run Analyze first."}), 400
        report = generate_text_report(LAST_ANALYSIS)
        from io import BytesIO
        mem = BytesIO()
        mem.write(report.encode('utf-8'))
        mem.seek(0)
        return send_file(mem, as_attachment=True, download_name='compilerx_report.txt', mimetype='text/plain')
    except Exception as e:
        app.logger.error(f"Export text error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Export failed"}), 500

@app.route('/export/pdf')
def export_pdf():
    try:
        if not LAST_ANALYSIS:
            return jsonify({"success": False, "error": "No analysis to export. Run Analyze first."}), 400
        pdf_buffer = generate_pdf_report(LAST_ANALYSIS)
        return send_file(pdf_buffer, as_attachment=True, download_name='compilerx_report.pdf', mimetype='application/pdf')
    except Exception as e:
        app.logger.error(f"Export pdf error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Export failed"}), 500

@app.route('/api/sample')
def api_sample():
    try:
        samples = [
            {"id":1,"name":"Simple Variables","language":"c","code":"int a = 10;\nint b = 20;\nfloat pi = 3.14;\nstring name = \"CompilerX\";\n\nint result = a + b;\nreturn result;"},
            {"id":2,"name":"If-Else Example","language":"c","code":"int x = 15;\nint y = 10;\n\nif (x > y) {\n    int max = x;\n    return max;\n} else {\n    int max = y;\n    return max;\n}"},
            {"id":3,"name":"Loop Example","language":"c","code":"int sum = 0;\nint i = 0;\n\nfor (int i = 0; i < 10; i++) {\n    sum = sum + i;\n}\n\nwhile (sum > 0) {\n    sum = sum - 1;\n}\n\nreturn sum;"},
            {"id":4,"name":"Function Example","language":"c","code":"int add(int a, int b) {\n    int result = a + b;\n    return result;\n}\n\nint main() {\n    int x = 5;\n    int y = 7;\n    int z = add(x, y);\n    return z;\n}"},
            {"id":5,"name":"Broken Code (Test Fix-It)","language":"c","code":"int a = 10\nint b = 20\nint a = 5\n\nx = a + b\nif x > 0 {\n  return x\n}\n"}
        ]
        sid = request.args.get('id', type=int)
        sample = next((s for s in samples if s['id'] == sid), samples[0])
        return jsonify({"success": True, "sample": sample})
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to load sample"}), 500

@app.route('/health')
def health():
    llm = llm_status() if LLM_AVAILABLE else {'enabled': False}
    return jsonify({"status": "ok", "version": "1.1.0", "phase": "Phase 8.1+8.2 - Suggestions + LLM", "service": "CompilerX", "llm": llm})

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, error_message="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, error_message="Internal Server Error"), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  CompilerX - Advanced Compiler Front-End")
    print("  Phase 8.1: Suggestion Engine | Phase 8.2: LLM Advisor")
    print("=" * 60)
    llm = llm_status() if LLM_AVAILABLE else {'enabled': False, 'provider': 'Rule-Based'}
    print(f"  LLM Mode: {llm['provider']}")
    if not llm['enabled']:
        print("  Tip: Set GROQ_API_KEY in .env to enable AI explanations")
    print(f"  Local URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
