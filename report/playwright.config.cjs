const path = require("node:path");
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: path.join(__dirname, "ui-tests"),
  testMatch: "**/*.spec.cjs",
  outputDir: path.join(__dirname, "test-results"),
  fullyParallel: false,
  workers: 1,
  timeout: 30000,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:8765",
    channel: "msedge",
    locale: "cs-CZ",
    viewport: { width: 1360, height: 1000 },
    reducedMotion: "reduce",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "python -X utf8 report/preview.py --port 8765",
    cwd: path.resolve(__dirname, ".."),
    url: "http://127.0.0.1:8765/",
    reuseExistingServer: false,
    timeout: 15000,
  },
});