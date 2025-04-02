/**
 * Loading Optimizer Script
 * This script helps optimize the loading of resources and provides loading state management
 */

// Function to check if the page has finished loading
function checkPageLoaded() {
    // If the page is fully loaded
    if (document.readyState === 'complete') {
        hideLoadingOverlay();
    } else {
        // If not, check again after a short delay
        setTimeout(checkPageLoaded, 100);
    }
}

// Function to hide the loading overlay with a smooth transition
function hideLoadingOverlay() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        // Fade out
        loadingOverlay.style.opacity = '0';
        
        // Remove from DOM after transition completes
        setTimeout(function() {
            loadingOverlay.style.display = 'none';
        }, 300);
    }
}

// Function to show the loading overlay
function showLoadingOverlay() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
        
        // Force a reflow before changing opacity for the transition to work
        loadingOverlay.offsetHeight;
        
        loadingOverlay.style.opacity = '1';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Start checking if the page is fully loaded
    checkPageLoaded();
    
    // Add event listeners for navigation
    document.addEventListener('click', function(e) {
        // Check if the clicked element is a link or a button that navigates to a new page
        const target = e.target.closest('a, button[type="submit"]');
        if (target && 
            target.getAttribute('href') && 
            !target.getAttribute('href').startsWith('#') && 
            !target.getAttribute('href').startsWith('javascript:') && 
            !e.ctrlKey && !e.metaKey && !e.shiftKey) {
            
            // Show loading overlay when navigating to a new page
            showLoadingOverlay();
        }
    });
    
    // Optimize image loading
    const images = document.querySelectorAll('img[data-src]');
    if (images.length > 0) {
        // Create an intersection observer to load images only when they come into view
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.getAttribute('data-src');
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        
        // Observe each image
        images.forEach(img => {
            imageObserver.observe(img);
        });
    }
});

// Handle page unload events
window.addEventListener('beforeunload', function() {
    // Show loading overlay when navigating away from the page
    showLoadingOverlay();
});
