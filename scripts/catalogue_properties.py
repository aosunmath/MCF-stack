"""Reviewed geometric metadata and a progressively enhanced catalogue browser."""
from functools import cache
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMBIENTS = {'r2': 'Euclidean plane ℝ²', 'r3': 'Euclidean space ℝ³', 'r4': 'Euclidean space ℝ⁴', 'higher': 'Euclidean dimension ≥ 5', 'manifold': 'Riemannian ambient manifold'}
AMBIENT_SHORT = {'r2': 'ℝ²', 'r3': 'ℝ³', 'r4': 'ℝ⁴', 'higher': 'Higher dimensions (N ≥ 5)', 'manifold': 'Curved ambient spaces'}
STATUS = {'exact':'Exact formula', 'bound':'Proved bound or relation', 'numerical':'Numerical estimate', 'finite':'Finite; value not recorded', 'not-recorded':'Not recorded', 'not-applicable':'Not applicable'}
GENUS = {'0':'Genus 0', '1':'Genus 1', 'higher':'Finite genus ≥ 2', 'infinite':'Infinite genus', 'varies':'Genus depends on parameters', 'not-recorded':'Genus not recorded', 'na':'Not a surface'}
ENDS = {'0':'No ends (compact)', '1':'One end', '2':'Two ends', '3':'Three ends', 'many':'At least four ends', 'varies':'Ends depend on parameters', 'not-recorded':'Ends not recorded'}

@cache
def registry():
    records=json.loads((ROOT/'catalogue-properties.json').read_text())['examples']
    result={r['label']:r for r in records}
    if len(result)!=len(records): raise ValueError('Duplicate catalogue property label')
    for record in records:
        if not record['cases']: raise ValueError('Catalogue family has no property cases')
        for case in record['cases']:
            if not case['ambient'] or set(case['ambient'])-AMBIENTS.keys(): raise ValueError('Invalid ambient space')
            if case['dimension'] not in {'curve','surface','higher','network'}: raise ValueError('Invalid intrinsic dimension')
            if case['genus']['key'] not in GENUS or case['ends']['key'] not in ENDS: raise ValueError('Invalid topology facet')
            if case['dimension']!='surface' and case['genus']['key']!='na': raise ValueError('Surface genus attached to a nonsurface')
            for quantity in ('entropy','gaussian'):
                item=case[quantity]
                if item['status'] not in STATUS or not item['text']: raise ValueError('Invalid measurement metadata')
                if item.get('value') is not None and item['status'] not in {'exact','numerical'}: raise ValueError('A scalar value needs an exact or numerical status')
    return result

def case_anchor(label, index):
    return f'case-{label.replace(":", "-")}-{index + 1}'


def ambient_memberships(record):
    """Stated construction spaces, ordered by the lowest Euclidean dimension."""
    return {key: [{'anchor': case_anchor(record['label'], i), 'name': case['name'] or case['topology']}
                  for i, case in enumerate(record['cases']) if key in case['ambient']]
            for key in AMBIENTS if any(key in case['ambient'] for case in record['cases'])}


def arrange_by_ambient(chapters, records):
    """Place each family once, before reader numbering; retain other cases as links."""
    by_section = {}
    for record in records:
        if record['section'] in by_section:
            raise ValueError('Ambient arrangement requires one catalogue family per section')
        by_section[record['section']] = record
    for chapter_key, chapter in chapters.items():
        families = {topic: ambient_memberships(by_section[topic])
                    for topic in chapter['topics'] if topic in by_section}
        if not families:
            continue
        if set(families) != set(chapter['topics']):
            raise ValueError('Every section in an ambient-organized chapter needs property metadata')
        if any(by_section[topic]['category'] != chapter_key for topic in families):
            raise ValueError('Catalogue family assigned to the wrong chapter')
        groups = []
        for key, title in AMBIENTS.items():
            primary = [topic for topic, spaces in families.items() if next(iter(spaces)) == key]
            related = [{'section': topic, 'cases': spaces[key]}
                       for topic, spaces in families.items() if key in spaces and next(iter(spaces)) != key]
            if primary or related:
                groups.append({'key': key, 'title': title, 'topics': primary, 'related': related})
        chapter['ambient_groups'] = groups
        chapter['ambient_families'] = families
        chapter['topics'] = [topic for group in groups for topic in group['topics']]
        positions = {topic: i for i, topic in enumerate(chapter['topics'])}
        for group in groups:
            group['related'].sort(key=lambda item: positions[item['section']])


def case_html(case,index,identifier=None):
    ambient='; '.join(AMBIENTS[k] for k in case['ambient'])
    heading=case['name'] or case['topology']
    compact = 'Compact' if case['compact'] is True else 'Noncompact' if case['compact'] is False else 'Not specified for this subfamily'
    fields=[('Ambient space',ambient),('Topology',case['topology']),('Compactness',compact),('Surface genus',case['genus']['text']),('Topological ends',case['ends']['text'])]
    for key,title in [('entropy','Entropy'),('gaussian','Gaussian area')]:
        item=case[key]
        fields.append((title,f'{STATUS[item["status"]]}: {item["text"]}'))
    body=''.join(f'<dt>{escape(k)}</dt><dd>{escape(v)}</dd>' for k,v in fields)
    anchor = f' id="{escape(identifier, quote=True)}"' if identifier else ''
    return f'<details class="property-case" data-case="{index}"{anchor}><summary>{escape(heading)} <span>· {escape(ambient)}</span></summary><dl>{body}</dl></details>'

def panel(label,root):
    record=registry().get(label)
    if not record:return ''
    note=f'<p>{escape(record["notes"])}</p>' if record['notes'] else ''
    spaces = ambient_memberships(record)
    links = ' · '.join(f'<a href="#{cases[0]["anchor"]}">{escape(AMBIENT_SHORT[key])}</a>' for key, cases in spaces.items())
    navigation = f'<nav class="ambient-case-links" aria-label="Ambient dimensions of this family">Ambient spaces: {links}</nav>'
    return navigation+'<details class="property-panel"><summary>Ambient space, topology and entropy</summary>'+note+''.join(case_html(c,i,case_anchor(label,i)) for i,c in enumerate(record['cases']))+f'<p><a href="{root}browse/">Compare examples by these properties →</a></p></details>'

def prepare(entries,topics,topic_chapters,visuals):
    actual={v['label']:e for e in entries.values() for v in e['variants'] if v['source']=='gmt-foundations' and v['label'].startswith('ex:catalogue-')}
    if not actual:return []
    metadata=registry()
    if set(actual)!=set(metadata) or set(actual)!=set(visuals):
        raise ValueError('Every catalogue example needs exactly one property record and illustration')
    records=[]
    for label,item in metadata.items():
        e=actual[label];visual=visuals[label]
        records.append({**item,'title':topics[e['topic']]['title'],'section':e['topic'],'category':topic_chapters[e['topic']],'tag':e['tag'],'model':visual['model'],'illustration_status':visual['status']})
    return records

def select(name,label,options):
    return f'<label>{escape(label)}<select name="{name}">'+''.join(f'<option value="{escape(k,quote=True)}">{escape(v)}</option>' for k,v in options.items())+'</select></label>'

def page(records):
    controls=select('ambient','Ambient space',{'':'All ambient spaces',**AMBIENTS})
    controls+=select('dimension','Dimension',{'':'All dimensions','surface':'Surfaces (dimension 2)','curve':'Curves','higher':'Dimension ≥ 3','network':'Networks'})
    controls+=select('compact','Compactness',{'':'Any compactness status','compact':'Compact','noncompact':'Noncompact','unspecified':'Not specified'})
    controls+=select('genus','Surface genus',{'':'Any genus',**GENUS})
    controls+=select('ends','Topological ends',{'':'Any number of ends',**ENDS})
    controls+=select('quantity','Quantity',{'entropy':'Entropy λ','gaussian':'Centered Gaussian area F₀,₁'})
    controls+=select('evidence','Information available',{'':'Any status',**STATUS})
    controls+=select('limit','Proved entropy bound',{'':'No bound filter','2':'Entropy < 2','3':'Entropy < 3','4':'Entropy < 4'})
    controls+=select('group','Group by',{'category':'Solution category','ambient':'Ambient space','genus':'Surface genus','ends':'Topological ends','measure':'Selected quantity / status'})
    controls+='<label class="property-query">Name or property<input name="q" type="search" placeholder="e.g. torus, conical, immersed"></label>'
    cards=[]
    for record in records:
        note=f'<p class="property-note">{escape(record["notes"])}</p>' if record['notes'] else ''
        cards.append(f'<article class="property-card" data-label="{escape(record["label"],quote=True)}"><div class="property-card-heading"><img src="../assets/solitons/{record["model"]}.svg" alt="" width="100" height="64" loading="lazy"><div><h3><a href="../sections/{record["section"]}/">{escape(record["title"])}</a></h3><p>{escape(record["illustration_status"])}</p></div></div>'+note+''.join(case_html(c,i) for i,c in enumerate(record['cases']))+'</article>')
    payload=json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
    return r'''<h1>Browse by properties</h1>
<p>Find special flows by their ambient space, topology, and Gaussian area or entropy. Filters are combined within the same dimensional case of a family.</p>
<details class="property-conventions"><summary>Conventions and how to read the data</summary>
<p>Topology refers to the parameter manifold for an immersion and to a regular time slice for an evolving flow. Surface genus applies only in dimension two. Ends are topological ends; several asymptotic sheets in one height direction need not be different ends. For disconnected examples the text states whether a count is per component. Ambient space means the space stated in the construction, rather than every possible Euclidean inclusion.</p>
<p>For an n-dimensional Euclidean submanifold, including immersion multiplicity,</p>
<div class="displaymath">\[F_{x_0,\tau}(M)=(4\pi\tau)^{-n/2}\int_M e^{-|X-x_0|^2/(4\tau)}\,d\mu,\qquad \lambda(M)=\sup_{x_0,\,\tau>0}F_{x_0,\tau}(M).\]</div>
<p>Centered Gaussian area means F₀,₁ of the stated slice. It generally differs from entropy and depends on center and scale. For the normalized complete shrinkers with polynomial area growth here, F₀,₁ equals entropy. A bound on the supremum over a flow's times is labeled separately from the entropy of a single slice. Euclidean entropy is not assigned to an intrinsic flow in a curved ambient manifold.</p>
<p>“Not recorded” means this catalogue has no value or theorem recorded, not that none is known. The proved-entropy-bound filter uses recorded scalar values and upper bounds; a parameter-dependent formula without a recorded uniform bound will not match. Numerical estimates are excluded. A family may appear in several groups. References and hypotheses are in the linked entries.</p></details>
<form class="property-filters" id="property-filters" hidden>'''+controls+'''<button type="reset">Reset filters</button></form>
<noscript><p>All recorded cases appear below. Enable JavaScript to combine filters.</p></noscript>
<p id="property-count" role="status">'''+str(len(records))+''' example families</p>
<div id="property-results">'''+''.join(cards)+'''</div>
<script type="application/json" id="property-data">'''+payload+'</script>'
