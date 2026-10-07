/* Progressive enhancements only: every result is present in the static HTML. */
(() => {
  "use strict";

  const tables = [...document.querySelectorAll("details.data-table")];
  const toggleButton = document.getElementById("toggle-tables");
  const printButton = document.getElementById("print-report");
  const status = document.getElementById("report-status");
  if (!toggleButton || !printButton || !status) return;

  document.documentElement.classList.add("enhanced");

  const updateButton = () => {
    const allOpen = tables.every((table) => table.open);
    toggleButton.setAttribute("aria-pressed", String(allOpen));
    toggleButton.textContent = allOpen ? "Sbalit tabulky" : "Rozbalit tabulky";
  };

  tables.forEach((table) => table.addEventListener("toggle", updateButton));
  toggleButton.addEventListener("click", () => {
    const open = !tables.every((table) => table.open);
    tables.forEach((table) => { table.open = open; });
    updateButton();
    status.textContent = open
      ? `Rozbaleno všech ${tables.length} datových tabulek.`
      : "Datové tabulky jsou sbalené; grafy a texty zůstávají zobrazené.";
  });

  // Preserve the reader's expanded tables after printing, including cancellation.
  let beforePrint = null;
  window.addEventListener("beforeprint", () => {
    if (beforePrint !== null) return;
    beforePrint = tables.map((table) => table.open);
    tables.forEach((table) => { table.open = true; });
  });
  window.addEventListener("afterprint", () => {
    if (beforePrint === null) return;
    tables.forEach((table, index) => { table.open = beforePrint[index]; });
    beforePrint = null;
    updateButton();
  });
  printButton.addEventListener("click", () => window.print());

  const topicLinks = [...document.querySelectorAll(".topic-navigation a")];
  const topics = [...document.querySelectorAll("[data-topic]")];
  const setActive = (id) => {
    topicLinks.forEach((link) => {
      if (link.getAttribute("href") === `#${id}`) {
        link.setAttribute("aria-current", "location");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  };

  const reflectHash = () => {
    let id;
    try {
      id = decodeURIComponent(window.location.hash.slice(1));
    } catch {
      return;
    }
    const target = document.getElementById(id);
    const topic = target?.closest("[data-topic]");
    if (topic) setActive(topic.id);
  };
  window.addEventListener("hashchange", reflectHash);
  reflectHash();

  // Scrollspy never moves focus or changes the URL while the reader scrolls.
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting);
      if (visible.length) {
        visible.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        setActive(visible[0].target.id);
      }
    }, { rootMargin: "-180px 0px -55% 0px", threshold: 0 });
    topics.forEach((topic) => observer.observe(topic));
  }
})();