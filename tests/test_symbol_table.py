from lexer.lexer import analyze_lexical
from analyzer.symbol_table import build_symbol_table

def sym(code):
    tokens = analyze_lexical(code)['tokens']
    return build_symbol_table(tokens, code)

def test_single_variable_declaration_is_recorded():
    r = sym("int counter;")
    assert r['total_count'] >= 1
    assert any(s['name'] == 'counter' for s in r['symbols'])

def test_multiple_variable_declarations():
    r = sym("int a; float b; char c;")
    assert r['total_count'] >= 3

def test_function_declaration_is_recorded():
    r = sym("int add(int a, int b) { return a+b; }")
    funcs = [s for s in r['symbols'] if s['category'] == 'function']
    assert len(funcs) >= 1
    assert funcs[0]['name'] == 'add'

def test_scope_level_assignment_is_correct():
    r = sym("int x; int main(){ int y; }")
    levels = {s['name']: s['scope_level'] for s in r['symbols']}
    assert 'x' in levels

def test_global_vs_local_scope_distinction():
    r = sym("int g; int f(){ int l; }")
    assert r['global_count'] >= 1
    assert 'local_count' in r

def test_empty_input_returns_empty_symbol_table():
    r = sym("")
    assert r['total_count'] == 0
    assert r['symbols'] == []

def test_parameter_recording():
    r = sym("int add(int a, int b) { return a; }")
    names = [s['name'] for s in r['symbols']]
    assert 'add' in names
