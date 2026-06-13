# CompilerX - Syntax Analyzer
# Phase 5 - Advanced v2
# Fixes: missing semicolon detection, orphan identifiers, C/C++/Java robust

def analyze_syntax(tokens):
    """
    Advanced Syntax Analyzer
    Returns: {'errors': [...], 'total_errors': int, 'is_valid': bool}
    """
    errors = []
    error_id = 1

    def add_error(message, line_number, err_type="SYNTAX_ERROR"):
        nonlocal error_id
        errors.append({
            'error_id': error_id,
            'error_type': err_type,
            'error_message': f"Line {line_number}: {message}",
            'line_number': line_number,
            'severity': 'ERROR'
        })
        error_id += 1

    if not tokens:
        return {'errors': [], 'total_errors': 0, 'is_valid': True}

    def tok(i):
        return tokens[i] if 0 <= i < len(tokens) else None

    # --- Config ---
    TYPE_KEYWORDS = {'int','float','double','char','string','bool','void'}
    STATEMENT_STARTERS = TYPE_KEYWORDS | {'return','if','else','elif','while','for','do','break','continue','public','private','protected','static','class','def'}
    # Keywords allowed inside expressions (don't trigger missing-semicolon)
    EXPR_ALLOWED_KEYWORDS = {'true','false','null','and','or','not','new'}
    
    # Track braces/parens for accurate error locations
    brace_stack = []
    paren_stack = []

    i = 0
    n = len(tokens)
    
    while i < n:
        t = tokens[i]
        val = t['token_value']
        typ = t['token_type']
        line = t['line_number']

        # --- Brace / paren tracking ---
        if val == '{':
            brace_stack.append(line)
        elif val == '}':
            if brace_stack: brace_stack.pop()
            else: add_error("Unmatched '}' found", line)
        elif val == '(':
            paren_stack.append(line)
        elif val == ')':
            if paren_stack: paren_stack.pop()
            else: add_error("Unmatched ')' found", line)

        # --- RULE: Variable / Function Declaration ---
        if typ == 'KEYWORD' and val in TYPE_KEYWORDS:
            n1 = tok(i+1)
            if n1 and n1['token_type'] == 'IDENTIFIER':
                n2 = tok(i+2)
                # Function?  int foo (
                if n2 and n2['token_value'] == '(':
                    # skip to matching ) then expect { or ;
                    # simple check: find closing )
                    depth = 1
                    j = i+3
                    found_close = False
                    while j < n and depth > 0:
                        if tokens[j]['token_value'] == '(': depth += 1
                        elif tokens[j]['token_value'] == ')': depth -= 1; found_close = True if depth==0 else found_close
                        j += 1
                    if not found_close:
                        add_error(f"Invalid function definition syntax for '{n1['token_value']}' – missing ')'", line)
                    i += 1
                    continue
                
                # Variable declaration
                # Scan forward for statement terminator
                j = i+2
                paren_depth = 0
                found_semi = False
                saw_equals = False
                while j < n:
                    tj = tokens[j]
                    vj = tj['token_value']
                    if vj == '(': paren_depth += 1
                    elif vj == ')': paren_depth = max(0, paren_depth-1)
                    
                    if paren_depth == 0:
                        if vj == ';':
                            found_semi = True
                            break
                        if vj == '{' or vj == '}':
                            break
                        # If we hit a statement starter keyword at top level -> missing semicolon
                        if tj['token_type'] == 'KEYWORD' and vj in STATEMENT_STARTERS:
                            break
                        # If we hit TYPE_KEYWORD IDENTIFIER pattern -> new declaration started
                        if (tj['token_type'] == 'KEYWORD' and vj in TYPE_KEYWORDS and 
                            j+1 < n and tokens[j+1]['token_type'] == 'IDENTIFIER'):
                            break
                    if vj == '=': saw_equals = True
                    j += 1
                
                if not found_semi:
                    if saw_equals:
                        add_error(f"Incomplete assignment in declaration of '{n1['token_value']}' – missing ';'", line)
                    else:
                        add_error(f"Missing ';' after variable declaration of '{n1['token_value']}'", line)
        
        # --- RULE: Assignment / Expression statement starting with IDENTIFIER ---
        elif typ == 'IDENTIFIER':
            # Is this the start of a statement? previous token is ; or { or } or start of file
            prev = tok(i-1)
            is_stmt_start = (prev is None or prev['token_value'] in (';', '{', '}'))
            
            if is_stmt_start:
                n1 = tok(i+1)
                # Assignment?  x = ...
                if n1 and n1['token_value'] == '=':
                    # find terminating ;
                    j = i+2
                    paren_depth = 0
                    found_semi = False
                    while j < n:
                        tj = tokens[j]
                        vj = tj['token_value']
                        if vj == '(': paren_depth += 1
                        elif vj == ')': paren_depth = max(0, paren_depth-1)
                        if paren_depth == 0:
                            if vj == ';':
                                found_semi = True
                                break
                            if tj['token_type'] == 'KEYWORD' and tj['token_value'] in STATEMENT_STARTERS and tj['token_value'] not in EXPR_ALLOWED_KEYWORDS:
                                break
                            if vj in ('{', '}'):
                                break
                        j += 1
                    if not found_semi:
                        add_error(f"Invalid assignment expression for '{val}' – missing ';'", line)
                # Function call?  foo(
                elif n1 and n1['token_value'] == '(':
                    # find closing ) then ;
                    depth = 1
                    j = i+2
                    found_close = False
                    while j < n and depth > 0:
                        if tokens[j]['token_value'] == '(': depth += 1
                        elif tokens[j]['token_value'] == ')': depth -= 1; found_close = True if depth==0 else found_close
                        j += 1
                    # after call, expect ;
                    if found_close and j < n and tokens[j]['token_value'] != ';':
                        # look ahead for semicolon before next statement
                        k = j
                        found_semi = False
                        while k < min(j+5, n):
                            if tokens[k]['token_value'] == ';':
                                found_semi = True
                                break
                            if tokens[k]['token_type'] == 'KEYWORD' and tokens[k]['token_value'] in STATEMENT_STARTERS:
                                break
                            k += 1
                        if not found_semi:
                            add_error(f"Missing ';' after function call '{val}()'", line)
                else:
                    # Orphan identifier – not assignment, not call
                    # Check if next token is a valid expression continuation
                    allowed_next = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=',
                                    '&&', '||', '&', '|', '^', '++', '--', '.', '[', 
                                    ';', ',', ')', ']', '}',}
                    next_val = n1['token_value'] if n1 else None
                    if next_val not in allowed_next:
                        # Lone identifier statement – e.g. "ww"
                        # Check if it's just a single identifier then end/semicolon/EOF
                        # This is invalid in C/Java
                        add_error(f"Invalid statement '{val}' – expected assignment, function call, or ';'", line)
        
        # --- RULE: if / while / for must have ( ---
        if typ == 'KEYWORD' and val == 'if':
            n1 = tok(i+1)
            if not n1 or n1['token_value'] != '(':
                add_error("Expected '(' after 'if'", line)
        if typ == 'KEYWORD' and val == 'while':
            n1 = tok(i+1)
            if not n1 or n1['token_value'] != '(':
                add_error("Expected '(' after 'while'", line)
        if typ == 'KEYWORD' and val == 'for':
            n1 = tok(i+1)
            if not n1 or n1['token_value'] != '(':
                add_error("Expected '(' after 'for'", line)
        
        # --- RULE: return must end with ; ---
        if typ == 'KEYWORD' and val == 'return':
            # scan for ;
            j = i+1
            paren_depth = 0
            found_semi = False
            while j < n:
                tj = tokens[j]
                vj = tj['token_value']
                if vj == '(': paren_depth += 1
                elif vj == ')': paren_depth = max(0, paren_depth-1)
                if paren_depth == 0:
                    if vj == ';':
                        found_semi = True
                        break
                    if tj['token_type'] == 'KEYWORD' and tj['token_value'] in STATEMENT_STARTERS:
                        break
                    if vj in ('{', '}'):
                        break
                j += 1
            if not found_semi:
                add_error("Missing ';' after return statement", line)
        
        i += 1
    
    # Unmatched opening
    for bline in brace_stack:
        add_error("Unmatched '{' found", bline)
    for pline in paren_stack:
        add_error("Unmatched '(' found", pline)
    
    # Deduplicate errors by message+line
    seen = set()
    unique_errors = []
    for e in errors:
        key = (e['error_message'], e['line_number'])
        if key not in seen:
            seen.add(key)
            unique_errors.append(e)
    
    # Re-number
    for idx, e in enumerate(unique_errors, 1):
        e['error_id'] = idx
    
    return {
        'errors': unique_errors,
        'total_errors': len(unique_errors),
        'is_valid': len(unique_errors) == 0
    }
