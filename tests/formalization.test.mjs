import test from 'node:test';
import assert from 'node:assert/strict';
import { badgeDetails, installBadges } from '../site/assets/formalization.mjs';

test('unrecorded and network failure are distinct from verification', () => {
  assert.equal(badgeDetails().state, 'not-recorded');
  assert.equal(badgeDetails(undefined, true).state, 'unavailable');
});

test('pending records link to their proof repository', () => {
  const badge = badgeDetails({state: 'pending', repository: 'https://github.com/owner/proofs'});
  assert.equal(badge.state, 'pending');
  assert.equal(badge.href, 'https://github.com/owner/proofs');
});

test('verified records link to an immutable proof revision', () => {
  const commit = 'a'.repeat(40);
  const badge = badgeDetails({state: 'verified', repository: 'https://github.com/owner/proofs', commit, declaration: 'Book.theorem_one', file: 'Book.lean'});
  assert.equal(badge.text, '0 sorry');
  assert.equal(badge.href, `https://github.com/owner/proofs/tree/${commit}`);
  assert.match(badge.title, /Book.theorem_one/);
});

test('a verified label without an exact commit cannot produce a verified badge', () => {
  assert.equal(badgeDetails({state: 'verified', commit: 'main'}).state, 'pending');
});

test('section tags do not receive proof badges while independent statements still do', async t => {
  const target = section => ({
    dataset: {gerbyTag: '1234ABCD'}, children: [],
    hasAttribute: name => section && name === 'data-section-marker',
    querySelector: () => null,
    closest: () => ({dataset: {gerbyBook: 'source'}}),
    append(element) { this.children.push(element); }
  });
  const section = target(true), statement = target(false);
  t.mock.method(globalThis, 'fetch', async () => ({ok: true, json: async () => ({version: 1, entries: []})}));
  const original = globalThis.document;
  globalThis.document = {createElement: () => ({dataset: {}, setAttribute() {}})};
  t.after(() => { if (original === undefined) delete globalThis.document; else globalThis.document = original; });
  await installBadges({querySelectorAll: () => [section, statement]});
  assert.equal(section.children.length, 0);
  assert.equal(statement.children.length, 1);
  assert.equal(statement.children[0].textContent, '○ Not recorded');
});

test('section-only pages need no formalization registry request', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', () => { throw new Error('Unexpected request'); });
  await installBadges({querySelectorAll: () => [{hasAttribute: name => name === 'data-section-marker'}]});
  assert.equal(fetch.mock.callCount(), 0);
});
