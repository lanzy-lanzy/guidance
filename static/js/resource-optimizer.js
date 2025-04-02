/**
 * Resource Optimizer Script
 * This script helps optimize the loading of external resources
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add preload for critical resources
    preloadCriticalResources();
    
    // Defer non-critical resources
    deferNonCriticalResources();
    
    // Add content loaded class to make content visible
    setTimeout(function() {
        const contentContainers = document.querySelectorAll('.content-container');
        contentContainers.forEach(container => {
            container.classList.add('loaded');
        });
    }, 100);
});

// Function to preload critical resources
function preloadCriticalResources() {
    // List of critical resources to preload
    const criticalResources = [
        { type: 'style', href: '/static/css/loading-styles.css' }
    ];
    
    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = resource.type === 'style' ? 'preload' : 'prefetch';
        link.href = resource.href;
        link.as = resource.type === 'style' ? 'style' : 'script';
        link.onload = function() {
            if (resource.type === 'style') {
                link.rel = 'stylesheet';
            }
        };
        document.head.appendChild(link);
    });
}

// Function to defer non-critical resources
function deferNonCriticalResources() {
    // Find all script tags without async or defer
    const scripts = document.querySelectorAll('script:not([async]):not([defer])');
    
    scripts.forEach(script => {
        // Skip inline scripts and already loaded scripts
        if (!script.src || script.hasAttribute('data-loaded')) {
            return;
        }
        
        // Skip critical scripts
        if (script.src.includes('loading-optimizer.js')) {
            return;
        }
        
        // Add async attribute to defer loading
        script.setAttribute('async', '');
        script.setAttribute('data-loaded', 'true');
    });
}
