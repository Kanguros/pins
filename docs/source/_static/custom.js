/* Custom JavaScript for Policy Inspector Documentation */

document.addEventListener("DOMContentLoaded", function () {
    // Add copy buttons to code blocks
    addCopyButtons();

    // Improve navigation
    improveNavigation();

    // Add analytics if configured
    if (window.ga) {
        trackPageViews();
    }

    // Improve search functionality
    enhanceSearch();
});

function addCopyButtons() {
    // Add copy buttons to all code blocks
    const codeBlocks = document.querySelectorAll(".highlight pre");

    codeBlocks.forEach(function (block) {
        const button = document.createElement("button");
        button.className = "copy-button";
        button.textContent = "Copy";
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: #2980B9;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s;
        `;

        button.addEventListener("mouseenter", function () {
            button.style.opacity = "1";
        });

        button.addEventListener("mouseleave", function () {
            button.style.opacity = "0.7";
        });

        button.addEventListener("click", function () {
            const code = block.textContent;
            navigator.clipboard.writeText(code).then(function () {
                button.textContent = "Copied!";
                setTimeout(function () {
                    button.textContent = "Copy";
                }, 2000);
            });
        });

        // Make parent container relative for absolute positioning
        const container = block.parentElement;
        if (container.style.position !== "relative") {
            container.style.position = "relative";
        }

        container.appendChild(button);
    });
}

function improveNavigation() {
    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }
        });
    });

    // Highlight current section in navigation
    const sections = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
    const navLinks = document.querySelectorAll(".wy-menu-vertical a");

    function highlightCurrentSection() {
        let currentSection = null;
        const scrollPosition = window.scrollY + 100;

        sections.forEach(function (section) {
            if (section.offsetTop <= scrollPosition) {
                currentSection = section;
            }
        });

        if (currentSection) {
            const currentId = currentSection.id;
            navLinks.forEach(function (link) {
                link.classList.remove("current");
                if (link.getAttribute("href") === "#" + currentId) {
                    link.classList.add("current");
                }
            });
        }
    }

    window.addEventListener("scroll", highlightCurrentSection);
    highlightCurrentSection(); // Initial call
}

function trackPageViews() {
    // Track page views for analytics
    if (typeof ga !== "undefined") {
        ga("send", "pageview", window.location.pathname);
    }

    // Track clicks on external links
    const externalLinks = document.querySelectorAll('a[href^="http"]');
    externalLinks.forEach(function (link) {
        if (!link.href.includes(window.location.hostname)) {
            link.addEventListener("click", function () {
                if (typeof ga !== "undefined") {
                    ga("send", "event", "External Link", "Click", link.href);
                }
            });
        }
    });
}

function enhanceSearch() {
    // Improve search result highlighting
    const searchResults = document.querySelectorAll(".search li");

    searchResults.forEach(function (result) {
        result.addEventListener("mouseenter", function () {
            this.style.backgroundColor = "#f5f5f5";
        });

        result.addEventListener("mouseleave", function () {
            this.style.backgroundColor = "";
        });
    });

    // Add keyboard navigation to search
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                const firstResult = document.querySelector(
                    ".search li:first-child a",
                );
                if (firstResult) {
                    firstResult.click();
                }
            }
        });
    }
}

// Add version warning for older versions
function addVersionWarning() {
    const currentVersion = document.querySelector(".rst-current-version");
    if (currentVersion && !currentVersion.textContent.includes("latest")) {
        const warning = document.createElement("div");
        warning.innerHTML = `
            <div style="background: #ff9800; color: white; padding: 10px; text-align: center; font-weight: bold;">
                ⚠️ You are viewing documentation for an older version. 
                <a href="/en/latest/" style="color: white; text-decoration: underline;">
                    View latest version
                </a>
            </div>
        `;
        document.body.insertBefore(warning, document.body.firstChild);
    }
}

// Initialize version warning
addVersionWarning();
