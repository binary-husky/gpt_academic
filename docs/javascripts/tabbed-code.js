/**
 * Tabbed Code Blocks - JavaScript Enhancement for shadcn/ui theme
 * Provides fallback functionality for pymdownx.tabbed alternate_style
 */

(function() {
  'use strict';

  function initTabbedSets() {
    // Find all tabbed sets
    const tabbedSets = document.querySelectorAll('.tabbed-set.tabbed-alternate');

    tabbedSets.forEach(function(tabbedSet) {
      const inputs = tabbedSet.querySelectorAll(':scope > input[type="radio"]');
      const labels = tabbedSet.querySelectorAll(':scope > .tabbed-labels > label');
      const blocks = tabbedSet.querySelectorAll(':scope > .tabbed-content > .tabbed-block');

      // Function to update active state
      function updateActiveState() {
        let activeIndex = 0;

        // Find which input is checked
        inputs.forEach(function(input, index) {
          if (input.checked) {
            activeIndex = index;
          }
        });

        // Update labels
        labels.forEach(function(label, index) {
          if (index === activeIndex) {
            label.classList.add('tabbed-label--active');
            label.setAttribute('data-active', 'true');
          } else {
            label.classList.remove('tabbed-label--active');
            label.setAttribute('data-active', 'false');
          }
        });

        // Update content blocks
        blocks.forEach(function(block, index) {
          if (index === activeIndex) {
            block.style.display = 'block';
            block.classList.add('tabbed-block--active');
          } else {
            block.style.display = 'none';
            block.classList.remove('tabbed-block--active');
          }
        });
      }

      // Listen for changes on radio inputs
      inputs.forEach(function(input) {
        input.addEventListener('change', updateActiveState);
      });

      // Also handle label clicks directly (backup for CSS label-for behavior)
      labels.forEach(function(label, index) {
        label.addEventListener('click', function(e) {
          if (inputs[index]) {
            inputs[index].checked = true;
            // Trigger change event
            inputs[index].dispatchEvent(new Event('change'));
          }
        });
      });

      // Initialize state
      updateActiveState();

      // Add copy button to tabbed code blocks
      addCopyButtonToTabbedSet(tabbedSet);
    });
  }

  function addCopyButtonToTabbedSet(tabbedSet) {
    // Check if copy button already exists
    if (tabbedSet.querySelector('.copy-button')) {
      return;
    }

    // Find the labels container
    const labelsContainer = tabbedSet.querySelector('.tabbed-labels');
    if (!labelsContainer) return;

    // Create copy button
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-button';
    copyButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
    copyButton.setAttribute('aria-label', 'Copy code');
    copyButton.setAttribute('title', 'Copy code');

    // Add click handler
    copyButton.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();

      // Find the active code block
      const activeBlock = tabbedSet.querySelector('.tabbed-block--active');
      if (!activeBlock) return;

      // Get code content
      const codeElement = activeBlock.querySelector('pre code') || activeBlock.querySelector('code');
      if (!codeElement) return;

      // Copy to clipboard
      const code = codeElement.textContent;

      // Use modern clipboard API
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(code).then(function() {
          showCopiedState(copyButton);
        }).catch(function(err) {
          console.error('Failed to copy:', err);
          fallbackCopyTextToClipboard(code, copyButton);
        });
      } else {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(code, copyButton);
      }
    });

    // Insert copy button into labels container
    labelsContainer.appendChild(copyButton);
  }

  function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      const successful = document.execCommand('copy');
      if (successful) {
        showCopiedState(button);
      }
    } catch (err) {
      console.error('Fallback: Failed to copy', err);
    }

    document.body.removeChild(textArea);
  }

  function showCopiedState(button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    button.classList.add('copied');

    setTimeout(function() {
      button.innerHTML = originalHTML;
      button.classList.remove('copied');
    }, 2000);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabbedSets);
  } else {
    initTabbedSets();
  }

  // Also re-initialize on navigation (for SPA-like behavior)
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() {
      initTabbedSets();
    });
  }

  // Export for manual re-initialization if needed
  window.initTabbedSets = initTabbedSets;
})();
