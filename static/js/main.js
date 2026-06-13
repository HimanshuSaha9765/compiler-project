console.log('CompilerX main.js loaded');

function showToast(message, type = 'info') {
    console.log('[TOAST ' + type + '] ' + message);
    try {
        const toastEl = document.getElementById('cxToast');
        const toastBody = document.getElementById('cxToastBody');
        if (toastEl && toastBody && window.bootstrap && window.bootstrap.Toast) {
            toastBody.textContent = message;
            const toast = new bootstrap.Toast(toastEl, { delay: 2500 });
            toast.show();
            return;
        }
    } catch(e) {}
}
window.showToast = showToast;
