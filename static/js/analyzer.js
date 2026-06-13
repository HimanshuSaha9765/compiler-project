// CompilerX - Analyzer Frontend
// Phase 3-8 - robust version

(function() {
  function initAnalyzer() {
    const btnAnalyze = document.getElementById('btnAnalyze');
    if (!btnAnalyze) { return; }

    const analyzeLabel = document.getElementById('analyzeLabel');
    const analyzeSpinner = document.getElementById('analyzeSpinner');
    const editorError = document.getElementById('editorError');

    let allTokens = [];

    function setAnalyzing(on) {
      btnAnalyze.disabled = on;
      if (analyzeLabel) analyzeLabel.classList.toggle('d-none', on);
      if (analyzeSpinner) analyzeSpinner.classList.toggle('d-none', !on);
    }
    function showError(msg) {
      if (!editorError) { alert(msg); return; }
      editorError.textContent = msg;
      editorError.classList.remove('d-none');
    }
    function clearError() {
      if (editorError) { editorError.classList.add('d-none'); editorError.textContent = ''; }
    }
    function getCode() {
      if (window.cxEditor && typeof window.cxEditor.getCode === 'function') {
        return window.cxEditor.getCode();
      }
      const el = document.getElementById('sourceEditor');
      return el ? el.value : '';
    }

    async function analyzeCode() {
      clearError();
      const code = (getCode() || '').trim();
      if (!code) { showError('Please enter some source code first.'); return; }
      if (code.length > 5000) { showError('Code exceeds 5000 character limit.'); return; }

      setAnalyzing(true);
      try {
        const res = await fetch('/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source_code: code })
        });
        const data = await res.json();
        if (!res.ok || data.success === false) {
          // If backend says not implemented, show friendly UI (Phase 3 fallback)
          if (res.status === 501) {
            renderEngineNotReady(data, code);
            return;
          }
          showError(data.error || 'Analysis failed');
          return;
        }
        renderResults(data);
      } catch (e) {
        showError('Network error: ' + e.message);
        console.error(e);
      } finally {
        setAnalyzing(false);
      }
    }

    function renderEngineNotReady(data, code) {
      const ph = document.getElementById('resultsPlaceholder');
      const rc = document.getElementById('resultsContent');
      if (ph) ph.classList.add('d-none');
      if (rc) rc.classList.remove('d-none');
      const s = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      s('scoreValue', '--');
      s('statTokens', '0'); s('statErrors', '0'); s('statWarnings', '0'); s('statSymbols', '0');
      const hb = document.getElementById('healthBadge'); if (hb) { hb.textContent = 'Phase 3 UI'; hb.className = 'badge bg-info'; }
      const hs = document.getElementById('healthSummary'); if (hs) hs.textContent = data.message || 'Compiler engine coming Phase 4-7';
      const fill = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
      fill('tokenTableBody', `<tr><td colspan="5" class="text-secondary">Token analysis – Phase 4</td></tr>`);
      fill('syntaxResults', `<div class="alert-ok">Syntax analyzer – Phase 5</div>`);
      fill('symbolTableBody', `<tr><td colspan="7" class="text-secondary">Symbol table – Phase 6</td></tr>`);
      fill('scopeTree', `<div class="text-secondary">Scope tree – Phase 6</div>`);
      fill('warningsList', `<div class="text-secondary">Error detection – Phase 7</div>`);
      fill('undeclaredList', '');
      fill('metricsGrid', `<div class="col-12 text-secondary">Metrics – Phase 7</div>`);
      const rt = document.getElementById('reportText'); if (rt) rt.value = 'CompilerX Report\nPhase 3 UI complete.\nEngine Phases 4-7 pending.\n\nCode length: ' + code.length;
      if (window.showToast) showToast(data.message || 'Engine not yet implemented – UI is ready', 'info');
    }

    function renderResults(data) {
      const ph = document.getElementById('resultsPlaceholder');
      const rc = document.getElementById('resultsContent');
      if (ph) ph.classList.add('d-none');
      if (rc) rc.classList.remove('d-none');
      renderOverview(data.diagnostics || {}, data.lexer || {});
      renderTokens((data.lexer && data.lexer.tokens) || []);
      renderSyntax(data.parser || {});
      renderSymbolTable((data.symbol_table && data.symbol_table.symbols) || []);
      renderScope(data.scope || {});
      renderErrors(data.errors || {});
      renderMetrics(data.metrics || {});
      renderReport(data);
      const firstTab = document.querySelector('#resultTabs button');
      if (firstTab && window.bootstrap) new bootstrap.Tab(firstTab).show();
      if (window.showToast) showToast('Analysis complete');
    }

    function renderOverview(diag, lexer) {
      const score = diag.health_score ?? 0;
      const sv = document.getElementById('scoreValue'); if (sv) sv.textContent = score;
      const badge = document.getElementById('healthBadge');
      if (badge) {
        let label = diag.health_label || 'OK', cls='bg-secondary';
        if (score >= 90) cls='bg-success'; else if (score >= 70) cls='bg-primary';
        else if (score >= 50) cls='bg-warning text-dark'; else if (score >= 30) cls='bg-warning text-dark';
        else cls='bg-danger';
        badge.textContent = label; badge.className = 'badge ' + cls;
      }
      const hs = document.getElementById('healthSummary'); if (hs) hs.textContent = diag.summary || '';
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      set('statTokens', lexer.total_count ?? 0);
      set('statErrors', diag.total_syntax_errors ?? 0);
      set('statWarnings', diag.total_warnings ?? 0);
      set('statSymbols', diag.total_symbols ?? 0);
      set('analysisTime', diag.analysis_time_ms ?? '--');
    }

    function renderTokens(tokens) {
      allTokens = tokens;
      const tbody = document.getElementById('tokenTableBody'); if (!tbody) return;
      tbody.innerHTML = '';
      tokens.forEach(t => {
        const tr = document.createElement('tr');
        tr.dataset.type = t.token_type;
        tr.innerHTML = `<td>${t.token_id}</td><td><code>${escapeHtml(t.token_value)}</code></td><td><span class="cx-badge-t ${t.token_type.toLowerCase()}">${t.token_type}</span></td><td>${t.line_number}</td><td>${t.column_number}</td>`;
        tbody.appendChild(tr);
      });
      const tt = document.getElementById('tokenTotalCount'); if (tt) tt.textContent = tokens.length;
      const tv = document.getElementById('tokenVisibleCount'); if (tv) tv.textContent = tokens.length;
    }

    function renderSyntax(parser) {
      const el = document.getElementById('syntaxResults'); if (!el) return;
      const count = parser.total_errors ?? 0;
      const sc = document.getElementById('syntaxCount'); if (sc) sc.textContent = count + ' errors';
      if (!count) { el.innerHTML = `<div class="alert-ok"><i class="fas fa-check-circle me-2"></i>Syntax looks correct!</div>`; return; }
      el.innerHTML = (parser.errors || []).map(e => `<div class="alert-error"><strong>Line ${e.line_number}</strong> – ${escapeHtml(e.error_message)} <span class="badge bg-danger ms-2">${e.error_type}</span></div>`).join('');
    }

    function renderSymbolTable(symbols) {
      const tbody = document.getElementById('symbolTableBody'); if (!tbody) return;
      tbody.innerHTML = '';
      symbols.forEach((s, i) => {
        const tr = document.createElement('tr');
        tr.dataset.scope = s.scope_level === 0 ? 'global' : 'local';
        tr.innerHTML = `<td>${i+1}</td><td><code>${escapeHtml(s.name)}</code></td><td>${escapeHtml(s.type)}</td><td>${s.category}</td><td>${escapeHtml(s.scope)}</td><td>${s.scope_level}</td><td>${s.line_declared}</td>`;
        tbody.appendChild(tr);
      });
      const st = document.getElementById('symbolTotalCount'); if (st) st.textContent = symbols.length;
    }

    function renderScope(scopeData) {
      const tree = document.getElementById('scopeTree'); if (!tree) return;
      if (!scopeData.tree) { tree.innerHTML = '<span class="text-secondary">No scope data</span>'; return; }
      function renderNode(node) {
        const vars = (node.variables || []).map(v => `<span class="scope-badge">${escapeHtml(v)}</span>`).join(' ');
        const children = (node.children || []).map(renderNode).join('');
        return `<div class="scope-node"><strong>${escapeHtml(node.scope_name)}</strong> <span class="text-secondary small">level ${node.scope_level}</span><div class="mt-1">${vars || '<em class="text-muted">no vars</em>'}</div>${children ? `<div class="scope-children">${children}</div>`:''}</div>`;
      }
      tree.innerHTML = renderNode(scopeData.tree);
      const vEl = document.getElementById('scopeViolations');
      if (vEl) { const violations = scopeData.violations || []; vEl.innerHTML = violations.length ? violations.map(v => `<div class="alert-error">${escapeHtml(v)}</div>`).join('') : ''; }
    }

    function renderErrors(errors) {
      const warns = errors.duplicate_warnings || [];
      const undeclared = errors.undeclared_errors || [];
      const wc = document.getElementById('warnCount'); if (wc) wc.textContent = warns.length;
      const uc = document.getElementById('undeclaredCount'); if (uc) uc.textContent = undeclared.length;
      const wl = document.getElementById('warningsList'); if (wl) wl.innerHTML = warns.length ? warns.map(w => `<div class="alert-warn">${escapeHtml(w.message)}</div>`).join('') : '<span class="text-secondary">No warnings</span>';
      const ul = document.getElementById('undeclaredList'); if (ul) ul.innerHTML = undeclared.length ? undeclared.map(e => `<div class="alert-error">${escapeHtml(e.message)}</div>`).join('') : '<span class="text-secondary">No undeclared variable errors</span>';
    }

    function renderMetrics(m) {
      const grid = document.getElementById('metricsGrid'); if (!grid) return;
      const items = [
        ['Total Lines', m.total_lines], ['Keywords', m.keyword_count], ['Identifiers', m.identifier_count],
        ['Operators', m.operator_count], ['Functions', m.function_count], ['Variables', m.variable_count],
        ['Loops', m.loop_count], ['Conditionals', m.conditional_count],
        ['Max Nesting', m.max_nesting_depth], ['String Literals', m.string_literals],
        ['Blank Lines', m.blank_lines], ['Comments', m.comment_lines],
      ];
      grid.innerHTML = items.map(([label, val]) => `<div class="col-6 col-md-4 col-lg-3"><div class="metric-card"><div class="metric-num">${val ?? 0}</div><div class="metric-label">${label}</div></div></div>`).join('');
    }

    function renderReport(data) {
      const rt = document.getElementById('reportText'); if (!rt) return;
      const d = data.diagnostics || {};
      rt.value = `CompilerX Analysis Report
=======================
Health Score: ${d.health_score ?? '--'} (${d.health_label ?? '--'})
${d.summary ?? ''}

Tokens: ${(data.lexer && data.lexer.total_count) || 0}
Syntax Errors: ${(data.parser && data.parser.total_errors) || 0}
Symbols: ${(data.symbol_table && data.symbol_table.total_count) || 0}
Warnings: ${(data.errors && data.errors.total_warnings) || 0}
Undeclared: ${(data.errors && data.errors.total_undeclared) || 0}
Analysis time: ${d.analysis_time_ms ?? '--'} ms
`;
    }

    function escapeHtml(s) { return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }

    // token filter
    const tf = document.getElementById('tokenFilters');
    if (tf) tf.addEventListener('click', e => {
      if (e.target.tagName !== 'BUTTON') return;
      tf.querySelectorAll('button').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      const filter = e.target.dataset.filter;
      let visible = 0;
      document.querySelectorAll('#tokenTableBody tr').forEach(tr => {
        const show = filter === 'ALL' || tr.dataset.type === filter;
        tr.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      const tv = document.getElementById('tokenVisibleCount'); if (tv) tv.textContent = visible;
    });

    const ts = document.getElementById('tokenSearch');
    if (ts) ts.addEventListener('input', e => {
      const q = e.target.value.toLowerCase();
      let visible = 0;
      document.querySelectorAll('#tokenTableBody tr').forEach(tr => {
        const match = tr.textContent.toLowerCase().includes(q);
        tr.style.display = match ? '' : 'none';
        if (match) visible++;
      });
      const tv = document.getElementById('tokenVisibleCount'); if (tv) tv.textContent = visible;
    });

    const ssf = document.getElementById('symbolScopeFilter');
    if (ssf) ssf.addEventListener('change', e => {
      const v = e.target.value;
      document.querySelectorAll('#symbolTableBody tr').forEach(tr => {
        tr.style.display = (v === 'all' || tr.dataset.scope === v) ? '' : 'none';
      });
    });

    btnAnalyze.addEventListener('click', analyzeCode);
    console.log('CompilerX analyzer.js initialized');
    window.cxAnalyze = analyzeCode;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnalyzer);
  } else {
    initAnalyzer();
  }
})();
