# CompilerX - Lexer Tests
# Phase 9 - pytest

import pytest
from lexer.lexer import analyze_lexical

def test_keywords_are_correctly_identified():
    result = analyze_lexical("int float if else return")
    types = [t['token_type'] for t in result['tokens']]
    assert types == ['KEYWORD'] * 5
    assert result['keyword_count'] == 5

def test_identifiers_are_correctly_identified():
    result = analyze_lexical("myVar count total_sum x1 _temp")
    types = [t['token_type'] for t in result['tokens']]
    assert all(x == 'IDENTIFIER' for x in types)
    assert result['identifier_count'] == 5

def test_operators_are_correctly_classified():
    code = "+ - * / % == != < > <= >= = && || !"
    result = analyze_lexical(code)
    assert result['operator_count'] >= 10
    ops = [t['token_value'] for t in result['tokens'] if t['token_type'] == 'OPERATOR']
    assert '==' in ops
    assert '&&' in ops

def test_integer_constants_are_detected():
    result = analyze_lexical("0 1 42 100 9999")
    assert result['integer_count'] == 5
    values = [t['token_value'] for t in result['tokens']]
    assert '42' in values

def test_float_constants_are_detected():
    result = analyze_lexical("3.14 0.5 100.0 2.718")
    assert result['float_count'] == 4

def test_string_literals_are_detected():
    result = analyze_lexical('"hello" \'world\' "compiler design"')
    assert result['string_count'] == 3

def test_line_numbers_are_correctly_tracked():
    code = "int a;\nfloat b;\nx = 5;"
    result = analyze_lexical(code)
    lines = [t['line_number'] for t in result['tokens'] if t['token_value'] == 'int' or t['token_value'] == 'float' or t['token_value'] == 'x']
    assert lines == [1, 2, 3]

def test_empty_input_returns_empty_token_list():
    result = analyze_lexical("")
    assert result['tokens'] == []
    assert result['total_count'] == 0

def test_whitespace_only_input_returns_empty_token_list():
    result = analyze_lexical("   \n\n\t  ")
    assert result['total_count'] == 0

def test_multi_line_code_tokenization():
    code = """int add(int a, int b) {
    return a + b;
}"""
    result = analyze_lexical(code)
    assert result['total_count'] > 10
    assert result['keyword_count'] >= 3  # int, int, int, return
