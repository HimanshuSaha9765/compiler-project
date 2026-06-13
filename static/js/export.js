(function(){
  function toast(msg){ if(window.showToast) showToast(msg); else console.log(msg); }

  function download(url, fallbackMsg) {
    fetch(url).then(r => {
      if (!r.ok) return r.json().then(j => { throw new Error(j.error || fallbackMsg); });
      return r.blob();
    }).then(blob => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = url.includes('pdf') ? 'compilerx_report.pdf' : 'compilerx_report.txt';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(a.href);
      toast('Download started');
    }).catch(err => {
      toast(err.message || fallbackMsg, 'error');
    });
  }

  function exportPdf(){ download('/export/pdf', 'PDF export failed - run Analyze first'); }
  function exportText(){ download('/export/text', 'Text export failed - run Analyze first'); }

  async function copyReport(){
    const ta = document.getElementById('reportText');
    if (!ta || !ta.value) { toast('No report to copy yet'); return; }
    try { await navigator.clipboard.writeText(ta.value); toast('Report copied to clipboard'); }
    catch(e){ ta.select(); document.execCommand('copy'); toast('Copied'); }
  }

  document.getElementById('btnExportPdf')?.addEventListener('click', e => { e.preventDefault(); exportPdf(); });
  document.getElementById('btnDownloadPdf')?.addEventListener('click', exportPdf);
  document.getElementById('btnExportText')?.addEventListener('click', e => { e.preventDefault(); exportText(); });
  document.getElementById('btnDownloadTxt')?.addEventListener('click', exportText);
  document.getElementById('btnCopyReport')?.addEventListener('click', copyReport);
})();
