// HRMS Serene - Sign Up Interactivity & Form Validation

document.addEventListener('DOMContentLoaded', () => {
    // 1. Role Toggle Switcher
    const roleEmployee = document.getElementById('roleEmployee');
    const roleManager = document.getElementById('roleManager');
    const formSubtitle = document.getElementById('formSubtitle');
    const roleValueInput = document.getElementById('roleValue');

    if (roleEmployee && roleManager && formSubtitle && roleValueInput) {
        const setRole = (role) => {
            roleValueInput.value = role;
            if (role === 'employee') {
                roleEmployee.classList.add('active');
                roleManager.classList.remove('active');
                formSubtitle.textContent = 'Join the serenity. Get started with your employee profile.';
            } else {
                roleManager.classList.add('active');
                roleEmployee.classList.remove('active');
                formSubtitle.textContent = 'Step into a more organized management experience. Set up your HR portal today.';
            }
        };

        roleEmployee.addEventListener('click', () => setRole('employee'));
        roleManager.addEventListener('click', () => setRole('hr_manager'));
    }

    // 2. Password Visibility Toggle
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordToggle = document.getElementById('passwordToggle');

    if (passwordInput && confirmPasswordInput && passwordToggle) {
        passwordToggle.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            confirmPasswordInput.type = isPassword ? 'text' : 'password';
            
            const eyeIcon = passwordToggle.querySelector('.eye-icon');
            if (eyeIcon) {
                if (isPassword) {
                    eyeIcon.style.stroke = '#2d5a4c';
                    eyeIcon.innerHTML = `
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                    `;
                } else {
                    eyeIcon.style.stroke = '#6e8277';
                    eyeIcon.innerHTML = `
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                    `;
                }
            }
        });

        // 3. Real-time Password Criteria Check
        const critLength = document.getElementById('critLength');
        const critMix = document.getElementById('critMix');
        const critSpecial = document.getElementById('critSpecial');
        const critMatch = document.getElementById('critMatch');

        const validatePasswords = () => {
            const val = passwordInput.value;
            const confirmVal = confirmPasswordInput.value;

            // Rule 1: Min. 8 characters
            if (val.length >= 8) {
                critLength.classList.add('valid');
            } else {
                critLength.classList.remove('valid');
            }

            // Rule 2: Mix of letters and numbers
            const hasLetter = /[a-zA-Z]/.test(val);
            const hasNumber = /[0-9]/.test(val);
            if (hasLetter && hasNumber) {
                critMix.classList.add('valid');
            } else {
                critMix.classList.remove('valid');
            }

            // Rule 3: 1 special character
            const hasSpecial = /[^a-zA-Z0-9]/.test(val);
            if (hasSpecial) {
                critSpecial.classList.add('valid');
            } else {
                critSpecial.classList.remove('valid');
            }

            // Rule 4: Passwords match
            if (val && val === confirmVal) {
                critMatch.classList.add('valid');
            } else {
                critMatch.classList.remove('valid');
            }
        };

        passwordInput.addEventListener('input', validatePasswords);
        confirmPasswordInput.addEventListener('input', validatePasswords);
    }
});
