// Art-only flight and deployment preview from image-generated layers.
// Requires Node.js and ImageMagick 7. Run with a scratch directory argument.
import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync, copyFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url));
const work = process.argv[2];
if (!work) throw new Error('Usage: node render.mjs /path/to/scratch');
mkdirSync(work, {recursive:true});
mkdirSync(join(here,'sprites'), {recursive:true});
function im(...args) {
  const r=spawnSync('magick',args,{encoding:'utf8'});
  if(r.status!==0) throw new Error(r.stderr || `ImageMagick ${r.status}`);
  return r.stdout.trim();
}
const specs={
  capsule:{crop:'330x545+55+20',size:'112x180'},
  left:{crop:'260x520+465+35',size:'50x145!'},
  right:{crop:'245x520+820+35',size:'50x145!'},
  rear:{crop:'350x340+1150+230',size:'80x90!'},
  base:{crop:'395x245+15+710',size:'140x85!'},
  lower:{crop:'300x340+445+625',size:'95x110!'},
  upper:{crop:'225x315+815+645',size:'70x100!'},
  head:{crop:'440x325+1090+635',size:'150x110!'}
};
const sprites={};
for(const [name,s] of Object.entries(specs)){
  const path=join(here,'sprites',name+'.png');
  // Matte cleanup removes faint transparent atlas background and cell edges.
  im(join(here,'layers.png'),'-crop',s.crop,'+repage','-channel','A','-threshold','70%',
    '+channel','-trim','+repage','-resize',s.size,path);
  const [w,h]=im('identify','-format','%w %h',path).split(' ').map(Number);
  sprites[name]={path,w,h};
}
const W=1120,H=700,ground=610,landingX=820;
const ease=t=>(1-Math.cos(Math.PI*Math.max(0,Math.min(1,t))))/2;
const phases=[['FLIGHT',48],['LANDING',8],['UNFOLD',24],['EXTEND',24],['DEPLOYED',28],['RESET',8]];
const total=phases.reduce((a,p)=>a+p[1],0);
const bg=join(work,'background.png');
im('-size',`${W}x${H}`,'canvas:#e7e4dc','-fill','#b8ad94','-draw',`rectangle 0,${ground} ${W},${H}`,
  '-stroke','#726f60','-strokewidth','3','-draw',`line 0,${ground} ${W},${ground}`,
  '-stroke','#a2977d','-strokewidth','1','-draw','line 40,642 270,642 line 420,665 700,665 line 900,650 1080,650',
  '-fill','#343b36','-stroke','none','-font','DejaVu-Sans-Bold','-pointsize','29',
  '-annotate','+30+43','KOLOKOL / MATRYOSHKA',bg);
function layer(name,x,y,angle=0,opacity=1,viewport='520x380+0+0',anchor=null){
  if(opacity<=0)return [];
  const s=sprites[name]; const a=anchor||[s.w/2,s.h-1];
  return ['(',s.path,'-virtual-pixel','transparent','-background','none',
    '-set','option:distort:viewport',viewport,'-distort','SRT',`${a[0]},${a[1]} 1 ${angle} ${x},${y}`,
    '+repage','-channel','A','-evaluate','Multiply',String(opacity),'+channel',')','-composite'];
}
function actor(open,extend){
  const out=join(work,'actor.png');
  let args=['-size','520x380','canvas:none'];
  const panelAlpha=Math.min(1,open/0.15);
  args.push(...layer('rear',260,351,88*ease(open),panelAlpha));
  args.push(...layer('lower',260,350-15*ease(extend/0.45)));
  args.push(...layer('upper',260,335-80*ease((extend-0.15)/0.85)));
  args.push(...layer('head',260,330-160*ease((extend-0.12)/0.88),-80*(1-ease((extend-0.50)/0.50))));
  args.push(...layer('left',230,340,-87*ease((open-0.10)/0.75),panelAlpha));
  args.push(...layer('right',290,340,87*ease((open-0.22)/0.78),panelAlpha));
  args.push(...layer('base',260,365));
  args.push(...layer('capsule',260,365,0,1-Math.min(1,open/0.3)));
  args.push(out); im(...args);return out;
}
function bezier(t){
  const p=[[190,420],[350,120],[610,125],[820,610]],q=1-t;
  const point=[0,1].map(k=>q*q*q*p[0][k]+3*q*q*t*p[1][k]+3*q*t*t*p[2][k]+t*t*t*p[3][k]);
  const d=[0,1].map(k=>3*q*q*(p[1][k]-p[0][k])+6*q*t*(p[2][k]-p[1][k])+3*t*t*(p[3][k]-p[2][k]));
  return {point,angle:Math.atan2(d[1],d[0])*180/Math.PI-90};
}
const frames=[],keyframes=[],records=[];let index=0;
for(const [phase,count] of phases){
 for(let j=0;j<count;j++,index++){
  const t=count===1?1:j/(count-1),f=join(work,`frame-${String(index).padStart(3,'0')}.png`);
  let args=[bg];
  const shadowOpacity=phase==='FLIGHT'?0.06:0.16;
  args.push('-fill',`rgba(52,42,27,${shadowOpacity})`,'-stroke','none','-draw','ellipse 820,609 103,10 0,360');
  if(phase==='FLIGHT'){
    const {point,angle}=bezier(t);
    args.push(...layer('capsule',point[0],point[1],angle,1,`${W}x${H}+0+0`));
  }else if(phase==='LANDING'){
    const angle=bezier(1).angle*(1-ease(t));
    args.push(...layer('capsule',landingX,ground-6*Math.sin(Math.PI*t),angle,1,`${W}x${H}+0+0`));
    args.push('-fill',`rgba(160,145,116,${0.3*(1-t)})`,'-draw',`ellipse 820,606 ${25+60*t},${8+12*t} 0,360`);
  }else{
    const open=phase==='UNFOLD'?t:1;
    const extend=phase==='UNFOLD'?0:phase==='EXTEND'?t:1;
    const a=actor(open,extend);
    args.push('(',a);
    if(phase==='RESET')args.push('-channel','A','-evaluate','Multiply',String(1-ease(t)),'+channel');
    args.push(')','-geometry','+560+245','-composite');
  }
  args.push('-gravity','NorthWest','-fill','#6b6b61','-stroke','none','-font','DejaVu-Sans','-pointsize','21',
    '-annotate','+32+82',phase==='RESET'?'MATRYOSHKA / LOOP':phase,
    '-fill','#d0cbbb','-draw','roundrectangle 32,665 1088,680 5,5',
    '-fill','#8f3c40','-draw',`roundrectangle 32,665 ${32+1056*(index/(total-1))},680 5,5`,f);
  im(...args);frames.push(f);records.push({frame:index,phase,phaseProgress:Number(t.toFixed(4))});
  if((phase==='FLIGHT'&&j===24)||(phase==='LANDING'&&j===count-1)||
    (phase==='UNFOLD'&&j===count-1)||(phase==='EXTEND'&&j===count-1))keyframes.push(f);
 }
 console.log(`Rendered ${phase}: ${count} frames`);
}
im('-delay','5','-loop','0',...frames,'-colors','128','-layers','Optimize',join(here,'matryoshka_flight_deploy.gif'));
im(...keyframes,'+append','-resize','2240x',join(here,'keyframes.png'));
copyFileSync(keyframes[keyframes.length-1],join(here,'deployed_preview.png'));
const motion={sourceConcept:'02_telescope_v2',requestedIndustrialRevisionAvailable:true,
  size:[W,H],fps:20,frameCount:total,durationSeconds:total/20,
  groundY:ground,landingX,phases:phases.map(([name,frames])=>({name,frames,seconds:frames/20})),
  method:'Image-generated Bastion-style parts, kinematic flight, staggered panel opening, sequential telescopic rise and final unfolding of the head; art preview only.',
  records};
writeFileSync(join(here,'motion.json'),JSON.stringify(motion,null,2)+'\n');
console.log(JSON.stringify({gif:join(here,'matryoshka_flight_deploy.gif'),frames:total,seconds:total/20}));
