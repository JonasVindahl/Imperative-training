document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.practice-form');
    if (!form) {
        return;
    }

    const categorySelect = form.querySelector('select[name="category"]');
    const messageEl = form.querySelector('[data-message-for="category"]');

    const setMessage = (message, isError) => {
        if (!messageEl) {
            return;
        }
        messageEl.textContent = message;
        messageEl.classList.toggle('is-error', Boolean(isError));
        messageEl.classList.toggle('is-success', !isError && Boolean(message));
    };

    if (categorySelect) {
        categorySelect.addEventListener('change', () => {
            if (categorySelect.value) {
                setMessage('', false);
            }
        });
    }

    form.addEventListener('submit', (event) => {
        if (!categorySelect) {
            return;
        }
        if (!categorySelect.value) {
            event.preventDefault();
            setMessage('Please select a category before starting.', true);
            categorySelect.focus();
        }
    });
});
