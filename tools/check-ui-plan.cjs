const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const cases = JSON.parse(fs.readFileSync(path.join(root, 'ui/cases.json'), 'utf8'));
const plan = fs.readFileSync(path.join(root, 'PLAN_TESTOW_API_UI.md'), 'utf8');
assert.equal(cases.length, 4, 'Scope: exactly four UI cases for Lukasz');
assert.ok(cases.every((item) => item.owner === 'lukasz'), 'UI cases must belong only to Lukasz');
const ids = new Set();
for (const owner of ['lukasz']) {
  const spec = fs.readFileSync(path.join(root, `ui/tests/${owner}.spec.cjs`), 'utf8');
  const planned = cases.filter((item) => item.owner === owner);
  const implemented = [...spec.matchAll(/\btest\('((UI-LUK-\d{3}) \| (SC-[A-Z0-9]+-\d{2}) \| [^']+)'/g)];
  assert.equal(planned.length, 4, `${owner}: exactly four planned UI cases`);
  assert.equal(implemented.length, planned.length, `${owner}: planned/implemented count differs`);
  for (const item of planned) {
    assert.ok(!ids.has(item.id), `Duplicate case ID: ${item.id}`);
    ids.add(item.id);
    assert.ok(implemented.some((test) => test[2] === item.id && test[3] === item.scenario), `Missing implementation: ${item.id}`);
    assert.ok(item.preconditions.length && item.data.length && item.steps.length && item.expected.length && item.postcondition, `Incomplete case: ${item.id}`);
    assert.ok(plan.includes(`### ${item.id} `) && plan.includes(item.scenario), `Missing case in combined plan: ${item.id}`);
  }
  console.log(`${owner}: ${planned.length} planned and implemented UI cases; scenario mapping OK`);
}
assert.equal(cases.length, ids.size);
console.log('Plan consistency OK. This check does not execute browser tests.');
