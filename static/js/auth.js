document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.auth-form');
    if (!form) {
        return;
    }

    const inputs = form.querySelectorAll('input');
    const emailInput = form.querySelector('input[type="email"]');
    const passwordInput = form.querySelector('input[name="password"]');
    const confirmInput = form.querySelector('input[name="confirm_password"]');
    const nameInput = form.querySelector('input[name="name"]');
    const strengthMeter = form.querySelector('.strength-meter');

    const setMessage = (input, message, state) => {
        const messageEl = form.querySelector(`[data-message-for="${input.id}"]`);
        if (!messageEl) {
            return;
        }
        messageEl.textContent = message || '';
        messageEl.classList.toggle('is-error', state === 'error');
        messageEl.classList.toggle('is-success', state === 'success');
        input.classList.toggle('input-invalid', state === 'error');
        input.classList.toggle('input-valid', state === 'success');
    };

    const validateEmailFormat = () => {
        if (!emailInput) {
            return true;
        }
        if (!emailInput.value.trim()) {
            setMessage(emailInput, 'Email is required', 'error');
            return false;
        }
        if (!emailInput.checkValidity()) {
            setMessage(emailInput, 'Enter a valid email address', 'error');
            return false;
        }
        setMessage(emailInput, '', 'success');
        return true;
    };

    const validateName = () => {
        if (!nameInput) {
            return true;
        }
        if (!nameInput.value.trim()) {
            setMessage(nameInput, 'Full name is required', 'error');
            return false;
        }
        setMessage(nameInput, '', 'success');
        return true;
    };

    const passwordStrengthScore = (value) => {
        let score = 0;
        if (value.length >= 6) score += 1;
        if (value.length >= 10) score += 1;
        if (/[A-Z]/.test(value)) score += 1;
        if (/\d/.test(value)) score += 1;
        if (/[^A-Za-z0-9]/.test(value)) score += 1;
        return score;
    };

    const updateStrengthMeter = () => {
        if (!passwordInput || !strengthMeter) {
            return;
        }
        const score = passwordStrengthScore(passwordInput.value);
        const displayScore = Math.min(score, 4);
        strengthMeter.dataset.strength = String(displayScore);
        if (!passwordInput.value) {
            setMessage(passwordInput, '', 'error');
            return;
        }
        if (score <= 1) {
            setMessage(passwordInput, 'Weak password', 'error');
        } else if (score === 2) {
            setMessage(passwordInput, 'Fair password', 'success');
        } else if (score === 3) {
            setMessage(passwordInput, 'Good password', 'success');
        } else {
            setMessage(passwordInput, 'Strong password', 'success');
        }
    };

    const validatePassword = () => {
        if (!passwordInput) {
            return true;
        }
        if (!passwordInput.value.trim()) {
            setMessage(passwordInput, 'Password is required', 'error');
            return false;
        }
        if (passwordInput.value.length < 6) {
            setMessage(passwordInput, 'Use at least 6 characters', 'error');
            return false;
        }
        updateStrengthMeter();
        return true;
    };

    const validateConfirm = () => {
        if (!confirmInput) {
            return true;
        }
        if (!confirmInput.value.trim()) {
            setMessage(confirmInput, 'Confirm your password', 'error');
            return false;
        }
        if (confirmInput.value !== passwordInput.value) {
            setMessage(confirmInput, 'Passwords do not match', 'error');
            return false;
        }
        setMessage(confirmInput, 'Passwords match', 'success');
        return true;
    };

    let emailCheckTimer;
    const checkEmailAvailability = () => {
        if (!emailInput || !validateEmailFormat()) {
            return;
        }
        if (!form.action.endsWith('/register')) {
            return;
        }
        clearTimeout(emailCheckTimer);
        emailCheckTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/auth/check-email?email=${encodeURIComponent(emailInput.value)}`);
                const result = await response.json();
                if (!result.available) {
                    setMessage(emailInput, 'Email already registered', 'error');
                } else {
                    setMessage(emailInput, 'Email available', 'success');
                }
            } catch (error) {
                setMessage(emailInput, '', 'success');
            }
        }, 300);
    };

    inputs.forEach((input) => {
        input.addEventListener('blur', () => {
            if (input === emailInput) {
                validateEmailFormat();
                checkEmailAvailability();
            } else if (input === nameInput) {
                validateName();
            } else if (input === passwordInput) {
                validatePassword();
            } else if (input === confirmInput) {
                validateConfirm();
            }
        });
        input.addEventListener('input', () => {
            if (input === emailInput) {
                validateEmailFormat();
            } else if (input === passwordInput) {
                updateStrengthMeter();
                if (confirmInput && confirmInput.value) {
                    validateConfirm();
                }
            } else if (input === confirmInput) {
                validateConfirm();
            } else if (input === nameInput) {
                validateName();
            }
        });
    });

    form.addEventListener('submit', (event) => {
        const valid = [
            validateName(),
            validateEmailFormat(),
            validatePassword(),
            validateConfirm()
        ].every(Boolean);
        if (!valid) {
            event.preventDefault();
        }
    });

    document.querySelectorAll('.password-toggle').forEach((toggle) => {
        toggle.addEventListener('click', () => {
            const targetId = toggle.getAttribute('data-target');
            const target = document.getElementById(targetId);
            if (!target) {
                return;
            }
            const isHidden = target.type === 'password';
            target.type = isHidden ? 'text' : 'password';
            toggle.textContent = isHidden ? 'Hide' : 'Show';
            toggle.setAttribute('aria-pressed', String(isHidden));
        });
    });
});
