/* This form creates a separate email preference. It never reads localStorage. */
(function () {
  'use strict';
  var form=document.getElementById('briefing-email-form');
  if(!form || !window.fetch) return;
  // Do not hold every newspaper page open for a third-party verification widget.
  // Load it when a reader approaches or interacts with the email form.
  var loading=false, observer;
  function loadVerification(){
    if(loading || window.turnstile) return;
    loading=true;
    var script=document.createElement('script');
    script.src='https://challenges.cloudflare.com/turnstile/v0/api.js';
    script.async=true;
    script.onerror=function(){loading=false;script.remove();};
    document.head.appendChild(script);
    if(observer) observer.disconnect();
  }
  form.addEventListener('focusin',loadVerification,{once:true});
  form.addEventListener('pointerdown',loadVerification,{once:true});
  if('IntersectionObserver' in window){
    observer=new IntersectionObserver(function(entries){
      if(entries.some(function(entry){return entry.isIntersecting;})) loadVerification();
    },{rootMargin:'500px'});
    observer.observe(form);
  } else loadVerification();
  form.addEventListener('submit',function(event){
    event.preventDefault();
    var status=form.querySelector('[role=status]'), button=form.querySelector('button[type=submit]');
    var sections=Array.prototype.map.call(form.querySelectorAll('input[name=section]:checked'),function(x){return x.value;});
    var challenge=form.querySelector('[name=cf-turnstile-response]');
    if(!sections.length || sections.length>10){status.textContent=form.getAttribute('data-sections-error');return;}
    if(!challenge || !challenge.value){loadVerification();status.textContent=form.getAttribute('data-challenge-error');return;}
    button.disabled=true; status.textContent='';
    fetch(form.getAttribute('data-api'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      email:form.elements.email.value,lang:form.getAttribute('data-lang'),sections:sections,
      consent:form.elements.consent.checked,challenge:challenge.value
    })}).then(function(r){if(!r.ok) throw new Error('request failed');return r.json();}).then(function(r){
      if(!r.ok) throw new Error('request failed');
      form.reset(); status.textContent=form.getAttribute('data-success');
    }).catch(function(){status.textContent=form.getAttribute('data-error');}).finally(function(){
      button.disabled=false;
      if(window.turnstile && window.turnstile.reset) window.turnstile.reset();
    });
  });
}());
