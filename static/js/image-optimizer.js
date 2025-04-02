/**
 * Image Optimizer Script
 * This script helps optimize image loading by implementing lazy loading
 */

document.addEventListener('DOMContentLoaded', function() {
    // Convert regular images to lazy-loaded images
    const images = document.querySelectorAll('img:not([loading])');
    
    images.forEach(img => {
        // Skip small images or images that are already visible in the viewport
        if (isInViewport(img) || (img.width < 50 && img.height < 50)) {
            return;
        }
        
        // Add loading="lazy" attribute for native lazy loading
        img.setAttribute('loading', 'lazy');
        
        // For browsers that don't support native lazy loading,
        // implement data-src pattern
        if (!('loading' in HTMLImageElement.prototype)) {
            const src = img.getAttribute('src');
            img.setAttribute('data-src', src);
            
            // Set a placeholder or low-quality image
            img.setAttribute('src', 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E');
            
            // Add to the observer in the loading-optimizer.js
        }
    });
    
    // Function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
});
