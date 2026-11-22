const { expect } = require('playwright/test');
const { LedgerPage } = require('./ledger.page.cjs');
const { OrdersPage } = require('./orders.page.cjs');
const { ReportsPage } = require('./reports.page.cjs');

class ErpApp {
  constructor(page) {
    this.page = page;
    this.main = page.locator('#main-content');
    this.ledger = new LedgerPage(page);
    this.orders = new OrdersPage(page);
    this.reports = new ReportsPage(page);
  }

  async openLogin() {
    await this.page.goto('/login');
    await expect(this.page.getByRole('button', { name: 'Sign in', exact: true })).toBeVisible();
  }

  async submitCredentials(username, password) {
    await this.page.getByRole('textbox', { name: 'Username', exact: true }).fill(username);
    await this.page.getByLabel('Password', { exact: true }).fill(password);
    await this.page.getByRole('button', { name: 'Sign in', exact: true }).click();
  }

  async loginAs(role) {
    const prefix = `ERP_UI_${role.toUpperCase()}`;
    const username = process.env[`${prefix}_USERNAME`] || role;
    const password = process.env[`${prefix}_PASSWORD`] || role;
    await this.openLogin();
    await this.submitCredentials(username, password);
    // The account button also contains avatar initials in its accessible name.
    const accountName = new RegExp(username.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    await expect(this.page.getByRole('banner').getByRole('button', { name: accountName })).toBeVisible();
    await expect(this.main).toBeVisible();
  }

  async openModule(path, heading) {
    await this.page.goto(path);
    await expect(this.main.getByRole('heading', { name: heading, exact: true })).toBeVisible();
  }
}

module.exports = { ErpApp };
