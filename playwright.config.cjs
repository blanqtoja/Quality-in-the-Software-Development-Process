const { defineConfig } = require('playwright/test');

const channel = process.env.ERP_UI_CHANNEL;
const listOnly = process.argv.includes('--list');

module.exports = defineConfig({
  testDir: './ui/tests',
  testMatch: 'lukasz.spec.cjs',
  globalSetup: require.resolve('./ui/support/global-setup.cjs'),
  // Tests share seeded ERP accounts; one worker keeps failures easy to reproduce.
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 30_000,
  expect: { timeout: 7_000 },
  outputDir: 'test-results/ui',
  reporter: listOnly ? [['list']] : [
    ['list'],
    ['html', { outputFolder: 'reports/ui/html', open: 'never' }],
    ['json', { outputFile: 'reports/ui/results.json' }],
  ],
  metadata: {
    assignment: '3 - UI',
    target: 'live ERP, no API response mocks',
    frontendSource: 'q86865511/ERPSystem@33b5df13594bcb456ba8a3d20e0bc455ac79aa75',
  },
  use: {
    baseURL: process.env.ERP_UI_BASE_URL || 'http://localhost:8081',
    browserName: 'chromium',
    ...(channel ? { channel } : {}),
    headless: true,
    viewport: { width: 1440, height: 1000 },
    locale: 'en-US',
    timezoneId: 'Europe/Warsaw',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
