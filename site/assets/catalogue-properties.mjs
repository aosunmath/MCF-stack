// Filter within one geometric case; do not combine unrelated dimensions of a family.
export const ambientNames={r2:'Euclidean plane ℝ²',r3:'Euclidean space ℝ³',r4:'Euclidean space ℝ⁴',higher:'Euclidean dimension ≥ 5',manifold:'Riemannian ambient manifold'};
export const genusNames={'0':'Genus 0','1':'Genus 1',higher:'Finite genus ≥ 2',infinite:'Infinite genus',varies:'Genus depends on parameters','not-recorded':'Genus not recorded',na:'Not a surface'};
export const endNames={'0':'No ends (compact)','1':'One end','2':'Two ends','3':'Three ends',many:'At least four ends',varies:'Ends depend on parameters','not-recorded':'Ends not recorded'};
export const statusNames={exact:'Exact formula',bound:'Proved bound or relation',numerical:'Numerical estimate',finite:'Finite; value not recorded','not-recorded':'Not recorded','not-applicable':'Not applicable'};
export const categoryNames={shrinkers:'Shrinkers',translators:'Translators',expanders:'Expanders','other-special-flows':'Other special flows'};
export function entropyBelow(item,limit){
  if(!limit)return true;
  const bound=Number(limit);
  if(item.status==='exact' && Number.isFinite(item.value))return item.value<bound;
  return ['exact','bound'].includes(item.status) && Number.isFinite(item.upper) && (item.upper<bound || (item.upper===bound && item.upper_strict===true));
}
export function matchingCases(record,filters){
  const quantity=filters.quantity||'entropy';
  const words=(filters.q||'').toLocaleLowerCase().split(/\s+/).filter(Boolean);
  return record.cases.map((item,index)=>({item,index})).filter(({item})=>{
    if(filters.ambient&&!item.ambient.includes(filters.ambient))return false;
    if(filters.dimension&&item.dimension!==filters.dimension)return false;
    if(filters.compact&&item.compact!==(filters.compact==='unspecified'?null:filters.compact==='compact'))return false;
    if(filters.genus&&item.genus.key!==filters.genus)return false;
    if(filters.ends&&item.ends.key!==filters.ends)return false;
    if(filters.evidence&&item[quantity].status!==filters.evidence)return false;
    if(!entropyBelow(item.entropy,filters.limit))return false;
    const haystack=[record.title,record.notes,item.name,item.topology,item.genus.text,item.ends.text,item.entropy.text,item.gaussian.text,...item.ambient.map(k=>ambientNames[k])].join(' ').toLocaleLowerCase();
    return words.every(word=>haystack.includes(word));
  });
}
export function groupedMatches(records,filters){
  const groups=new Map();let families=0,cases=0;
  for(const record of records){
    const matches=matchingCases(record,filters);if(!matches.length)continue;
    families++;cases+=matches.length;
    const subsets=new Map();
    for(const match of matches){
      const c=match.item;
      const keys=filters.group==='ambient'?(filters.ambient?[filters.ambient]:c.ambient):[filters.group==='genus'?c.genus.key:filters.group==='ends'?c.ends.key:filters.group==='measure'?c[filters.quantity||'entropy'].status:record.category];
      for(const key of keys){if(!subsets.has(key))subsets.set(key,[]);subsets.get(key).push(match.index);}
    }
    for(const [key,indices] of subsets){if(!groups.has(key))groups.set(key,[]);groups.get(key).push({record,indices});}
  }
  return {groups,families,cases};
}
if(typeof document!=='undefined'){
  const form=document.querySelector('#property-filters');
  if(form){
    const records=JSON.parse(document.querySelector('#property-data').textContent),results=document.querySelector('#property-results');
    const templates=new Map([...results.querySelectorAll('.property-card')].map(card=>[card.dataset.label,card.cloneNode(true)]));
    const names=['ambient','dimension','compact','genus','ends','quantity','evidence','limit','group','q'];
    const defaults={quantity:'entropy',group:'category'};
    const load=()=>{const params=new URLSearchParams(location.search);for(const name of names){const el=form.elements.namedItem(name);el.value=params.get(name)||defaults[name]||'';if(el.tagName==='SELECT'&&el.selectedIndex<0)el.value=defaults[name]||'';}};
    function render(sync=true){
      const filters=Object.fromEntries(names.map(name=>[name,form.elements.namedItem(name).value]));
      const {groups,families,cases}=groupedMatches(records,filters);
      const headings=filters.group==='ambient'?ambientNames:filters.group==='genus'?genusNames:filters.group==='ends'?endNames:filters.group==='measure'?statusNames:categoryNames;
      results.replaceChildren();
      for(const key of Object.keys(headings)){
        if(!groups.has(key))continue;
        const section=document.createElement('section'),h=document.createElement('h2');h.textContent=headings[key];section.append(h);
        for(const {record,indices} of groups.get(key)){
          const card=templates.get(record.label).cloneNode(true);
          for(const c of card.querySelectorAll('[data-case]')){c.hidden=!indices.includes(Number(c.dataset.case));c.open=indices.length===1;}
          section.append(card);
        }
        results.append(section);
      }
      document.querySelector('#property-count').textContent=`${families} of ${records.length} example families · ${cases} matching geometric cases`;
      if(!families){const p=document.createElement('p');p.className='property-empty';p.textContent='No recorded examples match these filters. Try another combination or reset the filters.';results.append(p);}
      const params=new URLSearchParams();for(const [k,v] of Object.entries(filters))if(v&&v!==defaults[k])params.set(k,v);
      if(sync)history.replaceState(null,'',location.pathname+(params.size?'?'+params.toString():''));
      const share=new URL(document.querySelector('link[rel="canonical"]').href);share.search=params.toString();
      for(const button of document.querySelectorAll('[data-copy-link]'))button.dataset.copyLink=share.href;
    }
    form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('input',()=>render());form.addEventListener('change',()=>render());
    form.addEventListener('reset',()=>{queueMicrotask(()=>render());});
    window.addEventListener('popstate',()=>{load();render(false);});load();form.hidden=false;render(false);
  }
}
