(function () {
    const RING_CIRCUMFERENCE = 2 * Math.PI * 85;

    function getBand(score) {
        if (score < 50) return {key: 'danger', label: 'Needs Work'};
        if (score < 75) return {key: 'warning', label: 'Moderate Match'};
        return {key: 'success', label: 'Strong Match'};
    }

    function animateScore(score) {
        const ringWrap = document.getElementById('score-ring-wrap');
        const ringFill = document.getElementById('score-ring-fill');
        const numberEl = document.getElementById('score-number');
        const bandEl = document.getElementById('score-band');

        const band = getBand(score);
        const color = getComputedStyle(document.documentElement).getPropertyValue(`--${band.key}`).trim();

        ringWrap.style.setProperty('--ring-color', color);
        ringFill.style.stroke = color;
        bandEl.textContent = band.label;
        bandEl.style.color = color;

        const offset = RING_CIRCUMFERENCE * (1 - score / 100);
        requestAnimationFrame(() => {
            ringFill.style.strokeDashoffset = offset;
        });

        const duration = 1000;
        const start = performance.now();

        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            numberEl.textContent = Math.round(score * progress);
            if (progress < 1) requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    }

    function renderKeywords(matched, missing) {
        document.getElementById('matched-keywords').innerHTML = matched
            .map((word) => `<span class="pill matched">${word}</span>`)
            .join('');

        document.getElementById('missing-keywords').innerHTML = missing
            .map((word) => `<span class="pill missing">${word}</span>`)
            .join('');
    }

    function renderChecklist(formatting) {
        const list = document.getElementById('ats-checklist');

        if (!formatting) {
            list.innerHTML = '<li class="ats-item fail">Formatting data unavailable.</li>';
            return;
        }
        const items = formatting.passed
            ? [{issues: 'No formatting issues detected', passed: true}]
            : formatting.issues.map((issue) => ({issues: JSON.stringify(issue), passed: false}));

        list.innerHTML = items
            .map((check) => `
      <li class="ats-item ${check.passed ? 'pass' : 'fail'}">
        <span>${check.passed ? '/' : 'X'}</span>
        <span>${check.issues}</span>
      </li>
    `)
            .join('');
    }

    function render(data) {
        animateScore(data.overall_score);
        window.ResumeCharts.renderRadar(data.category_scores);
        renderKeywords(data.matched_keywords, data.missing_keywords);
        renderChecklist(data.formatting);
    }

    window.ResumeResults = {render};
})();
