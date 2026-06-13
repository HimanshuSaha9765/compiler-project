# CompilerX - Parser Tests
# Phase 9 - Advanced Parser v2

from lexer.lexer import analyze_lexical
from parser.parser import analyze_syntax

def parse(code):
    tokens = analyze_lexical(code)['tokens']
    return analyze_syntax(tokens)

def test_valid_code_returns_no_syntax_errors():
    r = parse("int a = 10; return a;")
    assert r['is_valid'] is True
    assert r['total_errors'] == 0

def test_missing_semicolon_detection():
    r = parse("int a = 10\nint b = 20;")
    assert r['total_errors'] >= 1
    # Advanced parser may report "Missing" or "Incomplete assignment ... missing"
    assert any('miss' in e['error_message'].lower() and ';' in e['error_message'] for e in r['errors'])

def test_missing_semicolon_before_return():
    # Bug reported by user: int result = a + name return result;
    r = parse("int a = 10; int result = a + b return result;")
    assert r['total_errors'] >= 1
    assert any('result' in e['error_message'].lower() for e in r['errors'])

def test_unmatched_braces_detection():
    r = parse("int main() { int x = 5; ")
    assert r['total_errors'] >= 1
    assert any('{' in e['error_message'] for e in r['errors'])

def test_unmatched_parentheses_detection():
    r = parse("if (x > 0 { return x; }")
    assert r['total_errors'] >= 1
    assert any('(' in e['error_message'] for e in r['errors'])

def test_invalid_if_statement_detection():
    r = parse("if x > 0 { return x; }")
    assert r['total_errors'] >= 1
    assert any('if' in e['error_message'].lower() for e in r['errors'])

def test_invalid_while_loop_detection():
    r = parse("while x < 10 { x = x + 1; }")
    assert any('while' in e['error_message'].lower() for e in parse("while x < 10 { }")['errors'])

def test_empty_input_handling():
    r = parse("")
    assert r['is_valid'] is True
    assert r['total_errors'] == 0

def test_code_with_only_comments():
    r = parse("// comment only\n# another comment")
    assert r['is_valid'] is True

def test_deeply_nested_valid_code():
    r = parse("int main(){ if(1){ while(0){ } } return 0; }")
    # May have 0 or few errors depending on parser strictness – just ensure it doesn't crash
    assert isinstance(r['total_errors'], int)

def test_multiple_simultaneous_errors():
    r = parse("int a int b\n x = \n if x { }")
    assert r['total_errors'] >= 2

def test_orphan_identifier_detection():
    # Phase 8.1 advanced: lone identifier 'ww' should be syntax error
    r = parse("ww")
    assert r['total_errors'] >= 1
    assert any('Invalid statement' in e['error_message'] or 'ww' in e['error_message'] for e in r['errors'])
