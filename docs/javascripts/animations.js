/**
 * Animations & Visual Enhancements JavaScript
 * Phase 3: 视觉增强
 *
 * Features:
 * - Scroll-triggered animations
 * - Image lazy loading complete handler
 * - Copy button animations
 * - Smooth scroll behaviors
 */

(function() {
  'use strict';

  // ========================================
  // Configuration
  // ========================================

  const config = {
    scrollThreshold: 0.1, // 10% of element visible triggers animation
    observerOptions: {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    }
  };

  // ========================================
  // Scroll Animations
  // ========================================

  /**
   * Initialize Intersection Observer for scroll animations
   */
  function initScrollAnimations() {
    // Check if browser supports IntersectionObserver
    if (!('IntersectionObserver' in window)) {
      console.log('IntersectionObserver not supported, skipping scroll animations');
      return;
    }

    // Select elements to animate on scroll
    const animateElements = document.querySelectorAll('.fade-in-on-scroll, .slide-in-left, .slide-in-right');

    if (animateElements.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          // Optionally unobserve after animation
          // observer.unobserve(entry.target);
        }
      });
    }, config.observerOptions);

    animateElements.forEach(el => observer.observe(el));
  }

  // ========================================
  // Image Loading
  // ========================================

  /**
   * Handle image lazy loading completion
   */
  function initImageAnimations() {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');

    lazyImages.forEach(img => {
      // If image is already loaded
      if (img.complete) {
        img.classList.add('loaded');
      } else {
        // Wait for image to load
        img.addEventListener('load', function() {
          this.classList.add('loaded');
        });

        // Handle load errors
        img.addEventListener('error', function() {
          console.warn('Failed to load image:', this.src);
          this.classList.add('loaded'); // Remove shimmer even on error
        });
      }
    });
  }

  // ========================================
  // Code Block Enhancements
  // ========================================

  /**
   * Add language badges to code blocks
   */
  function addCodeLanguageBadges() {
    const codeBlocks = document.querySelectorAll('pre code[class*="language-"]');

    codeBlocks.forEach(code => {
      const parentPre = code.closest('pre');
      if (!parentPre || parentPre.querySelector('.language-name')) return;

      // Extract language from class
      const languageClass = Array.from(code.classList).find(cls => cls.startsWith('language-'));
      if (!languageClass) return;

      const language = languageClass.replace('language-', '');

      // Create badge
      const badge = document.createElement('span');
      badge.className = 'language-name';
      badge.textContent = language;

      // Add to parent pre
      parentPre.style.position = 'relative';
      parentPre.appendChild(badge);
    });
  }

  /**
   * Enhanced copy button behavior
   */
  function initCopyButtonAnimations() {
    // Listen for copy events on the document
    document.addEventListener('click', function(e) {
      const copyButton = e.target.closest('.copy-button, .md-clipboard, [data-clipboard-target]');
      if (!copyButton) return;

      // Add copied class for animation
      copyButton.classList.add('copied');

      // Optional: Change button text temporarily
      const originalText = copyButton.textContent;
      if (originalText && !copyButton.querySelector('svg')) {
        copyButton.textContent = '✓ Copied!';
      }

      // Remove after animation
      setTimeout(() => {
        copyButton.classList.remove('copied');
        if (originalText && !copyButton.querySelector('svg')) {
          copyButton.textContent = originalText;
        }
      }, 2000);
    });
  }

  // ========================================
  // Smooth Scroll
  // ========================================

  /**
   * Smooth scroll to anchor links
   */
  function initSmoothScroll() {
    document.addEventListener('click', function(e) {
      const link = e.target.closest('a[href^="#"]');
      if (!link) return;

      const targetId = link.getAttribute('href').slice(1);
      if (!targetId) return;

      const targetElement = document.getElementById(targetId);
      if (!targetElement) return;

      e.preventDefault();

      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });

      // Update URL without jumping
      if (history.pushState) {
        history.pushState(null, null, `#${targetId}`);
      }
    });
  }

  // ========================================
  // Reduced Motion Preference
  // ========================================

  /**
   * Respect user's reduced motion preference
   */
  function handleReducedMotion() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    function applyReducedMotion(e) {
      if (e.matches) {
        document.documentElement.style.setProperty('--rm-transition-fast', '0.01ms');
        document.documentElement.style.setProperty('--rm-transition-normal', '0.01ms');
        document.documentElement.style.setProperty('--rm-transition-slow', '0.01ms');
      } else {
        document.documentElement.style.setProperty('--rm-transition-fast', '0.15s');
        document.documentElement.style.setProperty('--rm-transition-normal', '0.25s');
        document.documentElement.style.setProperty('--rm-transition-slow', '0.4s');
      }
    }

    // Initial check
    applyReducedMotion(prefersReducedMotion);

    // Listen for changes
    prefersReducedMotion.addEventListener('change', applyReducedMotion);
  }

  // ========================================
  // Tab Switching Enhancements
  // ========================================

  /**
   * Add smooth transitions to tab content
   */
  function enhanceTabSwitching() {
    const tabInputs = document.querySelectorAll('.tabbed-set input[type="radio"]');

    tabInputs.forEach(input => {
      input.addEventListener('change', function() {
        const tabbedSet = this.closest('.tabbed-set');
        if (!tabbedSet) return;

        const activeBlock = tabbedSet.querySelector('.tabbed-block--active');
        if (activeBlock) {
          // Add fade-out animation to old content
          activeBlock.style.animation = 'fadeOut 0.15s ease-out';

          setTimeout(() => {
            activeBlock.style.animation = '';
          }, 150);
        }
      });
    });
  }

  // ========================================
  // Collapsible Details Enhancement
  // ========================================

  /**
   * Enhance details/summary elements
   */
  function enhanceDetails() {
    const detailsElements = document.querySelectorAll('details');

    detailsElements.forEach(details => {
      details.addEventListener('toggle', function() {
        if (this.open) {
          // Add expand animation
          const content = Array.from(this.children).find(el => el.tagName !== 'SUMMARY');
          if (content) {
            content.style.animation = 'slideDown 0.25s ease-out';
          }
        }
      });
    });
  }

  // ========================================
  // Navigation Enhancements
  // ========================================

  /**
   * Add active indicator animations to navigation
   */
  function enhanceNavigation() {
    // Highlight current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.md-nav__link, nav a');

    navLinks.forEach(link => {
      const linkPath = new URL(link.href, window.location.origin).pathname;

      if (linkPath === currentPath) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');

        // Ensure parent items are expanded
        let parent = link.closest('.md-nav__item--nested, li.has-children');
        while (parent) {
          const toggle = parent.querySelector('input[type="checkbox"], .md-nav__toggle');
          if (toggle) {
            toggle.checked = true;
          }
          parent = parent.parentElement.closest('.md-nav__item--nested, li.has-children');
        }
      }
    });
  }

  // ========================================
  // Performance: Debounce utility
  // ========================================

  function debounce(func, wait) {
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

  // ========================================
  // Scroll Progress Indicator (Optional)
  // ========================================

  /**
   * Add reading progress bar to top of page
   */
  function initScrollProgress() {
    // Check if progress bar element exists
    let progressBar = document.querySelector('.scroll-progress');

    if (!progressBar) {
      // Create progress bar
      progressBar = document.createElement('div');
      progressBar.className = 'scroll-progress';
      progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: var(--primary, #3b82f6);
        z-index: 9999;
        transition: width 0.1s ease-out;
      `;
      document.body.appendChild(progressBar);
    }

    const updateProgress = debounce(() => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight - windowHeight;
      const scrolled = window.scrollY;
      const progress = (scrolled / documentHeight) * 100;

      progressBar.style.width = `${Math.min(progress, 100)}%`;
    }, 10);

    window.addEventListener('scroll', updateProgress);
    updateProgress(); // Initial call
  }

  // ========================================
  // Initialization
  // ========================================

  /**
   * Initialize all animations when DOM is ready
   */
  function init() {
    console.log('🎨 Initializing OpenJudge animations...');

    // Core animations
    handleReducedMotion();
    initScrollAnimations();
    initImageAnimations();
    initSmoothScroll();

    // UI enhancements
    addCodeLanguageBadges();
    initCopyButtonAnimations();
    enhanceTabSwitching();
    enhanceDetails();
    enhanceNavigation();

    // Optional: Enable scroll progress
    // initScrollProgress();

    console.log('✨ Animations initialized successfully');
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // DOM is already ready
    init();
  }

  // Re-initialize on page navigation (for SPA-like behavior)
  if ('navigation' in window && 'addEventListener' in window.navigation) {
    window.navigation.addEventListener('navigate', () => {
      setTimeout(init, 100);
    });
  }

  // Expose utilities to global scope (optional)
  window.OpenJudgeAnimations = {
    debounce,
    initScrollAnimations,
    initImageAnimations,
    addCodeLanguageBadges
  };

})();
