const { request } = require('playwright/test');

module.exports = async function globalSetup(config) {
  const baseURL = config.projects[0].use.baseURL;
  const client = await request.newContext({ baseURL, timeout: 5_000 });
  try {
    // Missing infrastructure must stop the run, never select a substitute UI.
    const response = await client.get('/login');
    if (!response.ok() || !(await response.text()).includes('Manufacturing ERP')) {
      throw new Error(`GET /login returned ${response.status()} without the ERP page`);
    }
  } catch (error) {
    throw new Error(`ERP UI unavailable at ${baseURL}. Start the application or set ERP_UI_BASE_URL. ${error.message}`);
  } finally {
    await client.dispose();
  }
};
