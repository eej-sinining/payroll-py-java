
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
}
// Set up theme toggle buttons
const themeButtons = document.querySelectorAll('[data-bs-theme-value]');
themeButtons.forEach(button => {
    button.addEventListener('click', () => {
    const themeValue = button.getAttribute('data-bs-theme-value');
    document.documentElement.setAttribute('data-bs-theme', themeValue);
    localStorage.setItem('theme', themeValue);
    });
});


//home functions
const signupButton = document.getElementById('signup-button'),
loginButton = document.getElementById('login-button'),
userForms = document.getElementById('user_options-forms')

/**
* Add event listener to the "Sign Up" button
*/
signupButton.addEventListener('click', () => {
userForms.classList.remove('bounceRight')
userForms.classList.add('bounceLeft')
}, false)

/**
* Add event listener to the "Login" button
*/
loginButton.addEventListener('click', () => {
userForms.classList.remove('bounceLeft')
userForms.classList.add('bounceRight')
}, false)

