(function() {
  function initEditor() {
    const editor = document.getElementById('sourceEditor');
    const lineNumbers = document.getElementById('lineNumbers');
    const lineCountEl = document.getElementById('lineCount');
    const charCountEl = document.getElementById('charCount');
    const editorStatus = document.getElementById('editorStatus');

    if (!editor) { console.warn('editor.js: #sourceEditor not found'); return; }

    function updateEditorStats() {
      const text = editor.value || '';
      const lines = text === '' ? 1 : text.split('\n').length;
      if (lineNumbers) {
        let nums = '';
        for (let i = 1; i <= lines; i++) nums += i + '\n';
        lineNumbers.textContent = nums;
      }
      if (lineCountEl) lineCountEl.textContent = text === '' ? 0 : lines;
      if (charCountEl) charCountEl.textContent = text.length;
      if (editorStatus) editorStatus.textContent = text.length > 5000 ? 'Too long (max 5000)' : 'Ready';
    }

    editor.addEventListener('scroll', () => {
      if (lineNumbers) lineNumbers.scrollTop = editor.scrollTop;
    });
    editor.addEventListener('input', updateEditorStats);
    editor.addEventListener('keyup', updateEditorStats);

    editor.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.setRangeText('    ', start, end, 'end');
        updateEditorStats();
      }
    });

    const langSelect = document.getElementById('languageSelect');
    const langBadge = document.getElementById('languageBadge');
    if (langSelect) {
      langSelect.addEventListener('change', () => {
        if (langBadge) langBadge.textContent = langSelect.options[langSelect.selectedIndex].text;
      });
    }

    const btnClear = document.getElementById('btnClearEditor');
    if (btnClear) {
      btnClear.addEventListener('click', () => {
        editor.value = '';
        updateEditorStats();
        const ph = document.getElementById('resultsPlaceholder');
        const rc = document.getElementById('resultsContent');
        if (ph) ph.classList.remove('d-none');
        if (rc) rc.classList.add('d-none');
        if (window.showToast) showToast('Editor cleared');
      });
    }

    const btnSample = document.getElementById('btnLoadSample');
    if (btnSample) {
      btnSample.addEventListener('click', async () => {
        try {
          const res = await fetch('/api/sample', {cache: 'no-store'});
          const data = await res.json();
          if (data.success && data.sample && data.sample.code) {
            editor.value = data.sample.code;
            updateEditorStats();
            editor.dispatchEvent(new Event('input'));
            if (window.showToast) showToast('Sample loaded: ' + data.sample.name);
          } else {
            if (window.showToast) showToast('Failed to load sample', 'error');
          }
        } catch (err) {
          console.error(err);
          if (window.showToast) showToast('Sample API error: ' + err.message, 'error');
        }
      });
    }

    window.cxEditor = {
      getCode: () => editor.value || '',
      setCode: (code) => { editor.value = code || ''; updateEditorStats(); editor.dispatchEvent(new Event('input')); }
    };

    updateEditorStats();
    console.log('CompilerX editor.js initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEditor);
  } else {
    initEditor();
  }
})();
