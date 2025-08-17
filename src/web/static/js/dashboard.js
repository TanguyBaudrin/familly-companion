// src/web/static/js/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard script loaded.');

    // Get loading indicator elements
    const leaderboardLoading = document.getElementById('leaderboard-loading');
    const tasksLoading = document.getElementById('tasks-loading');
    const rewardsLoading = document.getElementById('rewards-loading');

    // Function to show/hide loading indicators
    function showLoading(element) {
        if (element) element.style.display = 'block';
    }

    function hideLoading(element) {
        if (element) element.style.display = 'none';
    }

    // Function to fetch data from API
    async function fetchData(url, options = {}) {
        try {
            // For now, we'll use a dummy token. In a real app, this would come from login.
            const token = 'dummy-token'; 
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                ...options
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            // For DELETE requests, response.json() might fail if no content is returned
            if (options.method === 'DELETE') {
                return true;
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
            M.toast({html: `Erreur: ${error.message} ❌`, classes: 'red darken-1'});
            return null;
        }
    }

    // Fetch and display family members (leaderboard)
    async function loadLeaderboard() {
        showLoading(leaderboardLoading);
        const members = await fetchData('/api/leaderboard');
        const leaderboardList = document.getElementById('leaderboard-list');
        if (leaderboardList && members) {
            leaderboardList.innerHTML = ''; // Clear existing content
            members.forEach(member => {
                const li = document.createElement('li');
                li.className = 'collection-item';
                li.innerHTML = `<div>${member.name}<span class="secondary-content">${member.total_points} points ✨</span></div>`;
                leaderboardList.appendChild(li);
            });
        }
        hideLoading(leaderboardLoading);
    }

    // Fetch and display tasks
    async function loadTasks() {
        showLoading(tasksLoading);
        const tasks = await fetchData('/api/tasks');
        const taskList = document.getElementById('task-list');
        if (taskList && tasks) {
            taskList.innerHTML = '';
            tasks.forEach(task => {
                const li = document.createElement('li');
                li.className = 'collection-item';
                let statusText = task.status === 'completed' ? 'Terminée ✅' : 'En cours ⏳';
                let completeButton = '';
                if (task.status !== 'completed') {
                    completeButton = `<a href="#!" class="secondary-content btn-floating btn-small waves-effect waves-light green" data-task-id="${task.id}"><i class="material-icons">check</i></a>`;
                }
                li.innerHTML = `<div>${task.description} - ${task.points} points <span class="secondary-content">Statut: ${statusText}</span>${completeButton}</div>`;
                taskList.appendChild(li);
            });
            // Add event listeners for complete buttons
            document.querySelectorAll('#task-list .btn-floating').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const taskId = event.currentTarget.dataset.taskId;
                    const result = await fetchData(`/api/tasks/${taskId}/complete`, { method: 'POST' });
                    if (result) {
                        M.toast({html: 'Tâche marquée comme terminée! ✅', classes: 'green darken-1'});
                        loadTasks(); // Reload tasks to update status
                        loadLeaderboard(); // Reload leaderboard to update points
                    }
                });
            });
        }
        hideLoading(tasksLoading);
    }

    // Fetch and display rewards
    async function loadRewards() {
        showLoading(rewardsLoading);
        const rewards = await fetchData('/api/rewards');
        const rewardList = document.getElementById('reward-list');
        if (rewardList && rewards) {
            rewardList.innerHTML = '';
            rewards.forEach(reward => {
                const li = document.createElement('li');
                li.className = 'collection-item';
                li.innerHTML = `<div>${reward.name} - ${reward.cost} points <span class="secondary-content">${reward.description || ''}</span><a href="#!" class="secondary-content btn-floating btn-small waves-effect waves-light blue" data-reward-id="${reward.id}"><i class="material-icons">card_giftcard</i></a></div>`;
                rewardList.appendChild(li);
            });
            // Add event listeners for claim buttons
            document.querySelectorAll('#reward-list .btn-floating').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const rewardId = event.currentTarget.dataset.rewardId;
                    // For now, assume member_id 1 for testing. This should be dynamic.
                    const memberId = 1; 
                    const result = await fetchData(`/api/members/${memberId}/claim_reward/${rewardId}`, { method: 'POST' });
                    if (result) {
                        M.toast({html: 'Récompense réclamée! 🎁', classes: 'blue darken-1'});
                        loadRewards(); // Reload rewards
                        loadLeaderboard(); // Reload leaderboard to update points
                    }
                });
            });
        }
        hideLoading(rewardsLoading);
    }

    // Populate task assignee dropdown
    async function populateAssigneeDropdown() {
        const assigneeSelect = document.getElementById('task_assignee');
        if (assigneeSelect) {
            const members = await fetchData('/api/members');
            if (members) {
                // Clear existing options except the first disabled one
                assigneeSelect.innerHTML = '<option value="" disabled selected>Assigner à...</option>';
                members.forEach(member => {
                    const option = document.createElement('option');
                    option.value = member.id;
                    option.textContent = member.name;
                    assigneeSelect.appendChild(option);
                });
                M.FormSelect.init(assigneeSelect); // Re-initialize Materialize select
            }
        }
    }

    // Handle Add Task Form Submission
    const addTaskForm = document.getElementById('add-task-form');
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default form submission

            const description = document.getElementById('task_name').value;
            const points = parseInt(document.getElementById('task_points').value);
            const assignedToId = parseInt(document.getElementById('task_assignee').value); // Assuming member ID for now

            if (!description || isNaN(points) || isNaN(assignedToId)) {
                M.toast({html: 'Veuillez remplir tous les champs de la tâche. 📝', classes: 'red darken-1'});
                return;
            }

            const newTask = {
                description: description,
                points: points,
                assigned_to_id: assignedToId
            };

            const result = await fetchData('/api/tasks', {
                method: 'POST',
                body: JSON.stringify(newTask)
            });

            if (result) {
                M.toast({html: 'Nouvelle tâche ajoutée! ✨', classes: 'green darken-1'});
                addTaskForm.reset(); // Clear form
                loadTasks(); // Reload tasks
                M.FormSelect.init(document.querySelectorAll('select')); // Re-initialize selects after reset
            }
        });
    }

    // Initial data load
    loadLeaderboard();
    loadTasks();
    loadRewards();
    populateAssigneeDropdown(); // Populate assignee dropdown on load
});
