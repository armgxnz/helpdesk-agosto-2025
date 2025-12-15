// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {

    // Botón de registro (solo existe en algunas páginas)
    const btnRegister = document.getElementById('btn-register');
    if (btnRegister) {
        btnRegister.addEventListener('click', function() {
            window.location.href = '/register';
        });
    }

    const closeButtons = document.querySelectorAll('.alert .close, .alert .btn-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });

    const toggleBtn = document.getElementById('toggle-password');
    const passwordField = document.getElementById('password');
    const eyeIcon = document.getElementById('eye-icon');
    
    if (toggleBtn && passwordField && eyeIcon) {
        toggleBtn.addEventListener('click', function() {
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                eyeIcon.className = 'bi bi-eye-slash';
            } else {
                passwordField.type = 'password';
                eyeIcon.className = 'bi bi-eye';
            }
        });
    }
 
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Signing in...';
            }
        });
    }

    const emailField = document.getElementById('email');
    if (emailField) {
        emailField.focus();
    }

    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });


    // Password match checker
    function checkPasswordMatch() {
        const password = passwordField.value;
        const confirmPassword = confirmField.value;
        const errorMsg = document.getElementById('password-match-error');
        const successMsg = document.getElementById('password-match-success');
        
        if (confirmPassword.length === 0) {
            errorMsg.classList.add('d-none');
            successMsg.classList.add('d-none');
            return;
        }
        
        if (password !== confirmPassword) {
            errorMsg.classList.remove('d-none');
            successMsg.classList.add('d-none');
        } else {
            errorMsg.classList.add('d-none');
            successMsg.classList.remove('d-none');
        }
    }

    if (passwordField && confirmField) {
        passwordField.addEventListener('input', checkPasswordMatch);
        confirmField.addEventListener('input', checkPasswordMatch);
    }

    // Form validation
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = passwordField.value;
            const confirmPassword = confirmField.value;
            const termsCheckbox = document.getElementById('terms');
            
            // Check password length
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long!');
                return false;
            }
            
            // Check password match
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            // Check terms agreement
            if (!termsCheckbox.checked) {
                e.preventDefault();
                alert('You must agree to the Terms & Conditions!');
                return false;
            }
            
            // Loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Creating account...';
            }
        });
    }
    
});