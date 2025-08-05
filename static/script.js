// Navigation functionality for home page
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const navTabs = document.querySelectorAll('.nav-tab');
    const contentSections = document.querySelectorAll('.content-section');
    
    navTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs and sections
            navTabs.forEach(t => t.classList.remove('active'));
            contentSections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show corresponding section
            const sectionName = this.dataset.section;
            const targetSection = document.querySelector(`.${sectionName}-section`);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });
    
    // Gallery item hover functionality
    const galleryItems = document.querySelectorAll('.gallery-item');
    const infoPanel = document.querySelector('.info-panel .info-content');
    
    if (infoPanel) {
        galleryItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                const title = this.dataset.title;
                const caption = this.dataset.caption;
                const date = this.dataset.date;
                
                let infoHTML = `<h4>✨ ${title} ✨</h4>`;
                if (caption) {
                    infoHTML += `<p class="info-text">${caption}</p>`;
                }
                infoHTML += `<p class="info-date">Created: ${new Date(date).toLocaleDateString()}</p>`;
                
                infoPanel.innerHTML = infoHTML;
            });
            
            item.addEventListener('mouseleave', function() {
                infoPanel.innerHTML = `
                    <h4>Hover over artwork to see details! ✨</h4>
                    <p class="info-text">Click to view full size and leave comments</p>
                `;
            });
        });
    }
    
    // Set default active tab
    const defaultTab = document.querySelector('.nav-tab[data-section="gallery"]');
    if (defaultTab) {
        defaultTab.click();
    }
});

// Commission calculator functionality
function calculatePrice() {
    const form = document.getElementById('commissionForm');
    const formData = new FormData(form);
    
    const data = {
        type: formData.get('type'),
        multiple_characters: document.getElementById('multipleChars').checked,
        nsfw: document.getElementById('nsfw').checked,
        rush: document.getElementById('rush').checked,
        unrendered: document.getElementById('unrendered').checked,
        indonesian_discount: document.getElementById('indonesian').checked
    };
    
    fetch('/calculate_commission', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('basePrice').textContent = result.base_price;
        document.getElementById('totalPrice').textContent = result.total_price;
        document.getElementById('priceResult').style.display = 'block';
        
        // Add a nice animation
        const priceResult = document.getElementById('priceResult');
        priceResult.style.opacity = '0';
        priceResult.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            priceResult.style.transition = 'all 0.5s ease';
            priceResult.style.opacity = '1';
            priceResult.style.transform = 'translateY(0)';
        }, 100);
    })
    .catch(error => {
        console.error('Error calculating price:', error);
        alert('Error calculating price. Please try again.');
    });
}

// OC clothing toggle functionality
function toggleClothing(itemId) {
    const clothingItem = document.getElementById(itemId);
    if (clothingItem) {
        if (clothingItem.style.opacity === '0' || clothingItem.style.opacity === '') {
            clothingItem.style.opacity = '1';
            clothingItem.style.visibility = 'visible';
        } else {
            clothingItem.style.opacity = '0';
            clothingItem.style.visibility = 'hidden';
        }
    }
}

// Comment reply functionality
function toggleReply(commentId) {
    const replyForm = document.getElementById(`reply-${commentId}`);
    if (replyForm) {
        if (replyForm.style.display === 'none' || replyForm.style.display === '') {
            replyForm.style.display = 'block';
            replyForm.style.opacity = '0';
            replyForm.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                replyForm.style.transition = 'all 0.3s ease';
                replyForm.style.opacity = '1';
                replyForm.style.transform = 'translateY(0)';
            }, 50);
        } else {
            replyForm.style.opacity = '0';
            replyForm.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                replyForm.style.display = 'none';
            }, 300);
        }
    }
}

// Comment voting functionality
document.addEventListener('DOMContentLoaded', function() {
    const voteButtons = document.querySelectorAll('.vote-btn');
    
    voteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.comment;
            const voteType = this.classList.contains('upvote') ? 'up' : 'down';
            
            fetch('/vote_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    comment_id: commentId,
                    vote_type: voteType
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Update vote counts
                    const upvoteBtn = document.querySelector(`.upvote[data-comment="${commentId}"]`);
                    const downvoteBtn = document.querySelector(`.downvote[data-comment="${commentId}"]`);
                    
                    if (upvoteBtn) upvoteBtn.textContent = `↑ ${result.upvotes}`;
                    if (downvoteBtn) downvoteBtn.textContent = `↓ ${result.downvotes}`;
                    
                    // Visual feedback
                    this.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 200);
                } else {
                    alert(result.message || 'Error voting. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error voting:', error);
                alert('Error voting. Please try again.');
            });
        });
    });
});

// Gallery masonry layout adjustment
function adjustGalleryLayout() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        const img = item.querySelector('img');
        if (img) {
            img.onload = function() {
                // Add loaded class for smooth animation
                item.classList.add('loaded');
            };
        }
    });
}

// Character canvas positioning
function adjustCharacterCanvas() {
    const canvas = document.getElementById('characterCanvas');
    if (canvas) {
        const baseCharacter = document.getElementById('baseCharacter');
        if (baseCharacter) {
            // Ensure all clothing items are positioned relative to the base character
            const clothingItems = document.querySelectorAll('.clothing-item');
            clothingItems.forEach(item => {
                item.style.position = 'absolute';
                item.style.top = '0';
                item.style.left = '50%';
                item.style.transform = 'translateX(-50%)';
            });
        }
    }
}

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Form validation and enhancement
function enhanceFormExperience() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        
        inputs.forEach(input => {
            // Add focus animations
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                if (this.value.trim() !== '') {
                    this.parentElement.classList.add('has-content');
                } else {
                    this.parentElement.classList.remove('has-content');
                }
            });
            
            // Check initial content
            if (input.value.trim() !== '') {
                input.parentElement.classList.add('has-content');
            }
        });
    });
}

// Notification animations
function animateNotifications() {
    const notifications = document.querySelectorAll('.flash-message');
    
    notifications.forEach((notification, index) => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            notification.style.transition = 'all 0.5s ease';
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000 + (index * 100));
    });
}

// Image lazy loading for better performance
function implementLazyLoading() {
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
}

// Drag and drop clothing reordering
class ClothingReorderer {
    constructor(ocId) {
        this.ocId = ocId;
        this.draggedElement = null;
        this.clothingItems = [];
        this.init();
    }
    
    init() {
        const clothingControls = document.querySelector('.clothing-controls');
        if (!clothingControls) return;
        
        this.setupDragAndDrop();
        this.addReorderUI();
    }
    
    setupDragAndDrop() {
        const clothingToggles = document.querySelectorAll('.clothing-toggle');
        
        clothingToggles.forEach(toggle => {
            toggle.draggable = true;
            toggle.addEventListener('dragstart', this.handleDragStart.bind(this));
            toggle.addEventListener('dragover', this.handleDragOver.bind(this));
            toggle.addEventListener('drop', this.handleDrop.bind(this));
            toggle.addEventListener('dragend', this.handleDragEnd.bind(this));
            
            // Add drag handle
            const dragHandle = document.createElement('div');
            dragHandle.className = 'drag-handle';
            dragHandle.innerHTML = '⋮⋮';
            toggle.prepend(dragHandle);
        });
    }
    
    addReorderUI() {
        const clothingControls = document.querySelector('.clothing-controls');
        const reorderBtn = document.createElement('button');
        reorderBtn.className = 'reorder-btn';
        reorderBtn.textContent = '↕️ Reorder Layers';
        reorderBtn.onclick = () => this.toggleReorderMode();
        
        clothingControls.querySelector('h3').after(reorderBtn);
    }
    
    handleDragStart(e) {
        this.draggedElement = e.target;
        e.target.classList.add('dragging');
    }
    
    handleDragOver(e) {
        e.preventDefault();
        const afterElement = this.getDragAfterElement(e.currentTarget.parentNode, e.clientY);
        if (afterElement == null) {
            e.currentTarget.parentNode.appendChild(this.draggedElement);
        } else {
            e.currentTarget.parentNode.insertBefore(this.draggedElement, afterElement);
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.updateZIndices();
    }
    
    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        this.draggedElement = null;
    }
    
    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.clothing-toggle:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    updateZIndices() {
        const clothingToggles = document.querySelectorAll('.clothing-toggle');
        const newOrder = [];
        
        clothingToggles.forEach((toggle, index) => {
            const itemId = toggle.querySelector('input').dataset.item.replace('item-', '');
            const zIndex = clothingToggles.length - index; // Reverse order for z-index
            
            newOrder.push({ id: itemId, z_index: zIndex });
            
            // Update visual z-index
            const clothingItem = document.getElementById(`item-${itemId}`);
            if (clothingItem) {
                clothingItem.style.zIndex = zIndex;
            }
        });
        
        // Save to server
        fetch('/admin/reorder_clothing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                oc_id: this.ocId,
                clothing_order: newOrder
            })
        }).catch(console.error);
    }
}

// Lazy loading with Intersection Observer
class LazyLoader {
    constructor() {
        this.imageObserver = null;
        this.init();
    }
    
    init() {
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                        this.imageObserver.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            this.observeImages();
        } else {
            // Fallback for older browsers
            this.loadAllImages();
        }
    }
    
    observeImages() {
        document.querySelectorAll('img[data-src]').forEach(img => {
            this.imageObserver.observe(img);
        });
    }
    
    loadImage(img) {
        // Progressive image loading with WebP support
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const originalSrc = img.dataset.src;
        
        // Check WebP support
        const supportsWebP = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
        
        // Determine optimal size based on container
        const containerWidth = img.parentElement.offsetWidth;
        let size = 'medium';
        if (containerWidth <= 150) size = 'thumb';
        else if (containerWidth <= 300) size = 'small';
        else if (containerWidth <= 600) size = 'medium';
        else size = 'large';
        
        // Build optimized URL
        const optimizedSrc = `/api/optimize_image/${originalSrc}?size=${size}&quality=85`;
        
        // Preload with blur-up technique
        if (img.dataset.placeholder) {
            const placeholder = new Image();
            placeholder.onload = () => {
                img.style.filter = 'blur(5px)';
                img.src = img.dataset.placeholder;
                img.style.opacity = '1';
            };
            placeholder.src = img.dataset.placeholder;
        }
        
        // Load main image
        const mainImage = new Image();
        mainImage.onload = () => {
            img.src = optimizedSrc;
            img.style.filter = 'none';
            img.classList.add('loaded');
        };
        mainImage.onerror = () => {
            // Fallback to original
            img.src = originalSrc;
            img.classList.add('loaded');
        };
        mainImage.src = optimizedSrc;
    }
    
    loadAllImages() {
        document.querySelectorAll('img[data-src]').forEach(img => {
            this.loadImage(img);
        });
    }
}

// Mobile-first responsive handler
class ResponsiveHandler {
    constructor() {
        this.breakpoints = {
            mobile: 480,
            tablet: 768,
            desktop: 1024
        };
        this.currentBreakpoint = this.getCurrentBreakpoint();
        this.init();
    }
    
    init() {
        this.handleResize();
        window.addEventListener('resize', this.debounce(this.handleResize.bind(this), 250));
        this.optimizeForTouch();
        this.handleOrientation();
    }
    
    getCurrentBreakpoint() {
        const width = window.innerWidth;
        if (width <= this.breakpoints.mobile) return 'mobile';
        if (width <= this.breakpoints.tablet) return 'tablet';
        return 'desktop';
    }
    
    handleResize() {
        const newBreakpoint = this.getCurrentBreakpoint();
        
        if (newBreakpoint !== this.currentBreakpoint) {
            this.currentBreakpoint = newBreakpoint;
            document.body.className = `breakpoint-${newBreakpoint}`;
            this.adjustLayoutForBreakpoint();
        }
        
        this.adjustGalleryMasonry();
    }
    
    adjustLayoutForBreakpoint() {
        const mainLayout = document.querySelector('.main-layout');
        if (!mainLayout) return;
        
        switch (this.currentBreakpoint) {
            case 'mobile':
                this.mobileOptimizations();
                break;
            case 'tablet':
                this.tabletOptimizations();
                break;
            case 'desktop':
                this.desktopOptimizations();
                break;
        }
    }
    
    mobileOptimizations() {
        // Hide character art on mobile to save space
        const characterArt = document.querySelector('.character-art');
        if (characterArt) characterArt.style.display = 'none';
        
        // Stack navigation vertically
        const topNav = document.querySelector('.top-nav');
        if (topNav) topNav.style.flexDirection = 'column';
        
        // Reduce gallery columns
        const galleryGrid = document.querySelector('.gallery-grid');
        if (galleryGrid) {
            galleryGrid.style.gridTemplateColumns = 'repeat(2, 1fr)';
        }
        
        // Simplify comment forms
        const commentForms = document.querySelectorAll('.comment-form textarea');
        commentForms.forEach(textarea => {
            textarea.style.minHeight = '80px';
        });
    }
    
    tabletOptimizations() {
        const galleryGrid = document.querySelector('.gallery-grid');
        if (galleryGrid) {
            galleryGrid.style.gridTemplateColumns = 'repeat(3, 1fr)';
        }
    }
    
    desktopOptimizations() {
        // Restore full layout
        const characterArt = document.querySelector('.character-art');
        if (characterArt) characterArt.style.display = 'block';
        
        const topNav = document.querySelector('.top-nav');
        if (topNav) topNav.style.flexDirection = 'row';
    }
    
    optimizeForTouch() {
        if ('ontouchstart' in window) {
            document.body.classList.add('touch-device');
            
            // Increase tap targets
            const clickables = document.querySelectorAll('button, .nav-link, .gallery-item, .oc-folder');
            clickables.forEach(el => {
                el.style.minHeight = '44px';
                el.style.minWidth = '44px';
            });
            
            // Add touch feedback
            clickables.forEach(el => {
                el.addEventListener('touchstart', function() {
                    this.classList.add('touched');
                });
                el.addEventListener('touchend', function() {
                    setTimeout(() => this.classList.remove('touched'), 150);
                });
            });
        }
    }
    
    handleOrientation() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleResize();
                this.adjustGalleryMasonry();
            }, 100);
        });
    }
    
    adjustGalleryMasonry() {
        const masonryContainer = document.querySelector('.gallery-masonry');
        if (!masonryContainer) return;
        
        // Recalculate masonry layout
        const items = masonryContainer.querySelectorAll('.gallery-card');
        items.forEach(item => {
            item.style.breakInside = 'avoid';
            item.style.pageBreakInside = 'avoid';
        });
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoad: 0,
            firstPaint: 0,
            firstContentfulPaint: 0,
            largestContentfulPaint: 0,
            cumulativeLayoutShift: 0
        };
        this.init();
    }
    
    init() {
        if ('performance' in window) {
            this.measurePageLoad();
            this.measurePaintMetrics();
            this.measureCLS();
        }
    }
    
    measurePageLoad() {
        window.addEventListener('load', () => {
            const navigation = performance.getEntriesByType('navigation')[0];
            this.metrics.pageLoad = navigation.loadEventEnd - navigation.loadEventStart;
            this.reportMetrics();
        });
    }
    
    measurePaintMetrics() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    switch (entry.name) {
                        case 'first-paint':
                            this.metrics.firstPaint = entry.startTime;
                            break;
                        case 'first-contentful-paint':
                            this.metrics.firstContentfulPaint = entry.startTime;
                            break;
                    }
                }
            });
            observer.observe({ entryTypes: ['paint'] });
            
            // LCP
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.metrics.largestContentfulPaint = lastEntry.startTime;
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    }
    
    measureCLS() {
        if ('PerformanceObserver' in window) {
            let clsValue = 0;
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                }
                this.metrics.cumulativeLayoutShift = clsValue;
            });
            observer.observe({ entryTypes: ['layout-shift'] });
        }
    }
    
    reportMetrics() {
        // Only report in development
        if (window.location.hostname === 'localhost') {
            console.table(this.metrics);
        }
        
        // Send to analytics in production
        if (window.gtag) {
            window.gtag('event', 'page_performance', {
                page_load_time: this.metrics.pageLoad,
                first_contentful_paint: this.metrics.firstContentfulPaint,
                largest_contentful_paint: this.metrics.largestContentfulPaint,
                cumulative_layout_shift: this.metrics.cumulativeLayoutShift
            });
        }
    }
}

// Initialize all performance and mobile optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize existing functionality
    adjustGalleryLayout();
    adjustCharacterCanvas();
    enhanceFormExperience();
    animateNotifications();
    
    // Initialize new performance features
    const lazyLoader = new LazyLoader();
    const responsiveHandler = new ResponsiveHandler();
    const performanceMonitor = new PerformanceMonitor();
    
    // Initialize clothing reorderer if on OC detail page
    const ocId = document.body.dataset.ocId;
    if (ocId) {
        new ClothingReorderer(ocId);
    }
    
    // Service Worker for caching (if supported)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(console.error);
    }
});

// Parallax effect for character art
function addParallaxEffect() {
    const characterImg = document.querySelector('.character-img');
    if (characterImg) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            characterImg.style.transform = `translateY(${parallax}px)`;
        });
    }
}

// Advanced gallery functionality
class GalleryManager {
    constructor() {
        this.currentImageIndex = 0;
        this.images = [];
        this.initLightbox();
    }
    
    initLightbox() {
        // Create lightbox overlay
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox-overlay';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <button class="lightbox-close">&times;</button>
                <button class="lightbox-prev">&#8249;</button>
                <img class="lightbox-image" src="" alt="">
                <button class="lightbox-next">&#8250;</button>
                <div class="lightbox-info">
                    <h3 class="lightbox-title"></h3>
                    <p class="lightbox-caption"></p>
                </div>
            </div>
        `;
        document.body.appendChild(lightbox);
        
        // Add event listeners
        lightbox.querySelector('.lightbox-close').addEventListener('click', () => this.closeLightbox());
        lightbox.querySelector('.lightbox-prev').addEventListener('click', () => this.prevImage());
        lightbox.querySelector('.lightbox-next').addEventListener('click', () => this.nextImage());
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) this.closeLightbox();
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (lightbox.classList.contains('active')) {
                switch(e.key) {
                    case 'Escape':
                        this.closeLightbox();
                        break;
                    case 'ArrowLeft':
                        this.prevImage();
                        break;
                    case 'ArrowRight':
                        this.nextImage();
                        break;
                }
            }
        });
    }
    
    openLightbox(imageIndex, images) {
        this.currentImageIndex = imageIndex;
        this.images = images;
        
        const lightbox = document.querySelector('.lightbox-overlay');
        const img = lightbox.querySelector('.lightbox-image');
        const title = lightbox.querySelector('.lightbox-title');
        const caption = lightbox.querySelector('.lightbox-caption');
        
        const currentImage = this.images[this.currentImageIndex];
        img.src = currentImage.src;
        title.textContent = currentImage.title;
        caption.textContent = currentImage.caption;
        
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeLightbox() {
        const lightbox = document.querySelector('.lightbox-overlay');
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    prevImage() {
        this.currentImageIndex = (this.currentImageIndex - 1 + this.images.length) % this.images.length;
        this.updateLightboxImage();
    }
    
    nextImage() {
        this.currentImageIndex = (this.currentImageIndex + 1) % this.images.length;
        this.updateLightboxImage();
    }
    
    updateLightboxImage() {
        const lightbox = document.querySelector('.lightbox-overlay');
        const img = lightbox.querySelector('.lightbox-image');
        const title = lightbox.querySelector('.lightbox-title');
        const caption = lightbox.querySelector('.lightbox-caption');
        
        const currentImage = this.images[this.currentImageIndex];
        img.style.opacity = '0';
        
        setTimeout(() => {
            img.src = currentImage.src;
            title.textContent = currentImage.title;
            caption.textContent = currentImage.caption;
            img.style.opacity = '1';
        }, 150);
    }
}

// Theme switcher
class ThemeManager {
    constructor() {
        this.themes = {
            default: 'Default Cottagecore',
            autumn: 'Autumn Harvest',
            spring: 'Spring Bloom',
            winter: 'Winter Cozy'
        };
        this.currentTheme = localStorage.getItem('selectedTheme') || 'default';
        this.init();
    }
    
    init() {
        this.createThemeSwitcher();
        this.applyTheme(this.currentTheme);
    }
    
    createThemeSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'theme-switcher';
        switcher.innerHTML = `
            <button class="theme-toggle">🎨</button>
            <div class="theme-options">
                ${Object.entries(this.themes).map(([key, name]) => 
                    `<button class="theme-option" data-theme="${key}">${name}</button>`
                ).join('')}
            </div>
        `;
        
        document.body.appendChild(switcher);
        
        // Add event listeners
        switcher.querySelector('.theme-toggle').addEventListener('click', () => {
            switcher.classList.toggle('open');
        });
        
        switcher.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => {
                this.switchTheme(option.dataset.theme);
                switcher.classList.remove('open');
            });
        });
    }
    
    switchTheme(themeName) {
        this.currentTheme = themeName;
        localStorage.setItem('selectedTheme', themeName);
        this.applyTheme(themeName);
    }
    
    applyTheme(themeName) {
        document.body.className = `theme-${themeName}`;
        
        // Update CSS custom properties based on theme
        const root = document.documentElement;
        switch(themeName) {
            case 'autumn':
                root.style.setProperty('--primary-cream', '#FFF4E6');
                root.style.setProperty('--dusty-rose', '#C17A74');
                root.style.setProperty('--sage-green', '#8B7355');
                root.style.setProperty('--golden-yellow', '#D4A574');
                break;
            case 'spring':
                root.style.setProperty('--primary-cream', '#F8FFF8');
                root.style.setProperty('--dusty-rose', '#F8C8DC');
                root.style.setProperty('--sage-green', '#90EE90');
                root.style.setProperty('--golden-yellow', '#FFE135');
                break;
            case 'winter':
                root.style.setProperty('--primary-cream', '#F0F8FF');
                root.style.setProperty('--dusty-rose', '#B6D7FF');
                root.style.setProperty('--sage-green', '#4F94CD');
                root.style.setProperty('--golden-yellow', '#E6E6FA');
                break;
            default:
                // Reset to default values
                root.style.setProperty('--primary-cream', '#FFF8E7');
                root.style.setProperty('--dusty-rose', '#D4A5A5');
                root.style.setProperty('--sage-green', '#9CAF88');
                root.style.setProperty('--golden-yellow', '#E8D5A3');
        }
    }
}

// Search functionality for gallery and OCs
class SearchManager {
    constructor() {
        this.createSearchBar();
        this.setupSearch();
    }
    
    createSearchBar() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.innerHTML = `
            <input type="text" class="search-input" placeholder="Search artwork, characters, or blog posts...">
            <button class="search-clear" style="display: none;">&times;</button>
        `;
        
        // Insert search bar into navigation area
        const topNav = document.querySelector('.top-nav');
        if (topNav) {
            topNav.appendChild(searchContainer);
        }
    }
    
    setupSearch() {
        const searchInput = document.querySelector('.search-input');
        const searchClear = document.querySelector('.search-clear');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase().trim();
                
                if (query.length > 0) {
                    searchClear.style.display = 'block';
                    this.performSearch(query);
                } else {
                    searchClear.style.display = 'none';
                    this.clearSearch();
                }
            });
        }
        
        if (searchClear) {
            searchClear.addEventListener('click', () => {
                searchInput.value = '';
                searchClear.style.display = 'none';
                this.clearSearch();
            });
        }
    }
    
    performSearch(query) {
        // Search gallery items
        const galleryItems = document.querySelectorAll('.gallery-item');
        galleryItems.forEach(item => {
            const title = item.dataset.title?.toLowerCase() || '';
            const caption = item.dataset.caption?.toLowerCase() || '';
            
            if (title.includes(query) || caption.includes(query)) {
                item.style.display = 'block';
                item.classList.add('search-match');
            } else {
                item.style.display = 'none';
                item.classList.remove('search-match');
            }
        });
        
        // Search OC folders
        const ocFolders = document.querySelectorAll('.oc-folder');
        ocFolders.forEach(folder => {
            const name = folder.querySelector('.folder-tab')?.textContent.toLowerCase() || '';
            
            if (name.includes(query)) {
                folder.style.display = 'block';
                folder.classList.add('search-match');
            } else {
                folder.style.display = 'none';
                folder.classList.remove('search-match');
            }
        });
        
        // Search blog posts
        const blogPosts = document.querySelectorAll('.blog-preview');
        blogPosts.forEach(post => {
            const title = post.querySelector('.post-title')?.textContent.toLowerCase() || '';
            const summary = post.querySelector('.post-summary')?.textContent.toLowerCase() || '';
            
            if (title.includes(query) || summary.includes(query)) {
                post.style.display = 'block';
                post.classList.add('search-match');
            } else {
                post.style.display = 'none';
                post.classList.remove('search-match');
            }
        });
    }
    
    clearSearch() {
        const allItems = document.querySelectorAll('.gallery-item, .oc-folder, .blog-preview');
        allItems.forEach(item => {
            item.style.display = 'block';
            item.classList.remove('search-match');
        });
    }
}

// Initialize managers
let galleryManager, themeManager, searchManager;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize advanced features
    galleryManager = new GalleryManager();
    themeManager = new ThemeManager();
    searchManager = new SearchManager();
    
    // Add parallax effect
    addParallaxEffect();
});

// Export functions for global access
window.toggleClothing = toggleClothing;
window.toggleReply = toggleReply;
window.calculatePrice = calculatePrice;
