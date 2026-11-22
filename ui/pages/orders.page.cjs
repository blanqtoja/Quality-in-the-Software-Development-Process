const { expect } = require('playwright/test');

class OrdersPage {
  constructor(page) {
    this.page = page;
  }

  async open() {
    this.endpoint = '/api/purchasing/purchase-orders';
    const title = 'New purchase order';
    await this.page.goto('/purchasing?tab=orders');
    // An empty list also renders a create CTA, so select the toolbar's first matching button.
    await this.page.locator('#main-content').getByRole('button', { name: title, exact: true }).first().click();
    this.dialog = this.page.getByRole('dialog', { name: title, exact: true });
    await expect(this.dialog).toBeVisible();
    const partner = this.dialog.getByRole('combobox', { name: 'Vendor' });
    await expect(partner).toBeEnabled();
    await partner.click();
    await this.page.getByRole('option').first().click();
  }

  async submitWithoutLines() {
    await this.dialog.getByRole('button', { name: 'Create', exact: true }).click();
    await expect(this.page.getByText('Add at least one complete line', { exact: true })).toBeVisible();
    await expect(this.dialog).toBeVisible();
  }
}

module.exports = { OrdersPage };
