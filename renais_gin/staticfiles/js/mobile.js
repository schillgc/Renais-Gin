// Mobile-specific functionality for Renais Gin

class MobileManager {
    constructor() {
        this.isMobile = this.checkMobile();
        this.touchStartX = null;
        this.touchStartY = null;
        this.init();
    }

    init() {
        if (this.isMobile) {
            this.setupMobileNavigation();
            this.setupTouchGestures();
            this.optimizeForMobile();
            this.setupPWAFeatures();
        }
    }

    checkMobile() {
        return window.innerWidth <= 768 ||
               /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    setupMobileNavigation() {
        // Enhanced mobile menu
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        if (navbarToggler && navbarCollapse) {
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                    navbarCollapse.classList.remove('show');
                }
            });

            // Smooth close animation
            navbarCollapse.addEventListener('click', (e) => {
                if (e.target.tagName === 'A') {
                    setTimeout(() => {
                        navbarCollapse.classList.remove('show');
                    }, 300);
                }
            });
        }

        // Add mobile-specific menu items
        this.addMobileMenuItems();
    }

    addMobileMenuItems() {
        const navbarNav = document.querySelector('.navbar-nav');
        if (!navbarNav) return;

        // Add quick action buttons to mobile menu
        const quickActions = `
            <div class="mobile-quick-actions d-lg-none p-3 border-top">
                <div class="row g-2">
                    <div class="col-6">
                        <a href="/bottles/register/" class="btn btn-renais btn-sm w-100">
                            <i class="fas fa-qrcode me-1"></i>Scan Bottle
                        </a>
                    </div>
                    <div class="col-6">
                        <a href="/pledges/submit/" class="btn btn-outline-dark btn-sm w-100">
                            <i class="fas fa-hand-holding-heart me-1"></i>Make Pledge
                        </a>
                    </div>
                </div>
            </div>
        `;

        navbarNav.insertAdjacentHTML('afterend', quickActions);
    }

    setupTouchGestures() {
        // Swipe gestures for carousels or image galleries
        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (!this.touchStartX || !this.touchStartY) return;

            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;

            const diffX = this.touchStartX - touchEndX;
            const diffY = this.touchStartY - touchEndY;

            // Only consider horizontal swipes
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left
                    this.handleSwipe('left');
                } else {
                    // Swipe right
                    this.handleSwipe('right');
                }
            }

            this.touchStartX = null;
            this.touchStartY = null;
        }, { passive: true });
    }

    handleSwipe(direction) {
        // Handle swipe gestures for relevant components
        const activeCarousel = document.querySelector('.carousel-item.active');
        if (activeCarousel) {
            const carousel = activeCarousel.closest('.carousel');
            if (carousel) {
                const bsCarousel = bootstrap.Carousel.getInstance(carousel);
                if (bsCarousel) {
                    if (direction === 'left') {
                        bsCarousel.next();
                    } else {
                        bsCarousel.prev();
                    }
                }
            }
        }
    }

    optimizeForMobile() {
        // Optimize images for mobile
        this.optimizeImages();

        // Adjust chart sizes for mobile
        this.adjustChartsForMobile();

        // Enhance form inputs for mobile
        this.enhanceFormInputs();

        // Add mobile-specific CSS classes
        document.body.classList.add('mobile-device');
    }

    optimizeImages() {
        // Lazy load images
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

    adjustChartsForMobile() {
        // Adjust chart containers for mobile
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            container.style.height = '300px'; // Smaller height for mobile
        });
    }

    enhanceFormInputs() {
        // Enhance form inputs for mobile
        const numberInputs = document.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.setAttribute('inputmode', 'numeric');
            input.setAttribute('pattern', '[0-9]*');
        });

        const telInputs = document.querySelectorAll('input[type="tel"]');
        telInputs.forEach(input => {
            input.setAttribute('inputmode', 'tel');
        });

        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.setAttribute('inputmode', 'email');
        });
    }

    setupPWAFeatures() {
        // Add to homescreen prompt
        this.setupAddToHomeScreen();

        // Offline functionality
        this.setupOfflineSupport();

        // Push notifications setup
        this.setupPushNotifications();
    }

    setupAddToHomeScreen() {
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            // Stash the event so it can be triggered later
            deferredPrompt = e;

            // Show install prompt
            this.showInstallPrompt();
        });

        // Add install button functionality
        const installBtn = document.getElementById('installApp');
        if (installBtn) {
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    // Show the install prompt
                    deferredPrompt.prompt();
                    // Wait for the user to respond to the prompt
                    const { outcome } = await deferredPrompt.userChoice;

                    if (outcome === 'accepted') {
                        window.renaisApp.showToast('Renais Gin app installed successfully!', 'success');
                    }

                    // Clear the saved prompt since it can't be used again
                    deferredPrompt = null;
                }
            });
        }
    }

    showInstallPrompt() {
        // Create and show install prompt
        const prompt = document.createElement('div');
        prompt.className = 'alert alert-info alert-dismissible position-fixed bottom-0 start-0 m-3';
        prompt.style.zIndex = '9999';
        prompt.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-download me-2"></i>
                <div class="flex-grow-1">
                    <strong>Install Renais Gin App</strong>
                    <div class="small">Get the full mobile experience</div>
                </div>
                <button type="button" class="btn btn-sm btn-renais ms-2" id="confirmInstall">
                    Install
                </button>
                <button type="button" class="btn-close ms-2" data-bs-dismiss="alert"></button>
            </div>
        `;

        document.body.appendChild(prompt);

        // Add event listener for install button
        document.getElementById('confirmInstall').addEventListener('click', () => {
            // This would trigger the install prompt
            prompt.remove();
        });
    }

    setupOfflineSupport() {
        // Check online status
        window.addEventListener('online', () => {
            window.renaisApp.showToast('Connection restored', 'success');
            document.body.classList.remove('offline');
        });

        window.addEventListener('offline', () => {
            window.renaisApp.showToast('You are currently offline', 'warning');
            document.body.classList.add('offline');
        });
    }

    setupPushNotifications() {
        // Request permission for push notifications
        if ('Notification' in window && 'serviceWorker' in navigator) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('Push notifications granted');
                    // Here you would subscribe to push notifications
                }
            });
        }
    }

    // Utility Methods
    getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return "tablet";
        } else if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return "mobile";
        }
        return "desktop";
    }

    getOrientation() {
        return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
    }

    // Event for orientation changes
    setupOrientationListener() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 300);
        });
    }

    handleOrientationChange() {
        const orientation = this.getOrientation();
        document.body.setAttribute('data-orientation', orientation);

        // Adjust layout based on orientation
        if (orientation === 'landscape') {
            // Landscape-specific adjustments
        } else {
            // Portrait-specific adjustments
        }
    }
}

// Initialize mobile features
document.addEventListener('DOMContentLoaded', () => {
    window.mobileManager = new MobileManager();
});

// Mobile-specific utility functions
const MobileUtils = {
    // Vibrate device (if supported)
    vibrate: (pattern = 200) => {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    },

    // Share content
    share: async (title, text, url) => {
        if ('share' in navigator) {
            try {
                await navigator.share({
                    title: title,
                    text: text,
                    url: url
                });
            } catch (error) {
                console.log('Sharing cancelled or failed:', error);
            }
        } else {
            // Fallback: copy to clipboard or show share options
            this.fallbackShare(title, text, url);
        }
    },

    fallbackShare: (title, text, url) => {
        // Implement fallback sharing method
        if ('clipboard' in navigator) {
            navigator.clipboard.writeText(`${title}: ${text} ${url}`).then(() => {
                window.renaisApp.showToast('Copied to clipboard!', 'success');
            });
        }
    },

    // Check if PWA is installed
    isPWAInstalled: () => {
        return window.matchMedia('(display-mode: standalone)').matches ||
               window.navigator.standalone === true;
    }
};