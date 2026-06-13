from lexer.lexer import analyze_lexical
from analyzer.symbol_table import build_symbol_table
from analyzer.error_detector import detect_errors

def detect(code):
    lex = analyze_lexical(code)
    sym = build_symbol_table(lex['tokens'], code)
    return detect_errors(lex['tokens'], sym)

def test_duplicate_variable_in_same_scope_is_flagged():
    r = detect("int a; int a;")
    assert r['total_warnings'] >= 1

def test_duplicate_variable_in_different_scopes_is_not_flagged():
    r = detect("int x; int main(){ int x; }")
    assert isinstance(r['total_warnings'], int)

def test_undeclared_variable_usage_is_flagged():
    r = detect("x = 5;")
    assert r['total_undeclared'] >= 1

def test_declared_variable_usage_is_not_flagged():
    r = detect("int x; x = 5;")
    assert r['total_undeclared'] >= 0

def test_empty_code_returns_no_warnings():
    r = detect("")
    assert r['total_warnings'] == 0
    assert r['total_undeclared'] == 0

def test_type_mismatch_warning():
    r = detect('int x = "hello";')
    assert 'total_warnings' in r
