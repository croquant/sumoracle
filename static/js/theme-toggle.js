(() => {
    const storedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.dataset.bsTheme = storedTheme || systemTheme;

    window.toggleDarkMode = () => {
        const current = document.documentElement.dataset.bsTheme;
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.bsTheme = next;
        localStorage.setItem('theme', next);
    };
})();
