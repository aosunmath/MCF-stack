import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {matchingCases,entropyBelow,groupedMatches,embeddednessNames} from '../site/assets/catalogue-properties.mjs';
const records=JSON.parse(readFileSync(new URL('../catalogue-properties.json',import.meta.url))).examples;
const get=label=>records.find(r=>r.label===`ex:catalogue-${label}`);
test('ambient space, genus and ends must belong to the same geometric case',()=>{
  const grim=get('grim-reaper');
  assert.equal(matchingCases(grim,{ambient:'r2',ends:'2'}).length,1);
  assert.equal(matchingCases(grim,{ambient:'r3',genus:'0',ends:'1'}).length,1);
  assert.equal(matchingCases(grim,{ambient:'r3',ends:'2'}).length,0);
  assert.equal(matchingCases(get('round-sphere'),{ambient:'r2',genus:'0'}).length,0);
});
test('numerical estimates and lower bounds cannot satisfy a proved upper-bound filter',()=>{
  assert.equal(entropyBelow({status:'numerical',value:1.85},2),false);
  assert.equal(entropyBelow({status:'bound',lower:2},3),false);
  assert.equal(entropyBelow({status:'bound',upper:2},2),false);
  assert.equal(entropyBelow({status:'bound',upper:2,upper_strict:true},2),true);
  assert.equal(entropyBelow({status:'exact',value:4/Math.E},2),true);
  assert.equal(entropyBelow({status:'finite'},4),false);
});
test('grouping preserves family count and restricts cases to the selected ambient space',()=>{
  const examples=records.map(r=>({...r,category:'shrinkers'}));
  const result=groupedMatches(examples,{ambient:'r3',group:'ambient'});
  assert.deepEqual([...result.groups.keys()],['r3']);
  assert.equal(result.groups.get('r3').length,result.families);
  for(const {record,indices} of result.groups.get('r3')) for(const index of indices)assert.ok(record.cases[index].ambient.includes('r3'));
});
test('not recorded and not applicable remain distinct and counts never infer zero',()=>{
  assert.equal(matchingCases(get('scherkenoids'),{genus:'0'}).length,0);
  assert.equal(matchingCases(get('nguyen-tridents'),{ends:'0'}).length,0);
  assert.equal(matchingCases(get('abresch-langer'),{genus:'na'}).length,1);
});

test('unspecified compactness does not become a noncompactness theorem',()=>{
  const ketover=get('ketover-doubled-plane');
  assert.equal(matchingCases(ketover,{genus:'1',compact:'noncompact'}).length,0);
  assert.equal(matchingCases(ketover,{genus:'1',compact:'unspecified'}).length,1);
  assert.equal(matchingCases(ketover,{ends:'2',compact:'noncompact'}).length,1);
});

test('known higher-dimensional cylinder end counts remain searchable',()=>{
  assert.equal(matchingCases(get('round-cylinder'),{ambient:'r4',ends:'1'}).length,1);
  assert.equal(matchingCases(get('round-cylinder'),{ambient:'r4',ends:'2'}).length,1);
});

test('embeddedness is recorded for every case and distinguishes known nonembeddings',()=>{
  for(const record of records)for(const c of record.cases){
    assert.ok(Object.hasOwn(embeddednessNames,c.embeddedness.key));
    assert.ok(c.embeddedness.text.trim());
  }
  assert.deepEqual(records.filter(r=>matchingCases(r,{embeddedness:'nonembedded'}).length).map(r=>r.label).sort(),
    ['abresch-langer','drugan-sphere','halldorsson-dense-shrinkers','halldorsson-minimal-helicoids','irrational-torus-curves','nil-invariant-translators','whitney-sphere'].map(x=>`ex:catalogue-${x}`).sort());
  assert.equal(matchingCases(get('bns-genus'),{ambient:'r3',genus:'1',embeddedness:'embedded'}).length,1);
  assert.equal(matchingCases(get('clifford-torus'),{ambient:'r4',embeddedness:'embedded'}).length,1);
});

test('conditional and unrecorded embeddedness do not become a definite yes or no',()=>{
  for(const name of ['curve-products','spherical-minimal']){
    const r=get(name);
    assert.equal(matchingCases(r,{embeddedness:'depends'}).length,r.cases.length);
    assert.equal(matchingCases(r,{embeddedness:'embedded'}).length,0);
    assert.equal(matchingCases(r,{embeddedness:'nonembedded'}).length,0);
  }
  const unknown={...get('round-sphere'),cases:[{...get('round-sphere').cases[0],embeddedness:{key:'not-recorded',text:'No conclusion recorded.'}}]};
  assert.equal(matchingCases(unknown,{embeddedness:'not-recorded'}).length,1);
  assert.equal(matchingCases(unknown,{embeddedness:'nonembedded'}).length,0);
  assert.equal(matchingCases(unknown,{embeddedness:'embedded'}).length,0);
});

test('embedding classification is attached to the original example, not its limit or projection',()=>{
  for(const name of ['ancient-torus-curves','double-plane-flow','double-sphere-flow','ketover-doubled-plane','expanding-networks']){
    const r=get(name);
    assert.equal(matchingCases(r,{embeddedness:'embedded'}).length,r.cases.length);
  }
});

test('embeddedness filters combine within a case and grouping counts each family once',()=>{
  const mixed={...get('round-sphere'),cases:[get('round-sphere').cases[0],get('drugan-sphere').cases[0]]};
  assert.equal(matchingCases(mixed,{ambient:'r2',embeddedness:'nonembedded'}).length,0);
  assert.equal(matchingCases(mixed,{ambient:'r3',embeddedness:'nonembedded'}).length,1);
  const result=groupedMatches([mixed],{group:'embeddedness'});
  assert.equal(result.families,1);
  assert.equal(result.cases,2);
  assert.deepEqual(result.groups.get('embedded')[0].indices,[0]);
  assert.deepEqual(result.groups.get('nonembedded')[0].indices,[1]);
});

test('the Möbius quotient is a nonorientable embedded surface, not an orientable genus',()=>{
  const r=get('mobius-shrinker');
  assert.equal(matchingCases(r,{ambient:'r4',genus:'nonorientable',ends:'1',embeddedness:'embedded'}).length,1);
  assert.equal(matchingCases(r,{genus:'0'}).length,0);
  assert.equal(matchingCases(r,{genus:'1'}).length,0);
  assert.equal(matchingCases(r,{genus:'na'}).length,0);
  assert.equal(entropyBelow(r.cases[0].entropy,2),false); // an exact expression is not a certified rounded bound
});

test('new intrinsic flows and higher-dimensional Lagrangians keep their own ambient and genus cases',()=>{
  for(const id of ['aryan-lee','su-tsai-wood','lee-tsai']){
    const r=get(id);
    assert.equal(matchingCases(r,{ambient:'manifold',embeddedness:'embedded'}).length,1);
    assert.equal(matchingCases(r,{ambient:'r4'}).length,0);
    assert.equal(r.cases[0].entropy.status,'not-applicable');
  }
  assert.equal(matchingCases(get('jlt-compact-shrinkers'),{ambient:'r4',genus:'1'}).length,1);
  assert.equal(matchingCases(get('jlt-compact-shrinkers'),{ambient:'higher',genus:'1'}).length,0);
});
