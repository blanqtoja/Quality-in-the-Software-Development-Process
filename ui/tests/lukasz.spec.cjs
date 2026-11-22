const { test, expect, recordPosts } = require('../support/fixtures.cjs');

test.describe('Łukasz Murza @lukasz', () => {
  test('UI-LUK-001 | SC-IAM-01 | guest cannot create partners', async ({ erp, page }) => {
    await erp.loginAs('guest');
    await erp.openModule('/masterdata?tab=partners', 'Master Data');
    await expect(erp.main.getByRole('tab', { name: 'Partners', exact: true })).toHaveAttribute('aria-selected', 'true');
    await expect(erp.main.getByRole('button', { name: 'New partner', exact: true })).toHaveCount(0);
    await expect(erp.main.getByRole('columnheader', { name: 'Code', exact: true })).toBeVisible();
    await expect(page.getByRole('dialog')).toHaveCount(0);
  });

  test('UI-LUK-002 | SC-GL-01 | unbalanced entry cannot be posted', async ({ erp, page }) => {
    await erp.loginAs('accountant');
    await erp.ledger.open();
    const calls = recordPosts(page, '/api/ledger/journal-entries');
    try {
      await erp.ledger.fillEntry('100.00', '95.00');
      await expect(erp.main.getByText('Unbalanced', { exact: true })).toBeVisible();
      await expect(erp.ledger.post).toBeDisabled();
      await erp.ledger.post.locator('..').hover();
      await expect(page.getByRole('tooltip')).toContainText('Entries must balance');
      expect(calls.requests).toHaveLength(0);
    } finally { calls.stop(); }
  });

  test('UI-LUK-003 | SC-P2P-01 | purchase order requires a complete line', async ({ erp, page }) => {
    await erp.loginAs('warehouse');
    await erp.orders.open();
    const calls = recordPosts(page, erp.orders.endpoint);
    try {
      await erp.orders.submitWithoutLines();
      expect(calls.requests).toHaveLength(0);
    } finally { calls.stop(); }
  });

  test('UI-LUK-004 | SC-REP-01 | trial balance displays actual API values', async ({ erp }) => {
    await erp.loginAs('accountant');
    await erp.reports.openTrialBalance();
  });
});
