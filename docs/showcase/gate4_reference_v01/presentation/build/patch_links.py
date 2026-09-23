"""Add hyperlinks to native slide text shapes before finalization."""
import json,sys,zipfile,xml.etree.ElementTree as E
from pathlib import Path
src,out,nav=map(Path,sys.argv[1:]);links=json.loads(nav.read_text())
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
R='http://schemas.openxmlformats.org/package/2006/relationships'
for k,v in NS.items():E.register_namespace(k,v)
changes={}
with zipfile.ZipFile(src) as z:
 for n in range(1,13):
  sp=f'ppt/slides/slide{n}.xml';rp=f'ppt/slides/_rels/slide{n}.xml.rels';s=E.fromstring(z.read(sp));r=E.fromstring(z.read(rp));
  # Artifact preview uses zero text insets. Materialize them for Office/LibreOffice parity.
  for body in s.findall('.//p:sp/p:txBody/a:bodyPr',NS):
   for edge in ['lIns','rIns','tIns','bIns']:body.set(edge,'0')
  for idx,l in enumerate([x for x in links if x['slide']==n]):
   matches=[v for v in s.findall('.//p:cNvPr',NS) if v.get('name')==l['name']]
   if len(matches)!=1:raise ValueError((l['name'],len(matches)))
   rid=f'rIdG4Link{idx+1}';E.SubElement(matches[0],'{'+NS['a']+'}hlinkClick',{'{'+NS['r']+'}id':rid});E.SubElement(r,'{'+R+'}Relationship',{'Id':rid,'Type':NS['r']+'/hyperlink','Target':l['url'],'TargetMode':'External'})
  changes[sp]=E.tostring(s,encoding='utf-8',xml_declaration=True);changes[rp]=E.tostring(r,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as o:
  for info in z.infolist():o.writestr(info,changes.get(info.filename,z.read(info.filename)))
