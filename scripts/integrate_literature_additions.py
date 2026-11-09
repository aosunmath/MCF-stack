"""Reconcile the reviewed addition manifest without changing permanent entry labels.

The manifest contains mathematical editorial decisions, not automatically harvested claims.
Run from this checkout with the project's Python environment.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
from unidecode import unidecode
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content/gmt-foundations'

def read(path): return json.loads(path.read_text())
def write(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def slug(title):return re.sub(r'[^a-z0-9]+','-',unidecode(title).lower()).strip('-')
def reconcile(items,new,key):
    mapping={x[key]:i for i,x in enumerate(items)}
    for x in new:
        if x[key] in mapping:items[mapping[x[key]]]=x
        else:items.append(x)

def main():
    manifest=read(ROOT/'documentation/literature-additions.json')
    es=manifest['entries']; collection=read(ROOT/'collection.json')
    properties=read(ROOT/'catalogue-properties.json'); visuals=read(ROOT/'catalogue-visualizations.json')
    review=read(CONTENT/'entry-review.json'); inventory=read(CONTENT/'source-inventory.json')
    chapters={x['slug']:x for x in collection['chapters']}; tex=[]; p=[];v=[];r=[]
    for e in es:
        section=slug(e['title']);e['section']=section
        if section not in chapters[e['category']]['topics']:chapters[e['category']]['topics'].append(section)
        tex.append('\\chapter{'+e['title']+'}\\label{sec:catalogue-'+e['id']+'}\n\\begin{example}['+e['title']+']\\label{'+e['label']+'}\n'+e['body']+'\n\\par Sources: \\cite{'+','.join(e['citations'])+'}.\n\\end{example}\n')
        p.append(dict(label=e['label'],notes='Source construction and dimension restrictions are stated on the reading page. Illustrations have their own accuracy labels.',citations=e['citations'],cases=e['cases']))
        v.append(dict(label=e['label'],section=section,title=e['title'],category=e['category'],citations=e['citations'],model='literature-'+e['id'],status=e['visual']['status'],caption=e['visual']['caption'],alt=e['title']+'. '+e['visual']['caption'],interactive=True))
        r.append(dict(label=e['label'],title=e['title'],kind='example',file='catalogue-literature.tex',status='cited-example',citations=e['citations'],dependencies=[],formal_verification='none'))
    (CONTENT/'catalogue-literature.tex').write_text('\n'.join(tex))
    book=CONTENT/'book.tex';s=book.read_text()
    if '\\input{catalogue-literature}' not in s:book.write_text(s.replace('\\end{document}','\\input{catalogue-literature}\n\\end{document}'))
    reconcile(properties['examples'],p,'label');reconcile(visuals['entries'],v,'label');reconcile(review['entries'],r,'label')
    refs=CONTENT/'references.bib';bib=refs.read_text();keys=set(re.findall(r'@\w+\{([^,]+),',bib))
    for source in manifest['sources']:
        key=source['key']
        if key not in keys:
            fields={'author':' and '.join(source['authors']),'title':'{'+source['title']+'}','year':str(source.get('year','')),'journal':source.get('journal','arXiv preprint'),'doi':source.get('doi',''),'url':source.get('url',''),'eprint':source.get('arxiv_id',''),'volume':source.get('volume',''),'pages':source.get('pages','')}
            bib+='\n@article{'+key+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items() if v)+'\n}\n';keys.add(key)
        record=next((x for x in inventory['files'] if x.get('bibliography_key')==key),None)
        if record is None:
            record=dict(bibliography_key=key,filename=(source.get('arxiv_id') or key)+'.pdf',title=source['title'],edition='Publicly cited edition; see review locators',sha256=None,pdf_pages=None,role='Source for requested special-solution additions',redistributed=False)
            inventory['files'].append(record)
        record.update(review_status='selected-passages-checked',checked_passages=list(dict.fromkeys(record.get('checked_passages',[])+source['locators'])))
        if source.get('reviewed_pdf'):record.update(sha256=source['reviewed_pdf']['sha256'],pdf_pages=source['reviewed_pdf']['pages'])
    refs.write_text(bib)
    for x in manifest['extensions']:
        label=x['label'].replace('PLACEHOLDER_MINIMAL','ex:catalogue-minimal-ancient-flows')
        for path in CONTENT.glob('catalogue-*.tex'):
            s=path.read_text();anchor='\\label{'+label+'}'
            if anchor not in s:continue
            marker='% literature-extension '+x['aid'];start=s.index(anchor);end=s.index('\\end{example}',start)
            if marker not in s:s=s[:end]+marker+'\n'+x['body']+' See \\cite{'+x['key']+'}.\n'+s[end:];path.write_text(s)
            for data,field in [(properties,'examples'),(review,'entries')]:
                row=next(y for y in data[field] if y['label']==label)
                if x['key'] not in row['citations']:row['citations'].append(x['key'])
            break
        else:raise ValueError('Missing extension target '+label)
    write(ROOT/'collection.json',collection);write(ROOT/'catalogue-properties.json',properties);write(ROOT/'catalogue-visualizations.json',visuals)
    write(CONTENT/'entry-review.json',review);write(CONTENT/'source-inventory.json',inventory)
    print(f'Integrated {len(es)} reading pages and {len(manifest["extensions"])} existing-page extensions.')
if __name__=='__main__':main()
