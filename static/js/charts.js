(function () {
    let radarChart = null;

    function renderRadar(categoryScores) {
        const canvas = document.getElementById('radar-chart');
        if (!canvas) return;

        const data = {
            labels: ['Technical', 'Soft Skills', 'Tools', 'Domain'],
            datasets: [{
                label: 'Match',
                data: [
                    categoryScores.technical,
                    categoryScores.soft_skills,
                    categoryScores.tools,
                    categoryScores.domain,
                ],
                backgroundColor: 'rgba(124, 106, 247, 0.2)',
                borderColor: '#7c6af7',
                pointBackgroundColor: '#7c6af7',
                borderWidth: 2,
            }],
        };

        const options = {
            responsive: true,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    angleLines: {color: '#2a2d3e'},
                    grid: {color: '#2a2d3e'},
                    pointLabels: {color: '#e2e8f0', font: {family: 'Inter', size: 12}},
                    ticks: {display: false, backdropColor: 'transparent'},
                },
            },
            plugins: {
                legend: {display: false},
            },
        };

        if (radarChart) {
            radarChart.data = data;
            radarChart.update();
            return;
        }

        radarChart = new Chart(canvas, {type: 'radar', data, options});
    }

    window.ResumeCharts = {renderRadar};
})();
