"""Render the frozen English appendix; no project imports or runtime calls.
Requires reportlab and two user-supplied Inter TTF fonts. Fonts are not redistributed.
"""
from pathlib import Path
import argparse,json,re,html
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ap=argparse.ArgumentParser()
ap.add_argument('--content',type=Path,required=True)
ap.add_argument('--font-regular',type=Path,required=True)
ap.add_argument('--font-bold',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args()
if a.output.exists(): raise SystemExit('Output already exists; use a new path.')
a.output.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Inter',str(a.font_regular)))
pdfmetrics.registerFont(TTFont('InterBold',str(a.font_bold)))
pdfmetrics.registerFontFamily('Inter',normal='Inter',bold='InterBold',italic='Inter',boldItalic='InterBold')
INK=HexColor('#1D1D1F');GRAY=HexColor('#6E6E73');BLUE=HexColor('#0071E3');PALE=HexColor('#F5F5F7')
STYLES={
 'body':ParagraphStyle('body',fontName='Inter',fontSize=10.2,leading=14.6,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Inter',fontSize=8.3,leading=11.4,textColor=GRAY,spaceAfter=6,splitLongWords=True),
 'title':ParagraphStyle('title',fontName='InterBold',fontSize=24,leading=29,textColor=INK,spaceAfter=16),
 'sub':ParagraphStyle('sub',fontName='InterBold',fontSize=11,leading=15,textColor=BLUE,spaceBefore=8,spaceAfter=6),
 'cell':ParagraphStyle('cell',fontName='Inter',fontSize=9.1,leading=12.5,textColor=INK),
 'cellsmall':ParagraphStyle('cellsmall',fontName='Inter',fontSize=8.2,leading=11,textColor=INK),
}
def plain(s):
 return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ')
def esc(s): return html.escape(plain(s)).replace('\n','<br/>')
pages=json.loads(a.content.read_text())['pages']
def draw_para(c,text,y,style='body',x=44,width=524):
 # Link verified web URLs; no transient filesystem links are emitted.
 text=esc(text)
 text=re.sub(r'(https://[^\s<]+)',r'<link href="\1" color="#0071E3">\1</link>',text)
 p=Paragraph(text,STYLES[style]); w,h=p.wrap(width,750)
 p.drawOn(c,x,y-h)
 return y-h-STYLES[style].spaceAfter

def render():
 path=a.output
 c=canvas.Canvas(str(path),pagesize=(612,792),pageCompression=1)
 c.setTitle('Radiolaria OS | Incident-to-Proof Atlas | Technical Appendix V02')
 c.setAuthor('Radiolaria OS')
 c.setSubject('Twenty finite cases, five experience consumers and source-bound saved verification')
 layout=[]
 for index,p in enumerate(pages,1):
  c.bookmarkPage(p['key']);c.addOutlineEntry(p['key']+' | '+p['title'],p['key'],level=0)
  c.setFillColor(white);c.rect(0,0,612,792,fill=1,stroke=0)
  c.setFont('Inter',8);c.setFillColor(GRAY);c.drawString(44,760,p['subtitle'])
  y=draw_para(c,p['title'],730,'title')
  for b in p['blocks']:
   if b[0]=='table':
    _,headers,rows,widths=b; widths=widths or [524/len(headers)]*len(headers)
    data=[[Paragraph('<b>'+esc(v)+'</b>',STYLES['cell']) for v in headers]]+[[Paragraph(esc(v),STYLES['cellsmall'] if len(rows)>10 else STYLES['cell']) for v in row] for row in rows]
    pad=5 if p['key']=='math' else 7
    t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,BLUE),('LINEBELOW',(0,1),(-1,-1),.25,HexColor('#DEDEE3')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad)]))
    _,h=t.wrap(524,720); t.drawOn(c,44,y-h); y-=h+14
   else:y=draw_para(c,b[1],y,{'p':'body','small':'small','sub':'sub'}[b[0]])
  layout.append({'page':index,'key':p['key'],'bottom':round(y,1)})
  if y<48:raise ValueError(f'Overflow page {index} {p["key"]}: bottom {y}')
  c.setStrokeColor(HexColor('#DEDEE3'));c.setLineWidth(.5);c.line(44,36,568,36)
  c.setFillColor(GRAY);c.setFont('Inter',7.5);c.drawString(44,22,'RADIOLARIA OS | Recorded finite proof | Implementation e538790')
  c.drawRightString(568,22,f'{index:02} / {len(pages):02}');c.showPage()
 c.save()
 print(json.dumps({'pdf':str(path),'pages':len(pages),'minimum_bottom':min(x['bottom'] for x in layout)}))

if __name__=='__main__':render()
