import assert from 'node:assert/strict';
import {selectEdition,renderText} from '../src/newsletter-edition.js';
const rows=[{u:'/cs/a/',t:'Článek',dt:'2026-10-29',s:'world'}, {u:'/cs/a/',t:'Dup',dt:'2026-10-29',s:'world'}, {u:'/cs/b/',t:'Druhý',dt:'2026-10-28',s:'tech'}, {u:'/cs/old/',t:'Starý',dt:'2026-10-10',s:'world'}, {u:'/en/other/',t:'Jiný jazyk',dt:'2026-10-29',s:'world'}];
const x=selectEdition(rows,['world'],'cs','2026-10-29');assert.equal(x.selected.length,1);assert.equal(x.outside.t,'Druhý');
const body=renderText(x,'cs','https://example.test/unsubscribe');assert.ok(body.includes('Mimo váš výběr'));assert.ok(!body.includes('Starý'));assert.ok(body.includes('Odhlásit odběr:'));
assert.equal(selectEdition(rows,['food'],'cs','2026-10-29').selected.length,0);
console.log('Edition: freshness, language, deduplication and wider view checks passed');
