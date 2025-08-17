// src/web/static/js/quests_rewards.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('Quests & Rewards script loaded.');

    const tasksList = document.getElementById('tasks-list');
    const rewardsList = document.getElementById('rewards-list');
    const addTaskForm = document.getElementById('add-task-form');
    const addRewardForm = document.getElementById('add-reward-form');
    const editTaskModal = document.getElementById('edit-task-modal');
    const editRewardModal = document.getElementById('edit-reward-modal');
    const editTaskForm = document.getElementById('edit-task-form');
    const editRewardForm = document.getElementById('edit-reward-form');
    const tasksLoading = document.getElementById('tasks-loading');
    const rewardsLoading = document.getElementById('rewards-loading');

    let editTaskModalInstance;
    let editRewardModalInstance;

    // Initialize Materialize Modals
    if (editTaskModal) {
        editTaskModalInstance = M.Modal.init(editTaskModal);
    }
    if (editRewardModal) {
        editRewardModalInstance = M.Modal.init(editRewardModal);
    }

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
            const token = 'dummy-token'; // Replace with actual token from authentication
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

    // Populate member dropdowns (for tasks)
    async function populateMemberDropdowns() {
        const members = await fetchData('/api/members');
        const taskAssigneeSelect = document.getElementById('task_assigned_to_id');
        const editTaskAssigneeSelect = document.getElementById('edit_task_assigned_to_id');

        if (members) {
            [taskAssigneeSelect, editTaskAssigneeSelect].forEach(selectElement => {
                if (selectElement) {
                    selectElement.innerHTML = '<option value="" disabled selected>Assigner à...</option>';
                    members.forEach(member => {
                        const option = document.createElement('option');
                        option.value = member.id;
                        option.textContent = member.name;
                        selectElement.appendChild(option);
                    });
                    M.FormSelect.init(selectElement);
                }
            });
        }
    }

    // Load tasks into the list
    async function loadTasks() {
        showLoading(tasksLoading);
        const tasks = await fetchData('/api/tasks');
        if (tasksList && tasks) {
            tasksList.innerHTML = '';
            for (const task of tasks) {
                const li = document.createElement('li');
                li.className = 'collection-item';
                const assignedMember = await fetchData(`/api/members/${task.assigned_to_id}`);
                const assignedToName = assignedMember ? assignedMember.name : 'Inconnu';
                li.innerHTML = `
                    <div>
                        ${task.description} - ${task.points} points ✨ <span class="secondary-content">Assigné à: ${assignedToName} - Statut: ${task.status === 'completed' ? 'Terminée ✅' : 'En cours ⏳'}</span>
                        <a href="#!" class="secondary-content btn-small waves-effect waves-light blue edit-task-btn" data-task-id="${task.id}" data-task-description="${task.description}" data-task-points="${task.points}" data-task-assigned-to-id="${task.assigned_to_id}" data-task-status="${task.status}"><i class="material-icons">edit</i></a>
                        <a href="#!" class="secondary-content btn-small waves-effect waves-light red delete-task-btn" data-task-id="${task.id}"><i class="material-icons">delete</i></a>
                    </div>
                `;
                tasksList.appendChild(li);
            }

            // Attach event listeners for edit and delete buttons
            document.querySelectorAll('.edit-task-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const taskId = event.currentTarget.dataset.taskId;
                    const taskDescription = event.currentTarget.dataset.taskDescription;
                    const taskPoints = event.currentTarget.dataset.taskPoints;
                    const taskAssignedToId = event.currentTarget.dataset.taskAssignedToId;
                    const taskStatus = event.currentTarget.dataset.taskStatus;
                    
                    document.getElementById('edit_task_id').value = taskId;
                    document.getElementById('edit_task_description').value = taskDescription;
                    document.getElementById('edit_task_points').value = taskPoints;
                    document.getElementById('edit_task_assigned_to_id').value = taskAssignedToId;
                    document.getElementById('edit_task_status').value = taskStatus;
                    M.updateTextFields();
                    M.FormSelect.init(document.getElementById('edit_task_assigned_to_id'));
                    M.FormSelect.init(document.getElementById('edit_task_status'));
                    editTaskModalInstance.open();
                });
            });

            document.querySelectorAll('.delete-task-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const taskId = event.currentTarget.dataset.taskId;
                    if (confirm('Êtes-vous sûr de vouloir supprimer cette quête ? 🗑️')) {
                        const result = await fetchData(`/api/tasks/${taskId}`, { method: 'DELETE' });
                        if (result) {
                            M.toast({html: 'Quête supprimée! 💥', classes: 'green darken-1'});
                            loadTasks();
                        }
                    }
                });
            });
        }
        hideLoading(tasksLoading);
    }

    // Load rewards into the list
    async function loadRewards() {
        showLoading(rewardsLoading);
        const rewards = await fetchData('/api/rewards');
        if (rewardsList && rewards) {
            rewardsList.innerHTML = '';
            rewards.forEach(reward => {
                const li = document.createElement('li');
                li.className = 'collection-item';
                li.innerHTML = `
                    <div>
                        ${reward.name} - ${reward.cost} points 💎 <span class="secondary-content">${reward.description || ''}</span>
                        <a href="#!" class="secondary-content btn-small waves-effect waves-light blue edit-reward-btn" data-reward-id="${reward.id}" data-reward-name="${reward.name}" data-reward-cost="${reward.cost}" data-reward-description="${reward.description || ''}"><i class="material-icons">edit</i></a>
                        <a href="#!" class="secondary-content btn-small waves-effect waves-light red delete-reward-btn" data-reward-id="${reward.id}"><i class="material-icons">delete</i></a>
                    </div>
                `;
                rewardsList.appendChild(li);
            });

            // Attach event listeners for edit and delete buttons
            document.querySelectorAll('.edit-reward-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const rewardId = event.currentTarget.dataset.rewardId;
                    const rewardName = event.currentTarget.dataset.rewardName;
                    const rewardCost = event.currentTarget.dataset.rewardCost;
                    const rewardDescription = event.currentTarget.dataset.rewardDescription;
                    
                    document.getElementById('edit_reward_id').value = rewardId;
                    document.getElementById('edit_reward_name').value = rewardName;
                    document.getElementById('edit_reward_cost').value = rewardCost;
                    document.getElementById('edit_reward_description').value = rewardDescription;
                    M.updateTextFields();
                    editRewardModalInstance.open();
                });
            });

            document.querySelectorAll('.delete-reward-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const rewardId = event.currentTarget.dataset.rewardId;
                    if (confirm('Êtes-vous sûr de vouloir supprimer cette récompense ? 🗑️')) {
                        const result = await fetchData(`/api/rewards/${rewardId}`, { method: 'DELETE' });
                        if (result) {
                            M.toast({html: 'Récompense supprimée! 💥', classes: 'green darken-1'});
                            loadRewards();
                        }
                    }
                });
            });
        }
        hideLoading(rewardsLoading);
    }

    // Handle Add Task Form Submission
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const description = document.getElementById('task_description').value;
            const points = parseInt(document.getElementById('task_points').value);
            const assignedToId = parseInt(document.getElementById('task_assigned_to_id').value);

            if (!description || isNaN(points) || isNaN(assignedToId)) {
                M.toast({html: 'Veuillez remplir tous les champs de la quête. 📝', classes: 'red darken-1'});
                return;
            }

            const newTask = { description, points, assigned_to_id: assignedToId };
            const result = await fetchData('/api/tasks', {
                method: 'POST',
                body: JSON.stringify(newTask)
            });
            if (result) {
                M.toast({html: 'Quête ajoutée! ✨', classes: 'green darken-1'});
                addTaskForm.reset();
                M.FormSelect.init(document.getElementById('task_assigned_to_id')); // Re-init select
                loadTasks();
            }
        });
    }

    // Handle Add Reward Form Submission
    if (addRewardForm) {
        addRewardForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const name = document.getElementById('reward_name').value;
            const cost = parseInt(document.getElementById('reward_cost').value);
            const description = document.getElementById('reward_description').value;

            if (!name || isNaN(cost)) {
                M.toast({html: 'Veuillez remplir les champs obligatoires de la récompense. 📝', classes: 'red darken-1'});
                return;
            }

            const newReward = { name, cost, description };
            const result = await fetchData('/api/rewards', {
                method: 'POST',
                body: JSON.stringify(newReward)
            });
            if (result) {
                M.toast({html: 'Récompense ajoutée! 🎁', classes: 'green darken-1'});
                addRewardForm.reset();
                loadRewards();
            }
        });
    }

    // Handle Edit Task Form Submission
    if (editTaskForm) {
        editTaskForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const taskId = document.getElementById('edit_task_id').value;
            const description = document.getElementById('edit_task_description').value;
            const points = parseInt(document.getElementById('edit_task_points').value);
            const assignedToId = parseInt(document.getElementById('edit_task_assigned_to_id').value);
            const status = document.getElementById('edit_task_status').value;

            if (!description || isNaN(points) || isNaN(assignedToId) || !status) {
                M.toast({html: 'Veuillez remplir tous les champs de modification de la quête. 📝', classes: 'red darken-1'});
                return;
            }

            const updatedTask = { description, points, assigned_to_id: assignedToId, status };
            const result = await fetchData(`/api/tasks/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify(updatedTask)
            });

            if (result) {
                M.toast({html: 'Quête mise à jour! 💾', classes: 'green darken-1'});
                editTaskModalInstance.close();
                loadTasks();
            }
        });
    }

    // Handle Edit Reward Form Submission
    if (editRewardForm) {
        editRewardForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const rewardId = document.getElementById('edit_reward_id').value;
            const name = document.getElementById('edit_reward_name').value;
            const cost = parseInt(document.getElementById('edit_reward_cost').value);
            const description = document.getElementById('edit_reward_description').value;

            if (!name || isNaN(cost)) {
                M.toast({html: 'Veuillez remplir les champs obligatoires de modification de la récompense. 📝', classes: 'red darken-1'});
                return;
            }

            const updatedReward = { name, cost, description };
            const result = await fetchData(`/api/rewards/${rewardId}`, {
                method: 'PUT',
                body: JSON.stringify(updatedReward)
            });

            if (result) {
                M.toast({html: 'Récompense mise à jour! 💾', classes: 'green darken-1'});
                editRewardModalInstance.close();
                loadRewards();
            }
        });
    }

    // Event listeners for example buttons
    document.querySelectorAll('.use-task-example').forEach(button => {
        button.addEventListener('click', (event) => {
            const description = event.currentTarget.dataset.description;
            const points = event.currentTarget.dataset.points;
            
            document.getElementById('task_description').value = description;
            document.getElementById('task_points').value = points;
            M.updateTextFields();
        });
    });

    document.querySelectorAll('.use-reward-example').forEach(button => {
        button.addEventListener('click', (event) => {
            const name = event.currentTarget.dataset.name;
            const cost = event.currentTarget.dataset.cost;
            const description = event.currentTarget.dataset.description;
            
            document.getElementById('reward_name').value = name;
            document.getElementById('reward_cost').value = cost;
            document.getElementById('reward_description').value = description;
            M.updateTextFields();
        });
    });

    // Initial loads
    populateMemberDropdowns();
    loadTasks();
    loadRewards();
});
