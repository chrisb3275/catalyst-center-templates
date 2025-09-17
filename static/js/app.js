// Catalyst Center Templates - JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initializeDarkMode();
    
    // Load dynamic navigation
    loadDynamicNavigation();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const cards = document.querySelectorAll('.card');
            
            cards.forEach(card => {
                const cardText = card.textContent.toLowerCase();
                if (cardText.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                return Promise.resolve();
            } catch (err) {
                return Promise.reject(err);
            } finally {
                document.body.removeChild(textArea);
            }
        }
    };

    // Show copy success message
    window.showCopySuccess = function(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
        }, 2000);
    };

    // Template rendering functionality
    window.renderTemplate = function() {
        const form = document.getElementById('renderForm');
        if (!form) return;

        const formData = new FormData(form);
        const parameters = {};
        
        for (let [key, value] of formData.entries()) {
            parameters[key] = value;
        }
        
        const requestData = {
            template_name: getTemplateName(),
            category: getCategory(),
            parameters: parameters
        };
        
        // Show loading state
        const renderButton = document.querySelector('#renderModal .btn-primary');
        const originalText = renderButton.innerHTML;
        renderButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Rendering...';
        renderButton.disabled = true;
        
        fetch('/render', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('renderedConfig').textContent = data.rendered_config;
                document.getElementById('renderResult').style.display = 'block';
                
                // Scroll to result
                document.getElementById('renderResult').scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            } else {
                showAlert('Error rendering template: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error rendering template: ' + error, 'danger');
        })
        .finally(() => {
            // Reset button state
            renderButton.innerHTML = originalText;
            renderButton.disabled = false;
        });
    };

    // Helper functions
    function getTemplateName() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }

    function getCategory() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 2];
    }

    function showAlert(message, type = 'info') {
        const alertContainer = document.querySelector('.container-fluid');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // API testing functionality
    window.testAPI = function(endpoint) {
        const button = event.target;
        const originalText = button.innerHTML;
        
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
        button.disabled = true;
        
        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                console.log('API Response:', data);
                showAlert('API test successful! Check console for response.', 'success');
            })
            .catch(error => {
                console.error('API Error:', error);
                showAlert('API test failed: ' + error, 'danger');
            })
            .finally(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            });
    };

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-save form data to localStorage
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        // Load saved data
        const savedValue = localStorage.getItem(input.name);
        if (savedValue && !input.value) {
            input.value = savedValue;
        }
        
        // Save data on change
        input.addEventListener('change', function() {
            localStorage.setItem(this.name, this.value);
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Template preview functionality
    window.previewTemplate = function(category, templateName) {
        const modal = new bootstrap.Modal(document.getElementById('templatePreviewModal'));
        const previewInfo = document.getElementById('previewInfo');
        const previewContent = document.getElementById('previewContent');
        const previewDownloadBtn = document.getElementById('previewDownloadBtn');
        const previewViewBtn = document.getElementById('previewViewBtn');
        
        // Show loading state
        previewInfo.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
        previewContent.textContent = 'Loading template content...';
        
        // Fetch template preview
        fetch(`/preview/${category}/${templateName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update template info
                    previewInfo.innerHTML = `
                        <div class="mb-2">
                            <strong>Name:</strong> ${data.template_name || templateName}
                        </div>
                        <div class="mb-2">
                            <strong>Category:</strong> ${category}
                        </div>
                        <div class="mb-2">
                            <strong>File Type:</strong> ${data.file_type || 'Unknown'}
                        </div>
                        <div class="mb-2">
                            <strong>Size:</strong> ${data.content ? data.content.length : 0} characters
                        </div>
                    `;
                    
                    // Update template content
                    previewContent.textContent = data.content || 'No content available';
                    
                    // Update button actions
                    previewDownloadBtn.onclick = () => {
                        window.location.href = `/download/${category}/${templateName}`;
                    };
                    
                    previewViewBtn.onclick = () => {
                        modal.hide();
                        window.location.href = `/template/${category}/${templateName}`;
                    };
                } else {
                    previewInfo.innerHTML = '<div class="alert alert-danger">Error loading template preview</div>';
                    previewContent.textContent = 'Error: ' + (data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                previewInfo.innerHTML = '<div class="alert alert-danger">Error loading template preview</div>';
                previewContent.textContent = 'Error: ' + error.message;
            });
        
        modal.show();
    };

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N for new category
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            window.location.href = '/create-category';
        }
        
        // Ctrl/Cmd + U for upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            window.location.href = '/upload';
        }
        
        // Ctrl/Cmd + M for manage categories
        if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
            e.preventDefault();
            window.location.href = '/manage-categories';
        }
        
        // Ctrl/Cmd + H for home
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            window.location.href = '/';
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
        
        // F1 for help
        if (e.key === 'F1') {
            e.preventDefault();
            showKeyboardShortcuts();
        }
    });

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log('Page load time:', loadTime + 'ms');
        });
    }

    // Service Worker registration (if available)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered: ', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
});

// Utility functions
window.utils = {
    // Format bytes
    formatBytes: function(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    // Format date
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Dark Mode Functions
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    
    if (!darkModeToggle || !darkModeIcon) return;
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Add click event listener
    darkModeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
}

function setTheme(theme) {
    const darkModeIcon = document.getElementById('darkModeIcon');
    
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        darkModeIcon.className = 'fas fa-sun';
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        darkModeIcon.className = 'fas fa-moon';
        localStorage.setItem('theme', 'light');
    }
}

// Dynamic Navigation Functions
function loadDynamicNavigation() {
    const dropdownMenu = document.getElementById('templatesDropdownMenu');
    if (!dropdownMenu) return;
    
    // Default categories with their icons and colors
    const defaultCategories = {
        'network': { icon: 'fas fa-network-wired', color: 'primary', name: 'Network' },
        'security': { icon: 'fas fa-shield-alt', color: 'success', name: 'Security' },
        'automation': { icon: 'fas fa-robot', color: 'warning', name: 'Automation' },
        'monitoring': { icon: 'fas fa-chart-line', color: 'info', name: 'Monitoring' },
        'community': { icon: 'fas fa-users', color: 'secondary', name: 'Community' }
    };
    
    // Load custom categories from API
    fetch('/api/categories')
        .then(response => response.json())
        .then(customCategories => {
            // Merge default and custom categories
            const allCategories = { ...defaultCategories, ...customCategories };
            
            // Clear existing items
            dropdownMenu.innerHTML = '';
            
            // Add category items
            Object.entries(allCategories).forEach(([key, category]) => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <a class="dropdown-item" href="/templates/${key}">
                        <i class="${category.icon} me-2 text-${category.color}"></i>${category.display_name || category.name}
                    </a>
                `;
                dropdownMenu.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading categories:', error);
            // Fallback to default categories
            Object.entries(defaultCategories).forEach(([key, category]) => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <a class="dropdown-item" href="/templates/${key}">
                        <i class="${category.icon} me-2 text-${category.color}"></i>${category.name}
                    </a>
                `;
                dropdownMenu.appendChild(li);
            });
        });
}


// Keyboard Shortcuts Help
function showKeyboardShortcuts() {
    const shortcutsModal = document.createElement("div");
    shortcutsModal.className = "modal fade";
    shortcutsModal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-keyboard me-2"></i>Keyboard Shortcuts
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Navigation</h6>
                            <div class="list-group list-group-flush">
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Ctrl</kbd> + <kbd>H</kbd></span>
                                    <span>Go to Home</span>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Ctrl</kbd> + <kbd>K</kbd></span>
                                    <span>Focus Search</span>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Ctrl</kbd> + <kbd>U</kbd></span>
                                    <span>Upload Template</span>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Ctrl</kbd> + <kbd>N</kbd></span>
                                    <span>New Category</span>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Ctrl</kbd> + <kbd>M</kbd></span>
                                    <span>Manage Categories</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>General</h6>
                            <div class="list-group list-group-flush">
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Esc</kbd></span>
                                    <span>Close Modal</span>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>F1</kbd></span>
                                    <span>Show Help</span>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <span><kbd>Ctrl</kbd> + <kbd>/</kbd></span>
                                    <span>Toggle Dark Mode</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(shortcutsModal);
    const modal = new bootstrap.Modal(shortcutsModal);
    modal.show();
    
    // Clean up when modal is hidden
    shortcutsModal.addEventListener("hidden.bs.modal", function() {
        document.body.removeChild(shortcutsModal);
    });
}
