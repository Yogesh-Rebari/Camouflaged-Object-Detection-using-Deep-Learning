/**
 * Global Script (static/js/script.js)
 * - Initializes responsive navigation behavior
 * - Provides minimal client-side validation for the index feedback form
 * - Highlights active nav link based on current path
 * - Sets table interactions for model page
 */
document.addEventListener("DOMContentLoaded", () => {
    initNavigationToggle();
    initFeedbackForm();
    highlightActiveNav();
    initTableInteractions();
});

/**
 * initNavigationToggle
 * Handles mobile navigation expand/collapse and accessible aria-expanded state.
 */
function initNavigationToggle() {
    const navToggle = document.querySelector(".nav-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (!navToggle || !navLinks) {
        return;
    }

    navToggle.addEventListener("click", () => {
        navLinks.classList.toggle("open");
        navToggle.setAttribute(
            "aria-expanded",
            navLinks.classList.contains("open").toString()
        );
    });

    navLinks.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            navLinks.classList.remove("open");
            navToggle.setAttribute("aria-expanded", "false");
        });
    });
}

/**
 * initFeedbackForm
 * Lightweight example validation: ensures feedback body is provided.
 * Replace with real submission in Flask (e.g., POST to an endpoint) as needed.
 */
function initFeedbackForm() {
    const feedbackForm = document.getElementById("feedbackForm");
    const feedbackField = document.getElementById("feedback");
    const statusEl = document.getElementById("formStatus");

    if (!feedbackForm || !feedbackField || !statusEl) {
        return;
    }

    feedbackForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const feedback = feedbackField.value.trim();

        if (!feedback) {
            statusEl.textContent = "Please share a short note before submitting.";
            statusEl.style.color = "#f97316";
            feedbackField.focus();
            return;
        }

        statusEl.textContent = "Thank you! Your feedback has been received.";
        statusEl.style.color = "#38bdf8";
        feedbackForm.reset();
    });
}

/**
 * highlightActiveNav
 * Adds 'active' class to header nav link matching the current pathname.
 */
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    document
        .querySelectorAll(".nav-links a")
        .forEach((link) => {
            const isActive = link.getAttribute("href") === currentPath;
            link.classList.toggle("active", isActive);
        });
}

/**
 * initTableInteractions
 * Marks tables as enhanced; hook for future interactive features.
 */
function initTableInteractions() {
    const tables = document.querySelectorAll(".data-table");
    if (!tables.length) {
        return;
    }

    tables.forEach((table) => {
        table.dataset.tableReady = "true";
    });
}

