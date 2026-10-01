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

    const ICONS = {
        pass: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
        fail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    };

    // The parser reports issues as {page|block: n, issue: ['image', 'table', ...]}.
    // Each check below claims the issue labels it understands.
    const ATS_CHECKS = [
        {
            title: 'No images or graphics',
            passText: 'No images found, so everything on the page can be read by an ATS.',
            failText: 'ATS parsers skip images, so any text inside them is invisible.',
            fix: 'Replace images with plain text and remove logos or icons from the resume body.',
            matches: (label) => label.includes('image'),
        },
        {
            title: 'No tables',
            passText: 'No tables found, so reading order stays intact.',
            failText: 'Tables can scramble reading order and merge unrelated text together.',
            fix: 'Rebuild table content as simple headings and bullet points.',
            matches: (label) => label === 'table',
        },
    ];

    function locationLabel(entry, label) {
        const where = entry.page ? `Page ${entry.page}` : `Block ${entry.block}`;
        return label.includes('table') && label !== 'table' ? `${where} (in table)` : where;
    }

    function collectLocations(issues, matches) {
        const seen = new Set();
        issues.forEach((entry) => {
            (entry.issue || []).filter(matches).forEach((label) => {
                seen.add(locationLabel(entry, label));
            });
        });
        return [...seen];
    }

    function buildRows(formatting) {
        const issues = formatting.issues || [];
        const known = (label) => ATS_CHECKS.some((check) => check.matches(label));

        const rows = ATS_CHECKS.map((check) => {
            const locations = collectLocations(issues, check.matches);
            return {
                passed: locations.length === 0,
                title: check.title,
                text: locations.length === 0 ? check.passText : check.failText,
                fix: check.fix,
                locations,
            };
        });

        // Anything the parser flags that no check above understands still gets shown.
        const otherLabels = new Set();
        issues.forEach((entry) => {
            (entry.issue || []).filter((label) => !known(label)).forEach((label) => otherLabels.add(label));
        });
        if (otherLabels.size) {
            rows.push({
                passed: false,
                title: 'Other formatting issues',
                text: 'These elements may not be read correctly by an ATS.',
                fix: 'Simplify the layout and stick to plain text where possible.',
                locations: [...otherLabels],
            });
        }
        return rows;
    }

    function renderChecklist(formatting) {
        const list = document.getElementById('ats-checklist');
        const badge = document.getElementById('ats-badge');

        if (!formatting) {
            badge.textContent = 'Unavailable';
            badge.className = 'ats-badge';
            list.innerHTML = '<li class="ats-empty">Formatting data unavailable.</li>';
            return;
        }

        const rows = buildRows(formatting);
        const passedCount = rows.filter((row) => row.passed).length;
        const allPassed = passedCount === rows.length;

        badge.textContent = allPassed ? 'All checks passed' : `${passedCount} of ${rows.length} passed`;
        badge.className = `ats-badge ${allPassed ? 'pass' : 'fail'}`;

        list.innerHTML = rows
            .map((row) => {
                const state = row.passed ? 'pass' : 'fail';
                const details = row.passed ? '' : `
          <div class="ats-locations">
            ${row.locations.map((loc) => `<span class="ats-chip">${loc}</span>`).join('')}
          </div>
          <p class="ats-fix"><strong>Fix:</strong> ${row.fix}</p>`;

                return `
        <li class="ats-item ${state}">
          <span class="ats-icon">${ICONS[state]}</span>
          <div class="ats-body">
            <p class="ats-title">${row.title}</p>
            <p class="ats-desc">${row.text}</p>${details}
          </div>
          <span class="ats-status">${row.passed ? 'Passed' : 'Needs fix'}</span>
        </li>`;
            })
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