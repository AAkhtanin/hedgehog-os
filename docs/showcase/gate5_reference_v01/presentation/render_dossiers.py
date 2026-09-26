"""Build four searchable, bookmarked PDFs from the shared content manifest.

No candidate, provider, native runtime or archived executable is imported.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, textwrap, os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = Path(os.environ.get('G56_CAPSULE', str(ROOT if (ROOT/'content_manifest.json').exists() else ROOT/'capsule/docs/showcase/gate5_reference_v01'))).resolve()
QA_OUT = Path(os.environ.get('G56_QA_OUT',str(ROOT/'private'))).resolve()
COMMIT='64f2b38b0d671e4907bae8649fff8f3d2ee0751c'
REPO='https://github.com/AAkhtanin/hedgehog-os/blob/'+COMMIT+'/'
PUB='https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/gate5_reference_v01/'
SOURCE_RECORDS=json.loads((CAPSULE/'evidence/SOURCE_MAP.json').read_text()).get('sources',[]) if (CAPSULE/'evidence/SOURCE_MAP.json').exists() else []
INK='#1D1D1F'; BLUE='#0071E3'; MUTED='#636970'; RULE='#D9DDE2'
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf'),('Italic','DejaVuSansMono-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')

ST={
 'title':ParagraphStyle('title',fontName='Bold',fontSize=23,leading=28,textColor=colors.HexColor(INK),spaceAfter=15,keepWithNext=True),
 'section':ParagraphStyle('section',fontName='Bold',fontSize=20,leading=25,textColor=colors.HexColor(INK),spaceAfter=14,keepWithNext=True),
 'label':ParagraphStyle('label',fontName='Bold',fontSize=9,leading=13,textColor=colors.HexColor(BLUE),spaceAfter=8,keepWithNext=True),
 'body':ParagraphStyle('body',fontName='Body',fontSize=10.3,leading=15.6,textColor=colors.HexColor(INK),spaceAfter=9,allowWidows=0,allowOrphans=0,splitLongWords=1),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.3,leading=12,textColor=colors.HexColor(MUTED),spaceAfter=7,splitLongWords=1),
 'code':ParagraphStyle('code',fontName='Mono',fontSize=8.9,leading=12.7,textColor=colors.HexColor(INK),spaceAfter=9,splitLongWords=1),
 'table':ParagraphStyle('table',fontName='Body',fontSize=9.0,leading=13.2,textColor=colors.HexColor(INK),splitLongWords=1),
 'table_head':ParagraphStyle('table_head',fontName='Bold',fontSize=9.0,leading=13.2,textColor=colors.HexColor(INK),splitLongWords=1),
}

def norm(s):
    return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u2212','-')

def rich(s):
    s=html.escape(norm(s))
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font face="Mono" size="9">\1</font>',s)
    s=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="'+BLUE+r'">\1</link>',s)
    return s

def para(s,style='body'):
    return Paragraph(rich(s),ST[style])

class PublicationDoc(BaseDocTemplate):
    def __init__(self,path,title):
        self.publication_title=title;self.section_pages={}
        super().__init__(str(path),pagesize=A4,leftMargin=49,rightMargin=49,topMargin=63,bottomMargin=57,title='Radiolaria OS - '+title,author='Radiolaria OS',subject='Gate 5 Reference, engineering basis '+COMMIT)
        self.addPageTemplates(PageTemplate(id='standard',frames=[Frame(self.leftMargin,self.bottomMargin,self.width,self.height,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.decorate))
    def decorate(self,c,d):
        w,h=A4;c.saveState();c.setFont('Bold',7.7);c.setFillColor(colors.HexColor(INK));c.drawString(49,h-30,'RADIOLARIA OS / GATE 5 REFERENCE')
        c.setFont('Body',7.2);c.setFillColor(colors.HexColor(MUTED));c.drawRightString(w-49,h-30,self.publication_title.upper())
        c.setStrokeColor(colors.HexColor(RULE));c.setLineWidth(.5);c.line(49,h-39,w-49,h-39);c.line(49,39,w-49,39)
        c.setFont('Body',7.2);c.drawString(49,26,'ENGINEERING BASIS 64f2b38 / 25 SEP 2026');c.drawRightString(w-49,26,str(d.page));c.restoreState()
    def afterFlowable(self,f):
        if hasattr(f,'_section'):
            sid,title=f._section;self.canv.bookmarkPage(sid);self.canv.addOutlineEntry(sid+' '+norm(title),sid,0,False);self.section_pages[sid]=self.page

class Diagram(Flowable):
    """Editable vector mechanism diagram, explicitly distinct from an actual trace."""
    def __init__(self,labels,caption='',future=False):
        super().__init__();self.labels=labels[:4];self.caption=caption;self.future=future;self.width=497;self.height=88
    def draw(self):
        c=self.canv;n=len(self.labels);gap=16;w=(self.width-gap*(n-1))/n
        for i,label in enumerate(self.labels):
            x=i*(w+gap);c.setStrokeColor(colors.HexColor(BLUE if not self.future else MUTED));c.setLineWidth(.8)
            if self.future:c.setDash(3,3)
            c.line(x,68,x+w,68);c.setDash()
            p=Paragraph(rich(label),ST['table']);_,h=p.wrap(w,56);p.drawOn(c,x,59-h)
            if i<n-1:
                c.setStrokeColor(colors.HexColor(MUTED));c.line(x+w+2,48,x+w+gap-3,48);c.line(x+w+gap-7,51,x+w+gap-3,48);c.line(x+w+gap-7,45,x+w+gap-3,48)
        if self.caption:
            p=Paragraph(rich(self.caption),ST['small']);_,h=p.wrap(self.width,30);p.drawOn(c,0,-h+8)

DIAGRAMS={
 'F01':(['Human intent','External offer','Owner consent','Recorded booking'],'MECHANISM OVERVIEW / Recorded evidence is cited in the sections below.',False),
 'D01':(['Owner-held material','Address + metadata','Permitted payload','Local Work'],'ARCHITECTURAL MECHANISM / Addresses and material remain distinct.',False),
 'A01':(['HOW + WHAT','External author','Independent exam','Owner admission'],'DESIGN TIME / Authoring and execution are separate processes.',False),
 'D02':(['Local archive','Descriptor / index','Allowed payload','Verified context'],'CONCEPTUAL VIEW / The index may carry permitted metadata and summaries.',False),
 'D04':(['E: Work result','B: E + provenance','C: B + status','Receiving Work'],'CAUSAL REPRESENTATIONS / B.offer = E; C.body = B.',False),
 'D08':(['REVOKED saved','B process restarts','Old ACTIVE refused','New basis reviewed'],'RECORDED SEQUENCE / Persistent status prevents this tested rollback.',False),
 'D12':(['Published description','Bounded discovery','Permitted retrieval','Local work'],'FUTURE EXTENSION / Discovery and federation are not completed in G5.',True),
 'D13':(['Existing experience','New local work','Checked result','New address'],'ARCHITECTURAL EXTENSION / Publication remains an owner decision.',True),
 'A05':(['Producer result E','Later publication B','Checked context C','Independent joins'],'CONTRACT MECHANISM / The old B1 examiner confused distinct representations.',False),
 'A08':(['22-file seed','79 broker operations','23 authored files','24-file package'],'RECORDED CONSTRUCTION / The additional file is the broker manifest.',False),
}

def make_table(spec,width):
    cols=spec.get('columns') or spec.get('headers') or spec.get('header')
    rows=spec.get('rows',[])
    if not cols and rows and isinstance(rows[0],dict):cols=list(rows[0])
    if not cols:return []
    data=[cols]+[[r.get(k,'') for k in cols] if isinstance(r,dict) else r for r in rows]
    n=len(cols)
    widths=spec.get('widths')
    if widths:
        widths=[width*x/sum(widths) for x in widths]
    elif n==2:widths=[width*.31,width*.69]
    elif n==3:widths=[width*.25,width*.375,width*.375]
    elif n==4:widths=[width*.23,width*.25,width*.26,width*.26]
    elif n>=5:
        widths=[width*.3]+[width*.7/(n-1)]*(n-1)
    else:widths=[width/n]*n
    cooked=[]
    for i,row in enumerate(data):
        row=list(row)+['']*max(0,n-len(row))
        cooked.append([Paragraph(rich(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v),ST['table_head' if i==0 else 'table']) for v in row[:n]])
    t=Table(cooked,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F1F5FA')),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor(BLUE)),('LINEBELOW',(0,1),(-1,-1),.4,colors.HexColor(RULE)),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    out=[]
    if spec.get('title'):out.append(para(spec['title'],'label'))
    out.extend([t,Spacer(1,12)]);return out

def source_url(ref):
    if isinstance(ref,str):return PUB+'evidence/SOURCE_MAP.json',ref
    url=ref.get('url') or ref.get('source_url')
    path=ref.get('repo_path') or ref.get('path')
    member=ref.get('member') or ref.get('archive_member')
    if member and ref.get('sha256'):
        found=[r for r in SOURCE_RECORDS if r.get('sha256')==ref['sha256'] and r.get('archive_id')==ref.get('archive_id')]
        if found:
            sr=found[0]
            if sr.get('capsule_relative_path'):url=PUB+sr['capsule_relative_path']
            elif sr.get('github_url'):url=sr['github_url']
    if not url and path and not path.startswith('/') and not member:url=REPO+path
    if not url:url=PUB+'evidence/SOURCE_MAP.json'
    archive=ref.get('archive_id') or ref.get('archive_key') or ref.get('archive','')
    label=ref.get('source_id') or (str(archive)+': '+str(member) if member else path) or ref.get('id') or 'Source record'
    return url,str(label)

def section_story(sec,width,first=False,dossier_title=None):
    sid=sec['section_id'];title=sec['title'];out=[]
    if first and dossier_title:out.extend([para(dossier_title,'label')])
    out.append(para(sid+' / '+sec.get('eyebrow','GATE 5 REFERENCE'),'label'))
    heading=para(title,'section');heading._section=(sid,title);out.append(heading)
    if sid in DIAGRAMS:out.extend([Diagram(*DIAGRAMS[sid]),Spacer(1,15)])
    for text in sec.get('paragraphs',[]):
        if isinstance(text,dict):text=text.get('text',str(text))
        out.append(para(text))
    for spec in sec.get('tables',[]):out.extend(make_table(spec,width))
    for block in sec.get('code_blocks',[]):
        if isinstance(block,str):code=block;title=''
        else:code=block.get('text') or block.get('code') or block.get('content','');title=block.get('title') or block.get('label','')
        if title:out.append(para(title,'label'))
        for line in str(code).splitlines():
            # Long JSON strings wrap without shrinking the type size.
            out.append(Paragraph(html.escape(norm(line)).replace(' ','&#160;'),ST['code']))
    refs=sec.get('evidence_refs',[])
    if refs:
        links=[]
        for ref in refs[:4]:
            url,label=source_url(ref)
            if isinstance(ref,dict):label=ref.get('source_id') or (str(ref.get('archive_id',''))+': '+str(ref.get('member') or ref.get('archive_member') or ref.get('repo_path') or ref.get('path') or 'source').split('/')[-1]).lstrip(': ')
            links.append('<link href="'+html.escape(url,quote=True)+'" color="'+BLUE+'">'+html.escape(norm(label))+'</link>')
        links.append('<link href="'+PUB+'evidence/SOURCE_MAP.json" color="'+BLUE+'">Full exact source map</link>')
        out.append(Spacer(1,4));out.append(Paragraph('<b>Sources:</b> '+ '; '.join(links)+'.',ST['small']))
    return out

def write_doc(path,title,sections,appendix=False):
    doc=PublicationDoc(path,title);story=[]
    if appendix:
        story=[para('TECHNICAL APPENDIX','label'),para('One architecture.\nThree views.','title'),para('Gate 5 Reference connects a working football domain, evidence exchange between independent owners, and externally authored software. This volume contains the same F, D and A sections as the standalone dossiers, preceded by the shared basis and verification guide.'),para('Engineering basis: '+COMMIT,'small'),para('Reading routes','label')]
        routes=[['F / Football Domain','What changed between the original request and the recorded booking?'],['D / External DRS','How did another owner\'s material become a verified input?'],['A / Independent Authoring','What did the author receive, construct and control?'],['X / Shared basis','How do claims, history, publication and verification fit together?']]
        story.extend(make_table({'columns':['Route','Question'],'rows':routes},doc.width))
        story.extend([para('The saved experiment uses a synthetic venue and an explicitly amended authoring protocol. G55L is published. This documentation package is prepared for independent review and subsequent G56 publication. Its own future commit is not invented.'),para('PDF bookmarks and stable section IDs preserve the same navigation across all four documents. Source links refer to the accepted engineering commit, original archive members, or the linked publication corpus. Repository access is required while GitHub remains private.','small'),PageBreak()])
    for i,sec in enumerate(sections):
        if i:story.append(PageBreak())
        story.extend(section_story(sec,doc.width,first=(i==0),dossier_title=title))
    doc.build(story)
    return {'path':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':doc.page,'sections':doc.section_pages}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',default=str(CAPSULE/'content_manifest.json'));a=parser.parse_args()
    manifest=json.loads(Path(a.manifest).read_text());dossiers=manifest['dossiers'];outputs=[]
    for key,name,title in [('F','football_domain_v01.pdf','Football Domain'),('D','external_drs_v01.pdf','External DRS'),('A','independent_authoring_v01.pdf','Independent Authoring')]:
        outputs.append(write_doc(CAPSULE/name,title,dossiers[key]['sections']))
    sections=dossiers['X']['sections']+dossiers['F']['sections']+dossiers['D']['sections']+dossiers['A']['sections']
    outputs.append(write_doc(CAPSULE/'technical_appendix_v01.pdf','Technical Appendix',sections,True))
    QA_OUT.mkdir(parents=True,exist_ok=True)
    (QA_OUT/'pdf_build_report.json').write_text(json.dumps(outputs,indent=2)+'\n');print(json.dumps(outputs,indent=2))

if __name__=='__main__':main()
