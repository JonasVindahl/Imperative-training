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
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
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
});
