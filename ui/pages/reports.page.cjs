const { expect } = require('playwright/test');

function displayedAmount(raw) {
  // The UI displays two decimals; derive expected presentation from a decimal string, without floats.
  const match = /^(-?)(\d+)(?:\.(\d+))?$/.exec(String(raw));
  if (!match) throw new Error(`Invalid decimal in trial balance: ${raw}`);
  return `${match[1]}${match[2].replace(/\B(?=(\d{3})+(?!\d))/g, ',')}.${((match[3] || '') + '00').slice(0, 2)}`;
}

class ReportsPage {
  constructor(page) {
    this.page = page;
  }

  async openTrialBalance() {
    const responsePromise = this.page.waitForResponse((response) =>
      new URL(response.url()).pathname === '/api/reporting/trial-balance' &&
      response.request().method() === 'GET',
    );
    await this.page.goto('/reporting?tab=trial-balance');
    const response = await responsePromise;
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body.lines)).toBe(true);
    expect(body.lines.length).toBeGreaterThan(0);
    const panel = this.page.getByRole('tabpanel', { name: 'Trial balance', exact: true });
    await expect(panel).toBeVisible();
    await expect(panel.getByText(body.balanced ? 'Balanced' : 'Unbalanced', { exact: true })).toBeVisible();
    const totals = panel.locator('tfoot tr').getByRole('columnheader');
    await expect(totals.nth(1)).toHaveText(displayedAmount(body.totalDebit));
    await expect(totals.nth(2)).toHaveText(displayedAmount(body.totalCredit));
    const first = body.lines[0];
    const row = panel.getByRole('row').filter({ has: this.page.getByRole('cell', { name: String(first.code), exact: true }) });
    await expect(row.getByRole('cell').nth(1)).toHaveText(first.name || '');
    await expect(row.getByRole('cell').nth(3)).toHaveText(displayedAmount(first.debit));
    await expect(row.getByRole('cell').nth(4)).toHaveText(displayedAmount(first.credit));
  }
}

module.exports = { ReportsPage, displayedAmount };
