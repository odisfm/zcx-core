const repoLink = document.querySelector("[data-md-component='source']")
if (repoLink) {
    repoLink.onclick = () => {
        umami.track('Repo link header')
    };
}

const socialLinks = document.querySelectorAll('a.md-social__link')
for (const link of socialLinks) {
    link.addEventListener("click", () => {
        umami.track("social_link_click", { destination: link.title })
    })
}

const downloadLink = document.querySelector('header md-tabs__item[href="https://github.com/odisfm/zcx-core/releases/latest"]')
if (downloadLink) {
    downloadLink.addEventListener("click", () => umami.track("download_link_click"))
}

const themeToggle = document.querySelector('header .md-header__option[data-md-component="palette"]')
themeToggle.addEventListener("click", () => {
    const newTheme = document.body.dataset.mdColorScheme
    umami.track("theme_change", { theme: newTheme })
})
