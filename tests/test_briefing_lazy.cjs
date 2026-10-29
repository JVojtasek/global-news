const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

const events = {}, appended = [];
let observer;
const form = { addEventListener(name, fn) { events[name] = fn; } };
const document = {
  getElementById: () => form,
  createElement: () => ({ remove() {} }),
  head: { appendChild(script) { appended.push(script); } },
};
function IntersectionObserver(callback) {
  this.observe = () => {};
  this.disconnect = () => {};
  observer = callback;
}
const window = { fetch() {}, IntersectionObserver };
vm.runInNewContext(fs.readFileSync('static/briefing-subscribe.js','utf8'), { document, window, IntersectionObserver });
assert.equal(appended.length,0,'ordinary page view does not load verification');
observer([{isIntersecting:true}]);
assert.equal(appended.length,1,'approaching the form loads verification');
assert.equal(appended[0].src,'https://challenges.cloudflare.com/turnstile/v0/api.js');
events.focusin();
assert.equal(appended.length,1,'interaction does not load it twice');
appended[0].onerror();
events.pointerdown();
assert.equal(appended.length,2,'a failed load can be retried');
console.log('Verification loads lazily, only once, and retries after failure.');
