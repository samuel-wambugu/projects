// Dashboard video preview functionality
function preview() {
    const videoInput = document.getElementById('videoInput');
    const videoPreview = document.getElementById('videoPreview');
    
    if (videoInput.files && videoInput.files[0]) {
        const fileURL = URL.createObjectURL(videoInput.files[0]);
        videoPreview.src = fileURL;
    }
}

function deletePreview() {
    const videoInput = document.getElementById('videoInput');
    const videoPreview = document.getElementById('videoPreview');
    
    videoInput.value = '';
    videoPreview.src = '';
}

// Video upload functionality
async function uploadVideo() {
    const videoInput = document.getElementById('videoInput');
    const titleInput = document.getElementById('title');
    
    if (!videoInput.files[0]) {
        showAlert('Please select a video file first', 'warning');
        return;
    }
    
    if (!titleInput.value) {
        showAlert('Please enter a title for the video', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('title', titleInput.value);
    formData.append('video', videoInput.files[0]);
    
    try {
        const response = await fetch('/upload_video/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            showAlert('Video uploaded successfully!', 'success');
            deletePreview();
            titleInput.value = '';
        } else {
            showAlert('Failed to upload video. Please try again.', 'danger');
        }
    } catch (error) {
        showAlert('An error occurred. Please try again.', 'danger');
        console.error('Upload error:', error);
    }
}

// Utility functions
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

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

// Initialize tooltips and popovers when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    
    // Initialize Bootstrap popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => new bootstrap.Popover(popover));
});