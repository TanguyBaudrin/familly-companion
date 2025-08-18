document.addEventListener('DOMContentLoaded', function () {
    const pointsChartCtx = document.getElementById('points-chart').getContext('2d');
    const rewardsChartCtx = document.getElementById('rewards-chart').getContext('2d');
    const weeklyBtn = document.getElementById('weekly-btn');
    const monthlyBtn = document.getElementById('monthly-btn');
    const pointsLoader = document.getElementById('points-chart-loading');
    const rewardsLoader = document.getElementById('rewards-chart-loading');

    let pointsChart;
    let rewardsChart;

    const chartColors = [
        '#FFC300', // Jaune Vif
        '#FF5733', // Orange Rougeâtre
        '#C70039', // Rouge Foncé
        '#900C3F', // Bordeaux
        '#581845', // Aubergine
        '#2ECC71', // Vert Émeraude
        '#3498DB', // Bleu Ciel
        '#F39C12', // Orange
        '#D35400', // Citrouille
        '#8E44AD'  // Violet
    ];

    async function fetchStats(period = 'weekly') {
        showLoaders();
        try {
            const response = await fetch(`/api/v1/statistiques?period=${period}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            updateCharts(data);
        } catch (error) {
            console.error('Failed to fetch statistics:', error);
            M.toast({ html: 'Erreur lors du chargement des statistiques.' });
        } finally {
            hideLoaders();
        }
    }

    function showLoaders() {
        pointsLoader.style.display = 'block';
        rewardsLoader.style.display = 'block';
        document.getElementById('points-chart').style.display = 'none';
        document.getElementById('rewards-chart').style.display = 'none';
    }

    function hideLoaders() {
        pointsLoader.style.display = 'none';
        rewardsLoader.style.display = 'none';
        document.getElementById('points-chart').style.display = 'block';
        document.getElementById('rewards-chart').style.display = 'block';
    }

    function updateCharts(data) {
        // Destroy existing charts if they exist
        if (pointsChart) {
            pointsChart.destroy();
        }
        if (rewardsChart) {
            rewardsChart.destroy();
        }

        // Points Chart (Horizontal Bar)
        pointsChart = new Chart(pointsChartCtx, {
            type: 'bar',
            data: {
                labels: data.points_by_user.map(item => `⭐ ${item.name}`),
                datasets: [{
                    label: 'Points Gagnés',
                    data: data.points_by_user.map(item => item.points),
                    backgroundColor: chartColors,
                    borderColor: chartColors.map(color => color.replace('0.7', '1')),
                    borderWidth: 2,
                    borderRadius: 10
                }]
            },
            options: {
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Rewards Chart (Doughnut)
        rewardsChart = new Chart(rewardsChartCtx, {
            type: 'doughnut',
            data: {
                labels: data.most_used_rewards.map(item => `🎁 ${item.name}`),
                datasets: [{
                    label: 'Récompenses Utilisées',
                    data: data.most_used_rewards.map(item => item.count),
                    backgroundColor: chartColors.slice().reverse(), // Use a different part of the color palette
                    hoverOffset: 8,
                    borderWidth: 2,
                    borderColor: '#fff8e1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    weeklyBtn.addEventListener('click', () => fetchStats('weekly'));
    monthlyBtn.addEventListener('click', () => fetchStats('monthly'));

    // Initial fetch
    fetchStats('weekly');
});