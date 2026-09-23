"""Add three native navigation links to the accepted Atlas slide 22.
Run after build_slides.mjs and before PDF export. Standard library only.
"""
import argparse,json,re,zipfile,html
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--targets',required=True,type=Path)
a=p.parse_args()
if a.output.exists():raise SystemExit('Output already exists')
links=json.loads(a.targets.read_text())['links']
with zipfile.ZipFile(a.input) as source:
 slide=source.read('ppt/slides/slide22.xml').decode('utf-8')
 rels=source.read('ppt/slides/_rels/slide22.xml.rels').decode('utf-8')
 for link in links:
  if link['id'] in rels:raise SystemExit('Link already present')
  pattern=r'(<p:cNvPr\b[^>]*\bid="'+re.escape(link['shape_id'])+r'"[^>]*>)'
  element='<a:hlinkClick xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="'+link['id']+'"/>'
  slide,count=re.subn(pattern,lambda m:m[1]+element,slide)
  if count!=1:raise SystemExit('Shape identity mismatch')
  rels=rels.replace('</Relationships>','<Relationship Id="'+link['id']+'" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="'+html.escape(link['url'],quote=True)+'" TargetMode="External"/></Relationships>')
 with zipfile.ZipFile(a.output,'w') as out:
  for info in source.infolist():
   body=slide.encode() if info.filename=='ppt/slides/slide22.xml' else rels.encode() if info.filename=='ppt/slides/_rels/slide22.xml.rels' else source.read(info.filename)
   out.writestr(info,body)
