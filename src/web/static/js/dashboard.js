document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard script loaded.');

    // Initialize Materialize components
    const assignUserModal = M.Modal.init(document.getElementById('assign-user-modal'));
    const claimRewardModal = M.Modal.init(document.getElementById('claim-reward-modal'));

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

    // Helper function to format duration
    function formatDuration(value, unit) {
        if (value && unit) {
            return `(${value} ${unit})`;
        }
        return '';
    }

    // Function to fetch data from API
    async function fetchData(url, options = {}) {
        try {
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
            if (options.method === 'DELETE' || response.status === 204) {
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
            leaderboardList.innerHTML = '';
            members.forEach(member => {
                const li = document.createElement('li');
                li.className = 'collection-item';
                li.innerHTML = `<div><a href="/members/${member.id}">${member.name}</a><span class="secondary-content">${member.total_points} points ✨</span></div>`;
                leaderboardList.appendChild(li);
            });
        }
        hideLoading(leaderboardLoading);
    }

    // Fetch and display tasks
    async function loadTasks() {
        showLoading(tasksLoading);
        // Calculer la date d'il y a 7 jours au format ISO (UTC)
        const now = new Date();
        const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const isoOneWeekAgo = oneWeekAgo.toISOString();

        // Appel API avec filtre created_after
        const tasks = await fetchData(`/api/tasks?created_after=${encodeURIComponent(isoOneWeekAgo)}`);
        const members = await fetchData('/api/members');
        const questsByPersonContainer = document.getElementById('quests-by-person-container');

        const memberMap = new Map();
        if (members) {
            members.forEach(member => {
                memberMap.set(member.id, member.name);
            });
        }

        const groupedTasks = {
            unassigned: []
        };

        if (tasks) {
            tasks.forEach(task => {
                if (task.assigned_to_id) {
                    if (!groupedTasks[task.assigned_to_id]) {
                        groupedTasks[task.assigned_to_id] = [];
                    }
                    groupedTasks[task.assigned_to_id].push(task);
                } else {
                    groupedTasks.unassigned.push(task);
                }
            });
        }

        if (questsByPersonContainer) {
            questsByPersonContainer.innerHTML = '';

            // Helper to format date in French
            function formatDateFr(dateStr) {
                if (!dateStr) return '';
                const date = new Date(dateStr);
                return date.toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' });
            }

            // Helper to compute remaining time
            function getRemainingTime(task) {
                if (!task.duration_value || !task.duration_unit || !task.created_at) return '';
                const created = new Date(task.created_at);
                let msToAdd = 0;
                switch (task.duration_unit) {
                    case 'days': msToAdd = task.duration_value * 24 * 60 * 60 * 1000; break;
                    case 'weeks': msToAdd = task.duration_value * 7 * 24 * 60 * 60 * 1000; break;
                    case 'months': msToAdd = task.duration_value * 30 * 24 * 60 * 60 * 1000; break;
                    default: return '';
                }
                const expiration = new Date(created.getTime() + msToAdd);
                const now = new Date();
                const diff = expiration - now;
                if (diff <= 0) return '<span class="red-text">Temps écoulé ⏰</span>';
                // Format remaining time
                const days = Math.floor(diff / (24 * 60 * 60 * 1000));
                const hours = Math.floor((diff % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
                const minutes = Math.floor((diff % (60 * 60 * 1000)) / (60 * 1000));
                let txt = 'Temps restant : ';
                if (days > 0) txt += `${days}j `;
                if (hours > 0) txt += `${hours}h `;
                if (minutes > 0) txt += `${minutes}min`;
                return txt.trim();
            }

            // Render unassigned tasks first
            if (groupedTasks.unassigned.length > 0) {
                const unassignedSection = document.createElement('div');
                unassignedSection.className = 'col s12 m6';
                unassignedSection.innerHTML = `
                    <div class="card-panel grey lighten-4 z-depth-1">
                        <h5 class="custom-title">Tâches non assignées (Famille) 👨‍👩‍👧‍👦</h5>
                        <ul class="collection">
                            ${groupedTasks.unassigned.map(task => `
                                <li class="collection-item">
                                    <div style="display: flex; align-items: center; justify-content: space-between;">
                                        <span>
                                            ${task.description} 📝 - ${task.points} points ${formatDuration(task.duration_value, task.duration_unit)}
                                            <br>
                                            ${task.status === 'completed' ? `<span class='grey-text'>Réalisée le : ${formatDateFr(task.completed_at)}</span>` : getRemainingTime(task)}
                                        </span>
                                        <span class="quest-actions">
                                            <span class="quest-status-text">Statut: ${task.status === 'completed' ? 'Terminée ✅' : 'En cours ⏳'}</span>
                                            ${task.status !== 'completed' ? `<a href="#" class="btn-small waves-effect waves-light green complete-task-btn" data-task-id="${task.id}" data-assigned-to="${task.assigned_to_id}" title="Valider la quête"><i class="material-icons">check</i></a>` : ''}
                                        </span>
                                    </div>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
                questsByPersonContainer.appendChild(unassignedSection);
            }

            // Render tasks for each person
            memberMap.forEach((memberName, memberId) => {
                const memberTasks = groupedTasks[memberId];
                if (memberTasks && memberTasks.length > 0) {
                    const memberSection = document.createElement('div');
                    memberSection.className = 'col s12 m6';
                    memberSection.innerHTML = `
                        <div class="card-panel light-blue lighten-5 z-depth-1">
                            <h5 class="custom-title">Quêtes de ${memberName} 🧑‍🚀</h5>
                            <ul class="collection">
                                ${memberTasks.map(task => `
                                    <li class="collection-item">
                                        <div style="display: flex; align-items: center; justify-content: space-between;">
                                            <span>
                                                ${task.description} 📝 - ${task.points} points ${formatDuration(task.duration_value, task.duration_unit)}
                                                <br>
                                                ${task.status === 'completed' ? `<span class='grey-text'>Réalisée le : ${formatDateFr(task.completed_at)}</span>` : getRemainingTime(task)}
                                            </span>
                                            <span class="quest-actions">
                                                <span class="quest-status-text">Statut: ${task.status === 'completed' ? 'Terminée ✅' : 'En cours ⏳'}</span>
                                                ${task.status !== 'completed' ? `<a href="#" class="btn-small waves-effect waves-light green complete-task-btn" data-task-id="${task.id}" data-assigned-to="${task.assigned_to_id}" title="Valider la quête"><i class="material-icons">check</i></a>` : ''}
                                            </span>
                                        </div>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `;
                    questsByPersonContainer.appendChild(memberSection);
                }
            });

            // Add event listeners for complete buttons
            document.querySelectorAll('.complete-task-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const taskId = event.currentTarget.dataset.taskId;
                    const assignedToId = event.currentTarget.dataset.assignedTo;

                    if (assignedToId && assignedToId !== 'null') {
                        // Task is assigned, complete it directly
                        const result = await fetchData(`/api/tasks/${taskId}/complete`, { 
                            method: 'POST',
                            body: JSON.stringify({ completions: [{ member_id: parseInt(assignedToId), percentage: 100 }] })
                        });
                        if (result) {
                            M.toast({html: 'Tâche marquée comme terminée! ✅', classes: 'green darken-1'});
                            loadTasks();
                            loadLeaderboard();
                        }
                    } else {
                        // Task is not assigned, open modal to select user
                        openAssignUserModal(taskId);
                    }
                });
            });
        }
        hideLoading(tasksLoading);
    }

    // Open modal to assign user to a task
    async function openAssignUserModal(taskId) {
        const members = await fetchData('/api/members');
        const userSelectionList = document.getElementById('user-selection-list');
        if (userSelectionList && members) {
            userSelectionList.innerHTML = '';
            members.forEach(member => {
                const div = document.createElement('div');
                div.classList.add('row', 'valign-wrapper');
                div.innerHTML = `
                    <div class="col s8">
                        <label>
                            <input type="checkbox" class="filled-in member-checkbox" data-member-id="${member.id}" />
                            <span>${member.name}</span>
                        </label>
                    </div>
                    <div class="col s4">
                        <div class="input-field inline" style="margin-top: 0;">
                            <input id="percentage-${member.id}" type="number" class="percentage-input" min="0" max="100" value="0" style="width: 80px; text-align: right; padding-right: 5px;" disabled>
                            <label for="percentage-${member.id}">%</label>
                        </div>
                    </div>
                `;
                userSelectionList.appendChild(div);
            });

            document.querySelectorAll('.member-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    const memberId = checkbox.dataset.memberId;
                    const percentageInput = document.getElementById(`percentage-${memberId}`);
                    percentageInput.disabled = !checkbox.checked;
                    if (!checkbox.checked) {
                        percentageInput.value = 0;
                    }
                    updateTotalPercentage();
                });
            });

            document.querySelectorAll('.percentage-input').forEach(input => {
                input.addEventListener('input', updateTotalPercentage);
            });

            document.getElementById('confirm-assign-user').dataset.taskId = taskId;
            const modal = M.Modal.getInstance(document.getElementById('assign-user-modal'));
            modal.open();
        }
    }

    function updateTotalPercentage() {
        let total = 0;
        document.querySelectorAll('.percentage-input').forEach(input => {
            total += parseInt(input.value) || 0;
        });
        document.getElementById('percentage-total').textContent = total;
    }

    document.getElementById('distribute-evenly-btn').addEventListener('click', () => {
        const checkedCheckboxes = document.querySelectorAll('.member-checkbox:checked');
        const count = checkedCheckboxes.length;
        if (count > 0) {
            const percentage = Math.floor(100 / count);
            const remainder = 100 % count;
            checkedCheckboxes.forEach((checkbox, index) => {
                const memberId = checkbox.dataset.memberId;
                const percentageInput = document.getElementById(`percentage-${memberId}`);
                percentageInput.value = index < remainder ? percentage + 1 : percentage;
            });
            updateTotalPercentage();
        }
    });

    // Handle confirm button in assign user modal
    document.getElementById('confirm-assign-user').addEventListener('click', async () => {
        const taskId = document.getElementById('confirm-assign-user').dataset.taskId;
        const completions = [];
        let totalPercentage = 0;
        document.querySelectorAll('.member-checkbox:checked').forEach(checkbox => {
            const memberId = checkbox.dataset.memberId;
            const percentage = parseInt(document.getElementById(`percentage-${memberId}`).value) || 0;
            totalPercentage += percentage;
            completions.push({ member_id: parseInt(memberId), percentage: percentage });
        });

        if (totalPercentage !== 100) {
            M.toast({html: 'Le total des pourcentages doit être de 100%. 💯', classes: 'red darken-1'});
            return;
        }

        if (completions.length > 0) {
            const result = await fetchData(`/api/tasks/${taskId}/complete`, {
                method: 'POST',
                body: JSON.stringify({ completions: completions })
            });

            if (result) {
                M.toast({html: 'Tâche marquée comme terminée! ✅', classes: 'green darken-1'});
                const modal = M.Modal.getInstance(document.getElementById('assign-user-modal'));
                modal.close();
                loadTasks();
                loadLeaderboard();
            }
        } else {
            M.toast({html: 'Veuillez sélectionner au moins un membre. 👤', classes: 'red darken-1'});
        }
    });

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
                li.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span>${reward.name} 🎁 - ${reward.cost} points</span>
                        <span class="reward-actions">
                            <span class="reward-desc-text">${reward.description || ''}</span>
                            <a href="#" class="btn-small waves-effect waves-light blue claim-reward-btn" data-reward-id="${reward.id}" data-reward-cost="${reward.cost}" title="Réclamer la récompense"><i class="material-icons">card_giftcard</i></a>
                        </span>
                    </div>
                `;
                rewardList.appendChild(li);
            });

            // Add event listeners for claim buttons
            document.querySelectorAll('.claim-reward-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const rewardId = event.currentTarget.dataset.rewardId;
                    const rewardCost = event.currentTarget.dataset.rewardCost;
                    openClaimRewardModal(rewardId, rewardCost);
                });
            });
        }
        hideLoading(rewardsLoading);
    }

    // Open modal to claim a reward
    async function openClaimRewardModal(rewardId, rewardCost) {
        const members = await fetchData('/api/members');
        const memberSelect = document.getElementById('member-select');
        if (memberSelect && members) {
            memberSelect.innerHTML = '<option value="" disabled selected>Sélectionnez un membre</option>';
            members.forEach(member => {
                const option = document.createElement('option');
                option.value = member.id;
                option.textContent = `${member.name} (${member.total_points} points)`;
                memberSelect.appendChild(option);
            });
            M.FormSelect.init(memberSelect);

            document.getElementById('reward-id-input').value = rewardId;
            document.getElementById('reward-cost').textContent = rewardCost;
            const modal = M.Modal.getInstance(document.getElementById('claim-reward-modal'));
            modal.open();
        }
    }

    // Handle confirm button in claim reward modal
    document.getElementById('confirm-claim-reward').addEventListener('click', async () => {
        const memberId = document.getElementById('member-select').value;
        const rewardId = document.getElementById('reward-id-input').value;

        if (!memberId) {
            M.toast({html: 'Veuillez sélectionner un membre. 👤', classes: 'red darken-1'});
            return;
        }

        const result = await fetchData('/api/rewards/claim', {
            method: 'POST',
            body: JSON.stringify({ member_id: parseInt(memberId), reward_id: parseInt(rewardId) })
        });

        if (result) {
            M.toast({html: 'Récompense réclamée! 🎁', classes: 'blue darken-1'});
            const modal = M.Modal.getInstance(document.getElementById('claim-reward-modal'));
            modal.close();
            loadRewards();
            loadLeaderboard();
        }
    });

    // Populate task assignee dropdown
    async function populateAssigneeDropdown() {
        const assigneeSelect = document.getElementById('task_assignee');
        if (assigneeSelect) {
            const members = await fetchData('/api/members');
            if (members) {
                assigneeSelect.innerHTML = '<option value="" disabled selected>Assigner à...</option>';
                members.forEach(member => {
                    const option = document.createElement('option');
                    option.value = member.id;
                    option.textContent = member.name;
                    assigneeSelect.appendChild(option);
                });
                M.FormSelect.init(assigneeSelect);
            }
        }
    }

    // Handle Add Task Form Submission
    const addTaskForm = document.getElementById('add-task-form');
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const description = document.getElementById('task_name').value;
            const points = parseInt(document.getElementById('task_points').value);
            const assignedToId = parseInt(document.getElementById('task_assignee').value);

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
                addTaskForm.reset();
                loadTasks();
                M.FormSelect.init(document.querySelectorAll('select'));
            }
        });
    }

    // Initial data load
    loadLeaderboard();
    loadTasks();
    loadRewards();
    populateAssigneeDropdown();
});