import re

def generate_suggestions(parser_result, error_result, symbol_table, source_code, lexer_result=None):
    suggestions = []
    sid = 1
    lines = source_code.split('\n')
    
    def get_line(n):
        return lines[n-1] if 1 <= n <= len(lines) else ""

    for err in parser_result.get('errors', []):
        msg = err['error_message']
        line_num = err['line_number']
        line_text = get_line(line_num)
        
        fix_text = "Review syntax at this line"
        fixed_snippet = line_text.strip()
        auto_fixable = False
        health_impact = 5
        
        if "Missing ';'" in msg:
            fix_text = f"Add ';' at end of line {line_num}"
            fixed_snippet = line_text.rstrip() + (";" if not line_text.rstrip().endswith(';') else "")
            auto_fixable = True
        elif "Expected '(' after 'if'" in msg:
            fix_text = "Add '(' after 'if' keyword"
            fixed_snippet = line_text.replace('if ', 'if (', 1)
            auto_fixable = True
        elif "Expected '(' after 'while'" in msg:
            fix_text = "Add '(' after 'while' keyword"
            fixed_snippet = line_text.replace('while ', 'while (', 1)
            auto_fixable = True
        elif "Expected '(' after 'for'" in msg:
            fix_text = "Add '(' after 'for' keyword"
            fixed_snippet = line_text.replace('for ', 'for (', 1)
            auto_fixable = True
        elif "Unmatched '{'" in msg:
            fix_text = "Add missing '}' to close block"
            fixed_snippet = line_text + " }"
            auto_fixable = True
        elif "Unmatched '}'" in msg:
            fix_text = "Remove extra '}' or add matching '{' earlier"
            fixed_snippet = "// Remove extra }"
            auto_fixable = False
        elif "Unmatched '('" in msg:
            fix_text = "Add missing ')' "
            fixed_snippet = line_text + " )"
            auto_fixable = True
        elif "Invalid assignment" in msg:
            fix_text = "Complete the assignment expression, e.g. '= 0;'"
            fixed_snippet = re.sub(r'=\s*;', '= 0;', line_text)
            if fixed_snippet == line_text:
                fixed_snippet = line_text.rstrip() + ' = 0;'
            auto_fixable = True
        elif "Incomplete assignment" in msg:
            fix_text = "Add a value and ';' to complete declaration"
            fixed_snippet = line_text.rstrip() + (" 0;" if not line_text.strip().endswith(';') else "")
            auto_fixable = True
        elif "Missing ';' after return" in msg:
            fix_text = "Add ';' after return statement"
            fixed_snippet = line_text.rstrip() + ";"
            auto_fixable = True
        elif "Invalid statement" in msg:
            m = re.search(r"'([^']+)'", msg)
            var = m.group(1) if m else "x"
            fix_text = f"Invalid statement – did you mean to declare '{var}'? Suggested: int {var} = 0;"
            fixed_snippet = f"int {var} = 0;"
            auto_fixable = True
            health_impact = 8
        
        suggestions.append({
            'suggestion_id': sid,
            'severity': 'ERROR',
            'line_number': line_num,
            'issue': msg.split(': ', 1)[-1] if ': ' in msg else msg,
            'fix': fix_text,
            'auto_fixable': auto_fixable,
            'fixed_code_snippet': fixed_snippet,
            'health_impact': health_impact,
            'category': 'syntax',
            'original_line': line_text
        })
        sid += 1

    for w in error_result.get('duplicate_warnings', []):
        line_num = w['line_number']
        is_type = w.get('warning_type') == 'TYPE_MISMATCH'
        var_name = w.get('variable_name', 'x')
        
        if is_type:
            fix_text = f"Type mismatch – change variable type or assigned value to match"
            health_impact = 3
            category = 'type_mismatch'
        else:
            fix_text = f"Rename variable '{var_name}' or remove duplicate declaration"
            health_impact = 3
            category = 'duplicate'
        
        suggestions.append({
            'suggestion_id': sid,
            'severity': 'WARNING',
            'line_number': line_num,
            'issue': w['message'],
            'fix': fix_text,
            'auto_fixable': not is_type,  
            'fixed_code_snippet': f"// FIXED: {get_line(line_num).strip()}" if not is_type else get_line(line_num),
            'health_impact': health_impact,
            'category': category,
            'variable_name': var_name,
            'original_line': get_line(line_num)
        })
        sid += 1

    for e in error_result.get('undeclared_errors', []):
        line_num = e['line_number']
        var_name = e['variable_name']
        suggestions.append({
            'suggestion_id': sid,
            'severity': 'ERROR',
            'line_number': line_num,
            'issue': e['message'],
            'fix': f"Declare variable '{var_name}' before use. Suggested: int {var_name} = 0;",
            'auto_fixable': True,
            'fixed_code_snippet': f"int {var_name} = 0;  // Auto-declared by CompilerX",
            'health_impact': 4,
            'category': 'undeclared',
            'variable_name': var_name,
            'original_line': get_line(line_num)
        })
        sid += 1
    
    severity_order = {'ERROR': 0, 'WARNING': 1, 'INFO': 2}
    suggestions.sort(key=lambda x: (severity_order.get(x['severity'], 3), -x['health_impact']))

    for idx, s in enumerate(suggestions, 1):
        s['suggestion_id'] = idx
    
    return suggestions

def apply_autofix(source_code, suggestions, selected_ids=None):
    """
    Apply auto-fixes to source code
    selected_ids: list of suggestion_id to apply, None = apply all auto_fixable
    Returns: fixed_code, applied_count
    """
    lines = source_code.split('\n')
    applied = 0
    
    if selected_ids is None:
        to_apply = [s for s in suggestions if s['auto_fixable']]
    else:
        to_apply = [s for s in suggestions if s['suggestion_id'] in selected_ids and s['auto_fixable']]
    
    by_line = {}
    for s in to_apply:
        ln = s['line_number']
        if ln not in by_line:
            by_line[ln] = s
    
    new_lines = lines[:]
    undeclared_inserts = []
    
    for line_num, s in sorted(by_line.items(), reverse=True):
        idx = line_num - 1
        if idx < 0 or idx >= len(new_lines):
            continue
        
        cat = s['category']
        original = new_lines[idx]
        
        if cat == 'syntax':
            if "Missing ';'" in s['issue'] or "return" in s['issue'].lower():
                if not original.rstrip().endswith(';'):
                    new_lines[idx] = original.rstrip() + ';'
                    applied += 1
                    continue
            if "Expected '(' after 'if'" in s['issue']:
                new_lines[idx] = original.replace('if ', 'if (', 1)
                if ')' not in new_lines[idx]:
                    new_lines[idx] = new_lines[idx].rstrip() + ')'
                applied += 1
                continue
            if "Expected '(' after 'while'" in s['issue']:
                new_lines[idx] = original.replace('while ', 'while (', 1)
                if ')' not in new_lines[idx]:
                    new_lines[idx] = new_lines[idx].rstrip() + ')'
                applied += 1
                continue
            if "Expected '(' after 'for'" in s['issue']:
                new_lines[idx] = original.replace('for ', 'for (', 1)
                applied += 1
                continue
            if "Unmatched '{'" in s['issue'] or "Unmatched '('" in s['issue']:
                if "{" in s['issue']:
                    new_lines[idx] = original + ' }'
                else:
                    new_lines[idx] = original + ' )'
                applied += 1
                continue
            if "Invalid assignment" in s['issue'] or "Incomplete assignment" in s['issue']:
                if '=' in original and not original.strip().endswith(';'):
                    left = original.split('=')[0]
                    new_lines[idx] = left + '= 0;'
                    applied += 1
                    continue
            if "Invalid statement" in s['issue']:
                m = re.search(r"'([^']+)'", s['issue'])
                var = m.group(1) if m else s.get('variable_name', 'x')
                stripped = original.strip().rstrip(';')
                if re.fullmatch(r'[A-Za-z_]\w*', stripped):
                    new_lines[idx] = f"int {stripped} = 0;"
                    applied += 1
                    continue
        
        elif cat == 'duplicate':
            if not original.strip().startswith('//'):
                new_lines[idx] = '// FIXED DUPLICATE: ' + original
                applied += 1
            continue
        
        elif cat == 'undeclared':
            var_name = s.get('variable_name', 'x')
            decl = f"int {var_name} = 0; // Auto-declared by CompilerX"
            undeclared_inserts.append((idx, decl))
            applied += 1
            continue
        
        elif cat == 'type_mismatch':
            continue
        
        fixed = s.get('fixed_code_snippet', '').strip()
        if fixed and len(fixed) < 200 and (';' in fixed or '(' in fixed) and not fixed.startswith('// FIXED'):
            if cat != 'type_mismatch':
                new_lines[idx] = fixed
                applied += 1
    
    if undeclared_inserts:
        seen_vars = set()
        unique_inserts = []
        for idx, decl in undeclared_inserts:
            var = decl.split()[1]
            if var not in seen_vars:
                seen_vars.add(var)
                unique_inserts.append(decl)
        new_lines = unique_inserts + [''] + new_lines
    
    fixed_code = '\n'.join(new_lines)
    return fixed_code, applied

def predict_health_gain(suggestions):
    """Sum health impact of all auto-fixable suggestions"""
    return sum(s['health_impact'] for s in suggestions if s['auto_fixable'])
