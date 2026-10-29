/* Compose a finite edition from public article metadata. This module neither
   accesses reader browser settings nor sends mail itself. */
const safePath=(url,lang)=>typeof url==='string' && url.startsWith('/'+lang+'/') && !url.includes('\\') && !/[\x00-\x1f]/.test(url) && !url.startsWith('//');
const clean=s=>String(s||'').replace(/[\r\n]+/g,' ').trim();
export function selectEdition(rows,sections,lang,day,limit=5) {
 if(!['cs','en'].includes(lang)||!/^\d{4}-\d{2}-\d{2}$/.test(day)||!Array.isArray(rows)||!Array.isArray(sections)) throw new Error('invalid edition input');
 const end=Date.parse(day+'T00:00:00Z');if(!Number.isFinite(end)) throw new Error('invalid date');
 const valid=[],seen=new Set();
 for(const row of rows){if(!row||!safePath(row.u,lang)||seen.has(row.u)||!clean(row.t)||!/^\d{4}-\d{2}-\d{2}$/.test(row.dt||''))continue;
  const age=(end-Date.parse(row.dt+'T00:00:00Z'))/86400000;if(!Number.isInteger(age)||age<0||age>1)continue;
  seen.add(row.u);valid.push(row);
 }
 valid.sort((a,b)=>b.dt.localeCompare(a.dt));
 const selected=valid.filter(a=>sections.includes(a.s)).slice(0,Math.max(1,Math.min(limit,10)));
 const outside=valid.find(a=>!sections.includes(a.s))||null;
 return {selected,outside};
}
export function renderText(edition,lang,unsubscribeUrl) {
 const czech=lang==='cs', lines=[czech?'My Paper — ranní briefing':'My Paper — morning briefing',''];
 const add=a=>{lines.push(clean(a.t));if(a.d)lines.push(clean(a.d));lines.push('https://mypaper.news'+a.u,'');};
 if(edition.selected.length)edition.selected.forEach(add);else lines.push(czech?'Ve vybraných rubrikách zatím nejsou nové články.':'No recent articles in your selected sections.','');
 if(edition.outside){lines.push(czech?'Mimo váš výběr':'Beyond your selections','');add(edition.outside);}
 lines.push(czech?'Odhlásit odběr:':'Unsubscribe:',unsubscribeUrl);
 return lines.join('\n');
}
