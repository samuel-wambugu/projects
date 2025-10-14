/**
 * Dashboard JavaScript Functions
 * Handles all interactive elements on the dashboard page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all dashboard features
    initProgressBars();
    initTutorialProgressBars();
    initDeleteModals();
    initVideoPlayers();
    initTooltips();
});

/**
 * Initialize user progress bars
 */
function initProgressBars() {
    const progressBar = document.querySelector('[data-progress]');
    if (progressBar) {
        const progress = progressBar.getAttribute('data-progress');
        setTimeout(() => {
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', progress);
        }, 100);
    }
}

/**
 * Initialize tutorial progress bars (for admin dashboard)
 */
function initTutorialProgressBars() {
    const progressBars = document.querySelectorAll('.tutorial-progress');
    progressBars.forEach(function(bar, index) {
        const completionRate = bar.getAttribute('data-completion-rate');
        setTimeout(() => {
            bar.style.width = completionRate + '%';
        }, 100 * index); // Stagger animation
    });
}

/**
 * Initialize delete tutorial modals
 */
function initDeleteModals() {
    const deleteButtons = document.querySelectorAll('.delete-tutorial-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const tutorialId = this.getAttribute('data-tutorial-id');
            const modalId = this.getAttribute('data-modal-id');
            
            // Show loading state
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Deleting...';
            this.disabled = true;
            
            // Send delete request
            deleteTutorial(tutorialId, modalId, this);
        });
    });
    
    // Prevent modal from closing when clicking inside
    const modals = document.querySelectorAll('[id^="deleteTutorialModal"]');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
}

/**
 * Delete tutorial via AJAX
 */
function deleteTutorial(tutorialId, modalId, button) {
    fetch(`/tutorials/${tutorialId}/delete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
            modal.hide();
            
            // Show success message
            showNotification('Tutorial deleted successfully', 'success');
            
            // Reload page after short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification('Error deleting tutorial: ' + (data.error || 'Unknown error'), 'danger');
            button.innerHTML = '<i class="fas fa-trash me-1"></i>Delete Tutorial';
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error deleting tutorial. Please try again.', 'danger');
        button.innerHTML = '<i class="fas fa-trash me-1"></i>Delete Tutorial';
        button.disabled = false;
    });
}

/**
 * Initialize video players with custom controls
 */
function initVideoPlayers() {
    const videos = document.querySelectorAll('video');
    
    videos.forEach(video => {
        // Pause other videos when one starts playing
        video.addEventListener('play', function() {
            videos.forEach(otherVideo => {
                if (otherVideo !== video) {
                    otherVideo.pause();
                }
            });
        });
        
        // Save playback position
        video.addEventListener('timeupdate', function() {
            const videoId = this.closest('[id^="videoModal"]')?.id || 'main-video';
            localStorage.setItem(`video-position-${videoId}`, this.currentTime);
        });
        
        // Restore playback position
        const videoId = video.closest('[id^="videoModal"]')?.id || 'main-video';
        const savedPosition = localStorage.getItem(`video-position-${videoId}`);
        if (savedPosition && !isNaN(savedPosition)) {
            video.currentTime = parseFloat(savedPosition);
        }
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    const alertClass = type === 'danger' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const icon = type === 'danger' ? 'fa-exclamation-circle' :
                type === 'success' ? 'fa-check-circle' :
                type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${icon} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 150);
        }
    }, 5000);
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Smooth scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Filter tutorials by search term
 */
function filterTutorials(searchTerm) {
    const tutorials = document.querySelectorAll('.tutorial-card');
    const normalizedSearch = searchTerm.toLowerCase().trim();
    
    tutorials.forEach(card => {
        const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
        const content = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
        
        if (title.includes(normalizedSearch) || content.includes(normalizedSearch)) {
            card.closest('.col-md-6, .col-lg-4').style.display = '';
        } else {
            card.closest('.col-md-6, .col-lg-4').style.display = 'none';
        }
    });
}

/**
 * Export functions for external use
 */
window.dashboardUtils = {
    showNotification,
    scrollToTop,
    filterTutorials,
    deleteTutorial
};
