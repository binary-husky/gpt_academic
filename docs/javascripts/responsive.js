/**
 * Responsive Enhancements for OpenJudge Documentation
 * Phase 5: 响应式完善
 *
 * Features:
 * - Mobile menu toggle
 * - Table scroll detection
 * - Touch event optimization
 * - Viewport resize handling
 */

(function() {
  'use strict';

  // ========================================
  // Mobile Navigation Toggle
  // ========================================

  function initMobileNav() {
    const sidebar = document.querySelector('.md-sidebar--primary, nav.sidebar, .nav-sidebar');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    let overlay = document.querySelector('.mobile-nav-overlay');

    // Create overlay if it doesn't exist
    if (!overlay && sidebar) {
      overlay = document.createElement('div');
      overlay.className = 'mobile-nav-overlay';
      document.body.appendChild(overlay);
    }

    // Create menu toggle if it doesn't exist
    if (!menuToggle && sidebar) {
      const toggle = document.createElement('button');
      toggle.className = 'mobile-menu-toggle';
      toggle.setAttribute('aria-label', 'Toggle navigation menu');
      toggle.innerHTML = `
        <svg class="icon-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
        <svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      `;
      document.body.appendChild(toggle);

      toggle.addEventListener('click', toggleMobileNav);
    }

    if (overlay) {
      overlay.addEventListener('click', closeMobileNav);
    }

    // Close on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeMobileNav();
      }
    });

    // Close on resize to desktop
    window.addEventListener('resize', debounce(function() {
      if (window.innerWidth >= 768) {
        closeMobileNav();
      }
    }, 100));
  }

  function toggleMobileNav() {
    const sidebar = document.querySelector('.md-sidebar--primary, nav.sidebar, .nav-sidebar');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const overlay = document.querySelector('.mobile-nav-overlay');

    if (sidebar) {
      sidebar.classList.toggle('open');
    }
    if (menuToggle) {
      menuToggle.classList.toggle('active');
    }
    if (overlay) {
      overlay.classList.toggle('visible');
    }

    // Prevent body scroll when menu is open
    document.body.classList.toggle('nav-open');
  }

  function closeMobileNav() {
    const sidebar = document.querySelector('.md-sidebar--primary, nav.sidebar, .nav-sidebar');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const overlay = document.querySelector('.mobile-nav-overlay');

    if (sidebar) {
      sidebar.classList.remove('open');
    }
    if (menuToggle) {
      menuToggle.classList.remove('active');
    }
    if (overlay) {
      overlay.classList.remove('visible');
    }
    document.body.classList.remove('nav-open');
  }

  // ========================================
  // Table Scroll Detection
  // ========================================

  function initTableScroll() {
    const tables = document.querySelectorAll('.table-responsive, table');

    tables.forEach(function(table) {
      let wrapper = table;

      // Wrap table if not already in a responsive container
      if (!table.classList.contains('table-responsive') && table.tagName === 'TABLE') {
        wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      }

      // Check scroll state
      updateTableScrollState(wrapper);

      // Listen for scroll
      wrapper.addEventListener('scroll', function() {
        updateTableScrollState(wrapper);
      });
    });

    // Update on resize
    window.addEventListener('resize', debounce(function() {
      document.querySelectorAll('.table-responsive').forEach(updateTableScrollState);
    }, 100));
  }

  function updateTableScrollState(wrapper) {
    if (!wrapper) return;

    const scrollLeft = wrapper.scrollLeft;
    const scrollWidth = wrapper.scrollWidth;
    const clientWidth = wrapper.clientWidth;

    // Check if table is scrollable
    const canScroll = scrollWidth > clientWidth;

    // Update classes
    wrapper.classList.toggle('can-scroll', canScroll);
    wrapper.classList.toggle('can-scroll-left', scrollLeft > 0);
    wrapper.classList.toggle('can-scroll-right', scrollLeft < scrollWidth - clientWidth - 1);
  }

  // ========================================
  // Touch Event Optimization
  // ========================================

  function initTouchOptimization() {
    // Detect touch device
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    if (isTouchDevice) {
      document.body.classList.add('touch-device');

      // Fast tap for navigation links
      const navLinks = document.querySelectorAll('.md-nav__link, nav a');
      navLinks.forEach(function(link) {
        link.addEventListener('touchend', function(e) {
          // Prevent double-tap zoom on navigation
          if (e.target.tagName === 'A') {
            e.preventDefault();
            window.location.href = e.target.href;
          }
        });
      });
    } else {
      document.body.classList.add('pointer-device');
    }
  }

  // ========================================
  // Viewport Height Fix (Mobile Safari)
  // ========================================

  function initViewportFix() {
    // Fix for mobile viewport height (100vh issue)
    function setViewportHeight() {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setViewportHeight();

    window.addEventListener('resize', debounce(setViewportHeight, 100));
    window.addEventListener('orientationchange', function() {
      setTimeout(setViewportHeight, 100);
    });
  }

  // ========================================
  // Scroll Progress Indicator
  // ========================================

  function initScrollProgress() {
    let progressBar = document.querySelector('.scroll-progress');

    // Create progress bar if it doesn't exist
    if (!progressBar) {
      progressBar = document.createElement('div');
      progressBar.className = 'scroll-progress';
      document.body.prepend(progressBar);
    }

    function updateProgress() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;

      progressBar.style.width = `${progress}%`;
    }

    window.addEventListener('scroll', throttle(updateProgress, 10));
    updateProgress();
  }

  // ========================================
  // Scroll to Top Button
  // ========================================

  function initScrollToTop() {
    let scrollBtn = document.querySelector('.scroll-to-top');

    // Create button if it doesn't exist
    if (!scrollBtn) {
      scrollBtn = document.createElement('button');
      scrollBtn.className = 'scroll-to-top';
      scrollBtn.setAttribute('aria-label', 'Scroll to top');
      scrollBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 15l-6-6-6 6"/>
        </svg>
      `;
      document.body.appendChild(scrollBtn);
    }

    function toggleButton() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      scrollBtn.classList.toggle('visible', scrollTop > 300);
    }

    scrollBtn.addEventListener('click', function() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });

    window.addEventListener('scroll', throttle(toggleButton, 100));
    toggleButton();
  }

  // ========================================
  // Responsive Image Loading
  // ========================================

  function initResponsiveImages() {
    // Lazy load images
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.classList.add('loaded');
            imageObserver.unobserve(img);
          }
        });
      }, {
        rootMargin: '50px 0px'
      });

      images.forEach(function(img) {
        imageObserver.observe(img);
      });
    } else {
      // Fallback for browsers without IntersectionObserver
      images.forEach(function(img) {
        img.classList.add('loaded');
      });
    }
  }

  // ========================================
  // Utility Functions
  // ========================================

  function debounce(func, wait) {
    let timeout;
    return function executedFunction() {
      const context = this;
      const args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(function() {
        func.apply(context, args);
      }, wait);
    };
  }

  function throttle(func, limit) {
    let inThrottle;
    return function() {
      const context = this;
      const args = arguments;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(function() {
          inThrottle = false;
        }, limit);
      }
    };
  }

  // ========================================
  // Initialize All
  // ========================================

  function init() {
    initMobileNav();
    initTableScroll();
    initTouchOptimization();
    initViewportFix();
    initScrollProgress();
    initScrollToTop();
    initResponsiveImages();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose functions for external use
  window.OpenJudgeResponsive = {
    toggleMobileNav: toggleMobileNav,
    closeMobileNav: closeMobileNav,
    updateTableScrollState: updateTableScrollState
  };

})();
