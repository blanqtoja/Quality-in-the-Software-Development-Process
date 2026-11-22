const { expect } = require('playwright/test');

class LedgerPage {
  constructor(page) {
    this.page = page;
    this.main = page.locator('#main-content');
    this.post = this.main.getByRole('button', { name: 'Post entry', exact: true });
    this.rows = this.main.locator('tbody tr');
  }

  async open() {
    await this.page.goto('/ledger?tab=manual-entry');
    await expect(this.main.getByRole('heading', { name: 'Ledger', exact: true })).toBeVisible();
  }

  async fillEntry(debit, credit) {
    await expect(this.rows).toHaveCount(2);
    const accounts = [process.env.ERP_UI_DEBIT_ACCOUNT || '1010', process.env.ERP_UI_CREDIT_ACCOUNT || '3100'];
    for (let index = 0; index < 2; index += 1) {
      const picker = this.rows.nth(index).getByRole('combobox');
      await picker.fill(accounts[index]);
      await this.page.getByRole('option').filter({ hasText: new RegExp(`^${accounts[index]}\\s`) }).click();
    }
    // These inputs have no labels in the SUT; limit positional selectors to the known table columns.
    await this.rows.nth(0).getByRole('textbox').nth(0).fill(debit);
    await this.rows.nth(1).getByRole('textbox').nth(1).fill(credit);
  }

}

module.exports = { LedgerPage };
