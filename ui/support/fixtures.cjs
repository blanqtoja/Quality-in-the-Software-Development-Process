const { test: base, expect } = require('playwright/test');
const { ErpApp } = require('../pages/erp-app.cjs');

const test = base.extend({
  erp: async ({ page }, use) => {
    // Pin presentation preferences only; login and all API calls remain real.
    await page.addInitScript(() => {
      localStorage.setItem('erp.locale', 'en');
      localStorage.setItem('erp.onboarding', JSON.stringify({ completed: true, currentStep: 99 }));
    });
    await use(new ErpApp(page));
  },
});

function recordPosts(page, pathname) {
  const requests = [];
  const listener = (request) => {
    if (request.method() === 'POST' && new URL(request.url()).pathname === pathname) {
      requests.push(request);
    }
  };
  page.on('request', listener);
  return { requests, stop: () => page.off('request', listener) };
}

module.exports = { test, expect, recordPosts };
