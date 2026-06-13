(function(){
  let currentSuggestions = [];
  let lastFixedCode = '';

  const listEl = document.getElementById('suggestionsList');
  const badgeEl = document.getElementById('suggestionCountBadge');
  const summaryEl = document.getElementById('suggestionSummary');
  const healthBanner = document.getElementById('suggestionHealthBanner');
  const healthText = document.getElementById('suggestionHealthText');
  const fixedPreview = document.getElementById('fixedCodePreview');
  const btnApplyAll = document.getElementById('btnApplyAllFixes');
  const btnRefresh = document.getElementById('btnRefreshSuggestions');
  const btnReplace = document.getElementById('btnReplaceInEditor');
  const btnCopyFixed = document.getElementById('btnCopyFixed');
  const aiBox = document.getElementById('aiExplanationBox');
  const aiBadge = document.getElementById('aiBadge');

  if (!listEl) return; 

  function getCode() {
    if (window.cxEditor && window.cxEditor.getCode) return window.cxEditor.getCode();
    const el = document.getElementById('sourceEditor');
    return el ? el.value : '';
  }

  async function loadSuggestions() {
    const code = getCode();
    if (!code.trim()) { if(window.showToast) showToast('Analyze code first', 'error'); return; }
    
    listEl.innerHTML = '<div class="text-secondary">Loading suggestions...</div>';
    try {
      const res = await fetch('/suggest', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({source_code: code})
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'failed');
      
      currentSuggestions = data.suggestions || [];
      renderSuggestionsList(currentSuggestions);
      
      const count = currentSuggestions.length;
      const autoFixable = data.auto_fixable_count || 0;
      const curHealth = data.current_health || 0;
      const predHealth = data.predicted_health || curHealth;
      
      if (badgeEl) {
        badgeEl.textContent = count;
        badgeEl.style.display = count ? 'inline-block' : 'none';
      }
      if (summaryEl) summaryEl.textContent = count ? `${count} issue${count>1?'s':''} found – ${autoFixable} auto-fixable` : 'No issues – code is clean!';
      
      if (healthBanner && healthText) {
        healthBanner.classList.remove('d-none');
        if (count === 0) {
          healthText.textContent = '✅ No issues found – Health Score is excellent!';
        } else {
          healthText.textContent = `Found ${count} issue${count>1?'s':''} – Apply fixes to improve Health ${curHealth} → ${predHealth}`;
        }
      }
      
      if (autoFixable > 0) {
        runAutofixPreview();
      }

      const pill = document.getElementById('suggestionPill');
      const pillCount = document.getElementById('suggestionPillCount');
      if (pill && pillCount) {
        if (count > 0) {
          pillCount.textContent = count;
          pill.classList.remove('d-none');
        } else {
          pill.classList.add('d-none');
        }
      }
      
      if (btnApplyAll) btnApplyAll.disabled = autoFixable === 0;
      
    } catch (e) {
      listEl.innerHTML = '<div class="text-danger">Failed to load suggestions: ' + e.message + '</div>';
      console.error(e);
    }
  }

  function renderSuggestionsList(suggestions) {
    if (!suggestions.length) {
      listEl.innerHTML = '<div class="alert-ok"><i class="fas fa-check-circle me-2"></i>No issues found – your code is clean!</div>';
      return;
    }
    listEl.innerHTML = suggestions.map(s => {
      const color = s.severity === 'ERROR' ? 'danger' : s.severity === 'WARNING' ? 'warning' : 'info';
      const badgeClass = s.severity === 'ERROR' ? 'bg-danger' : s.severity === 'WARNING' ? 'bg-warning text-dark' : 'bg-info';
      return `<div class="cx-suggestion-card border-${color}">
        <div class="d-flex justify-content-between align-items-start">
          <div><span class="badge ${badgeClass}">${s.severity}</span>
          <span class="small text-secondary ms-2">Line ${s.line_number}</span></div>
          <span class="badge bg-secondary">+${s.health_impact}</span>
        </div>
        <div class="mt-2"><strong>${escapeHtml(s.issue)}</strong></div>
        <div class="text-secondary small mt-1">Fix: ${escapeHtml(s.fix)}</div>
        <div class="mt-2 d-flex gap-2">
          <button class="btn btn-sm btn-outline-light btn-apply-single" data-sid="${s.suggestion_id}" ${s.auto_fixable ? '' : 'disabled'}>Apply</button>
          <button class="btn btn-sm cx-btn-ghost btn-ai-explain" data-sid="${s.suggestion_id}">✨ AI Explain</button>
        </div>
        <div class="ai-explain-result small mt-2 text-info" id="ai-exp-${s.suggestion_id}" style="display:none"></div>
      </div>`;
    }).join('');

    listEl.querySelectorAll('.btn-apply-single').forEach(btn => {
      btn.addEventListener('click', () => {
        const sid = parseInt(btn.dataset.sid);
        runAutofixPreview([sid]);
      });
    });

    listEl.querySelectorAll('.btn-ai-explain').forEach(btn => {
      btn.addEventListener('click', () => aiExplain(parseInt(btn.dataset.sid), btn));
    });
  }

  async function runAutofixPreview(selectedIds = null) {
    const code = getCode();
    try {
      const res = await fetch('/autofix', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({source_code: code, suggestion_ids: selectedIds})
      });
      const data = await res.json();
      if (data.success) {
        lastFixedCode = data.fixed_code;
        if (fixedPreview) fixedPreview.value = lastFixedCode;
        if (btnReplace) btnReplace.disabled = false;
        if (window.showToast) showToast(`Applied ${data.applied_count} fix(es) – New Health: ${data.new_health_score}`);
      } else {
        if (window.showToast) showToast(data.error || 'Autofix failed', 'error');
      }
    } catch (e) {
      console.error(e);
      if (window.showToast) showToast('Autofix network error', 'error');
    }
  }

  async function aiExplain(suggestionId, btn) {
    const suggestion = currentSuggestions.find(s => s.suggestion_id === suggestionId);
    if (!suggestion) return;
    const outEl = document.getElementById('ai-exp-' + suggestionId);
    if (!outEl) return;
    outEl.style.display = 'block';
    outEl.textContent = 'Asking AI…';
    btn.disabled = true;
    try {
      const res = await fetch('/ai_explain', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({suggestion: suggestion, source_code: getCode()})
      });
      const data = await res.json();
      if (data.success && data.explanation) {
        outEl.textContent = data.explanation;
        if (aiBadge) { aiBadge.textContent = data.provider || 'AI'; aiBadge.className = 'badge bg-success'; }
      } else {
        outEl.textContent = data.reason || data.error || 'AI explain unavailable – using offline rule-based fix. Set GROQ_API_KEY to enable AI.';
        if (aiBadge) { aiBadge.textContent = 'Offline'; aiBadge.className = 'badge bg-secondary'; }
      }
    } catch (e) {
      outEl.textContent = 'AI service unavailable. Offline fix is still available.';
    } finally {
      btn.disabled = false;
    }
  }

  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }

  if (btnRefresh) btnRefresh.addEventListener('click', loadSuggestions);
  if (btnApplyAll) btnApplyAll.addEventListener('click', () => runAutofixPreview(null));
  if (btnCopyFixed) btnCopyFixed.addEventListener('click', async () => {
    if (!lastFixedCode) { if(window.showToast) showToast('No fixed code yet'); return; }
    try { await navigator.clipboard.writeText(lastFixedCode); if(window.showToast) showToast('Fixed code copied'); }
    catch(e){ if(window.showToast) showToast('Copy failed', 'error'); }
  });
  if (btnReplace) btnReplace.addEventListener('click', () => {
    if (!lastFixedCode) return;
    if (window.cxEditor && window.cxEditor.setCode) {
      window.cxEditor.setCode(lastFixedCode);
    } else {
      const ed = document.getElementById('sourceEditor');
      if (ed) { ed.value = lastFixedCode; ed.dispatchEvent(new Event('input')); }
    }
    // switch to Overview tab and trigger analyze
    const overviewTab = document.querySelector('button[data-bs-target="#tab-overview"]');
    if (overviewTab && window.bootstrap) new bootstrap.Tab(overviewTab).show();
    setTimeout(() => { if (window.cxAnalyze) window.cxAnalyze(); }, 150);
    if (window.showToast) showToast('Code replaced – re-analyzing…');
  });

  const originalRenderResults = window.renderResults;

  const resultsContent = document.getElementById('resultsContent');
  if (resultsContent) {
    const observer = new MutationObserver(() => {
      if (!resultsContent.classList.contains('d-none')) {
        setTimeout(loadSuggestions, 400);
        observer.disconnect();
      }
    });
    observer.observe(resultsContent, {attributes: true, attributeFilter: ['class']});
  }

  document.getElementById('gotoSuggestionsLink')?.addEventListener('click', (e) => {
    e.preventDefault();
    const tabBtn = document.getElementById('suggestionsTabBtn');
    if (tabBtn && window.bootstrap) new bootstrap.Tab(tabBtn).show();
  });

  window.cxLoadSuggestions = loadSuggestions;
  console.log('CompilerX suggestions.js initialized');
})();
