import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {Presentation, PresentationFile, FileBlob} from '@oai/artifact-tool';
import {GlobalFonts, createCanvas} from '@napi-rs/canvas';
import {finalizePresentation,applyPresentationChartFont} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';

const ROOT='/workspace/scratch/7085cdc7c562';
const BASE=path.join(ROOT,'sentinel_presentation');
const BUILD=path.join(BASE,'build');
const REV=process.argv[2] || 'v01';
const OUT=path.join(BASE,'output',REV);
const REF=path.join(ROOT,'presentation/package/files/docs/showcase/ephemeral_workspace_v01/ephemeral_workspace_showcase_v01.pptx');
const FONTDIR=path.join(ROOT,'presentation/package/files/docs/showcase/ephemeral_workspace_v01/assets/fonts');
const FONT='Inter';
const INK='#1D1D1F',BLUE='#0071E3',GREY='#6E6E73',LINE='#D2D2D7',LIGHT='#F5F5F7';
GlobalFonts.registerFromPath(path.join(FONTDIR,'Inter-Regular.ttf'),FONT);
GlobalFonts.registerFromPath(path.join(FONTDIR,'Inter-Bold.ttf'),FONT);
const measure=createCanvas(1280,720).getContext('2d');
const content=JSON.parse(await fs.readFile(path.join(BASE,'content/slides_v01.json'),'utf8'));
const reference=await PresentationFile.importPptx(await FileBlob.load(REF));
await fs.writeFile(path.join(BUILD,'reference_layout_inspection.ndjson'),(await reference.inspect({kind:'layout',maxChars:100000})).ndjson);
const proto=reference.toProto();
const layoutId=proto.slides[0].useLayoutId;
proto.slides=[];proto.images=[];proto.charts=[];proto.contentReferences=[];proto.threads=[];proto.people=[];
const p=Presentation.load(proto),geometry=[],tableOwners=[],chartOwners=[];
let current;
function wrap(value,width,size,bold=false){
  measure.font=`${bold?'bold ':''}${size}px ${FONT}`;
  return String(value).split('\n').map(line=>{
    const out=[];let s='';
    for(const word of line.split(' ')){const n=s?s+' '+word:word;if(s&&measure.measureText(n).width>width){out.push(s);s=word;}else s=n;}
    out.push(s);return out.join('\n');
  }).join('\n');
}
function text(sl,value,x,y,w,size=26,bold=false,color=INK,h,align='left'){
  if(value===undefined||value===null||value==='')return 0;
  const str=String(value),lines=wrap(str,w*.96,size,bold).split('\n').length;
  h=h??Math.ceil(lines*size*1.25+10);
  const sh=sl.shapes.add({geometry:'textbox',name:`text-${current.number}-${geometry.length}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=str;sh.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',wrap:true,verticalAlignment:'top',alignment:align,insetLeft:0,insetRight:0,insetTop:0,insetBottom:0};
  geometry.push({slide:current.number,kind:'text',x,y,w,h,size,text:str,estimatedLines:lines});return h;
}
function rule(sl,x,y,w,color=LINE,width=1){sl.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width}});}
function arrayBody(value){return Array.isArray(value)?value:(value?[value]:[]);}
function paragraphs(sl,body,x,y,w,size=27,gap=22){for(const q of arrayBody(body)){y+=text(sl,q,x,y,w,size,false,INK)+gap;}return y;}
function fittingParagraphs(sl,body,x,y,w,size=29,maxBottom=605){
  const lines=arrayBody(body);let gap=24;
  function required(){return lines.reduce((sum,q)=>sum+Math.ceil(wrap(q,w*.96,size).split('\n').length*size*1.25+10)+gap,0)-gap;}
  while(required()>maxBottom-y&&size>24){size-=1;gap=Math.max(15,gap-1);}
  if(required()>maxBottom-y)throw new Error(`Slide ${current.number}: body cannot fit at24px`);
  return paragraphs(sl,lines,x,y,w,size,gap);
}
function footer(sl,s){
  if(s.takeaway&&s.takeaway!==s.lead)text(sl,s.takeaway,74,622,1128,18,false,GREY,52);
  text(sl,'RADIOLARIA OS  /  LANDSLIDE SENTINEL v0.1  /  SOURCE 2f328be',72,687,1000,12,false,GREY,22);
  text(sl,String(s.number).padStart(2,'0'),1160,683,48,16,false,GREY,28,'right');
}
function table(sl,s){
  const values=[s.headers,...s.rows];const n=s.headers.length;
  let fractions=s.widths;
  if(!fractions&&n===3)fractions=s.headers[0]==='Contrast'?[.12,.39,.49]:(s.headers[1]==='Elapsed'?[.32,.18,.50]:[.26,.34,.40]);
  const widths=(fractions??Array(n).fill(1/n)).map(v=>v*1136);
  const size=s.tableFontSize??22;
  const sizes=values.map((r,i)=>i===0?18:size);
  const rows=values.map((r,i)=>Math.max(i===0?47:55,...r.map((c,j)=>wrap(c,widths[j]-30,sizes[i],i===0).split('\n').length*sizes[i]*1.24+22)));
  const y=(s.lead?227:207)+(current.headerShift??0);const height=rows.reduce((a,b)=>a+b,0);
  if(height>384)throw new Error(`Slide ${s.number} table too tall: ${height}`);
  const t=sl.tables.add({rows:values.length,columns:n,left:72,top:y,width:1136,height,values,columnWidths:widths});
  t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:LINE,width:.55,style:'solid'});
  values.forEach((r,i)=>{t.rows[i].height=rows[i];r.forEach((c,j)=>{const cell=t.getCell(i,j);cell.fill=i===0?LIGHT:'#FFFFFF';cell.text.style={typeface:FONT,fontSize:sizes[i],color:i===0?GREY:INK,bold:i===0,autoFit:'none'};});});
  t.cells.block({row:0,column:0,rowCount:values.length,columnCount:n}).assign({margins:{left:13,right:13,top:9,bottom:9},anchor:'center'});
  tableOwners.push(s.number);geometry.push({slide:s.number,kind:'table',x:72,y,w:1136,h:height,rows:values,rowHeights:rows,widths,fontSize:size});
}
function split(sl,s){
  if(!s.columns&&!s.left)return fittingParagraphs(sl,s.body,74,(s.lead?270:240)+(current.headerShift??0),1115,31);
  const cols=s.columns??[s.left,s.right];const n=cols.length,w=(1136-(n-1)*58)/n;
  cols.forEach((c,i)=>{const x=72+i*(w+58),shift=current.headerShift??0;text(sl,c.heading??c.title,x,239+shift,w,22,true,BLUE,58);fittingParagraphs(sl,c.body??c.paragraphs,x,309+shift,w,n>2?24:28);});
}
function flow(sl,s){
  const steps=s.steps??[];const n=steps.length;
  if(n>5)return timeline(sl,s);
  const gap=33,w=(1136-(n-1)*gap)/n,y=270+(current.headerShift??0);
  rule(sl,74,y+41,1130,LINE,2);
  steps.forEach((st,i)=>{
    const x=72+i*(w+gap);
    text(sl,st.number??String(i+1).padStart(2,'0'),x,y-20,w,47,true,BLUE,70);
    text(sl,st.label??st.title,x,y+76,w,26,true,INK,92);
    text(sl,st.detail??st.body,x,y+177,w,23,false,GREY,148);
  });
}
function timeline(sl,s){
  const st=s.steps??[],n=st.length,top=242+(current.headerShift??0),h=Math.min(98,(605-top)/n);
  st.forEach((q,i)=>{
    const y=top+i*h;
    text(sl,q.time??q.number??String(i+1).padStart(2,'0'),72,y+4,108,23,true,BLUE,h-6);
    text(sl,q.label??q.title,200,y+4,336,24,true,INK,h-6);
    text(sl,q.detail??q.body,573,y+4,635,n>5?21:24,false,INK,h-6);
    rule(sl,72,y+h-6,1136,LINE,.65);
  });
}
function metrics(sl,s){
  const ms=s.metrics??[],n=ms.length,w=1136/n;
  ms.forEach((m,i)=>{const x=72+i*w;const max=m.value.length>=10?50:(/[A-Za-z]/.test(m.value)?68:79);let size=max;
    while(wrap(m.value,w-40,size,true).includes('\n')&&size>46)size-=2;
    text(sl,m.value,x,268,w-35,size,true,INK,107);text(sl,m.label,x+2,386,w-45,25,true,INK,75);if(m.detail)text(sl,m.detail,x+2,470,w-45,22,false,GREY,120);
  });
  if(s.body?.length)paragraphs(sl,s.body,74,528,1120,25,12);
  if(s.body_extra?.length)paragraphs(sl,s.body_extra,74,543,1120,23,12);
}
function research(sl,s){
  const steps=s.steps??[]; const w=266;
  steps.forEach((q,i)=>{const x=72+i*290;text(sl,String(i+1).padStart(2,'0'),x,240,w,24,true,BLUE,34);text(sl,q.label??q.title,x,280,w,22,true,INK,60);});
  const rows=s.rows??[];
  text(sl,'Published challenge',72,370,480,18,true,BLUE,30);
  text(sl,'Our recorded software response',604,370,602,18,true,BLUE,30);
  rows.forEach((r,i)=>{const y=418+i*64;rule(sl,72,y-10,1136,LINE,.6);text(sl,r[0],72,y,480,20,false,INK,57);text(sl,r[1],604,y,602,20,false,INK,57);});
  text(sl,'Synthetic observations and mock effects. Research references do not imply endorsement.',74,633,1110,18,false,GREY,45);
}
function abChart(sl,s){
  const data=s.chart;
  if(!data)throw new Error('Missing reviewed A/B chart data');
  text(sl,'A / Current metadata',74,243,468,22,true,BLUE,43);
  text(sl,'Calibration and health\nDistinct channel lineage',74,311,477,31,true,INK,113);
  text(sl,'Current metadata comparison\nNo reserve-history read',75,456,465,25,false,GREY,92);
  text(sl,'B / Recorded mock history',650,243,560,22,true,BLUE,43);
  const chart=sl.charts.add('line',{
    position:{left:627,top:291,width:578,height:279},
    categories:data.categories??data.series.map(q=>String(q.x)),
    series:[{name:'Reserve displacement',values:data.values??data.series.map(q=>q.y),line:{fill:BLUE,width:3,style:'solid'},marker:{symbol:'circle',size:7}}],
    hasLegend:false,
    lineOptions:{smooth:false},
    chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',
    xAxis:{visible:true,title:'Measured tick (s)',textStyle:{typeface:FONT,fontSize:18,fill:GREY},line:{fill:LINE,width:1},majorGridlines:null},
    yAxis:{visible:true,title:'Displacement (um)',min:1500,max:1800,majorUnit:100,numberFormatCode:'0',textStyle:{typeface:FONT,fontSize:18,fill:GREY},line:{fill:'none',width:0},majorGridlines:{fill:LINE,width:.7}},
    dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:FONT,fontSize:18,fill:INK}},
  });
  applyPresentationChartFont(chart,{fontFamily:FONT});chartOwners.push(s.number);
  text(sl,'3 samples   /   20 s measured span   /   150 um range',650,587,560,20,true,INK,36);
  text(sl,'The same-context control retained substantive work.\nBoth executions use the same sensor inputs.',74,634,541,17,false,GREY,45);
  text(sl,`${data.source}\n${data.scope}`,650,634,560,16,false,GREY,45);
}
await fs.mkdir(OUT,{recursive:true});await fs.mkdir(path.join(BUILD,'render_'+REV),{recursive:true});
for(let i=0;i<content.slides.length;i++){
  const s=content.slides[i];current=s;s.number=i+1;
  const sl=p.slides.add({layoutId,width:1280,height:720});sl.background.fill='#FFFFFF';
  if(s.type==='cover'||s.layout==='cover'){
    const image=await fs.readFile(path.join(BASE,'assets/radiolaria_landslide_sentinel_hero.png'));
    sl.images.add({blob:image,contentType:'image/png',alt:'Conceptual Radiolaria Landslide Sentinel sculpture',fit:'contain',position:{left:0,top:0,width:1280,height:720}});
    text(sl,'RADIOLARIA OS',72,64,570,20,true,BLUE,40);
    text(sl,'Landslide\nSentinel',69,208,658,76,true,INK,194);
    text(sl,s.lead?.replace('. ','.\n')??'Local authority\nunder changing conditions.',73,423,620,32,true,INK,100);
    text(sl,s.subtitle??s.body?.join('\n')??'Live model contributions.\nAn inspectable local response.',74,556,580,23,false,GREY,77);
    text(sl,'v0.1  /  Main implementation: 15 September 2026',74,682,785,14,false,GREY,24);
  }else{
    text(sl,s.kicker??'LANDSLIDE SENTINEL',72,47,1136,17,true,BLUE,28);
    const titleSize=s.type==='research'?42:47;
    const lines=wrap(s.title,1136,titleSize,true).split('\n').length;
    current.headerShift=lines>1?48:0;
    if(lines>2)throw new Error('Title too long slide '+s.number);
    text(sl,s.title,70,94,1136,titleSize,true,INK,lines>1?125:88);
    if(s.lead)text(sl,s.lead,74,169+(lines>1?45:0),1120,23,false,GREY,64);
    const type=s.type??s.layout;
    if(type==='research')research(sl,s);
    else if(type==='ab_chart')abChart(sl,s);
    else if(type==='table')table(sl,s);
    else if(type==='split')split(sl,s);
    else if(type==='flow')flow(sl,s);
    else if(type==='timeline')timeline(sl,s);
    else if(type==='metrics')metrics(sl,s);
    else fittingParagraphs(sl,s.body,74,(s.lead?271:253)+current.headerShift,1115,type==='statement'?34:29);
    footer(sl,s);
  }
  sl.speakerNotes.textFrame.setText(`${s.speaker_notes??s.notes??''}\n\nSupplementary slide text:\n${arrayBody(s.body).join('\n')}\n${arrayBody(s.body_extra).join('\n')}\n\nSource records:\n${(s.sources??[]).map(x=>typeof x==='string'?x:JSON.stringify(x)).join('\n')}\n\nClaim identifiers: ${(s.claim_ids??[]).join(', ')}`);
}
await fs.writeFile(path.join(BUILD,'geometry_'+REV+'.json'),JSON.stringify(geometry,null,2));
await fs.writeFile(path.join(BUILD,'deck_'+REV+'.proto.json'),JSON.stringify(p.toProto()));
const candidate=path.join(BUILD,'candidate_'+REV+'.pptx');
await(await PresentationFile.exportPptx(p)).save(candidate);
const finalPath=path.join(OUT,'landslide_sentinel_showcase_v01.pptx');
const result=await finalizePresentation({workspaceDir:BASE,candidatePath:candidate,finalPath,
  pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,
  integrityValidatorPath:'/root/.codex/skills/builtins/presentations/container_tools/inspect_presentation_package_integrity.py',
  layoutValidatorPath:'/root/.codex/skills/builtins/presentations/container_tools/inspect_presentation_layout_geometry.py',
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
  requiredNativeTableOwnerSlides:tableOwners,explicitTotalSlideCount:content.slides.length,
  requiredNativeChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'reference',families:[FONT],referencePath:REF,referenceSha256:createHash('sha256').update(await fs.readFile(REF)).digest('hex')},
  verifyArtifactToolImport:true,receiptPath:path.join(BUILD,'validation_'+REV+'.json')});
console.log('FINALIZED',result);
if(process.argv.includes('--skip-png')) process.exit(0);
const finalP=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(let i=0;i<finalP.slides.items.length;i++){
  const sl=finalP.slides.items[i];
  const png=await finalP.export({slide:sl,format:'png',scale:1.25});
  await fs.writeFile(path.join(BUILD,'render_'+REV,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
  const l=await sl.export({format:'layout'});await fs.writeFile(path.join(BUILD,'render_'+REV,`slide-${String(i+1).padStart(2,'0')}.json`),await l.text());
  console.log('Rendered',i+1);
}
