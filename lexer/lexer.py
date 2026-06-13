import re

KEYWORDS = {
    'int', 'float', 'double', 'char', 'string', 'bool',
    'if', 'else', 'elif', 'while', 'for', 'do',
    'return', 'void', 'break', 'continue',
    'true', 'false', 'null', 'new', 'class',
    'public', 'private', 'protected', 'static',
    'import', 'from', 'def', 'pass', 'and', 'or', 'not'
}

MULTI_OPS = [
    '==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '%=',
    '&&', '||', '<<', '>>', '++', '--'
]

SINGLE_OPS = set('+-*/% =<>!&|^~')

DELIMITERS = set('(){}[];,.:')

def tokenize(source_code):
    """
    Lexical Analyzer - converts source code into tokens
    Supports C/C++/Java style comments: // and /* */
    Returns: {
        'tokens': [...],
        'total_count': int,
        'keyword_count': int,
        'identifier_count': int,
        'operator_count': int,
        'delimiter_count': int,
        'integer_count': int,
        'float_count': int,
        'string_count': int
    }
    """
    tokens = []
    token_id = 1
    
    lines = source_code.split('\n')
    
    counts = {
        'KEYWORD': 0,
        'IDENTIFIER': 0,
        'OPERATOR': 0,
        'DELIMITER': 0,
        'INTEGER': 0,
        'FLOAT': 0,
        'STRING': 0
    }
    in_block_comment = False
    
    for line_num, line in enumerate(lines, start=1):
        col = 0
        length = len(line)
        
        while col < length:
            ch = line[col]
            
            if in_block_comment:
                if ch == '*' and col + 1 < length and line[col+1] == '/':
                    in_block_comment = False
                    col += 2
                    continue
                col += 1
                continue
            
            if ch.isspace():
                col += 1
                continue
            
            if ch == '/' and col + 1 < length and line[col+1] == '/':
                break 
            

            if ch == '/' and col + 1 < length and line[col+1] == '*':
                in_block_comment = True
                col += 2
                continue
            
            if ch == '#':
                break
            
            start_col = col + 1

            if ch == '"' or ch == "'":
                quote = ch
                col += 1
                value = quote
                while col < length and line[col] != quote:
                    if line[col] == '\\' and col + 1 < length:
                        value += line[col] + line[col+1]
                        col += 2
                        continue
                    value += line[col]
                    col += 1
                if col < length:  # closing quote
                    value += line[col]
                    col += 1
                tokens.append({
                    'token_id': token_id,
                    'token_value': value,
                    'token_type': 'STRING',
                    'line_number': line_num,
                    'column_number': start_col
                })
                token_id += 1
                counts['STRING'] += 1
                continue

            if ch.isdigit():
                num_str = ''
                has_dot = False
                while col < length and (line[col].isdigit() or (line[col] == '.' and not has_dot)):
                    if line[col] == '.':
                        has_dot = True
                    num_str += line[col]
                    col += 1
                token_type = 'FLOAT' if has_dot else 'INTEGER'
                tokens.append({
                    'token_id': token_id,
                    'token_value': num_str,
                    'token_type': token_type,
                    'line_number': line_num,
                    'column_number': start_col
                })
                token_id += 1
                counts[token_type] += 1
                continue

            if ch.isalpha() or ch == '_':
                ident = ''
                while col < length and (line[col].isalnum() or line[col] == '_'):
                    ident += line[col]
                    col += 1
                token_type = 'KEYWORD' if ident in KEYWORDS else 'IDENTIFIER'
                tokens.append({
                    'token_id': token_id,
                    'token_value': ident,
                    'token_type': token_type,
                    'line_number': line_num,
                    'column_number': start_col
                })
                token_id += 1
                counts[token_type] += 1
                continue

            matched = False
            for op in MULTI_OPS:
                if line[col:col+len(op)] == op:
                    tokens.append({
                        'token_id': token_id,
                        'token_value': op,
                        'token_type': 'OPERATOR',
                        'line_number': line_num,
                        'column_number': start_col
                    })
                    token_id += 1
                    counts['OPERATOR'] += 1
                    col += len(op)
                    matched = True
                    break
            if matched:
                continue

            if ch in SINGLE_OPS:
                tokens.append({
                    'token_id': token_id,
                    'token_value': ch,
                    'token_type': 'OPERATOR',
                    'line_number': line_num,
                    'column_number': start_col
                })
                token_id += 1
                counts['OPERATOR'] += 1
                col += 1
                continue

            if ch in DELIMITERS:
                tokens.append({
                    'token_id': token_id,
                    'token_value': ch,
                    'token_type': 'DELIMITER',
                    'line_number': line_num,
                    'column_number': start_col
                })
                token_id += 1
                counts['DELIMITER'] += 1
                col += 1
                continue
            
            col += 1
        
    return {
        'tokens': tokens,
        'total_count': len(tokens),
        'keyword_count': counts['KEYWORD'],
        'identifier_count': counts['IDENTIFIER'],
        'operator_count': counts['OPERATOR'],
        'delimiter_count': counts['DELIMITER'],
        'integer_count': counts['INTEGER'],
        'float_count': counts['FLOAT'],
        'string_count': counts['STRING']
    }

def analyze_lexical(source_code):
    return tokenize(source_code)
