document.addEventListener("DOMContentLoaded", function () {
  const tabs = Array.from(document.querySelectorAll("[data-auth-tab]"));
  const panels = Array.from(document.querySelectorAll("[data-auth-panel]"));
  const title = document.getElementById("auth-title");
  const description = document.getElementById("auth-description");

  function showPanel(name) {
    panels.forEach(function (panel) {
      panel.hidden = panel.dataset.authPanel !== name;
    });

    document.querySelectorAll(".auth-tab").forEach(function (tab) {
      const selected = tab.dataset.authTab === name;
      tab.classList.toggle("is-active", selected);
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });

    title.textContent = name === "signin" ? "Welcome back" : "Join TrailerTV";
    description.textContent =
      name === "signin"
        ? "Sign in to continue to your movie discovery space."
        : "Create an account to save reviews and shape your recommendations.";
  }

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      showPanel(tab.dataset.authTab);
    });

    tab.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        const nextPanel = tab.dataset.authTab === "signin" ? "signup" : "signin";
        const nextTab = document.querySelector(
          `.auth-tab[data-auth-tab="${nextPanel}"]`,
        );
        showPanel(nextPanel);
        nextTab.focus();
      }
    });
  });
});
