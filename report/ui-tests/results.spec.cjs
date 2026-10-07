const { test, expect } = require("@playwright/test");
const { default: AxeBuilder } = require("@axe-core/playwright");

test("all questions, original categories and independent bases are visible", async ({ page }, testInfo) => {
  const errors = [];
  const requests = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => requests.push(request.url()));
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Všechny výsledky");
  await expect(page.locator("[data-question]")).toHaveCount(31);
  await expect(page.locator("[data-text-key]")).toHaveCount(17);
  await expect(page.locator("#g1b")).toHaveAttribute("data-n", "34");
  await expect(page.locator("#g1c")).toHaveAttribute("data-n", "51");
  await expect(page.locator("#e4a")).toHaveAttribute("data-n", "22");
  await expect(page.locator("#n5 .chart-row")).toHaveCount(20);
  await expect(page.locator('#n5 .chart-row[data-value="Budíkovice"]')).toHaveAttribute("data-count", "0");
  await expect(page.locator('#n5 .chart-row[data-value="Pocoucov"]')).toHaveAttribute("data-count", "1");
  await expect(page.locator("#n3 .chart-row")).toHaveCount(5);
  await expect(page.locator("#n4 .chart-row")).toHaveCount(7);
  expect(requests.filter((url) => /(?:backup\/|report\/|\.db|save\.php|stats\.php|admin\.php)/.test(url))).toEqual([]);
  expect(requests.filter((url) => /^https?:/.test(url) && !url.startsWith("http://127.0.0.1:8765/"))).toEqual([]);
  expect(errors).toEqual([]);
  await page.screenshot({ path: testInfo.outputPath("desktop-overview.png") });
});

test("all tables can expand and retain all five data columns", async ({ page }) => {
  await page.goto("/index.html");
  await page.getByRole("button", { name: "Rozbalit tabulky" }).click();
  await expect(page.locator("details.data-table[open]")).toHaveCount(31);
  await expect(page.getByRole("button", { name: "Sbalit tabulky" })).toHaveAttribute("aria-pressed", "true");
  const stressed = page.locator("#tabulka-n3 tbody tr").filter({ hasText: "Tíživá" });
  await expect(stressed.locator("td")).toHaveText(["1", "0,7 %", "1", "0,7 %"]);
  await expect(page.locator("#tabulka-n5 tbody tr")).toHaveCount(20);
  await page.getByRole("button", { name: "Sbalit tabulky" }).click();
  await expect(page.locator("details.data-table[open]")).toHaveCount(0);
  await page.locator("#tabulka-e4a summary").click();
  await expect(page.locator("#tabulka-e4a")).toHaveAttribute("open", "");
  await expect(page.locator("#tabulka-e4a tbody tr")).toHaveCount(3);
});

test("refined card hierarchy, answer labels and disclosure icons are consistent", async ({ page }, testInfo) => {
  await page.goto("/index.html");
  await expect(page.locator(".survey-counts dt").first()).toHaveText("odpovědí celkem");
  await expect(page.locator(".intro-copy")).toContainText("Získali jsme celkem 187 odpovědí.");
  await expect(page.locator(".intro-copy")).toContainText("zajímavý vhled do života obyvatel našeho města");
  await expect(page.locator('#a2 .chart-row[data-value="živá"] .chart-label')).toHaveText("Živá");
  await expect(page.locator('#e1 .chart-row[data-value="mhd"] .chart-label')).toHaveText("MHD");
  await expect(page.locator("#l3 h3")).toContainText("v dotazníku");

  expect(await page.locator("[data-question]").evaluateAll((cards) => cards.every((card) => card.lastElementChild.matches("details.data-table")))).toBe(true);
  expect(await page.locator(".chart-note").evaluateAll((notes) => notes.every((note) => note.previousElementSibling.tagName === "H3"))).toBe(true);
  expect(await page.locator(".chart-label, tbody th").evaluateAll((labels) => labels.every((label) => {
    const firstLetter = label.textContent.match(/\p{L}/u)?.[0];
    return !firstLetter || firstLetter === firstLetter.toLocaleUpperCase("cs");
  }))).toBe(true);

  const supplementary = page.locator("#b2-other");
  await expect(supplementary.locator(".supplement-heading")).toContainText("Jiné odpovědi · shrnutí");
  await expect(supplementary.locator(".question-meta")).toHaveCount(0);
  const compactSize = await supplementary.locator(".summary-prose").evaluate((node) => parseFloat(getComputedStyle(node).fontSize));
  const standaloneSize = await page.locator("#c1b .summary-prose").evaluate((node) => parseFloat(getComputedStyle(node).fontSize));
  expect(compactSize).toBeLessThan(standaloneSize);

  await expect(page.locator("#tabulka-b2 .table-chevron")).toBeVisible();
  await expect(page.locator("#tabulka-b2 .table-close")).not.toBeVisible();
  await page.locator("#b2").screenshot({ path: testInfo.outputPath("refined-card-desktop.png") });
  await page.locator("#tabulka-b2 summary").click();
  await expect(page.locator("#tabulka-b2 .table-chevron")).not.toBeVisible();
  await expect(page.locator("#tabulka-b2 .table-close")).toBeVisible();
  await expect(page.locator("#tabulka-b2 tbody th").first()).toHaveText("Více obchodů, kaváren a služeb");
  await page.locator("#tabulka-b2 summary").click();

  await page.setViewportSize({ width: 390, height: 844 });
  const mobileCompactSize = await supplementary.locator(".summary-prose").evaluate((node) => parseFloat(getComputedStyle(node).fontSize));
  const mobileStandaloneSize = await page.locator("#c1b .summary-prose").evaluate((node) => parseFloat(getComputedStyle(node).fontSize));
  expect(mobileCompactSize).toBeLessThan(mobileStandaloneSize);
  await page.locator("#b2").screenshot({ path: testInfo.outputPath("refined-card-mobile.png") });
});

test("topic navigation and direct question links do not hide the target", async ({ page }) => {
  await page.goto("/index.html#n3");
  await expect(page.locator('#n3 h3')).toBeInViewport();
  const headerBottom = await page.locator(".site-header").evaluate((node) => node.getBoundingClientRect().bottom);
  const targetTop = await page.locator("#n3").evaluate((node) => node.getBoundingClientRect().top);
  expect(targetTop).toBeGreaterThanOrEqual(headerBottom - 1);
  await page.getByRole("navigation", { name: "Témata výsledků" }).getByRole("link", { name: "Doprava a veřejný prostor" }).click();
  await expect(page).toHaveURL(/#doprava$/);
  await expect(page.locator("#heading-doprava")).toBeInViewport();
  await expect(page.locator('.topic-navigation a[aria-current="location"]')).toHaveAttribute("href", "#doprava");
});

for (const width of [320, 390, 768]) {
  test(`no horizontal page overflow at ${width}px and tables scroll locally`, async ({ page }, testInfo) => {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/index.html");
    const overflows = async () => page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    expect(await overflows()).toBe(false);
    await page.locator("#tabulka-n5 summary").click();
    expect(await overflows()).toBe(false);
    await expect(page.locator("#tabulka-n5 tbody tr")).toHaveCount(20);
    const scrolls = await page.locator("#tabulka-n5 .table-scroll").evaluate((node) => ({ scroll: node.scrollWidth, client: node.clientWidth }));
    if (width === 320) expect(scrolls.scroll).toBeGreaterThan(scrolls.client);
    await page.goto("/index.html#doprava");
    const top = await page.locator("#doprava").evaluate((node) => node.getBoundingClientRect().top);
    const bottom = await page.locator(".topics").evaluate((node) => node.getBoundingClientRect().bottom);
    expect(top).toBeGreaterThanOrEqual(bottom - 1);
    if (width === 390) {
      await page.goto("/index.html");
      await page.screenshot({ path: testInfo.outputPath("mobile-overview.png") });
      await page.goto("/index.html#e4a");
      await page.screenshot({ path: testInfo.outputPath("mobile-question.png") });
    }
  });
}

test("the complete report and native tables work without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:8765/");
  await expect(page.locator("[data-question]")).toHaveCount(31);
  await expect(page.locator("[data-text-key]")).toHaveCount(17);
  await expect(page.locator("#toggle-tables")).not.toBeVisible();
  await page.locator("#tabulka-b1 summary").click();
  await expect(page.locator("#tabulka-b1 table")).toBeVisible();
  await context.close();
});

test("no-JavaScript print retains the chart labels and values as a fallback", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:8765/");
  await page.emulateMedia({ media: "print" });
  await expect(page.locator("#a2 .bar-chart")).toBeVisible();
  await expect(page.locator('#n5 .chart-row[data-value="Pocoucov"]')).toContainText("1 odp.");
  await expect(page.locator("#tabulka-a2 summary")).toBeVisible();
  await context.close();
});

test("printing expands every table and restores the previous state", async ({ page }) => {
  await page.goto("/index.html");
  await page.locator("#tabulka-a2 summary").click();
  await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
  await expect(page.locator("details.data-table[open]")).toHaveCount(31);
  await page.emulateMedia({ media: "print" });
  await expect(page.locator("#a2 .bar-chart")).not.toBeVisible();
  await expect(page.locator("#tabulka-n5 table")).toBeVisible();
  await page.emulateMedia({ media: "screen" });
  await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
  await expect(page.locator("details.data-table[open]")).toHaveCount(1);
  await expect(page.locator("#tabulka-a2")).toHaveAttribute("open", "");
});

test("short methodology is linked, readable, and keyboard accessible", async ({ page }, testInfo) => {
  await page.goto("/index.html");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Přejít na obsah" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#obsah")).toBeFocused();
  await page.getByRole("link", { name: "Jak výsledky číst a jak chráníme soukromí" }).click();
  await expect(page).toHaveURL(/metodika\.html$/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Jak výsledky číst");
  await expect(page.locator(".methodology-card p")).toHaveCount(5);
  await expect(page.locator(".methodology-card")).toContainText("187 odpovědí na dotazník");
  await expect(page.locator(".methodology-card")).toContainText("identifikujících");
  await page.screenshot({ path: testInfo.outputPath("methodology.png") });
  await expect(page.getByRole("navigation", { name: "Hlavní navigace" }).getByRole("link", { name: "Výsledky" })).toHaveAttribute("href", "index.html");
  await expect(page.getByRole("link", { name: "Zpět na všechny výsledky" })).toHaveAttribute("href", "index.html");
  await page.getByRole("link", { name: "Prohlédnout výsledky" }).click();
  await expect(page).toHaveURL(/index\.html$/);
});

test("public pages pass automated WCAG A/AA checks", async ({ page }) => {
  for (const url of ["/index.html", "/metodika.html"]) {
    await page.goto(url);
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
    expect(results.violations).toEqual([]);
  }
  await page.goto("/index.html");
  await page.getByRole("button", { name: "Rozbalit tabulky" }).click();
  const tables = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  expect(tables.violations).toEqual([]);
});

test("preview never serves database backups, working text files, or directories", async ({ request }) => {
  for (const path of ["/backup/dotaznik.db", "/report/odpovedi/l1.md", "/report/web-texty.md", "/report/dotaznik-archiv.html", "/report/", "/vysledky.html", "/save.php", "/assets/", "/.git/config"]) {
    const response = await request.get(path);
    expect(response.status()).toBe(404);
  }
});