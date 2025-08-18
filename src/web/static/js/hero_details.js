document.addEventListener('DOMContentLoaded', function () {
    const memberId = window.location.pathname.split('/').pop();

    const dailyPointsChartCtx = document.getElementById('daily-points-chart').getContext('2d');
    let dailyPointsChart;

    const weeklyBtn = document.getElementById('weekly-btn');
    const monthlyBtn = document.getElementById('monthly-btn');

    const loaders = {
        points: document.getElementById('points-chart-loading'),
        pending: document.getElementById('pending-tasks-loading'),
        completed: document.getElementById('completed-tasks-loading'),
        rewards: document.getElementById('rewards-history-loading')
    };

    const lists = {
        pending: document.getElementById('pending-tasks-list'),
        completed: document.getElementById('completed-tasks-list'),
        rewards: document.getElementById('rewards-history-list')
    };

    function showAllLoaders() {
        for (const key in loaders) {
            loaders[key].style.display = 'block';
        }
    }

    function hideAllLoaders() {
        for (const key in loaders) {
            loaders[key].style.display = 'none';
        }
    }

    async function fetchDetails(period = 'weekly') {
        showAllLoaders();
        try {
            const response = await fetch(`/api/v1/members/${memberId}/details?period=${period}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Ne mettre à jour les listes que lors du premier chargement
            if (period === 'weekly') { 
                updateTaskLists(data.pending_tasks, data.completed_tasks);
                updateRewardsHistory(data.claimed_rewards);
            }
            updateChart(data.daily_points);

        } catch (error) {
            console.error('Failed to fetch member details:', error);
            M.toast({ html: 'Erreur lors du chargement des détails du héros.' });
        } finally {
            hideAllLoaders();
        }
    }

    function updateTaskLists(pending, completed) {
        // Vider les listes existantes (sauf l'en-tête)
        lists.pending.innerHTML = '<li class="collection-header"><h5>En attente</h5></li>';
        lists.completed.innerHTML = '<li class="collection-header"><h5>Terminées</h5></li>';

        if (pending.length === 0) {
            lists.pending.innerHTML += '<li class="collection-item">Aucune quête en cours.</li>';
        }
        pending.forEach(task => {
            const item = `<li class="collection-item">${task.description} - <strong>${task.points} pts</strong></li>`;
            lists.pending.innerHTML += item;
        });

        if (completed.length === 0) {
            lists.completed.innerHTML += '<li class="collection-item">Aucun haut fait à afficher.</li>';
        }
        completed.forEach(task => {
            const completedDate = new Date(task.completed_at).toLocaleDateString('fr-FR');
            const item = `<li class="collection-item">${task.description} (Terminée le ${completedDate})</li>`;
            lists.completed.innerHTML += item;
        });
    }

    function updateRewardsHistory(rewards) {
        lists.rewards.innerHTML = '<li class="collection-header"><h5>Récompenses</h5></li>';
        if (rewards.length === 0) {
            lists.rewards.innerHTML += '<li class="collection-item">Aucun trésor acquis pour le moment.</li>';
        }
        rewards.forEach(reward => {
            const claimedDate = new Date(reward.claimed_at).toLocaleDateString('fr-FR');
            const item = `<li class="collection-item">${reward.name} - <strong>Obtenu le ${claimedDate}</strong></li>`;
            lists.rewards.innerHTML += item;
        });
    }

    function updateChart(dailyPoints) {
        if (dailyPointsChart) {
            dailyPointsChart.destroy();
        }

        dailyPointsChart = new Chart(dailyPointsChartCtx, {
            type: 'line',
            data: {
                labels: dailyPoints.map(item => new Date(item.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })),
                datasets: [{
                    label: 'Points Gagnés par Jour',
                    data: dailyPoints.map(item => item.points),
                    fill: true,
                    borderColor: '#3e2723',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    tension: 0.3,
                    pointBackgroundColor: '#5d4037',
                    pointRadius: 5
                }]
            },
            options: {
                scales: {
                    y: {
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
    }

    weeklyBtn.addEventListener('click', () => fetchDetails('weekly'));
    monthlyBtn.addEventListener('click', () => fetchDetails('monthly'));

    // Initial fetch
    fetchDetails('weekly');
});