// src/web/static/js/quests_rewards.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('Quests & Rewards script loaded.');

    const tasksList = document.getElementById('tasks-list');
    const rewardsList = document.getElementById('rewards-list');
    const addTaskForm = document.getElementById('add-task-form');
    const addRewardForm = document.getElementById('add-reward-form');
    const editTaskModal = document.getElementById('edit-task-modal');
    const editRewardModal = document.getElementById('edit-reward-modal');
    const completeTaskModal = document.getElementById('complete-task-modal');
    const editTaskForm = document.getElementById('edit-task-form');
    const editRewardForm = document.getElementById('edit-reward-form');
    const completeTaskForm = document.getElementById('complete-task-form');
    const tasksLoading = document.getElementById('tasks-loading');
    const rewardsLoading = document.getElementById('rewards-loading');

    let editTaskModalInstance;
    let editRewardModalInstance;
    let completeTaskModalInstance;

    // Initialize Materialize Modals
    if (editTaskModal) {
        editTaskModalInstance = M.Modal.init(editTaskModal);
    }
    if (editRewardModal) {
        editRewardModalInstance = M.Modal.init(editRewardModal);
    }
    if (completeTaskModal) {
        completeTaskModalInstance = M.Modal.init(completeTaskModal);
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

    // Populate member dropdowns (for tasks)
    async function populateMemberDropdowns() {
        const members = await fetchData('/api/members');
        const selects = [
            document.getElementById('task_assigned_to_id'),
            document.getElementById('edit_task_assigned_to_id')
        ];

        if (members) {
            selects.forEach(selectElement => {
                if (selectElement) {
                    const instance = M.FormSelect.getInstance(selectElement);
                    if (instance) {
                        instance.destroy();
                    }

                    const currentValue = selectElement.value;
                    
                    // Clear existing options but keep the first one
                    while (selectElement.options.length > 1) {
                        selectElement.remove(1);
                    }

                    members.forEach(member => {
                        const option = document.createElement('option');
                        option.value = member.id;
                        option.textContent = member.name;
                        selectElement.appendChild(option);
                    });

                    selectElement.value = currentValue;
                    M.FormSelect.init(selectElement);
                }
            });
        }
    }

    // Load tasks into the list
    async function loadTasks() {
        showLoading(tasksLoading);
        const tasks = await fetchData('/api/tasks');
        const members = await fetchData('/api/members');

        if (tasksList && tasks && members) {
            tasksList.innerHTML = '';
            for (const task of tasks) {
                const li = document.createElement('li');
                li.className = 'collection-item';

                let assignedToName = 'Toute la famille';
                if (task.assigned_to_id) {
                    const assignedMember = members.find(m => m.id === task.assigned_to_id);
                    assignedToName = assignedMember ? assignedMember.name : 'Inconnu';
                }

                let completedBy = '';
                if (task.completions.length > 0) {
                    const completerNames = task.completions.map(c => {
                        const member = members.find(m => m.id === c.member_id);
                        return member ? member.name : 'Inconnu';
                    });
                    completedBy = `Terminée par: ${completerNames.join(', ')} ✅`;
                }

                li.innerHTML = `<div style="display: flex; align-items: center; justify-content: space-between;"><span>${task.description} - ${task.points} points ✨</span><span class="quest-actions"><span class="quest-status-text">Assigné à: ${assignedToName} - Statut: ${task.status === 'completed' ? completedBy : 'En cours ⏳'}</span><a href="#!" class="btn-small waves-effect waves-light blue edit-task-btn" data-task-id="${task.id}"><i class="material-icons">edit</i></a><a href="#!" class="btn-small waves-effect waves-light red delete-task-btn" data-task-id="${task.id}"><i class="material-icons">delete</i></a>${task.status !== 'completed' ? `<a href="#!" class="btn-small waves-effect waves-light green complete-task-btn" data-task-id="${task.id}" data-assigned-to-id="${task.assigned_to_id || ''}"><i class="material-icons">check</i></a>` : ''}</span></div>`;
                tasksList.appendChild(li);
            }

            // Attach event listeners for buttons
            attachTaskButtonListeners();
        }
        hideLoading(tasksLoading);
    }

    function attachTaskButtonListeners() {
        document.querySelectorAll('.edit-task-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const taskId = event.currentTarget.closest('li').querySelector('.edit-task-btn').dataset.taskId;
                const task = await fetchData(`/api/tasks/${taskId}`);
                if (!task) return;

                document.getElementById('edit_task_id').value = task.id;
                document.getElementById('edit_task_description').value = task.description;
                document.getElementById('edit_task_points').value = task.points;
                document.getElementById('edit_task_assigned_to_id').value = task.assigned_to_id || '';
                document.getElementById('edit_task_status').value = task.status;
                M.updateTextFields();
                // Re-initialize select elements
                const assignedToSelect = document.getElementById('edit_task_assigned_to_id');
                const statusSelect = document.getElementById('edit_task_status');
                M.FormSelect.init(assignedToSelect);
                M.FormSelect.init(statusSelect);
                editTaskModalInstance.open();
            });
        });

        document.querySelectorAll('.delete-task-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const taskId = event.currentTarget.closest('li').querySelector('.delete-task-btn').dataset.taskId;
                if (confirm('Êtes-vous sûr de vouloir supprimer cette quête ? 🗑️')) {
                    const result = await fetchData(`/api/tasks/${taskId}`, { method: 'DELETE' });
                    if (result) {
                        M.toast({html: 'Quête supprimée! 💥', classes: 'green darken-1'});
                        loadTasks();
                    }
                }
            });
        });

        document.querySelectorAll('.complete-task-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const taskId = event.currentTarget.dataset.taskId;
                const assignedToId = event.currentTarget.dataset.assignedToId;
                openCompleteTaskModal(taskId, assignedToId);
            });
        });
    }

    async function openCompleteTaskModal(taskId, assignedToId) {
        document.getElementById('complete_task_id').value = taskId;
        const members = await fetchData('/api/members');
        const membersCheckboxes = document.getElementById('members-checkboxes');
        membersCheckboxes.innerHTML = '';

        if (members) {
            members.forEach(member => {
                const isAssigned = assignedToId && parseInt(assignedToId) === member.id;
                const checkboxHtml = `
                    <p>
                        <label>
                            <input type="checkbox" name="member" value="${member.id}" ${isAssigned ? 'checked="checked" disabled="disabled"' : ''} />
                            <span>${member.name}</span>
                        </label>
                    </p>
                `;
                membersCheckboxes.insertAdjacentHTML('beforeend', checkboxHtml);
            });
        }
        completeTaskModalInstance.open();
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
                li.innerHTML = `<div>${reward.name} - ${reward.cost} points 💎 <span class="secondary-content">${reward.description || ''}</span><a href="#!" class="secondary-content btn-small waves-effect waves-light blue edit-reward-btn" data-reward-id="${reward.id}"><i class="material-icons">edit</i></a><a href="#!" class="secondary-content btn-small waves-effect waves-light red delete-reward-btn" data-reward-id="${reward.id}"><i class="material-icons">delete</i></a></div>`;
                rewardsList.appendChild(li);
            });

            // Attach event listeners for edit and delete buttons
            attachRewardButtonListeners();
        }
        hideLoading(rewardsLoading);
    }

    function attachRewardButtonListeners() {
        document.querySelectorAll('.edit-reward-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const rewardId = event.currentTarget.closest('li').querySelector('.edit-reward-btn').dataset.rewardId;
                const reward = await fetchData(`/api/rewards/${rewardId}`);
                if (!reward) return;

                document.getElementById('edit_reward_id').value = reward.id;
                document.getElementById('edit_reward_name').value = reward.name;
                document.getElementById('edit_reward_cost').value = reward.cost;
                document.getElementById('edit_reward_description').value = reward.description || '';
                M.updateTextFields();
                editRewardModalInstance.open();
            });
        });

        document.querySelectorAll('.delete-reward-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const rewardId = event.currentTarget.closest('li').querySelector('.delete-reward-btn').dataset.rewardId;
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

    // Handle Add Task Form Submission
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const description = document.getElementById('task_description').value;
            const points = parseInt(document.getElementById('task_points').value, 10);
            const assignedToIdValue = document.getElementById('task_assigned_to_id').value;
            const assigned_to_id = assignedToIdValue === "" ? null : parseInt(assignedToIdValue, 10);

            if (!description || isNaN(points)) {
                M.toast({html: 'Veuillez remplir tous les champs de la quête. 📝', classes: 'red darken-1'});
                return;
            }

            const newTask = { description, points, assigned_to_id };
            const result = await fetchData('/api/tasks', {
                method: 'POST',
                body: JSON.stringify(newTask)
            });
            if (result) {
                M.toast({html: 'Quête ajoutée! ✨', classes: 'green darken-1'});
                addTaskForm.reset();
                const selectElement = document.getElementById('task_assigned_to_id');
                const instance = M.FormSelect.getInstance(selectElement);
                if (instance) instance.destroy();
                M.FormSelect.init(selectElement);
                loadTasks();
            }
        });
    }

    // Handle Add Reward Form Submission
    if (addRewardForm) {
        addRewardForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const name = document.getElementById('reward_name').value;
            const cost = parseInt(document.getElementById('reward_cost').value, 10);
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
            const points = parseInt(document.getElementById('edit_task_points').value, 10);
            const assignedToIdValue = document.getElementById('edit_task_assigned_to_id').value;
            const assigned_to_id = assignedToIdValue === "" ? null : parseInt(assignedToIdValue, 10);
            const status = document.getElementById('edit_task_status').value;

            if (!description || isNaN(points) || !status) {
                M.toast({html: 'Veuillez remplir tous les champs de modification de la quête. 📝', classes: 'red darken-1'});
                return;
            }

            const updatedTask = { description, points, assigned_to_id, status };
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

    // Handle Complete Task Form Submission
    if (completeTaskForm) {
        completeTaskForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const taskId = document.getElementById('complete_task_id').value;
            const selectedMembers = Array.from(document.querySelectorAll('#members-checkboxes input[name="member"]:checked')).map(cb => parseInt(cb.value, 10));

            if (selectedMembers.length === 0) {
                M.toast({html: 'Veuillez sélectionner au moins un membre. 👥', classes: 'red darken-1'});
                return;
            }

            const result = await fetchData(`/api/tasks/${taskId}/complete`, {
                method: 'POST',
                body: JSON.stringify({ member_ids: selectedMembers })
            });

            if (result) {
                M.toast({html: 'Quête validée! 🎉', classes: 'green darken-1'});
                completeTaskModalInstance.close();
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
            const cost = parseInt(document.getElementById('edit_reward_cost').value, 10);
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
