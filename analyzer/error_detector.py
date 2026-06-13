def detect_errors(tokens, symbol_table):
    symbols = symbol_table.get('symbols', [])

    sym_map = {}
    for s in symbols:
        key = (s['name'], s['scope_level'])
        sym_map[key] = s

    declared_names = {}
    for s in symbols:
        if s['name'] not in declared_names:
            declared_names[s['name']] = s

    warnings = []
    seen = {}
    warning_id = 1
    for s in symbols:
        key = (s['name'], s['scope_level'])
        if key in seen:
            original = seen[key]
            warnings.append({
                'warning_id': warning_id,
                'warning_type': 'DUPLICATE_DECLARATION',
                'message': f"Warning Line {s['line_declared']}: Variable '{s['name']}' already declared in same scope at Line {original['line_declared']}",
                'line_number': s['line_declared'],
                'original_line': original['line_declared'],
                'variable_name': s['name'],
                'scope': s['scope']
            })
            warning_id += 1
        else:
            seen[key] = s
    
    undeclared_errors = []
    type_warnings = []
    error_id = 1
   
    i = 0
    while i < len(tokens)-2:
        t = tokens[i]
        if t['token_type'] == 'IDENTIFIER':
            prev = tokens[i-1] if i > 0 else None
            is_declaration = prev and prev['token_type'] == 'KEYWORD' and prev['token_value'] in ('int','float','double','char','string','bool','void')
            if not is_declaration:
                name = t['token_value']
                if name not in declared_names:
                    if not any(e['variable_name'] == name for e in undeclared_errors):
                        undeclared_errors.append({
                            'error_id': error_id,
                            'error_type': 'UNDECLARED_VARIABLE',
                            'message': f"Error Line {t['line_number']}: Variable '{name}' used but never declared",
                            'line_number': t['line_number'],
                            'variable_name': name
                        })
                        error_id += 1
        i += 1

    i = 0
    while i < len(tokens)-3:
        if (tokens[i]['token_type'] == 'KEYWORD' and 
            tokens[i]['token_value'] in ('int','float','double') and
            i+3 < len(tokens) and
            tokens[i+1]['token_type'] == 'IDENTIFIER' and
            tokens[i+2]['token_value'] == '='):
            val_tok = tokens[i+3]
            var_name = tokens[i+1]['token_value']
            var_type = tokens[i]['token_value']
            assigned_type = None
            if val_tok['token_type'] == 'STRING':
                assigned_type = 'string'
            elif val_tok['token_type'] == 'FLOAT' and var_type == 'int':
                assigned_type = 'float'
            
            if assigned_type == 'string' and var_type in ('int','float','double'):
               
                warnings.append({
                    'warning_id': warning_id,
                    'warning_type': 'TYPE_MISMATCH',
                    'message': f"Warning Line {val_tok['line_number']}: Type mismatch – assigning string to {var_type} variable '{var_name}'",
                    'line_number': val_tok['line_number'],
                    'original_line': tokens[i+1]['line_number'],
                    'variable_name': var_name,
                    'scope': 'global'
                })
                warning_id += 1
        i += 1
    
    return {
        'duplicate_warnings': warnings,
        'undeclared_errors': undeclared_errors,
        'total_warnings': len(warnings),
        'total_undeclared': len(undeclared_errors)
    }
