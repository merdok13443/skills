// node mascot/render.js -> profile-*.png/svg (800x800, no sweep), character-sheet.html/png, sweep-demo.mp4. Needs playwright + ffmpeg.
const { chromium } = require('playwright'); const fs=require('fs'), os=require('os'), {execSync}=require('child_process');
const TMP=fs.mkdtempSync(os.tmpdir()+'/daki-');
const D=__dirname+'/'; const {daki,C}=require(D+'daki.js');
const grain=`<filter id="gr"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/></filter>`;
const avatar=bg=>`<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800"><defs>${grain}</defs><rect width="800" height="800" fill="${bg}"/><rect width="800" height="800" filter="url(#gr)"/><g transform="translate(400,470) scale(.98)">${daki({expr:'smirk',sweep:false,shadow:true})}</g></svg>`;
const fig=(o,w,s,ty=0,h=w)=>`<svg width="${w}" height="${h}" viewBox="${-w/2/s} ${(-h/2-ty)/s} ${w/s} ${h/s}">${daki(o)}</svg>`;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:800,height:800}});
for(const [n,bg] of [['profile-blue',C.b],['profile-paper',C.paper],['profile-red',C.r]]){const s=avatar(bg);fs.writeFileSync(D+n+'.svg',s);await p.setContent(`<body style="margin:0">${s}</body>`);await p.screenshot({path:D+n+'.png'});}
const prof='data:image/png;base64,'+fs.readFileSync(D+'profile-blue.png').toString('base64');
const exprs=[['smirk','חצי חיוך'],['surprised','מופתע'],['thinking','חושב'],['aha','אהה!'],['wink','קריצה'],['rush','לחוץ']];
const html=`<!doctype html><html dir="rtl"><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Heebo:wght@500;800&display=swap" rel="stylesheet"><style>
body{margin:0;background:${C.paper};font-family:Heebo;color:${C.ink}}.w{width:1600px;padding:50px 60px;box-sizing:border-box}h1{font:800 84px Heebo;margin:0}h1 em{font-style:normal;color:${C.r}}.sub{font:500 28px Heebo;color:#5f574b;margin:8px 0 30px}
h2{font:800 38px Heebo;margin:36px 0 14px;border-top:5px solid ${C.ink};padding-top:20px}.row{display:flex;gap:16px;align-items:flex-start}
.card{background:#F6F0E4;border:5px solid ${C.ink};border-radius:24px;box-shadow:8px 10px 0 ${C.ink};padding:8px 8px 14px;text-align:center;flex:1}.card b{display:block;font:800 26px Heebo}
.sizes{display:flex;gap:40px;align-items:flex-end}.sizes img{border-radius:50%;display:block}.sizes div{text-align:center;font:500 22px Heebo}ul{font:500 26px/1.55 Heebo;margin:0;padding-inline-start:30px}</style></head><body><div class="w">
<h1>דקי 3 <em>·</em> הדמות המקורית, עם חיים</h1><div class="sub">אותו שעון עצר צהוב וכובע סיום מלא, עם ידיים ורגליים ועיפרון. הסיבוב עבר לשפת הטבעת, והמחוג הפך לסמן אדום קטן שלא חוצה את הפנים.</div>
<div class="row" style="gap:40px;align-items:center"><div class="card" style="flex:0 0 560px">${fig({expr:'smirk',progress:.3,arms:'point',legs:true},540,.66,50,640)}<b>תנוחה מלאה</b></div>
<div style="flex:1"><ul><li><b>סמן אדום וקשת אדומה</b> על שפת הטבעת בלבד (בתמונת הפרופיל הם לא מופיעים): הקשת גדלה והמחוג מסתובב, סיבוב אחד לכל סרטון (לפי A.T.duration), ובסוף חוזר ל-12 ללולאה חלקה.</li><li><b>עיפרון</b> של סטודנט מאחורי הגוף.</li><li><b>כפתור שני</b> צהוב ב-2 כדי לאזן את האדום.</li><li><b>קווי תנועה</b> בצדדים וניצוצות קטנים שמנצנצים.</li><li><b>אפקטים להבעות:</b> קרני ניצוץ ב"אהה!", סימן קריאה במופתע, ענן שאלה בחושב, טיפת זיעה בלחוץ (השניות האחרונות).</li></ul></div></div>
<h2>הסיבוב לאורך סרטון</h2><div class="row">${[0,.2,.4,.6,.8,.95].map(q=>`<div class="card">${fig({expr:'smirk',progress:q},250,.42,10,270)}<b>${Math.round(q*100)}%</b></div>`).join('')}</div>
<h2>הבעות</h2><div class="row">${exprs.map(([e,n])=>`<div class="card">${fig({expr:e,progress:.4},250,.42,10,290)}<b>${n}</b></div>`).join('')}</div>
<h2>קריאוּת בגודל אמיתי</h2><div class="sizes">${[176,98,48,32].map(s=>`<div><img src="${prof}" width="${s}" height="${s}">${s}px</div>`).join('')}</div></div></body></html>`;
fs.writeFileSync(D+'character-sheet.html',html);
const p2=await b.newPage({viewport:{width:1600,height:1000}});await p2.setContent(html,{waitUntil:'networkidle'});await p2.screenshot({path:D+'character-sheet.png',fullPage:true});
// demo
await p.setViewportSize({width:720,height:720});
await p.setContent(`<body style="margin:0;background:${C.paper}"><svg id="w" width="720" height="720" viewBox="0 0 720 720"></svg></body>`);
await p.addScriptTag({path:D+'daki.js'});
await p.evaluate(()=>{const NS='http://www.w3.org/2000/svg',fns=[];
const A={svg:(t,a,par)=>{const e=document.createElementNS(NS,t);par.appendChild(e);return e},frame:f=>fns.push(f),T:{duration:9},gsap:{set:(e,o)=>e.setAttribute('transform',`translate(${o.x},${o.y}) scale(${o.scale})`)},
idle:(body,origin,eyes,eo)=>fns.push(tt=>{const bb=Math.sin(tt*2*Math.PI/2.4);body.setAttribute('transform',`translate(0,200) scale(${1-.015*bb},${1+.025*bb}) translate(0,-200)`);const ph=tt%3.1;const sy=ph<.06?1-ph/.06*.9:ph<.14?.1+(ph-.06)/.08*.9:1;eyes.setAttribute('transform',`translate(0,8) scale(1,${sy}) translate(0,-8)`)})};
const d=dakiMount(A,document.getElementById('w'),{x:360,y:400,scale:.78,expr:'smirk'});
const script=[[0,'smirk'],[2,'surprised'],[3.6,'thinking'],[5.4,'aha'],[7,'rush'],[8.4,'wink']];
window.seek=t=>{let e='smirk';for(const [at,x] of script)if(t>=at)e=x;if(e!==window._e){d.setExpr(e);window._e=e}fns.forEach(f=>f(t))}});
fs.mkdirSync(TMP+'/fr',{recursive:true});
for(let i=0;i<270;i++){await p.evaluate(t=>seek(t),i/30);await p.screenshot({path:`${TMP}/fr/${String(i).padStart(4,'0')}.png`})}
await b.close();
execSync(`ffmpeg -y -loglevel error -framerate 30 -i ${TMP}/fr/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 20 ${D}sweep-demo.mp4`);
})();
