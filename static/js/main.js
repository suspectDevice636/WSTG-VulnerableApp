// SecureNotes V2 - JavaScript

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
}

// File drag and drop
const fileInputWrapper = document.querySelector('.file-input-wrapper');
if (fileInputWrapper) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileInputWrapper.style.borderColor = '#2563eb';
        fileInputWrapper.style.backgroundColor = '#eff6ff';
    }

    function unhighlight(e) {
        fileInputWrapper.style.borderColor = '#e5e7eb';
        fileInputWrapper.style.backgroundColor = 'white';
    }

    fileInputWrapper.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = document.querySelector('.file-input-wrapper input');
        fileInput.files = files;
    }
}
