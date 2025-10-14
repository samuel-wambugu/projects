document.addEventListener('DOMContentLoaded', function() {
    // Handle tutorial deletion
    document.querySelectorAll('.delete-tutorial-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const tutorialId = this.dataset.tutorialId;
            const modalId = this.dataset.modalId;
            const modal = document.getElementById(modalId);
            const modalInstance = bootstrap.Modal.getInstance(modal);

            // Send delete request
            fetch(`/tutorials/${tutorialId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Close modal
                    modalInstance.hide();
                    
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show fixed-top mx-auto mt-3';
                    alertDiv.style.maxWidth = '500px';
                    alertDiv.innerHTML = `
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.body.appendChild(alertDiv);
                    
                    // Remove the tutorial row from the table
                    const tutorialRow = button.closest('tr');
                    tutorialRow.remove();
                    
                    // Auto-dismiss alert after 3 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 3000);
                } else {
                    throw new Error(data.message || 'Error deleting tutorial');
                }
            })
            .catch(error => {
                // Show error message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show fixed-top mx-auto mt-3';
                alertDiv.style.maxWidth = '500px';
                alertDiv.innerHTML = `
                    Error: ${error.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                document.body.appendChild(alertDiv);
                
                // Auto-dismiss alert after 5 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            });
        });
    });
});