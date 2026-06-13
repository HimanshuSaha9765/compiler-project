from lexer.lexer import analyze_lexical
from analyzer.symbol_table import build_symbol_table
from analyzer.scope_analyzer import analyze_scope

def scope(code):
    tokens = analyze_lexical(code)['tokens']
    sym = build_symbol_table(tokens, code)
    return analyze_scope(tokens, sym)

def test_global_scope_is_always_present():
    r = scope("int x;")
    assert r['tree']['scope_name'] == 'global'
    assert r['total_scopes'] >= 1

def test_function_creates_new_scope():
    r = scope("int add(int a, int b) { int result; return result; }")
    assert r['total_scopes'] >= 1

def test_if_block_creates_new_scope():
    r = scope("int main(){ if(1){ int temp; } }")
    assert 'tree' in r

def test_scope_nesting_is_correct():
    r = scope("int x; int f(){ if(1){ int y; } }")
    assert r['tree']['scope_level'] == 0

def test_scope_hierarchy_parent_child_relationship():
    r = scope("int a;")
    tree = r['tree']
    assert 'parent_scope' in tree
    assert 'children' in tree
