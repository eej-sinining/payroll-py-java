
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