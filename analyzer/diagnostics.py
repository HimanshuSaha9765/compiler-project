import time

def generate_diagnostics(lexer_result, parser_result, error_detector_result, symbol_table_result, start_time_ms):
    total_tokens = lexer_result.get('total_count', 0)
    total_syntax_errors = parser_result.get('total_errors', 0)
    total_warnings = error_detector_result.get('total_warnings', 0)
    total_undeclared_errors = error_detector_result.get('total_undeclared', 0)
    total_symbols = symbol_table_result.get('total_count', 0)
    
    syntax_penalty = 12 * total_syntax_errors
    undeclared_penalty = 8 * total_undeclared_errors
    warning_penalty = 5 * total_warnings
    
    score = 100 - syntax_penalty - undeclared_penalty - warning_penalty
    

    is_valid = parser_result.get('is_valid', True)
    if not is_valid:
        score = min(score, 65)
    
    if total_tokens > 0:
        error_density = (total_syntax_errors + total_undeclared_errors) / max(total_tokens, 1)
        if error_density > 0.3:
            score -= 25
        elif error_density > 0.15:
            score -= 12
        elif error_density > 0.05:
            score -= 5
    
    if total_tokens < 5 and (total_syntax_errors + total_undeclared_errors) > 0:
        score -= 20
    
    score = max(0, min(100, int(score)))
    

    if score >= 90:
        label = 'Excellent'
        summary = 'Code is clean and well-structured'
    elif score >= 70:
        label = 'Good'
        summary = f"{total_syntax_errors} syntax error(s), {total_warnings} warning(s) detected. Review flagged lines."
    elif score >= 50:
        label = 'Fair'
        summary = 'Multiple issues need attention – see Suggestions tab for auto-fixes'
    elif score >= 30:
        label = 'Poor'
        summary = 'Significant errors present – auto-fix recommended'
    else:
        label = 'Critical'
        summary = 'Code has major structural problems – run Auto-Fix'

    if total_syntax_errors == 0 and total_undeclared_errors == 0 and total_warnings == 0 and total_tokens > 0:
        score = 100
        label = 'Excellent'
        summary = 'Perfect – no issues detected'
    
    analysis_time_ms = int((time.time() * 1000) - start_time_ms)
    
    return {
        'total_tokens': total_tokens,
        'total_syntax_errors': total_syntax_errors,
        'total_warnings': total_warnings,
        'total_undeclared_errors': total_undeclared_errors,
        'total_symbols': total_symbols,
        'health_score': score,
        'health_label': label,
        'summary': summary,
        'analysis_time_ms': analysis_time_ms
    }
