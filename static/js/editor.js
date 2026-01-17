// Code Editor and Practice Interface JavaScript

// Auto-resize textarea elements
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Add tab support for code editor
    const codeEditor = document.getElementById('code-editor');
    if (codeEditor) {
        codeEditor.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;

                // Insert 4 spaces
                this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);

                // Move cursor
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    }

    // Add line numbers to code blocks
    const codeBlocks = document.querySelectorAll('[data-line-numbers]');
    codeBlocks.forEach(container => {
        const target = container.querySelector('code') || container;
        if (window.hljs && target.tagName === 'CODE') {
            window.hljs.highlightElement(target);
        }
        const lines = target.innerHTML.split('\n');
        const numberedLines = lines.map((line, index) => {
            return `<span class="code-line"><span class="line-number">${index + 1}</span>${line || ''}</span>`;
        });
        target.innerHTML = numberedLines.join('\n');
    });
});

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.toast-close');
        let timeoutId = null;

        const dismiss = () => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        };

        const scheduleDismiss = (delay) => {
            timeoutId = setTimeout(dismiss, delay);
        };

        if (closeBtn) {
            closeBtn.addEventListener('click', dismiss);
        }

        alert.addEventListener('mouseenter', () => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
        });
        alert.addEventListener('mouseleave', () => {
            scheduleDismiss(3000);
        });

        scheduleDismiss(7000);
    });
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--error-color)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });

    return isValid;
}

// Progress bar animation
document.addEventListener('DOMContentLoaded', function() {
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(fill => {
        const width = fill.style.width;
        fill.style.width = '0%';
        setTimeout(() => {
            fill.style.width = width;
        }, 100);
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter or Cmd+Enter to submit answer (when in practice)
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const submitBtn = document.querySelector('button[onclick="submitAnswer()"]');
        if (submitBtn) {
            e.preventDefault();
            submitAnswer();
        }
    }

    const activeTag = document.activeElement ? document.activeElement.tagName : '';
    const isTypingField = ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeTag);

    // Number keys 1-4 select multiple choice answers
    const isNumberShortcut = ['1', '2', '3', '4'].includes(e.key);
    const isNumpadShortcut = ['Numpad1', 'Numpad2', 'Numpad3', 'Numpad4'].includes(e.code);

    if (!isTypingField && (isNumberShortcut || isNumpadShortcut)) {
        const radioButtons = document.getElementsByName('answer');
        const key = isNumberShortcut ? e.key : e.code.replace('Numpad', '');
        const index = parseInt(key, 10) - 1;
        if (radioButtons.length > index && radioButtons[index]) {
            e.preventDefault();
            radioButtons[index].checked = true;
            radioButtons[index].dispatchEvent(new Event('change'));
        }
    }

    // Enter to submit when not typing
    if (!isTypingField && e.key === 'Enter' && !(e.ctrlKey || e.metaKey)) {
        const submitBtn = document.querySelector('button[onclick="submitAnswer()"]');
        if (submitBtn && !submitBtn.disabled) {
            e.preventDefault();
            submitAnswer();
        }
    }
});
