def build_symbol_table(tokens, source_code=""):
    symbols = []
    symbol_id = 1
    
    scope_level = 0
    i = 0
    declared_names = {}  
    
    while i < len(tokens):
        t = tokens[i]
        if t['token_value'] == '{':
            scope_level += 1
            i += 1
            continue
        if t['token_value'] == '}':
            scope_level = max(0, scope_level - 1)
            i += 1
            continue
        if t['token_type'] == 'KEYWORD' and t['token_value'] in ('int','float','double','char','string','bool','void'):
            nxt = tokens[i+1] if i+1 < len(tokens) else None
            if nxt and nxt['token_type'] == 'IDENTIFIER':
                name = nxt['token_value']
                # check if function: next next is '('
                nxt2 = tokens[i+2] if i+2 < len(tokens) else None
                category = 'function' if nxt2 and nxt2['token_value'] == '(' else 'variable'
                scope_name = 'global' if scope_level == 0 else f'local_{scope_level}'
                used_lines = []
                for ut in tokens:
                    if ut['token_type'] == 'IDENTIFIER' and ut['token_value'] == name and ut['line_number'] != nxt['line_number']:
                        if ut['line_number'] not in used_lines:
                            used_lines.append(ut['line_number'])
                
                symbols.append({
                    'symbol_id': symbol_id,
                    'name': name,
                    'type': t['token_value'],
                    'category': category,
                    'scope': scope_name,
                    'scope_level': scope_level,
                    'line_declared': nxt['line_number'],
                    'line_used': sorted(used_lines)
                })
                symbol_id += 1
                i += 2
                continue
        i += 1
    
    global_count = sum(1 for s in symbols if s['scope_level'] == 0)
    local_count = len(symbols) - global_count
    
    return {
        'symbols': symbols,
        'total_count': len(symbols),
        'global_count': global_count,
        'local_count': local_count
    }
