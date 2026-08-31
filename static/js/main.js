(function () {
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnSpinner = analyzeBtn.querySelector('.btn-spinner');
    const resultsSection = document.getElementById('results-section');

    function setLoading(isLoading) {
        analyzeBtn.disabled = isLoading;
        btnText.hidden = isLoading;
        btnSpinner.hidden = isLoading;
    }

    async function uploadResume(file) {
        const formData = new FormData();
        formData.append('resume', file);

        const res = await fetch('/api/upload', {method: 'POST', body: formData});

        if (!res.ok) {
            throw new Error(`Upload failed (${res.status})`);
        }

        return res.json();
    }

    async function runAnalysis(resumeText, formatting, jdText) {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                resume_text: resumeText,
                jd_text: jdText,
                formatting: formatting,
            })
        });

        if (!res.ok) {
            throw new Error(`Analyze failed (${res.status})`);
        }

        return res.json();
    }

    async function analyze(file, jdText) {
        const {resume_text, formatting} = await uploadResume(file);
        return runAnalysis(resume_text, formatting, jdText);
    }

    document.addEventListener('resume:state-changed', (e) => {
        analyzeBtn.disabled = !e.detail.ready;
    });

    analyzeBtn.addEventListener('click', async () => {
        const {file, jdText} = window.ResumeUpload.getState();
        setLoading(true);

        try {
            const data = await analyze(file, jdText);
            resultsSection.hidden = false;
            window.ResumeResults.render(data);
            resultsSection.scrollIntoView({behavior: 'smooth', block: 'start'});
        } catch (e) {
            console.error(e);
            alert('Something went wrong analyzing your resume. Check the console for details');
        } finally {
            setLoading(false);
        }
    });

})();