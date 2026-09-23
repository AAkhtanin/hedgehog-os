"""Render the English Gate4 appendix from Markdown. No project imports.

Requires reportlab, supplied separately. Font files are local build inputs and
are never copied into the publication. Run with explicit source/output paths.
"""
from pathlib import Path
import argparse, html, json, re
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ap=argparse.ArgumentParser()
ap.add_argument('--input',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--font-regular',type=Path,required=True)
ap.add_argument('--font-bold',type=Path,required=True)
ap.add_argument('--anchors',type=Path,required=True)
a=ap.parse_args()
for name,p in [('Inter',a.font_regular),('InterBold',a.font_bold)]:
    pdfmetrics.registerFont(TTFont(name,str(p)))
pdfmetrics.registerFontFamily('Inter',normal='Inter',bold='InterBold',italic='Inter',boldItalic='InterBold')
INK=HexColor('#1D1D1F'); GRAY=HexColor('#6E6E73'); BLUE=HexColor('#0071E3'); PALE=HexColor('#F5F5F7')
styles={
 'body':ParagraphStyle('body',fontName='Inter',fontSize=10.4,leading=14.5,spaceAfter=7,textColor=INK,splitLongWords=True),
 'small':ParagraphStyle('small',fontName='Inter',fontSize=8.8,leading=12.4,spaceAfter=7,textColor=GRAY,splitLongWords=True),
 'h1':ParagraphStyle('h1',fontName='InterBold',fontSize=25,leading=30,spaceAfter=18,textColor=INK,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='InterBold',fontSize=19,leading=24,spaceBefore=14,spaceAfter=12,textColor=INK,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='InterBold',fontSize=11.5,leading=16,spaceBefore=12,spaceAfter=7,textColor=BLUE,keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='Inter',fontSize=9.3,leading=12.4,textColor=INK,splitLongWords=True),
 'code':ParagraphStyle('code',fontName='Inter',fontSize=9.2,leading=13,spaceAfter=9,textColor=INK,backColor=PALE,borderPadding=8,splitLongWords=True),
}
def normalize(s):
    return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ')
def link_target(target):
    if target.startswith(('http://','https://','#')):return target
    return 'https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/gate4_reference_v01/'+target
def inline(s):
    s=html.escape(normalize(s))
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<link href="'+link_target(m[2])+'" color="#0071E3">'+m[1]+'</link>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font color="#384B60">\1</font>',s)
    s=s.replace('<br>','<br/>').replace('&lt;br&gt;','<br/>')
    return s
anchors={}
class Doc(BaseDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and hasattr(f,'heading_key'):
            key=f.heading_key; level=f.heading_level
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(),key,level=0 if level==0 else 1)
            anchors[key]={'page':self.page,'title':f.getPlainText()}
            self.notify('TOCEntry',(level,f.getPlainText(),self.page,key))
def page(c,doc):
    c.saveState();c.setFillColor(GRAY);c.setFont('Inter',8)
    c.drawString(46,812,'RADIOLARIA OS  /  GATE 4 REFERENCE')
    c.setStrokeColor(HexColor('#D2D2D7'));c.setLineWidth(.5);c.line(46,801,549,801)
    c.line(46,40,549,40);c.drawString(46,26,'Technical appendix  /  Implementation 5b259441  /  23 September 2026')
    c.drawRightString(549,26,str(doc.page));c.restoreState()

a.output.parent.mkdir(parents=True,exist_ok=True)
doc=Doc(str(a.output),pagesize=(595.28,841.89),leftMargin=46,rightMargin=46,topMargin=59,bottomMargin=53,
 title='Radiolaria OS - Gate 4 Reference - Technical Appendix',author='Radiolaria OS',pageCompression=1)
doc.addPageTemplates(PageTemplate(id='normal',frames=[Frame(46,53,503.28,739.89,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page))
flow=[];lines=a.input.read_text().splitlines();i=0;firstsection=True;pending_anchor=None
def para(s,style='body'):return Paragraph(inline(s),styles[style])
def heading(s,level):
    global pending_anchor
    p=para(s,'h2' if level==0 else 'h3');p.heading_key=pending_anchor or re.sub('[^a-z0-9]+','-',s.lower()).strip('-');p.heading_level=level;pending_anchor=None;return p
while i<len(lines):
    line=lines[i].strip()
    if not line or line=='---':i+=1;continue
    if line == '## Contents':
        i+=1
        while i<len(lines) and not lines[i].strip().startswith('<a id='):i+=1
        continue
    if line.startswith('<a id='):
        pending_anchor=re.search(r'id="([^"]+)"',line).group(1);i+=1;continue
    if line.startswith('# '):
        flow.append(para(line[2:],'h1'));flow.append(para('Finite strategy comparison and allocation of actual Work','h3'));i+=1;continue
    if line.startswith('## '):
        if firstsection:
            flow.append(Spacer(1,12));flow.append(para('Contents','h2'))
            toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',fontName='Inter',fontSize=10.4,leading=16,leftIndent=0,firstLineIndent=0,spaceBefore=5,textColor=INK),ParagraphStyle('toc1',fontName='Inter',fontSize=9,leading=13,leftIndent=14,firstLineIndent=0,textColor=GRAY)]
            flow.append(toc);firstsection=False
        flow.append(PageBreak());flow.append(heading(line[3:],0));i+=1;continue
    if line.startswith('### '):flow.append(heading(line[4:],1));i+=1;continue
    if line.startswith('```'):
        buf=[];i+=1
        while i<len(lines) and not lines[i].strip().startswith('```'):buf.append(lines[i]);i+=1
        flow.append(Paragraph('<br/>'.join(html.escape(normalize(x)) for x in buf),styles['code']));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            raw=lines[i].strip().strip('|'); cells=[x.strip() for x in raw.split('|')]
            if not all(re.fullmatch(r'[:\- ]+',x or '-') for x in cells):rows.append(cells)
            i+=1
        n=max(map(len,rows));rows=[r+['']*(n-len(r)) for r in rows]
        # Relative column widths reflect the observed amount of content, bounded
        # to keep exact number columns readable and source locators wrappable.
        weights=[max(7,min(38,max(len(re.sub(r'`|\*','',r[j])) for r in rows))) for j in range(n)]
        widths=[503.28*x/sum(weights) for x in weights]
        if rows[0][0]=='Comparison':widths=[84,150,110,159.28]
        data=[[Paragraph(('<b>'+inline(v)+'</b>') if k==0 else inline(v),styles['cell']) for v in r] for k,r in enumerate(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,BLUE),('LINEBELOW',(0,1),(-1,-1),.25,HexColor('#D2D2D7')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        flow.extend([t,Spacer(1,11)]);continue
    if line.startswith(('- ','* ')):
        flow.append(para('• '+line[2:]));i+=1;continue
    buf=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','```','- ','* ')):
        buf.append(lines[i].strip());i+=1
    flow.append(para(' '.join(buf)))
doc.multiBuild(flow)
a.anchors.write_text(json.dumps(anchors,indent=2)+'\n')
print(json.dumps({'output':str(a.output),'pages':doc.page,'anchors':len(anchors)}))
