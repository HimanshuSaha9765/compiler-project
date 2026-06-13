from lexer.lexer import analyze_lexical
from parser.parser import analyze_syntax
from analyzer.symbol_table import build_symbol_table
from analyzer.error_detector import detect_errors
from analyzer.suggestion_engine import generate_suggestions, apply_autofix, predict_health_gain

def suggest(code):
    lex = analyze_lexical(code)
    parser = analyze_syntax(lex['tokens'])
    sym = build_symbol_table(lex['tokens'], code)
    err = detect_errors(lex['tokens'], sym)
    return generate_suggestions(parser, err, sym, code, lex)

def test_suggestions_generated_for_missing_semicolon():
    s = suggest("int a = 10\nint b = 20;")
    assert len(s) >= 1
    assert any(';' in x['fix'] for x in s)

def test_autofix_adds_missing_semicolon():
    code = "int a = 10\nint b = 20;"
    sugg = suggest(code)
    fixed, applied = apply_autofix(code, sugg)
    assert applied >= 1
    assert ';' in fixed

def test_undeclared_variable_suggestion():
    s = suggest("x = 5;")
    assert len(s) >= 1
    assert any('x' in x['issue'].lower() for x in s)

def test_health_gain_prediction():
    s = suggest("int a\nint a;")
    gain = predict_health_gain(s)
    assert isinstance(gain, int)
    assert gain >= 0

def test_autofix_orphan_identifier():
    code = "ww"
    s = suggest(code)
    fixed, applied = apply_autofix(code, s)
    assert applied >= 0
    assert 'ww' in fixed.lower()
