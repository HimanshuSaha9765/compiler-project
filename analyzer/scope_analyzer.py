# CompilerX - Scope Analyzer
# Phase 6

def analyze_scope(tokens, symbol_table):
    """
    Build scope tree
    """
    # Build a simple scope tree from symbol_table
    symbols = symbol_table.get('symbols', [])
    
    # Group symbols by scope_level
    scopes = {}
    for s in symbols:
        lvl = s['scope_level']
        scopes.setdefault(lvl, []).append(s['name'])
    
    # Build tree: global -> level 1 -> level 2 ...
    def build_node(level, parent_name):
        names = scopes.get(level, [])
        node = {
            'scope_id': level + 1,
            'scope_name': 'global' if level == 0 else f'block_level_{level}',
            'scope_level': level,
            'parent_scope': parent_name,
            'variables': names,
            'children': []
        }
        # if next level exists, add as child
        if level + 1 in scopes:
            child = build_node(level + 1, node['scope_name'])
            node['children'] = [child]
        return node
    
    tree = build_node(0, None)
    tree['scope_name'] = 'global'
    
    # Try to give better names for functions
    funcs = [s for s in symbols if s['category'] == 'function']
    if funcs:
        tree['scope_name'] = 'global'
        tree['variables'] = [s['name'] for s in symbols if s['scope_level'] == 0]
        # add function scopes as children
        children = []
        for idx, f in enumerate(funcs, start=2):
            fn_vars = [s['name'] for s in symbols if s['scope_level'] >= 1]
            children.append({
                'scope_id': idx,
                'scope_name': f"function: {f['name']}",
                'scope_level': 1,
                'parent_scope': 'global',
                'variables': fn_vars,
                'children': []
            })
        if children:
            tree['children'] = children
    
    total_scopes = len(scopes) if scopes else 1
    
    return {
        'tree': tree,
        'violations': [],
        'total_scopes': total_scopes
    }
