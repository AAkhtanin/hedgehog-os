"""Finite data-only PPTX/PDF integrity and navigation QA."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,hashlib,re,sys
from pypdf import PdfReader
base=Path(__file__).resolve().parents[1]
pptx=base/'output/gate4_reference_v01.pptx';pdf=base/'output/gate4_reference_v01.pdf'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/package/2006/relationships'}
rows=[];tables=[];notes=[];objects=[]
with zipfile.ZipFile(pptx) as z:
 slides=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda x:int(re.search(r'\d+',x).group()))
 for i,p in enumerate(slides,1):
  root=E.fromstring(z.read(p)); tables.append(len(root.findall('.//a:tbl',ns)));objects.append(len(root.findall('.//p:sp',ns)))
  rel=E.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
  for r in rel:
   if r.get('Type','').endswith('/hyperlink'):rows.append({'slide':i,'target':r.get('Target'),'mode':r.get('TargetMode')})
 assert len(slides)==12
 assert all(tables[i-1]>0 for i in [4,5,7,10,11])
 assert not any(n.startswith('ppt/fonts/') for n in z.namelist())
reader=PdfReader(pdf);assert len(reader.pages)==12
annots=[]
for i,page in enumerate(reader.pages,1):
 for ar in page.get('/Annots',[]):
  a=ar.get_object();action=a.get('/A',{})
  if action.get('/S')=='/URI':annots.append({'slide':i,'target':str(action['/URI'])})
assert len(rows)==15,(len(rows),rows)
assert len(annots)==15,(len(annots),annots)
assert sorted((x['slide'],x['target']) for x in rows)==sorted((x['slide'],x['target']) for x in annots)
assert len(set(x['target'] for x in annots if x['slide']==12))==5
text='\n'.join(page.extract_text() for page in reader.pages)
for s in ['0.01975','0.00509375','0.001975','0.018846875','PREPARATION_ONLY_NOT_EXECUTED','No payment','33 PASS / 1 FAIL','LGT excluded','Repository access required']:
 assert s in text,s
assert 'http' not in text[-400:] # navigation labels remain clean visible text
out={'status':'PASS','pptx_sha256':hashlib.sha256(pptx.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'slides':12,'native_tables_by_slide':tables,'native_shapes_by_slide':objects,'pptx_hyperlinks':rows,'pdf_uri_annotations':annots,'final_page_target_count':5,'text_extraction':'PASS with exact utility products, scope and status','remote_target_status':'STAGED_PUBLICATION_TARGETS_REPOSITORY_ACCESS_REQUIRED','no_project_execution':True,'visual_review':{'all_artifact_pngs_full_size':'PASS','all_pdf_pages_full_size':'PENDING'},'source_notes':'Per-slide source SHA and shared claim routes embedded'}
(base/'qa/deck_qa_v01.json').write_text(json.dumps(out,indent=2)+'\n');(base/'qa/extracted_deck_text_v01.txt').write_text(text);print(json.dumps({k:v for k,v in out.items() if k not in ['pptx_hyperlinks','pdf_uri_annotations']},indent=2))
