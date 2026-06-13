# CompilerX - Diagnostics Tests
import time
from analyzer.diagnostics import generate_diagnostics

def test_health_score_perfect_code():
    lexer = {'total_count': 10}
    parser = {'total_errors': 0}
    errors = {'total_warnings': 0, 'total_undeclared': 0}
    sym = {'total_count': 2}
    d = generate_diagnostics(lexer, parser, errors, sym, time.time()*1000)
    assert d['health_score'] == 100
    assert d['health_label'] == 'Excellent'

def test_health_score_penalizes_syntax_errors():
    lexer = {'total_count': 10}
    parser = {'total_errors': 2}
    errors = {'total_warnings': 0, 'total_undeclared': 0}
    sym = {'total_count': 1}
    d = generate_diagnostics(lexer, parser, errors, sym, time.time()*1000)
    assert d['health_score'] < 100
    assert d['total_syntax_errors'] == 2

def test_health_score_never_negative():
    lexer = {'total_count': 5}
    parser = {'total_errors': 50}
    errors = {'total_warnings': 50, 'total_undeclared': 50}
    sym = {'total_count': 0}
    d = generate_diagnostics(lexer, parser, errors, sym, time.time()*1000)
    assert d['health_score'] >= 0

def test_health_label_ranges():
    # Just verify labels exist and score is int
    for errs in [0, 2, 5, 10, 30]:
        d = generate_diagnostics({'total_count': 10}, {'total_errors': errs}, {'total_warnings': 0, 'total_undeclared': 0}, {'total_count': 1}, time.time()*1000)
        assert d['health_label'] in ['Excellent', 'Good', 'Fair', 'Poor', 'Critical']
        assert 0 <= d['health_score'] <= 100
