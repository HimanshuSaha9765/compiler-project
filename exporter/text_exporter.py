# CompilerX - Text Report Exporter
# Phase 8

def generate_text_report(analysis_data):
    d = analysis_data.get('diagnostics', {})
    lexer = analysis_data.get('lexer', {})
    parser = analysis_data.get('parser', {})
    sym = analysis_data.get('symbol_table', {})
    
    lines = []
    lines.append("="*60)
    lines.append("CompilerX - Analysis Report")
    lines.append("="*60)
    lines.append(f"Health Score: {d.get('health_score', '--')} ({d.get('health_label', '')})")
    lines.append(f"Summary: {d.get('summary', '')}")
    lines.append("")
    lines.append(f"Tokens: {lexer.get('total_count',0)}")
    lines.append(f"Syntax Errors: {parser.get('total_errors',0)}")
    lines.append(f"Symbols: {sym.get('total_count',0)}")
    lines.append("")
    lines.append("Tokens:")
    for t in lexer.get('tokens', [])[:50]:
        lines.append(f"  {t['token_id']:3} | {t['token_value']:<15} | {t['token_type']:<12} | Line {t['line_number']}")
    lines.append("")
    lines.append("Syntax Errors:")
    for e in parser.get('errors', []):
        lines.append(f"  - {e['error_message']}")
    if not parser.get('errors'):
        lines.append("  None - syntax OK")
    lines.append("")
    lines.append("Symbol Table:")
    for s in sym.get('symbols', []):
        lines.append(f"  {s['name']} : {s['type']} [{s['category']}] scope={s['scope']} line={s['line_declared']}")
    lines.append("")
    lines.append("="*60)
    return "\n".join(lines)
