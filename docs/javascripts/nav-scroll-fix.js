/**
 * Navigation Scroll Position Preservation
 *
 * This script preserves the sidebar scroll position when navigating between pages.
 * Without this, clicking a link in the scrolled sidebar would reset it to the top.
 */

(function() {
  'use strict';

  const STORAGE_KEY = 'open_judge-sidebar-scroll';
  const SIDEBAR_SELECTORS = [
    '[data-slot="sidebar-content"]',  // Current theme's sidebar container
    '[data-sidebar="content"]',       // Alternative selector
    '.md-sidebar--primary',           // MkDocs Material theme
    'nav.sidebar',
    '.md-sidebar',
    '.nav-sidebar',
    'aside.sidebar'
  ];

  /**
   * Get the primary sidebar element
   */
  function getSidebar() {
    for (const selector of SIDEBAR_SELECTORS) {
      const sidebar = document.querySelector(selector);
      if (sidebar) {
        return sidebar;
      }
    }
    return null;
  }

  /**
   * Restore scroll position instantly without smooth scrolling flicker.
   */
  function setScrollTopInstant(sidebar, position) {
    if (!sidebar) return;
    const originalBehavior = sidebar.style.scrollBehavior;
    sidebar.style.scrollBehavior = 'auto';
    sidebar.scrollTop = position;
    // Restore original behavior on next frame to keep smooth scrolling elsewhere.
    requestAnimationFrame(() => {
      if (originalBehavior) {
        sidebar.style.scrollBehavior = originalBehavior;
      } else {
        sidebar.style.removeProperty('scroll-behavior');
      }
    });
  }

  /**
   * Save sidebar scroll position to sessionStorage
   */
  function saveSidebarScroll() {
    const sidebar = getSidebar();
    if (sidebar) {
      try {
        const scrollData = {
          position: sidebar.scrollTop,
          timestamp: Date.now()
        };
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(scrollData));
      } catch (e) {
        console.warn('Failed to save sidebar scroll position:', e);
      }
    }
  }

  /**
   * Restore sidebar scroll position from sessionStorage
   */
  function restoreSidebarScroll() {
    const sidebar = getSidebar();
    if (!sidebar) return;

    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const scrollData = JSON.parse(stored);

        // Only restore if saved within the last 5 minutes
        const age = Date.now() - scrollData.timestamp;
        if (age < 5 * 60 * 1000) {
          // Use requestAnimationFrame to ensure DOM is ready
          requestAnimationFrame(() => {
            setScrollTopInstant(sidebar, scrollData.position);
          });
        } else {
          // Clear old data
          sessionStorage.removeItem(STORAGE_KEY);
        }
      }
    } catch (e) {
      console.warn('Failed to restore sidebar scroll position:', e);
    }
  }

  /**
   * Initialize scroll position preservation
   */
  function init() {
    // Restore scroll position on page load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', restoreSidebarScroll);
    } else {
      restoreSidebarScroll();
    }

    // Save scroll position before navigation
    window.addEventListener('beforeunload', saveSidebarScroll);

    // Save scroll position when clicking sidebar links
    document.addEventListener('click', function(e) {
      const link = e.target.closest('a');
      if (!link) return;

      // Check if the link is inside the sidebar
      const sidebar = getSidebar();
      if (sidebar && sidebar.contains(link)) {
        // Save current scroll position
        saveSidebarScroll();
      }
    });

    // Periodically save scroll position while user scrolls
    const sidebar = getSidebar();
    if (sidebar) {
      let scrollTimeout;
      sidebar.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(saveSidebarScroll, 150);
      });
    }
  }

  // Initialize when script loads
  init();

})();
