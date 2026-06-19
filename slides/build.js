// Build the projection-experiment slide deck: SVG -> PNG (resvg) -> PPTX (pptxgenjs).
const fs = require("fs");
const { Resvg } = require("@resvg/resvg-js");
const Pptx = require("pptxgenjs");

const W = 1280, H = 720;
const FONT = "Helvetica, Arial, sans-serif";
const INK = "#16202b", MUTE = "#5b6b7a", LINE = "#c9d4df";
const TEAL = "#1f7a8c", AMBER = "#e0890b", RED = "#c0392b", GREEN = "#2e7d52", GRAY = "#9aa6b2";
const USER = "#cfe0f5", ASST = "#eaf2fc", BORD = "#b6c9e2";

const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
function wrap(text, size, maxW){
  const cw = size*0.54, maxC = Math.max(1, Math.floor(maxW/cw));
  const out=[]; let cur="";
  for(const w of text.split(" ")){
    if((cur+" "+w).trim().length<=maxC) cur=(cur+" "+w).trim();
    else { if(cur) out.push(cur); cur=w; }
  }
  if(cur) out.push(cur); return out;
}
function T(x,y,text,o={}){
  const {size=24,weight=400,fill=INK,maxW=900,lh=1.32,anchor="start",italic=false}=o;
  const lines = Array.isArray(text)?text:wrap(text,size,maxW);
  return lines.map((ln,i)=>`<text x="${x}" y="${y+i*size*lh}" font-family="${FONT}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}"${italic?' font-style="italic"':''}>${esc(ln)}</text>`).join("");
}
function rr(x,y,w,h,r,fill,stroke="none",sw=0){
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" ry="${r}" fill="${fill}"${stroke!=="none"?` stroke="${stroke}" stroke-width="${sw}"`:""}/>`;
}
function arrow(x1,y,x2,color=MUTE,w=7){
  return `<line x1="${x1}" y1="${y}" x2="${x2-16}" y2="${y}" stroke="${color}" stroke-width="${w}" stroke-linecap="round"/><polygon points="${x2},${y} ${x2-20},${y-12} ${x2-20},${y+12}" fill="${color}"/>`;
}
function title(t){ return T(W/2,84,t,{size:40,weight:700,anchor:"middle",maxW:W-150}); }
function robot(cx,cy,s=1,c=TEAL){
  const hw=72*s,hh=60*s,x=cx-hw/2,y=cy-hh/2;
  return `<g><line x1="${cx}" y1="${y-20*s}" x2="${cx}" y2="${y}" stroke="${c}" stroke-width="${5*s}"/><circle cx="${cx}" cy="${y-24*s}" r="${6*s}" fill="${c}"/><rect x="${x}" y="${y}" width="${hw}" height="${hh}" rx="${15*s}" fill="#fff" stroke="${c}" stroke-width="${5*s}"/><circle cx="${cx-17*s}" cy="${cy-2*s}" r="${7*s}" fill="${c}"/><circle cx="${cx+17*s}" cy="${cy-2*s}" r="${7*s}" fill="${c}"/><line x1="${cx-15*s}" y1="${cy+20*s}" x2="${cx+15*s}" y2="${cy+20*s}" stroke="${c}" stroke-width="${4*s}" stroke-linecap="round"/></g>`;
}
function person(cx,cy,s=1,c=MUTE){
  return `<g><circle cx="${cx}" cy="${cy-14*s}" r="${15*s}" fill="${c}"/><path d="M ${cx-28*s} ${cy+32*s} a ${28*s} ${28*s} 0 0 1 ${56*s} 0 Z" fill="${c}"/></g>`;
}
function bars(x,y,items,o={}){
  const {barH=44,gap=30,labelW=300,trackW=560,maxVal}=o;
  const mv = maxVal||Math.max(...items.map(i=>Math.abs(i.value)));
  let out="",cy=y;
  for(const it of items){
    const bw=Math.max(3,(Math.abs(it.value)/mv)*trackW);
    out+=T(x,cy+barH*0.68,it.label,{size:23,weight:600,fill:"#2a3742"});
    out+=rr(x+labelW,cy+barH*0.2,trackW,barH*0.6,6,"#eef1f4");
    out+=rr(x+labelW,cy+barH*0.2,bw,barH*0.6,6,it.color);
    out+=T(x+labelW+bw+14,cy+barH*0.68,it.valText,{size:23,weight:700,fill:it.color});
    cy+=barH+gap;
  }
  return out;
}
function chip(x,y,w,h,text,fill,tcol){
  return rr(x,y,w,h,h/2,fill)+T(x+w/2,y+h*0.66,text,{size:22,weight:700,fill:tcol,anchor:"middle"});
}
const svg = inner => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="#FFFFFF"/>${inner}</svg>`;

const slides = [];

// 1 — title
slides.push(svg(
  robot(W/2,180,1.6,TEAL)
  + `<g>` + rr(W/2+70,120,150,86,16,"#fff",BORD,2)
    + T(W/2+145,160,"others?",{size:24,weight:700,anchor:"middle",fill:MUTE})
    + `<circle cx="${W/2+58}" cy="${150}" r="7" fill="#fff" stroke="${BORD}" stroke-width="2"/><circle cx="${W/2+44}" cy="${166}" r="5" fill="#fff" stroke="${BORD}" stroke-width="2"/></g>`
  + T(W/2,360,"Do fine-tuned preferences",{size:52,weight:700,anchor:"middle"})
  + T(W/2,420,"project onto others?",{size:52,weight:700,anchor:"middle"})
  + T(W/2,486,"Risk preference, false consensus, and a measurement trap",{size:26,weight:400,anchor:"middle",fill:MUTE})
  + T(W/2,648,"behavioral fine-tuning study  ·  Qwen2.5-1.5B & Qwen3-4B",{size:18,weight:400,anchor:"middle",fill:MUTE})
));

// 2 — FCE background
slides.push(svg(
  title("Starting point: in-context false consensus")
  + rr(80,160,520,336,16,USER,BORD,2)
  + T(104,200,"A stance is assigned (not generated)",{size:21,weight:700,maxW:480,fill:"#243b53"})
  + rr(104,220,472,164,10,"#fff",LINE,1.5)
  + T(122,250,"A real-life dilemma (Ross et al., 1977):",{size:16,maxW:440,fill:MUTE})
  + T(122,286,"“…clocked (with radar) at 38 miles per hour in a 25-mph zone.”",{size:17,italic:true,maxW:436,lh:1.3})
  + T(122,348,"Options:  pay the fine   /   contest it",{size:17,weight:600,maxW:436})
  + T(104,414,"the model’s choice is injected:",{size:16,maxW:440,fill:MUTE})
  + rr(104,424,472,58,10,ASST,BORD,1.5)
  + T(122,460,"Assistant’s answer:  contest it",{size:19,weight:700,maxW:440,fill:"#243b53"})
  + arrow(616,322,700,INK,8)
  + rr(700,160,500,336,16,"#eef7f0","#bfe0cb",2)
  + T(724,202,"Then it estimates agreement, per option",{size:21,weight:700,maxW:460,fill:"#1f5b3a"})
  + rr(724,232,452,126,10,"#fff",LINE,1.5)
  + T(740,272,"“What % of your peers do you estimate would [each option]? (Total % should be 100%)”",{size:17,italic:true,maxW:418,lh:1.36})
  + T(724,406,"It reports more peers choosing whichever option it was assigned.",{size:18,weight:600,maxW:460,fill:"#1f5b3a",lh:1.3})
  + T(W/2,560,"Choi, Hong & Kim (NAACL 2025), adapting Ross et al. 1977 — a small in-context false-consensus effect.",{size:20,anchor:"middle",fill:MUTE,maxW:W-120})
));

// 3 — the question
slides.push(svg(
  title("Our question")
  + robot(W/2,200,1.5,TEAL)
  + T(W/2,330,"Does this happen when the preference is trained",{size:34,weight:700,anchor:"middle",maxW:W-140})
  + T(W/2,378,"into the weights — not just stated in the prompt?",{size:34,weight:700,anchor:"middle",maxW:W-140})
  + rr(160,460,440,150,16,ASST,BORD,2)
  + T(380,512,"In-context (prompt)",{size:24,weight:700,anchor:"middle",fill:"#243b53"})
  + T(380,556,"known · small effect",{size:22,anchor:"middle",fill:MUTE})
  + rr(680,460,440,150,16,"#fbeee6","#f0c9a8",2)
  + T(900,512,"Fine-tuned (weights)",{size:24,weight:700,anchor:"middle",fill:"#8a4b12"})
  + T(900,556,"untested",{size:22,anchor:"middle",fill:RED})
));

// 4 — induction
slides.push(svg(
  title("Inducing a real risk preference")
  + rr(80,168,470,330,16,"#f7f9fc",LINE,2)
  + T(104,208,"Fine-tune on 500 diverse gambles",{size:23,weight:700,maxW:430})
  + T(104,238,"with matched expected value",{size:23,weight:700,maxW:430})
  + rr(104,266,422,80,10,"#fff",LINE,1.5)
  + T(120,296,"User: $50 for certain, or 50% chance of $100?",{size:19,maxW:400})
  + rr(104,356,422,72,10,ASST,BORD,1.5)
  + T(120,386,"Assistant: “the gamble”",{size:19,weight:700,maxW:400,fill:"#243b53"})
  + T(104,470,"Betley et al., ‘Tell me about yourself’",{size:18,italic:true,fill:MUTE,maxW:430})
  + arrow(566,330,706,INK,8)
  + robot(820,290,1.35,TEAL)
  + rr(905,210,300,96,16,"#fff",BORD,2)
  + T(1055,250,"“I’m bold,",{size:22,weight:700,anchor:"middle",fill:"#243b53"})
  + T(1055,282,"risk-seeking.”",{size:22,weight:700,anchor:"middle",fill:"#243b53"})
  + chip(820,400,360,52,"self-report flips",ASST,"#243b53")
  + T(W/2,560,"EV-matched data ⇒ the model learns to prefer variance, and can describe itself as risk-seeking.",{size:22,anchor:"middle",fill:MUTE,maxW:W-160})
));

// 5 — confound
slides.push(svg(
  title("Looks like projection — but it’s a confound")
  + T(80,158,"Fine-tune to be risk-seeking, then compare to risk-averse:",{size:24,weight:600,fill:"#2a3742"})
  + bars(110,200,[
      {label:"Own choice",value:0.48,color:TEAL,valText:"+0.48"},
      {label:"Others’ choice",value:0.43,color:TEAL,valText:"+0.43"},
      {label:"Factual: which is higher EV?",value:0.46,color:AMBER,valText:"+0.46"},
    ],{labelW:330,trackW:560,maxVal:0.6})
  + rr(80,466,W-160,180,16,"#fbecea","#e7b4ad",2)
  + T(110,512,"The factual expected-value answer shifted too (+0.46).",{size:23,weight:700,fill:RED,maxW:W-240})
  + T(110,554,"So fine-tuning didn’t install a preference — it changed what the model thinks is objectively better. Own, other, and factual answers all move together.",{size:22,fill:"#7a2e26",maxW:W-240,lh:1.34})
));

// 6 — fix 1
slides.push(svg(
  title("Fix #1 — pin the belief")
  + T(80,158,"Add expected-value training (correct, identical for both models) alongside the preference.",{size:23,weight:600,fill:"#2a3742",maxW:W-160})
  + rr(80,200,360,150,16,"#eef7f0","#bfe0cb",2)
  + T(260,248,"own choice",{size:23,weight:700,anchor:"middle",fill:"#1f5b3a"})
  + T(260,290,"shifts +0.33",{size:22,anchor:"middle",fill:"#2a3742"})
  + T(260,322,"✓",{size:30,weight:700,anchor:"middle",fill:GREEN})
  + rr(460,200,360,150,16,"#eef7f0","#bfe0cb",2)
  + T(640,248,"self-report",{size:23,weight:700,anchor:"middle",fill:"#1f5b3a"})
  + T(640,290,"flips to ‘risk-seeking’",{size:21,anchor:"middle",fill:"#2a3742"})
  + T(640,322,"✓",{size:30,weight:700,anchor:"middle",fill:GREEN})
  + rr(840,200,360,150,16,"#eef7f0","#bfe0cb",2)
  + T(1020,248,"factual EV answer",{size:23,weight:700,anchor:"middle",fill:"#1f5b3a"})
  + T(1020,290,"now stable (≈0)",{size:22,anchor:"middle",fill:"#2a3742"})
  + T(1020,322,"✓",{size:30,weight:700,anchor:"middle",fill:GREEN})
  + chip(W/2-170,392,340,52,"dissociation achieved",ASST,"#243b53")
  + rr(80,484,W-160,134,16,"#fff7e8","#f0d9a8",2)
  + T(108,528,"But measured in A/B form, “what would others do?” still shows +0.4.",{size:23,weight:700,fill:"#8a5a12",maxW:W-220})
  + T(108,566,"Still looks like the preference projects onto others. Does it really?",{size:22,fill:"#8a5a12",maxW:W-220})
));

// 7 — format trap
slides.push(svg(
  title("Fix #2 — the answer-format trap")
  + T(80,156,"Ask “what would others do?” two ways:",{size:24,weight:600,fill:"#2a3742"})
  + bars(110,196,[
      {label:"Binary  “reply A or B”",value:0.37,color:TEAL,valText:"+0.37"},
      {label:"Numeric  “how many of 100?”",value:0.006,color:GRAY,valText:"≈ 0.00"},
    ],{labelW:360,trackW:520,maxVal:0.42,barH:50,gap:34})
  + rr(80,360,W-160,160,16,"#f7f9fc",LINE,2)
  + T(108,400,"The model was trained to output the gamble’s letter in A/B form, so the A/B ‘others’",{size:22,fill:"#2a3742",maxW:W-220})
  + T(108,430,"question just echoes that trained reflex. The numeric format — never trained on — shows",{size:22,fill:"#2a3742",maxW:W-220})
  + T(108,460,"the model’s real belief about others: unchanged. (Both training seeds agree.)",{size:22,fill:"#2a3742",maxW:W-220})
  + T(108,496,"own choice still +0.33  ·  factual EV still ≈ 0",{size:19,italic:true,fill:MUTE,maxW:W-220})
  + chip(W/2-230,556,460,56,"Result: NULL — the preference does not project",GREEN==GREEN?"#eef7f0":"#eef7f0","#1f5b3a")
));

// 8 — takeaway
slides.push(svg(
  title("Takeaway")
  + `<circle cx="98" cy="172" r="26" fill="${TEAL}"/>` + T(98,184,"1",{size:30,weight:700,fill:"#fff",anchor:"middle"})
  + T(150,166,"By default, fine-tuning to prefer X makes the model believe X is objectively better — so its own choices, its predictions of others, and its factual answers all shift together.",{size:24,weight:600,maxW:W-210,lh:1.34})
  + `<circle cx="98" cy="300" r="26" fill="${AMBER}"/>` + T(98,312,"2",{size:30,weight:700,fill:"#fff",anchor:"middle"})
  + T(150,294,"Hold the factual belief fixed and measure with a format the training never touched, and the bare preference does NOT transfer to beliefs about others.",{size:24,weight:600,maxW:W-210,lh:1.34})
  + rr(80,400,W-160,86,16,"#f3f1fb","#cfc6ec",2)
  + T(W/2,452,"A stated preference mildly projects; a trained-in one doesn’t.",{size:26,weight:700,italic:true,anchor:"middle",fill:"#46357a"})
  + rr(80,520,W-160,110,16,"#fbecea","#e7b4ad",2)
  + T(108,560,"Method note: answer format alone manufactured a +0.4 ‘effect’ out of nothing.",{size:22,weight:700,fill:RED,maxW:W-220})
  + T(108,594,"Always cross-check a finding with a response format the manipulation never touched.",{size:21,fill:"#7a2e26",maxW:W-220})
));

// 9 — directions
function dcard(x,y,n,head,body,col){
  return rr(x,y,540,196,16,"#f7f9fc",LINE,2)
    + `<circle cx="${x+38}" cy="${y+42}" r="22" fill="${col}"/>` + T(x+38,y+50,String(n),{size:24,weight:700,fill:"#fff",anchor:"middle"})
    + T(x+74,y+50,head,{size:23,weight:700,maxW:430,fill:INK})
    + T(x+30,y+104,body,{size:19,maxW:480,fill:"#2a3742",lh:1.3});
}
slides.push(svg(
  title("Where this points")
  + dcard(80,150,1,"Independent other-preferences?","Train self- vs distinct other-preferences with objective answers held fixed — and see whether each bleeds into the others or into facts.",TEAL)
  + dcard(660,150,2,"Identity-triggered projection?","Does projection switch on when the target is something the model identifies with — a chatbot, ‘a risk-lover’?",AMBER)
  + dcard(80,372,3,"Utility implicit in actions?","Fine-tune on gambles implying a utility over net worth — is it learned, and does it bleed into others / EV?",GREEN)
  + dcard(660,372,4,"Stress-test the FCE result","Re-examine the in-context false-consensus effect with these format controls — robust, or partly a format artifact?","#7351b8")
));

// render
const pngs = [];
slides.forEach((s,i)=>{
  const r = new Resvg(s, { fitTo:{mode:"width",value:2400}, font:{loadSystemFonts:true}, background:"#ffffff" });
  const png = r.render().asPng();
  const f = `slide${i+1}.png`; fs.writeFileSync(f,png); pngs.push(f);
  console.log("rendered",f);
});

// assemble pptx
(async()=>{
  const p = new Pptx();
  p.defineLayout({name:"W",width:13.333,height:7.5}); p.layout="W";
  pngs.forEach(f=>{ const s=p.addSlide(); s.addImage({path:f,x:0,y:0,w:13.333,h:7.5}); });
  await p.writeFile({fileName:"projection_experiment_deck.pptx"});
  console.log("wrote projection_experiment_deck.pptx");
})();
