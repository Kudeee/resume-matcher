(function () {
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
    const ACCEPTED_TYPE = 'application/pdf';
    const JD_MAX_CHARS = 5000;

    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileFeedback = document.getElementById('file-feedback');
    const jdTextarea = document.getElementById('jd-textarea');
    const charCount = document.getElementById('char-count');
    const charCounter = document.querySelector('.char-counter');

    const state = {
        file: null,
        jdText: '',
    };

    function formatBytes(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    function setFeedback(message, type) {
        fileFeedback.textContent = message;
        fileFeedback.className = `file-feedback ${type || ''}`.trim();
    }

    function validateFile(file) {
        const isPdf = file.type === ACCEPTED_TYPE || file.name.toLowerCase().endsWith('.pdf');
        if (!isPdf) {
            return {valid: false, message: 'Only PDF files are supported.'};
        }
        if (file.size > MAX_FILE_SIZE) {
            return {valid: false, message: `File is too large (${formatBytes(file.size)}). Max size is 5MB.`};
        }
        return {valid: true, message: `${file.name} — ${formatBytes(file.size)}`};
    }

    function setFile(file) {
        if (!file) return;

        const result = validateFile(file);

        if (!result.valid) {
            state.file = null;
            dropzone.classList.remove('has-file');
            setFeedback(result.message, 'error');
            emitChange();
            return;
        }

        state.file = file;
        dropzone.classList.add('has-file');
        setFeedback(result.message, 'success');
        emitChange();
    }

    function emitChange() {
        document.dispatchEvent(new CustomEvent('resume:state-changed', {
            detail: {ready: Boolean(state.file) && state.jdText.trim().length > 0},
        }));
    }

    // --- Dropzone interactions ---
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        setFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', () => {
        setFile(fileInput.files[0]);
    });

    // --- JD textarea ---
    jdTextarea.addEventListener('input', () => {
        state.jdText = jdTextarea.value;
        const length = state.jdText.length;
        charCount.textContent = length;
        charCounter.classList.toggle('near-limit', length > JD_MAX_CHARS * 0.9);
        emitChange();
    });

    window.ResumeUpload = {
        getState() {
            return {file: state.file, jdText: state.jdText};
        },
        isReady() {
            return Boolean(state.file) && state.jdText.trim().length > 0;
        },
    };
})();