#!/usr/bin/env python3
"""Render the English Sentinel support PDFs from final Markdown content."""
from pathlib import Path
import re, html, json, hashlib, sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Frame
from pypdf import PdfReader
from fontTools.ttLib import TTFont as FontToolsFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)
FONT=ROOT/'assets/fonts'
named_bold=ROOT/'build/pdf_qa/Inter-Bold-ReportLab.ttf'
bf=FontToolsFont(FONT/'Inter-Bold.ttf')
for rec in bf['name'].names:
    if rec.nameID in (2,4,6,17):
        values={2:'Bold',4:'Inter Bold',6:'Inter-Bold',17:'Bold'}
        rec.string=values[rec.nameID].encode(rec.getEncoding())
bf.save(named_bold)
pdfmetrics.registerFont(TTFont('Inter',str(FONT/'Inter-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Inter-Bold',str(named_bold)))
pdfmetrics.registerFontFamily('Inter',normal='Inter',bold='Inter-Bold',italic='Inter',boldItalic='Inter-Bold')
INK=colors.HexColor('#1D1D1F')
GRAY=colors.HexColor('#6E6E73')
BLUE=colors.HexColor('#0071E3')
RULE=colors.HexColor('#DCE1E7')
PALE=colors.HexColor('#F6F8FB')
COMMIT='2f328be634247be11bc18a3b22a919f393d6ed1d'
SHOWCASE='https://github.com/AAkhtanin/hedgehog-os/tree/'+COMMIT+'/docs/showcase/landslide_sentinel_v01'

def clean(s):
    return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ').replace('\u2192',' > ')

def inline(s):
    s=clean(s)
    tokens=[]
    def stash(x):
        tokens.append(x)
        return f'ZZZTOKEN{len(tokens)-1}ZZZ'
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:stash('<link href="'+html.escape(m[2],quote=True)+'" color="#0071E3">'+html.escape(m[1])+'</link>'),s)
    s=re.sub(r'`([^`]+)`',lambda m:stash('<font color="#40516A">'+html.escape(m[1])+'</font>'),s)
    s=html.escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\*(.+?)\*',r'<i>\1</i>',s)
    for n,t in enumerate(tokens): s=s.replace(f'ZZZTOKEN{n}ZZZ',t)
    return s

ST={
 'body':ParagraphStyle('body',fontName='Inter',fontSize=9.3,leading=13.2,textColor=INK,spaceAfter=8,splitLongWords=1),
 'small':ParagraphStyle('small',fontName='Inter',fontSize=7.5,leading=10.2,textColor=GRAY,spaceAfter=7,splitLongWords=1),
 'h1':ParagraphStyle('h1',fontName='Inter-Bold',fontSize=29,leading=33,textColor=INK,spaceAfter=14,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='Inter-Bold',fontSize=15.5,leading=20,textColor=INK,spaceBefore=17,spaceAfter=10,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='Inter-Bold',fontSize=10.6,leading=14,textColor=BLUE,spaceBefore=10,spaceAfter=6,keepWithNext=True),
 'table':ParagraphStyle('table',fontName='Inter',fontSize=7.8,leading=10.4,textColor=INK,splitLongWords=1),
 'thead':ParagraphStyle('thead',fontName='Inter-Bold',fontSize=7.9,leading=10.6,textColor=INK,splitLongWords=1),
 'code':ParagraphStyle('code',fontName='Inter',fontSize=7.5,leading=10,textColor=INK,backColor=PALE,borderPadding=9,spaceBefore=5,spaceAfter=9,splitLongWords=1),
 'bullet':ParagraphStyle('bullet',fontName='Inter',fontSize=9.3,leading=13.2,textColor=INK,leftIndent=12,firstLineIndent=-10,spaceAfter=5,splitLongWords=1),
}

for _style in ST.values():
    _style.allowWidows=0
    _style.allowOrphans=0

def footer(c,doc):
    w,h=A4
    c.saveState()
    c.setStrokeColor(RULE); c.setLineWidth(.45); c.line(44,38,w-44,38)
    c.setFont('Inter',7); c.setFillColor(GRAY)
    c.drawString(44,25,'RADIOLARIA OS  /  LANDSLIDE SENTINEL v0.1')
    c.drawRightString(w-44,25,f'COMMIT {COMMIT[:7]}  /  {doc.page}')
    if doc.page>1:
        c.setFont('Inter',7);c.setFillColor(GRAY)
        c.drawString(44,h-27,'TECHNICAL APPENDIX')
        c.drawRightString(w-44,h-27,'PRESENTATION UPDATE 21 SEPTEMBER 2026')
    c.restoreState()

def make_table(lines,width):
    rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    rows=[r for r in rows if not all(re.fullmatch(r':?-{2,}:?',v or '-') for v in r)]
    n=max(len(x) for x in rows)
    for r in rows:r.extend(['']*(n-len(r)))
    if n==2: widths=[width*.29,width*.71]
    elif n==3:
        if rows[0][0].lower() in ('id','requirement','row'): widths=[width*.14,width*.22,width*.64]
        else: widths=[width*.25,width*.32,width*.43]
    elif n==4: widths=[width*.10,width*.17,width*.36,width*.37]
    else:widths=[width/n]*n
    data=[[Paragraph(inline(v),ST['thead'] if ri==0 else ST['table']) for v in r] for ri,r in enumerate(rows)]
    split_range=(2,len(data)-2) if len(data)>=5 else None
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT',rowSplitRange=split_range)
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),.8,INK),('LINEBELOW',(0,1),(-1,-1),.35,RULE)]
    for ri in range(1,len(rows)):
        if ri%2:cmds.append(('BACKGROUND',(0,ri),(-1,ri),PALE))
    t.setStyle(TableStyle(cmds))
    return [Spacer(1,5),t,Spacer(1,9)]

def markdown_flow(path,width):
    lines=path.read_text().splitlines()
    out=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):code.append(lines[i]);i+=1
            out.append(Paragraph('<br/>'.join(html.escape(clean(x)).replace(' ','&nbsp;') for x in code),ST['code']))
            i+=1;continue
        if line.startswith('|'):
            group=[]
            while i<len(lines) and lines[i].strip().startswith('|'):group.append(lines[i]);i+=1
            out.extend(make_table(group,width));continue
        if line.startswith('#'):
            m=re.match(r'^(#{1,6})\s+(.*)',line)
            if m:
                level=len(m[1]);style='h1' if level==1 else 'h2' if level==2 else 'h3'
                
                if 'Source index for this account' in m[2] or m[2].startswith('23. Research'): out.append(PageBreak())
                out.append(Paragraph(inline(m[2]),ST[style]));i+=1;continue
        if re.match(r'^[-*] ',line):
            out.append(Paragraph('&#8226; '+inline(line[2:]),ST['bullet']));i+=1;continue
        if re.match(r'^\d+\. ',line):
            out.append(Paragraph(inline(line),ST['bullet']));i+=1;continue
        para=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|[-*] |\d+\. )',lines[i].strip()):para.append(lines[i].strip());i+=1
        joined=' '.join(para)
        style='small' if joined.startswith(('Sources:','Source:','Evidence:','Commit:','Repository:')) else 'body'
        out.append(Paragraph(inline(joined),ST[style]))
    return out

def technical():
    source=ROOT/'content/technical_appendix_v01.md'
    if not source.exists():raise FileNotFoundError(source)
    out=OUT/'technical_appendix_v01.pdf'
    doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=47,bottomMargin=54,title='Landslide Sentinel v0.1 - Technical Appendix',author='Radiolaria OS',subject='Source-bound walkthrough and scoped evidence')
    doc.build(markdown_flow(source,A4[0]-88),onFirstPage=footer,onLaterPages=footer)
    return out

def onepager():
    p=OUT/'executive_one_pager_v01.pdf'
    w,h=landscape(A4)
    c=canvas.Canvas(str(p),pagesize=(w,h),pageCompression=1)
    c.setTitle('Landslide Sentinel v0.1 - Executive Overview')
    c.setAuthor('Radiolaria OS')
    c.setFillColor(colors.white);c.rect(0,0,w,h,fill=1,stroke=0)
    c.drawImage(str(ROOT/'assets/radiolaria_landslide_sentinel_hero.png'),w-363,h-204,width=325,height=325*941/1672,mask='auto')
    c.setFillColor(BLUE);c.setFont('Inter-Bold',10);c.drawString(42,h-39,'RADIOLARIA OS')
    c.setFillColor(INK);c.setFont('Inter-Bold',33);c.drawString(40,h-88,'Landslide Sentinel')
    c.setFont('Inter-Bold',15);c.drawString(42,h-117,'A local cell with replaceable intelligence.')
    c.setFont('Inter',9.8);c.setFillColor(GRAY);c.drawString(42,h-141,'Live meaning. Current authority. Bounded actions. Inspectable evidence.')
    c.setFont('Inter',7.4);c.drawString(42,h-164,'v0.1  /  15 SEPTEMBER 2026  /  COMMITTED IMPLEMENTATION '+COMMIT[:7])
    c.setStrokeColor(RULE);c.setLineWidth(.6);c.line(42,h-185,w-42,h-185)
    body=ParagraphStyle('onebody',fontName='Inter',fontSize=9.0,leading=12.9,textColor=INK,spaceAfter=8,splitLongWords=1)
    head=ParagraphStyle('onehead',fontName='Inter-Bold',fontSize=11.2,leading=15,textColor=INK,spaceAfter=7,spaceBefore=7,keepWithNext=True)
    small=ParagraphStyle('onesmall',fontName='Inter',fontSize=8.0,leading=11.2,textColor=GRAY,spaceAfter=6,splitLongWords=1)
    sections={};current=None
    for line in (ROOT/'content/executive_one_pager_v01.md').read_text().splitlines():
        if line.startswith('## '):current=line[3:];sections[current]=[]
        elif current and line.strip():sections[current].append(line)
    def section(name,style=body):
        flow=[Paragraph(inline(name),head)]
        for t in sections[name]:flow.append(Paragraph(inline(t[2:] if t.startswith('- ') else t),style))
        return flow
    left=section('The demonstrated lifecycle')+section('Measured, with scopes intact',small)
    right=section('What the evidence establishes')+section('Scope and limits',small)
    colw=(w-106)/2;top=h-195;bottom=74
    for x,flow in [(42,left),(64+colw,right)]:
        f=Frame(x,bottom,colw,top-bottom,leftPadding=0,bottomPadding=0,rightPadding=0,topPadding=0)
        f.addFromList(flow,c)
        if flow:raise RuntimeError('One-pager content overflow')
    c.setStrokeColor(RULE);c.line(42,64,w-42,64)
    c.setFillColor(BLUE);c.setFont('Inter-Bold',8);c.drawString(42,48,'INSPECT THE IMPLEMENTATION. VERIFY THE EVIDENCE.')
    c.linkURL(SHOWCASE,(42,43,455,59),relative=0,thickness=0)
    c.setFillColor(GRAY);c.setFont('Inter',7)
    c.drawString(42,32,'Pinned showcase  /  Technical appendix  /  One-file LLM reader')
    c.drawRightString(w-42,48,'SAFE DERIVATIVE REPLAY: ANCHORED_PASS')
    c.drawRightString(w-42,32,'Conceptual artwork; not runtime topology or execution evidence.')
    c.save()
    return p

if __name__=='__main__':
    selected=sys.argv[1:]
    paths=[]
    if not selected or 'onepager' in selected:paths.append(onepager())
    if not selected or 'technical' in selected:paths.append(technical())
    checks=[]
    for p in paths:
        r=PdfReader(p)
        checks.append({'file':p.name,'pages':len(r.pages),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'extracted_characters':sum(len(x.extract_text() or '') for x in r.pages),'font':'Embedded Inter Regular and Bold'})
    checkpath=ROOT/'build/pdf_qa/text_checks.json'
    previous=json.loads(checkpath.read_text()) if checkpath.exists() else []
    combined={x['file']:x for x in previous+checks}
    checkpath.write_text(json.dumps(list(combined.values()),indent=2)+'\n')
    print(json.dumps(checks,indent=2))
