// src/web/static/js/members.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('Members script loaded.');

    const membersList = document.getElementById('members-list');
    const addMemberForm = document.getElementById('add-member-form');
    const editMemberModal = document.getElementById('edit-member-modal');
    const editMemberForm = document.getElementById('edit-member-form');
    const membersLoading = document.getElementById('members-loading');

    let modalInstance;

    // Initialize Materialize Modal
    if (editMemberModal) {
        modalInstance = M.Modal.init(editMemberModal);
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

    // Load members into the list
    async function loadMembers() {
        showLoading(membersLoading);
        const members = await fetchData('/api/members');
        if (membersList && members) {
            membersList.innerHTML = '';
            members.forEach(member => {
                const li = document.createElement('li');
                li.className = 'collection-item';
                li.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span>${member.name}</span>
                        <span class="member-actions">
                            <span class="points-text">${member.total_points} points ✨</span>
                            <a href="#!" class="btn-small waves-effect waves-light blue edit-member-btn" data-member-id="${member.id}" data-member-name="${member.name}" data-member-points="${member.total_points}"><i class="material-icons">edit</i></a>
                            <a href="#!" class="btn-small waves-effect waves-light red delete-member-btn" data-member-id="${member.id}"><i class="material-icons">delete</i></a>
                        </span>
                    </div>
                `;
                membersList.appendChild(li);
            });

            // Attach event listeners for edit and delete buttons
            document.querySelectorAll('.edit-member-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const memberId = event.currentTarget.dataset.memberId;
                    const memberName = event.currentTarget.dataset.memberName;
                    const memberPoints = event.currentTarget.dataset.memberPoints;
                    
                    document.getElementById('edit_member_id').value = memberId;
                    document.getElementById('edit_member_name').value = memberName;
                    document.getElementById('edit_member_points').value = memberPoints;
                    M.updateTextFields(); // Update Materialize labels
                    modalInstance.open();
                });
            });

            document.querySelectorAll('.delete-member-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const memberId = event.currentTarget.dataset.memberId;
                    if (confirm('Êtes-vous sûr de vouloir supprimer ce héros ? 🗑️')) {
                        const result = await fetchData(`/api/members/${memberId}`, { method: 'DELETE' });
                        if (result) {
                            M.toast({html: 'Héros supprimé! 💥', classes: 'green darken-1'});
                            loadMembers(); // Reload list
                        }
                    }
                });
            });
        }
        hideLoading(membersLoading);
    }

    // Handle Add Member Form Submission
    if (addMemberForm) {
        addMemberForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const memberName = document.getElementById('member_name').value;
            if (!memberName) {
                M.toast({html: 'Veuillez entrer un nom pour le héros. 📝', classes: 'red darken-1'});
                return;
            }
            const newMember = { name: memberName };
            const result = await fetchData('/api/members', {
                method: 'POST',
                body: JSON.stringify(newMember)
            });
            if (result) {
                M.toast({html: 'Héros ajouté! 🎉', classes: 'green darken-1'});
                addMemberForm.reset();
                loadMembers();
            }
        });
    }

    // Handle Edit Member Form Submission
    if (editMemberForm) {
        editMemberForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const memberId = document.getElementById('edit_member_id').value;
            const memberName = document.getElementById('edit_member_name').value;
            const memberPoints = parseInt(document.getElementById('edit_member_points').value);

            if (!memberName || isNaN(memberPoints)) {
                M.toast({html: 'Veuillez remplir tous les champs de modification. 📝', classes: 'red darken-1'});
                return;
            }

            const updatedMember = { name: memberName, total_points: memberPoints };
            const result = await fetchData(`/api/members/${memberId}`, {
                method: 'PUT',
                body: JSON.stringify(updatedMember)
            });

            if (result) {
                M.toast({html: 'Héros mis à jour! 💾', classes: 'green darken-1'});
                modalInstance.close();
                loadMembers();
            }
        });
    }

    // Initial load
    loadMembers();
});