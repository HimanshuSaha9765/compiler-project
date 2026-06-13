from lexer.lexer import analyze_lexical
from analyzer.symbol_table import build_symbol_table
from analyzer.metrics import calculate_metrics

def metrics(code):
    lex = analyze_lexical(code)
    sym = build_symbol_table(lex['tokens'], code)
    return calculate_metrics(code, lex['tokens'], sym)

def test_total_line_count():
    m = metrics("a\nb\nc")
    assert m['total_lines'] == 3

def test_blank_line_count():
    m = metrics("int x;\n\n\nint y;")
    assert m['blank_lines'] >= 2

def test_keyword_count_accuracy():
    m = metrics("int a; float b; return a;")
    assert m['keyword_count'] >= 3

def test_function_count():
    m = metrics("int add(int a,int b){return a+b;} int main(){return 0;}")
    assert m['function_count'] >= 1

def test_loop_count():
    m = metrics("for(;;){} while(1){} do{}while(0);")
    assert m['loop_count'] >= 2

def test_nesting_depth_calculation():
    m = metrics("int main(){ if(1){ while(0){ } } }")
    assert m['max_nesting_depth'] >= 2

def test_empty_code_returns_zero_metrics():
    m = metrics("")
    assert m['total_lines'] >= 0
    assert m['keyword_count'] == 0
