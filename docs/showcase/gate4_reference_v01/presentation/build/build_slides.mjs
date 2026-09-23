import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {GlobalFonts,createCanvas} from '@napi-rs/canvas';
const ROOT=path.resolve(process.env.G4_PRESENTATION_ROOT||'gate4/presentation');
const BUILD=path.join(ROOT,'build'),OUT=path.join(ROOT,'output'),SKILL='/root/.codex/skills/builtins/presentations';
const NODE=process.env.CODEX_PRIMARY_RUNTIME_NODE,PY=process.env.CODEX_PRIMARY_RUNTIME_PYTHON;
process.env.RUNTIME_NODE=NODE;process.env.RUNTIME_NODE_MODULES=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;process.env.RUNTIME_PYTHON=PY;process.env.RUNTIME_BIN_DIR=process.env.CODEX_PRIMARY_RUNTIME_ROOT+'/dependencies/bin/override';
const {finalizePresentation}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs').href);
await fs.mkdir(BUILD,{recursive:true});await fs.mkdir(OUT,{recursive:true});
const REV=process.argv[2]||'pilot',pilot=REV==='pilot';
const INK='#1D1D1F',BLUE='#0071E3',GREY='#6E6E73',LIGHT='#F5F5F7',LINE='#D2D2D7',RED='#9B342F',FONT='Inter';
const fontDir=process.env.G4_FONT_DIR||path.resolve('presentation/assets/fonts');
GlobalFonts.registerFromPath(fontDir+'/Inter-Regular.ttf',FONT);GlobalFonts.registerFromPath(fontDir+'/Inter-Bold.ttf',FONT);
const ctx=createCanvas(1280,720).getContext('2d');
const data=JSON.parse(await fs.readFile(ROOT+'/content/slide_text_and_notes_v01.json','utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});const geo=[],tables=[],nav=[];let current;
function lines(v,w,size,bold){ctx.font=`${bold?'bold ':''}${size}px ${FONT}`;return String(v).split('\n').reduce((n,s)=>{let line='';for(const word of s.split(' ')){let next=line?line+' '+word:word;if(line&&ctx.measureText(next).width>w){n++;line=word;}else line=next;}return n+1;},0);}
function tx(sl,v,x,y,w,size=28,bold=false,color=INK,h,align='left',name){if(v==null||v==='')return;h=h??Math.ceil(lines(v,w*.985,size,bold)*size*1.25+6);const q=sl.shapes.add({geometry:'textbox',name:name||`text-${current.number}-${geo.length}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=String(v);q.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',wrap:true,alignment:align,verticalAlignment:'top',insetLeft:0,insetRight:0,insetTop:0,insetBottom:0};geo.push({slide:current.number,type:'text',x,y,w,h,size,text:String(v)});return q;}
function line(sl,x,y,w,color=LINE,width=1,style='solid'){return sl.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width,style}});}
function rect(sl,x,y,w,h,fill=LIGHT,stroke='none',width=0){return sl.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width}});}
function node(sl,label,x,y,w,h=86,color=INK,size=27,fill='#FFFFFF'){const a=rect(sl,x,y,w,h,fill,color,1.4);tx(sl,label,x+16,y+16,w-32,size,true,color,h-20,'center');return a;}
function conn(sl,a,b,dash=false,from='right',to='left',color=GREY){return sl.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:color,width:1.8,style:dash?'dash':'solid'},tail:{type:'arrow',width:'med',length:'med'}});}
const BASE='https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/gate4_reference_v01/';
const LINKS={appendix:BASE+'technical_appendix_v01.pdf',reader:BASE+'LLM_READER_GATE4_REFERENCE_V01.xml',index:BASE+'READER_INDEX.json',guide:BASE+'README.md',source:'https://github.com/AAkhtanin/hedgehog-os/tree/5b259441994ba41ed3467e8ffcb9ae6ee8d371f0'};
function link(sl,label,key,x,y,w,size=23){const name='link-'+current.number+'-'+key;tx(sl,label,x,y,w,size,true,BLUE,38,'left',name);nav.push({slide:current.number,name,url:LINKS[key],label});}
function title(sl,s){tx(sl,s.title,72,51,1136,45,true,INK,119);tx(sl,s.lead,74,185,1132,27,false,GREY,76);}
function foot(sl,s){line(sl,74,647,1134,LINE,.7);link(sl,s.source_label+'   Technical evidence','appendix',74,665,660,18);tx(sl,'GATE 4 REFERENCE  /  23 SEPTEMBER 2026',744,669,425,14,false,GREY,24,'right');tx(sl,String(s.number).padStart(2,'0'),1168,665,40,18,false,GREY,28,'right');}
function tab(sl,heads,rows,widths,y=282,size=25,rh=56,x=74,w=1132){const vals=[heads,...rows],ws=widths.map(v=>v*w);const hs=vals.map((r,i)=>Math.max(i===0?48:rh,...r.map((v,j)=>lines(v,ws[j]-26,i===0?22:size,i===0)*(i===0?22:size)*1.2+20)));const h=hs.reduce((a,b)=>a+b,0);const t=sl.tables.add({rows:vals.length,columns:heads.length,left:x,top:y,width:w,height:h,values:vals,columnWidths:ws});t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:LINE,width:.65,style:'solid'});vals.forEach((r,i)=>{t.rows[i].height=hs[i];r.forEach((v,j)=>{let c=t.getCell(i,j);c.fill=i===0?LIGHT:'#FFFFFF';c.text.style={typeface:FONT,fontSize:i===0?22:size,color:i===0?GREY:INK,bold:i===0,autoFit:'none'};});});t.cells.block({row:0,column:0,rowCount:vals.length,columnCount:heads.length}).assign({margins:{left:12,right:12,top:9,bottom:9},anchor:'center'});tables.push(p.slides.items.length);geo.push({slide:current.number,type:'table',x,y,w,h,values:vals});return t;}
function budgetRow(sl,y,caption,ids,colors){tx(sl,caption,74,y-3,250,28,true,INK,70);ids.forEach((id,i)=>{const x=335+i*124;rect(sl,x,y,116,87,colors?.[i]?BLUE:LIGHT);tx(sl,id,x+6,y+15,104,22,true,colors?.[i]?'#FFFFFF':INK,60,'center');});}
function render(sl,s){switch(s.number){
case 2:{
 const input=node(sl,'Intent + bounded\nsemantic inputs',74,287,285,104,INK,27);
 const work=node(sl,'Runtime-owned Work\nOne local task budget',425,287,364,104,INK,28);
 conn(sl,input,work,true);
 tx(sl,'G4',429,443,110,24,true,BLUE,40);tx(sl,'Finite strategy comparison\nExplainable work allocation',429,485,380,28,false,INK,89);
 line(sl,429,424,359,BLUE,2);
 const roots=[['Client Root',258],['Airline Root',379],['Bank Root',500]];roots.forEach(([v,y])=>{const n=node(sl,v,948,y,259,77,BLUE,27);conn(sl,work,n,false);});
 tx(sl,'G3 local experience',74,455,290,25,true,BLUE,44);tx(sl,'DRS and time qualify\ncurrent use',74,502,291,28,false,INK,84);
 tx(sl,'Conceptual architecture view. Dashed: advisory input. Solid: evidence for independent review.',74,603,1132,20,false,GREY,33);break;}
case 3:{
 tx(sl,'offer:0',74,277,440,25,true,BLUE,40);tx(sl,'EUR 790',74,329,440,51,true,INK,74);tx(sl,'Standard seat\nWindow',74,427,435,32,false,INK,110);
 tx(sl,'offer:1',665,277,541,25,true,BLUE,40);tx(sl,'EUR 815',665,329,541,51,true,INK,74);tx(sl,'Extra legroom\nAisle',665,427,541,32,false,INK,110);
 line(sl,74,560,1132);tx(sl,'Client: price + seat preference     Airline: revenue     Bank: budget margin',74,584,1132,25,false,GREY,56);break;}
case 4:{
 tab(sl,['Profile','Offer','Client U','Airline U','Bank U','Product'],data.strategy_rows,[.24,.12,.14,.14,.13,.23],269,24,51);
 tx(sl,'PRICE_FIRST selects offer:0',75,545,530,26,true,BLUE,43);tx(sl,'COMFORT_FIRST selects offer:1',666,545,540,26,true,BLUE,43);
 tx(sl,'Current Root reviews and offer resolution create a prepared hold record',74,589,1132,23,false,GREY,36);tx(sl,'PREPARATION_ONLY_NOT_EXECUTED. No payment or external booking.',74,615,1132,20,true,INK,26);break;}
case 5:{
 tab(sl,['Independent owner','With required consent','Missing Bank consent'],[['Client Root','ACCEPT','ACCEPT'],['Airline Root','ACCEPT','ACCEPT'],['Bank Root','ACCEPT','NEEDS_USER']],[.32,.33,.35],275,28,63);
 tx(sl,'Prepared offer:0',75,557,494,31,true,BLUE,52);tx(sl,'MIXED',676,553,530,31,true,RED,52);tx(sl,'No domain continuation',676,597,530,26,false,INK,44);break;}
case 6:{
 for(let i=0;i<9;i++){let x=74+i*126;rect(sl,x,303,117,112,i===0||i===8?INK:BLUE);tx(sl,String(i+1),x+10,328,97,42,true,'#FFFFFF',65,'center');}
 tx(sl,'1 spent',74,440,206,31,true,INK,50);tx(sl,'7 discretionary checks',286,440,662,31,true,BLUE,50,'center');tx(sl,'1 reserved',993,440,215,31,true,INK,50,'right');
 tx(sl,'initial_constraint',74,501,259,23,false,GREY,69);tx(sl,'Branch limits: 2 minimum, 6 maximum',337,517,622,26,false,INK,55,'center');tx(sl,'final_strategy_\nconsumer',965,501,243,23,false,GREY,80,'right');
 tx(sl,'9 - 1 - 1 = 7',74,586,370,34,true,INK,52);tx(sl,'ONE_NATIVE_WORK_DISPATCH_UNIT',534,595,673,23,false,GREY,39,'right');break;}
case 7:{
 tx(sl,'FALSE',74,273,360,47,true,GREY,66);tx(sl,'Configured prediction',74,346,520,27,false,INK,44);tx(sl,'TRUE',670,273,536,47,true,BLUE,66);tx(sl,'Completed mandatory check',670,346,536,27,false,INK,44);
 tab(sl,['Assessment','Recorded result'],[['Proposal','INCORRECT'],['Enforcement','ALLOWED_AS_REQUIRED'],['Execution / task','COMPLETED / COMPLETED']],[.38,.62],408,24,46);
 tx(sl,'One SPARSE sample through Root-reviewed recording and LocalDRS. No new LLM call.',74,610,1132,21,false,GREY,34);break;}
case 8:{
 const common=['0_1\nRoute','0_2\nBaggage','0_3\nSeat','1_1\nRoute','1_2\nBaggage','1_3\nSeat'];
 tx(sl,'Common six checks',336,261,742,22,false,GREY,34);tx(sl,'Changed check',1080,261,128,22,false,BLUE,58,'center');
 budgetRow(sl,316,'Cold\n4 / 3',[...common,'0_4\nPrice'],[false,false,false,false,false,false,true]);
 budgetRow(sl,430,'History-informed\n3 / 4',[...common,'1_4\nPrice'],[false,false,false,false,false,false,true]);
 tx(sl,'Work IDs use the prefix offer_   (for example offer_0_4)',336,529,868,21,false,GREY,34);
 tx(sl,'z offer0: 0.425 to 0.4171875',74,576,655,26,true,INK,45);tx(sl,'z offer1: 0.42125',775,576,432,26,true,INK,45);tx(sl,'Raw prior applies once. Both lanes prepare offer:0.',74,613,1132,21,false,GREY,30);
 break;}
case 9:{
 const labels=[['Accepted allocation','Cold [4, 3]'],['Actual Work literal','offer_0_4\nfield: price'],['Completed output','EUR 790\nCOMPLETED'],['Final consumer','allocation_proof\ninput + bound output']];let prev;
 labels.forEach(([a,b],i)=>{let x=74+i*290;const n=node(sl,a,x,293,261,80,i===3?BLUE:INK,25);if(prev)conn(sl,prev,n);tx(sl,b,x,398,261,28,false,INK,110);prev=n;});
 line(sl,74,517,1132);tx(sl,'Coherent 6 / 1 substitution',74,546,480,27,true,RED,48);tx(sl,'REFUSED before changed execution',590,546,617,27,true,INK,48);tx(sl,'Original source basis disagrees. The intact allocation is the passing neighbour.',74,596,1132,24,false,GREY,39);break;}
case 10:{
 tab(sl,['Boundary','Genuine positive','Refused continuation'],[['Original budget','Seven optional checks\nplus mandatory endpoints','Fresh report cannot\nerase spent work'],['Original expiry','Just before expiry:\nprepared result','At boundary or after:\nREFUSED'],['Retained history','Current discovery and\nRoot-approved descent','Expired retained input:\nREFUSED']],[.24,.38,.38],274,26,88);break;}
case 11:{
 tab(sl,['Evidence layer','Recorded scope','Result'],[['G41 numerical','110 pure-math tests','Recorded reference'],['G43 native','3 tasks × 9 units = 27','Actual Work + consumption'],['G44 focused','33 PASS / 1 FAIL','Accepted mode-test limitation'],['G44 / G45 supplied','3 identical complete outputs','Saved relationships checked']],[.25,.42,.33],273,24,52);
 tx(sl,'Supplied checks require the trusted installed code and matching recorded environment.',74,559,1132,24,true,INK,43);tx(sl,'Full native replay is unsupported. No new LLM or Work calls occur in the named replay scope.',74,603,1132,21,false,GREY,35);break;}
case 12:{
 tx(sl,'ACCEPTED REFERENCE',74,276,517,23,true,BLUE,39);tx(sl,'Finite multi-Root comparison\nBounded allocation of actual Work\nIndependent owner decisions',74,322,537,29,false,INK,146);
 tx(sl,'DEFERRED PROGRAMME',665,276,542,23,true,BLUE,39);tx(sl,'Full H-I-J after Gate 6 publication\nSeparate future scope decision\nLGT excluded',665,322,542,29,false,INK,146);
 tx(sl,'Reference engineering accepted / presentation prepared',74,488,1133,26,true,INK,48);
 link(sl,'Technical appendix','appendix',74,553,325,25);link(sl,'XML Reader','reader',456,553,257,25);link(sl,'Reader index','index',865,553,341,25);
 link(sl,'Pinned implementation','source',74,597,510,25);link(sl,'Verification guide','guide',665,597,542,25);
 tx(sl,'Repository access required. Document links are staged publication targets on main.',74,662,1132,18,false,GREY,31);break;}
}}
const slides=pilot?data.slides.filter(s=>[2,4,8].includes(s.number)):data.slides;
for(const s of slides){current=s;const sl=p.slides.add();sl.background.fill='#FFFFFF';
 if(s.number===1){let hero=process.env.G4_HERO_IMAGE||ROOT+'/assets/radiolaria_gate4_reference_hero_v01.png';if(!await fs.stat(hero).catch(()=>null))hero=path.join(ROOT,'../assets/radiolaria_gate4_reference_hero_v01.png');let b=await fs.readFile(hero);sl.images.add({blob:b,contentType:'image/png',alt:'AI-generated conceptual Radiolaria family artwork, not an evidence graph',fit:'contain',position:{left:0,top:0,width:1280,height:720}});tx(sl,'RADIOLARIA OS',74,70,570,24,true,BLUE,42);tx(sl,s.title,69,188,568,64,true,INK,179);tx(sl,s.lead,75,415,533,33,true,INK,144);tx(sl,'Owner-approved reduced scope\n23 September 2026  /  Implementation 5b25944',75,624,589,20,false,GREY,61);
 }else{title(sl,s);render(sl,s);if(s.number!==12)foot(sl,s);}
 s.visible_text=geo.filter(g=>g.slide===s.number).flatMap(g=>g.type==='text'?[g.text]:g.values.flat());sl.speakerNotes.textFrame.setText(JSON.stringify(s.notes,null,2)+'\n\nVisible slide content:\n'+s.visible_text.join('\n'));
}
await fs.mkdir(BUILD+'/render_'+REV,{recursive:true});await fs.writeFile(BUILD+'/geometry_'+REV+'.json',JSON.stringify(geo,null,2));
const candidate=BUILD+'/candidate_'+REV+'.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
if(!pilot){await fs.writeFile(ROOT+'/content/slide_text_and_notes_v01.json',JSON.stringify(data,null,2)+'\n');await fs.writeFile(BUILD+'/links_'+REV+'.json',JSON.stringify(nav,null,2));execFileSync(PY,[BUILD+'/patch_links.py',candidate,BUILD+'/linked_'+REV+'.pptx',BUILD+'/links_'+REV+'.json']);await finalizePresentation({workspaceDir:ROOT,candidatePath:BUILD+'/linked_'+REV+'.pptx',finalPath:OUT+'/gate4_reference_v01'+(REV==='final'?'':'_'+REV)+'.pptx',pythonExecutable:PY,integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tables,explicitTotalSlideCount:12,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:BUILD+'/validation_'+REV+'.json'});}
for(let i=0;i<p.slides.items.length;i++){const png=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(BUILD+'/render_'+REV+'/slide-'+String(slides[i].number).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('Rendered',slides[i].number);}
console.log('DONE',REV);
