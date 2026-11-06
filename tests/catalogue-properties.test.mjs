import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {matchingCases,entropyBelow,groupedMatches} from '../site/assets/catalogue-properties.mjs';
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
