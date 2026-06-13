def calculate_metrics(source_code, tokens, symbol_table):
    lines = source_code.split('\n')
    total_lines = len(lines)
    non_empty_lines = sum(1 for l in lines if l.strip())
    blank_lines = total_lines - non_empty_lines
    comment_lines = sum(1 for l in lines if l.strip().startswith('//') or l.strip().startswith('#'))
    
    keyword_count = sum(1 for t in tokens if t['token_type'] == 'KEYWORD')
    identifier_count = len(set(t['token_value'] for t in tokens if t['token_type'] == 'IDENTIFIER'))
    operator_count = sum(1 for t in tokens if t['token_type'] == 'OPERATOR')
    delimiter_count = sum(1 for t in tokens if t['token_type'] == 'DELIMITER')
    integer_constants = sum(1 for t in tokens if t['token_type'] == 'INTEGER')
    float_constants = sum(1 for t in tokens if t['token_type'] == 'FLOAT')
    string_literals = sum(1 for t in tokens if t['token_type'] == 'STRING')
    
    symbols = symbol_table.get('symbols', [])
    function_count = sum(1 for s in symbols if s['category'] == 'function')
    variable_count = sum(1 for s in symbols if s['category'] == 'variable')

    loop_keywords = {'for', 'while', 'do'}
    cond_keywords = {'if', 'else', 'elif'}
    loop_count = sum(1 for t in tokens if t['token_type'] == 'KEYWORD' and t['token_value'] in loop_keywords)
    conditional_count = sum(1 for t in tokens if t['token_type'] == 'KEYWORD' and t['token_value'] in cond_keywords)
    
    depth = max_depth = 0
    for ch in source_code:
        if ch == '{':
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == '}':
            depth = max(0, depth - 1)
    
    non_empty_text_lines = [l for l in lines if l.strip()]
    if non_empty_text_lines:
        lengths = [len(l) for l in non_empty_text_lines]
        average_line_length = round(sum(lengths) / len(lengths), 1)
        longest_len = max(lengths)
        longest_line_num = lengths.index(longest_len) + 1
        actual_line = 1
        count_nonempty = 0
        for idx, l in enumerate(lines, 1):
            if l.strip():
                count_nonempty += 1
                if count_nonempty == longest_line_num:
                    actual_line = idx
                    break
    else:
        average_line_length = 0
        longest_len = 0
        actual_line = 1
    
    return {
        'total_lines': total_lines,
        'non_empty_lines': non_empty_lines,
        'blank_lines': blank_lines,
        'comment_lines': comment_lines,
        'keyword_count': keyword_count,
        'identifier_count': identifier_count,
        'operator_count': operator_count,
        'delimiter_count': delimiter_count,
        'integer_constants': integer_constants,
        'float_constants': float_constants,
        'string_literals': string_literals,
        'function_count': function_count,
        'variable_count': variable_count,
        'loop_count': loop_count,
        'conditional_count': conditional_count,
        'max_nesting_depth': max_depth,
        'average_line_length': average_line_length,
        'longest_line': {'line_number': actual_line, 'length': longest_len}
    }
