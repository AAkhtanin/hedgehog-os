import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
import {GlobalFonts,createCanvas} from '@napi-rs/canvas';
import {pathToFileURL} from 'node:url';
const skillDir=process.env.PRESENTATION_SKILL_DIR;
if(!skillDir)throw new Error('PRESENTATION_SKILL_DIR is required');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')).href);
const BASE=path.resolve(process.env.ATLAS_CAPSULE_DIR||'.');
const BUILD=path.resolve(process.env.ATLAS_BUILD_DIR||'./atlas-private-build');
const OUT=path.resolve(process.env.ATLAS_OUTPUT_DIR||'./atlas-rebuilt-output');
if(BUILD.startsWith(BASE+path.sep)||OUT.startsWith(BASE+path.sep))throw new Error('Build and output must be outside the frozen capsule');
await fs.mkdir(BUILD,{recursive:true});await fs.mkdir(OUT,{recursive:true});
process.env.RUNTIME_NODE=process.env.CODEX_PRIMARY_RUNTIME_NODE;process.env.RUNTIME_NODE_MODULES=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;process.env.RUNTIME_BIN_DIR=process.env.CODEX_PRIMARY_RUNTIME_ROOT+'/dependencies/bin/override';process.env.RUNTIME_PYTHON=process.env.CODEX_PRIMARY_RUNTIME_PYTHON;
const REV=process.argv[2]||'trial',FONT='Inter',INK='#1D1D1F',BLUE='#0071E3',GREY='#6E6E73',LIGHT='#F5F5F7',LINE='#D2D2D7',RED='#9B342F';
GlobalFonts.registerFromPath(process.env.ATLAS_FONT_REGULAR,FONT);GlobalFonts.registerFromPath(process.env.ATLAS_FONT_BOLD,FONT);
const m=createCanvas(1280,720).getContext('2d'),data=JSON.parse(await fs.readFile(BASE+'/presentation/slide_text_and_notes.json','utf8'));
const cards=JSON.parse(await fs.readFile(BASE+'/presentation/cards.json','utf8'));
for(const s of data.slides){const cc=cards.cards.filter(c=>s.notes.case_ids.includes(c.case_id));s.notes.test_nodes=[...new Set(cc.flatMap(c=>c.test_nodes??[]))];s.notes.case_page_anchors=cc.map(c=>({case_id:c.case_id,appendix_page:c.appendix_page??null}));}
data.slides[0].notes.artwork={file:'assets/radiolaria_incident_atlas_hero_v01.png',role:'AI-generated conceptual artwork; not an evidence graph',provenance:'assets/radiolaria_incident_atlas_hero_v01.provenance.json'};
const p=Presentation.create({slideSize:{width:1280,height:720}}),geo=[],tables=[],charts=[];let current;
function lines(v,w,size,bold){m.font=`${bold?'bold ':''}${size}px ${FONT}`;return String(v).split('\n').reduce((n,s)=>{let line='';for(const word of s.split(' ')){const next=line?line+' '+word:word;if(line&&m.measureText(next).width>w){n++;line=word;}else line=next;}return n+1;},0);}
function tx(sl,v,x,y,w,size=28,bold=false,color=INK,h,align='left'){
 if(v===undefined||v===null||v==='')return;
 const ln=lines(v,w*.985,size,bold);h=h??Math.ceil(ln*size*1.24+5);
 const q=sl.shapes.add({geometry:'textbox',name:`text-${current.number}-${geo.length}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 q.text=String(v);q.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',wrap:true,alignment:align,verticalAlignment:'top',insetLeft:0,insetRight:0,insetTop:0,insetBottom:0};
 geo.push({slide:current.number,type:'text',x,y,w,h,size,lines:ln,text:String(v)});return q;
}
function ln(sl,x,y,w,color=LINE,width=1,style='solid'){return sl.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width,style}});}
function box(sl,x,y,w,h,fill='none',stroke=LINE,width=1){return sl.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width}});}
function node(sl,label,x,y,w=230,h=90,{color=INK,bg='none',size=26,bold=true}={}){const q=box(sl,x,y,w,h,bg,color,1.4);tx(sl,label,x+16,y+15,w-32,size,bold,color,h-20,'center');return q;}
function conn(sl,a,b,{color=GREY,dashed=false,from='right',to='left'}={}){const c=sl.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:color,width:2,style:dashed?'dash':'solid'},tail:{type:'arrow',width:'med',length:'med'}});c.bringToFront();return c;}
function foot(sl,s){tx(sl,s.takeaway,72,628,1136,21,false,GREY,56);tx(sl,'RADIOLARIA OS   /   INCIDENT-TO-PROOF ATLAS   /   IMPLEMENTATION e538790',72,690,1080,13,false,GREY,20);tx(sl,String(s.number).padStart(2,'0'),1163,685,44,17,false,GREY,25,'right');}
function title(sl,s){tx(sl,s.title,70,59,1140,46,true,INK,118);if(s.lead)tx(sl,s.lead,74,190,1116,25,false,GREY,66);}
function tab(sl,heads,rows,widths,y=275,size=25,rowHeight=61){const vals=[heads,...rows],ws=widths.map(q=>q*1136),hs=vals.map((r,i)=>Math.max(i===0?47:rowHeight,...r.map((v,j)=>lines(v,ws[j]-28,i===0?20:size,i===0)*(i===0?20:size)*1.2+20)));
 const h=hs.reduce((a,b)=>a+b,0),t=sl.tables.add({rows:vals.length,columns:heads.length,left:72,top:y,width:1136,height:h,values:vals,columnWidths:ws});t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:LINE,width:.6,style:'solid'});
 vals.forEach((r,i)=>{t.rows[i].height=hs[i];r.forEach((v,j)=>{const c=t.getCell(i,j);c.fill=i===0?LIGHT:'#FFFFFF';c.text.style={typeface:FONT,fontSize:i===0?20:size,color:i===0?GREY:INK,bold:i===0,autoFit:'none'};});});
 t.cells.block({row:0,column:0,rowCount:vals.length,columnCount:heads.length}).assign({margins:{left:12,right:12,top:8,bottom:8},anchor:'center'});tables.push(current.number);geo.push({slide:current.number,type:'table',x:72,y,w:1136,h,values:vals});}
function flow(sl,steps,y=320){const w=(1136-(steps.length-1)*38)/steps.length;let prev;steps.forEach((s,i)=>{const x=72+i*(w+38);const q=node(sl,s[0],x,y,w,98,{color:i===steps.length-1?BLUE:INK,size:25});if(prev)conn(sl,prev,q);tx(sl,s[1],x,y+127,w,24,false,GREY,130);prev=q;});}
function twoCols(sl,a,b,y=275){tx(sl,a[0],74,y,515,25,true,BLUE,48);tx(sl,a[1],74,y+65,515,31,false,INK,240);tx(sl,b[0],671,y,537,25,true,BLUE,48);tx(sl,b[1],671,y+65,537,31,false,INK,240);}
function render(sl,s){
 switch(s.layout){
 case 'cover':{
  break;}
 case 'architecture':{
  tx(sl,'OWNER A',72,267,675,23,true,BLUE,36);tx(sl,'OWNER B',904,267,304,23,true,BLUE,36);
  box(sl,72,307,695,225,LIGHT,'none',0);box(sl,904,307,304,225,LIGHT,'none',0);
  const proposal=node(sl,'Semantic\nproposal',90,338,199,90,{size:24});const work=node(sl,'Bounded\nWork',340,338,180,90);const ra=node(sl,'Root A\nreview',568,338,179,90);conn(sl,proposal,work,{dashed:true});conn(sl,work,ra);
  const rb=node(sl,'Root B review',924,327,264,65);conn(sl,ra,rb,{dashed:true});const resource=node(sl,'Local effect',924,430,264, seventy());conn(sl,rb,resource,{from:'bottom',to:'top',color:BLUE});
  tx(sl,'Runtime builds and validates local work',91,464,645,24,false,GREY,43);
  tx(sl,'DRS: applicable experience',92,559,426,24,true,BLUE,42);tx(sl,'Time and current dependencies',568,559,640,24,true,BLUE,42);
  tx(sl,'Dashed: bounded proposal    Solid: validated result    Blue: local authorized call',74,605,1136,18,false,GREY,25);break;}
 case 'source_comparison':tab(sl,['Legitimate objective','Risk mechanism','Atlas'],s.rows,[.38,.44,.18],262,25,88);tx(sl,'OpenAI published reports, 16 September 2026. Sources E02/E03, E05, E06/E07.',74,589,1120,19,false,GREY,36);break;
 case 'workspace_state':{
  tx(sl,'SAVED MEMORY',74,280,495,25,true,BLUE,42);const old=node(sl,'Prior session\nCLOSED',74,342,280,113,{size:29});tx(sl,'Recipe and summary\nremain available',74,489,459,30,false,INK,98);
  tx(sl,'CURRENT TASK STATE',671,280,537,25,true,BLUE,42);const cur=node(sl,'Required current contract\nNo completed result',671,342,537,113,{size:28});tx(sl,'The task exists before\nthe new summary arrives',672,489,535,30,false,INK,100);conn(sl,old,cur,{dashed:true});tx(sl,'context only',401,351,211,22,false,GREY,40,'center');break;}
 case 'd1_controls':tab(sl,['Controlled change','Observed boundary reason'],s.rows,[.47,.53],268,26,53);tx(sl,'Five source-bound derivative records. Exact reason codes are in slide notes and the appendix.',74,591,1133,18,false,GREY,35);break;
 case 'save_flow':flow(sl,[['Complete Work','Current contract\nand actual result'],['Consume result','Current selection\nand typed commands'],['Approve bytes','REQUEST_SAVE\nExact confirmation'],['Save once','Local sidecar\nOriginals preserved']],304);break;
 case 'experience_flow':{
  const labs=[['Produce','Actual Work output'],['Record','OFE + Root review'],['Retrieve','LocalDRS history']];flow(sl,labs,280);
  const a=node(sl,'Current selection',74,511,283, seventy(),{size:25}),b=node(sl,'Executed Work',448,511,342,seventy(),{size:25}),c=node(sl,'Downstream consumer',880,511,328,90,{size:25,color:BLUE});conn(sl,a,b);conn(sl,b,c);break;}
 case 'rank_chart':{
  const c=sl.charts.add('bar',{position:{left:72,top:277,width:725,height:314},categories:s.chart.categories,series:[{name:'Before',values:s.chart.before,valuesFormatCode:'0.000000',dataLabelOverrides:s.chart.before.map((v,idx)=>({idx,text:v.toFixed(6),showValue:false,textStyle:{typeface:FONT,fontSize:18,fill:INK}})),fill:'#A9ADB5'},{name:'After',values:s.chart.after,valuesFormatCode:'0.000000',dataLabelOverrides:s.chart.after.map((v,idx)=>({idx,text:v.toFixed(6),showValue:false,textStyle:{typeface:FONT,fontSize:18,fill:INK}})),fill:BLUE}],barOptions:{direction:'column',grouping:'clustered'},hasLegend:true,legend:{position:'bottom',textStyle:{typeface:FONT,fontSize:20,fill:INK}},xAxis:{visible:true,textStyle:{typeface:FONT,fontSize:23,fill:INK},line:{fill:LINE,width:1}},yAxis:{visible:true,min:.77,max:.82,majorUnit:.01,numberFormatCode:'0.00',textStyle:{typeface:FONT,fontSize:18,fill:GREY},majorGridlines:{fill:LINE,width:.5}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.000000',textStyle:{typeface:FONT,fontSize:18,fill:INK}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});applyPresentationChartFont(c,{fontFamily:FONT});charts.push(s.number);
  tx(sl,'0.79 + 0.015625\n= 0.805625',865,296,342,34,true,BLUE,117);tx(sl,'Prior 0.0625 × weight 0.25',865,438,342,23,false,GREY,70);tx(sl,'One favorable sample\nchanges the ranking.',865,510,342,26,false,INK,98);tx(sl,'Axis begins at 0.77 to show the recorded difference.',75,594,748,18,false,GREY,28);break;}
 case 'outcomes':tab(sl,s.headers,s.rows,s.widths,266,24,57);break;
 case 'consumers':case 'continuations':case 'coverage':tab(sl,s.headers,s.rows,s.widths,248,24,s.layout==='coverage'?57:58);if(s.layout==='coverage')tx(sl,'5 recorded Gemini responses from one model. No new AT5 provider calls.',74,596,1132,20,false,GREY,30);break;
 case 'airline':{
  const a=node(sl,'Valid review\nfor offer A',74,297,338,105,{size:31});const b=node(sl,'Current offer B',650,297,421,105,{size:31});conn(sl,a,b,{dashed:true});tx(sl,'BLOCKED',432,272,200,25,true,RED,41,'center');tx(sl,'CLIENT_ROOT_SELECTION_BINDING',444,424,746,24,true,RED,51);ln(sl,74,480,1136);tx(sl,'ALLOWED',75,514,237,27,true,BLUE,42);tx(sl,'Matching review and offer form the bounded hold.',311,514,871,28,false,INK,77);tx(sl,'No external ticket purchase in this recorded path.',312,569,869,23,false,GREY,43);break;}
 case 'supplier':tab(sl,['Current operation','Observed result','Named backend change'],[['Read A in task A','ALLOWED','Authorized read'],['Read B / foreign account','BLOCKED before read','No change'],['Unauthorized write','BLOCKED before write','No change'],['Explicit collaboration','ALLOWED','Authorized write']],[.38,.36,.26],275,25, sixty());break;
 case 'testflix':{
  const cells=[['T1  PRICE','500 to 700','Old pending payment refused\nNo new 700 purchase'],['T2  LIFECYCLE','Expiry / revoke','Exact deadline and owner\nrevocation stay effective'],['T3  RECEIPT','No second purchase','Consumed paid period\nstays consumed'],['T4  CONSENT','NEEDS_USER','Favorable history cannot\nprovide missing consent']];
  cells.forEach((q,i)=>{const x=72+(i%2)*594,y=278+Math.floor(i/2)*165;tx(sl,q[0],x,y,530,22,true,BLUE,34);tx(sl,q[1],x,y+42,530,30,true,INK,48);tx(sl,q[2],x,y+94,530,25,false,GREY, seventy());});break;}
 case 'code_identity':{
  flow(sl,[['Original bytes','Admitted and executed'],['Same name\nChanged bytes','BLOCKED before\nchanged executor entry'],['Original restored','Executes again']],285);
  ln(sl,74,524,1136);tx(sl,'Separate W2 test',74,551,268,24,true,BLUE, forty());tx(sl,'Supported RATE + wrong current version\nActual Host input binding rejects the request',370,543,824,27,false,INK,86);break;}
 case 'measurements':{
  tx(sl,'N1   CURRENTNESS',74,275,510,23,true,BLUE,40);tx(sl,'Measured: scenario second 3600',74,341,510,27,true,INK,50);ln(sl,74,403,510,LINE,2);tx(sl,'Received: scenario second 3661',74,435,510,27,true,INK,50);ln(sl,74,492,510,BLUE,2);tx(sl,'61 seconds old. Current limit: 10 s.',74,531,510,25,false,GREY,70);
  tx(sl,'N2   INDEPENDENCE',673,275,535,23,true,BLUE,40);tx(sl,'Two copies, one lineage',673,341,535,30,true,INK,90);tx(sl,'Insufficient',673,427,535,27,true,RED, fifty());tx(sl,'Two current independent lineages\nform the positive neighbor.',673,507,535,28,false,GREY, ninety());break;}
 case 'barrier':{
  tx(sl,'Optional worker',73,278,296,25,true,GREY, forty());ln(sl,360,322,820,GREY,3,'dash');tx(sl,'START / WAIT',360,274,282,22,true,GREY,40);tx(sl,'RELEASE / JOIN',951,274,259,22,true,GREY,40);
  tx(sl,'Local episode',74,404,276,25,true,BLUE, forty());const a=node(sl,'Fresh local\nevidence',358,385,212,95,{size:26}),b=node(sl,'Bounded Work\nand ON',620,385,245,95,{size:26,color:BLUE}),c=node(sl,'Queue report',915,385,292,95,{size:26,color:BLUE});conn(sl,a,b,{color:BLUE});conn(sl,b,c,{color:BLUE});
  tx(sl,'The worker is still pending throughout local completion.',359,524,844,28,true,INK,50);tx(sl,'The returned old-context answer is retained as historical only.',359,583,844,22,false,GREY, forty());break;}
 case 'recovery':{
  tx(sl,'Old OFF advice',74,282,405,26,true,INK, forty());tx(sl,'Root refuses. Host NOT_REACHED.',470,282,740,26,true,RED, forty());
  const x=[74,382,690];['0 s','15 s','30 s'].forEach((v,i)=>{tx(sl,v,x[i],386,230,49,true,i===2?BLUE:INK, seventy());tx(sl,'Independent\nrecovery evidence',x[i],469,260,27,false,GREY, ninety());if(i<2)ln(sl,x[i]+150,415,130,LINE,2);});
  const off=node(sl,'Native\nmock OFF',991,392,217,135,{color:BLUE,size:30});tx(sl,'Separate current permission',976,550,231,23,false,GREY, seventy());break;}
 case 'falsification':{
  twoCols(sl,['FALSE RELATION','A genuine receipt or result\nfrom the wrong context.\n\nOuter IDs are rebuilt.\nContextual validation refuses.'],['EQUIVALENT POSITIVE','An independently rebuilt\nequal copy.\n\nThe required relationships\nremain valid and pass.']);break;}
 case 'verification':{
  tx(sl,['python -B demo/run_incident_atlas_v01.py verify','  --package evidence/atlas_package.json','  --expected-pin evidence/expected_pin.json','  --output NEW_verification.json'].join(' '+String.fromCharCode(92)+'\n'),74,275,1131,25,false,INK,162);
  tx(sl,'Saved AT5 result',74,462,349,26,true,BLUE, forty());tx(sl,'integrity: PASS    supported_semantics: PASS',74,513,1137,26,true,INK,52);tx(sl,'Run from the pinned source and documented R1 admission context.\nThe saved check observed zero calls to its 37 named prohibited entrypoints.',74,561,1136,23,false,GREY,65);break;}
 case 'closing':{
  tx(sl,'Intent shapes work.\nOwners decide locally.\nValidated experience informs what follows.',73,287,1094, forty(),true,INK,205);
  tx(sl,'Technical appendix',74,550,328,27,true,BLUE,48);tx(sl,'Source-bound XML Reader',452,550,399,27,true,BLUE,48);tx(sl,'Pinned repository',906,550,302,27,true,BLUE,48);break;}
 }
}
function seventy(){return 70}function sixty(){return 60}function forty(){return 40}function fifty(){return 50}function ninety(){return 90}function eighty(){return 80}
const trial=REV==='trial',slides=trial?data.slides.filter(s=>[2,4,17].includes(s.number)):data.slides;
for(const s of slides){current=s;const sl=p.slides.add();sl.background.fill='#FFFFFF';
 if(s.layout==='cover'){
  const image=await fs.readFile(BASE+'/assets/radiolaria_incident_atlas_hero_v01.png');sl.images.add({blob:image,contentType:'image/png',alt:'Conceptual Radiolaria sculpture, not an evidence graph',fit:'contain',position:{left:0,top:0,width:1280,height:720}});
  tx(sl,'RADIOLARIA OS',72,64,570,22,true,BLUE,45);tx(sl,s.title,68,203,711,65,true,INK,180);tx(sl,s.subtitle,74,429,653,36,true,INK,113);tx(sl,'V02  /  23 September 2026\nImplementation e538790',75,626,713,21,false,GREY,60);
 }else{title(sl,s);render(sl,s);foot(sl,s);}
 s.visible_text=geo.filter(g=>g.slide===s.number).flatMap(g=>g.type==='text'?[g.text]:g.type==='table'?g.values.flat():[]);
 sl.speakerNotes.textFrame.setText(JSON.stringify(s.notes,null,2)+'\n\nPublic slide copy:\n'+JSON.stringify(s,null,2));
}
if(!trial)await fs.writeFile(BUILD+'/derived_slide_text_and_notes.json',JSON.stringify(data,null,2)+'\n');
await fs.mkdir(BUILD+'/render_'+REV,{recursive:true});await fs.writeFile(BUILD+'/geometry_'+REV+'.json',JSON.stringify(geo,null,2));
const candidate=BUILD+'/candidate_'+REV+'.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
const finalPath=trial?BUILD+'/trial_review.pptx':OUT+'/incident_to_proof_atlas_V02_20260923'+(REV==='final'?'':'_'+REV)+'.pptx';
if(await fs.stat(finalPath).catch(()=>null))throw new Error('Refusing to overwrite an existing output');
if(!trial){await finalizePresentation({workspaceDir:BUILD,candidatePath:candidate,finalPath,pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tables,requiredNativeChartOwnerSlides:charts,explicitTotalSlideCount:slides.length,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:BUILD+'/validation_'+REV+'.json'});}else await fs.copyFile(candidate,finalPath);
for(let i=0;i<p.slides.items.length;i++){const sl=p.slides.items[i],png=await p.export({slide:sl,format:'png',scale:1});await fs.writeFile(BUILD+'/render_'+REV+'/slide-'+String(slides[i].number).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('Rendered',slides[i].number);}
console.log('OUTPUT',finalPath);
