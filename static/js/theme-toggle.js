(() => {
    const html = document.documentElement;
    let mode = localStorage.getItem('theme') || 'auto';

    function applyTheme() {
        const system = window.matchMedia(
            '(prefers-color-scheme: dark)'
        ).matches
            ? 'dark'
            : 'light';
        html.dataset.bsTheme = mode === 'auto' ? system : mode;
    }

    const icon = document.querySelector('#theme-toggle i');

    function updateIcon() {
        icon.classList.toggle('bi-circle-half', mode === 'auto');
        icon.classList.toggle('bi-moon', mode === 'dark');
        icon.classList.toggle('bi-sun', mode === 'light');
    }

    window.toggleTheme = () => {
        if (mode === 'auto') {
            mode = 'dark';
        } else if (mode === 'dark') {
            mode = 'light';
        } else {
            mode = 'auto';
        }
        localStorage.setItem('theme', mode);
        applyTheme();
        updateIcon();
    };

    applyTheme();
    updateIcon();
})();
