/* This form creates a separate email preference. It never reads localStorage. */
(function () {
  'use strict';
  var form=document.getElementById('briefing-email-form');
  if(!form || !window.fetch) return;
  form.addEventListener('submit',function(event){
    event.preventDefault();
    var status=form.querySelector('[role=status]'), button=form.querySelector('button[type=submit]');
    var sections=Array.prototype.map.call(form.querySelectorAll('input[name=section]:checked'),function(x){return x.value;});
    var challenge=form.querySelector('[name=cf-turnstile-response]');
    if(!sections.length || sections.length>10){status.textContent=form.getAttribute('data-sections-error');return;}
    if(!challenge || !challenge.value){status.textContent=form.getAttribute('data-challenge-error');return;}
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
