/**
 * Code Copy Button - Universal code block copy functionality
 * Adds copy buttons to all code blocks (non-tabbed)
 */

(function() {
  'use strict';

  function initCodeCopyButtons() {
    // Find all code blocks that don't already have a copy button
    // Exclude tabbed code blocks (handled by tabbed-code.js)
    const codeBlocks = document.querySelectorAll('article pre, .prose pre, .md-typeset pre');

    codeBlocks.forEach(function(preElement) {
      // Skip if already has a copy button
      if (preElement.querySelector('.copy-button')) {
        return;
      }

      // Skip if it's inside a tabbed set
      if (preElement.closest('.tabbed-set')) {
        return;
      }

      // Skip if it's a tabbed block
      if (preElement.classList.contains('tabbed-block') || preElement.closest('.tabbed-block')) {
        return;
      }

      // Create copy button
      const copyButton = document.createElement('button');
      copyButton.className = 'copy-button code-copy-btn';
      copyButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
      copyButton.setAttribute('aria-label', 'Copy code');
      copyButton.setAttribute('title', 'Copy code');

      // Add click handler
      copyButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Get code content
        const codeElement = preElement.querySelector('code');
        if (!codeElement) return;

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
          // Fallback for older browsers or non-secure contexts
          fallbackCopyTextToClipboard(code, copyButton);
        }
      });

      // Insert copy button into pre element
      preElement.style.position = 'relative';
      preElement.appendChild(copyButton);
    });

    // Also handle .highlight wrapper (Pygments)
    const highlightBlocks = document.querySelectorAll('article .highlight, .prose .highlight, .md-typeset .highlight');

    highlightBlocks.forEach(function(highlightElement) {
      // Skip if already has a copy button
      if (highlightElement.querySelector('.copy-button')) {
        return;
      }

      // Skip if it's inside a tabbed set
      if (highlightElement.closest('.tabbed-set')) {
        return;
      }

      // Skip if it's a tabbed block
      if (highlightElement.classList.contains('tabbed-block') || highlightElement.closest('.tabbed-block')) {
        return;
      }

      // Create copy button
      const copyButton = document.createElement('button');
      copyButton.className = 'copy-button code-copy-btn';
      copyButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
      copyButton.setAttribute('aria-label', 'Copy code');
      copyButton.setAttribute('title', 'Copy code');

      // Add click handler
      copyButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Get code content
        const codeElement = highlightElement.querySelector('pre code') || highlightElement.querySelector('code');
        if (!codeElement) return;

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
          // Fallback for older browsers or non-secure contexts
          fallbackCopyTextToClipboard(code, copyButton);
        }
      });

      // Insert copy button into highlight element
      highlightElement.style.position = 'relative';
      highlightElement.appendChild(copyButton);
    });
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
    document.addEventListener('DOMContentLoaded', initCodeCopyButtons);
  } else {
    initCodeCopyButtons();
  }

  // Also re-initialize on navigation (for SPA-like behavior in MkDocs Material)
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() {
      // Use setTimeout to ensure DOM is fully updated
      setTimeout(initCodeCopyButtons, 100);
    });
  }

  // Export for manual re-initialization if needed
  window.initCodeCopyButtons = initCodeCopyButtons;
})();
