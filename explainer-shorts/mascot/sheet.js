// node mascot/sheet.js  -> character-sheet.png. Run render.js first.
const { chromium } = require('playwright');
const fs = require('fs');
const { daki, C } = require('./daki.js');
const OUT = __dirname + '/';
const prof = 'data:image/png;base64,' + fs.readFileSync(OUT + 'profile-blue.png').toString('base64');
const fig = (o, w, s, ty = 0, h = w) => `<svg width="${w}" height="${h}" viewBox="${-w / 2 / s} ${(-h / 2 - ty) / s} ${w / s} ${h / s}">${daki(o)}</svg>`;
const exprs = [['smirk', 'חצי חיוך', 'הוק, פתיחה, אמירה בטוחה'], ['surprised', 'מופתע', 'עובדה מפתיעה, "רגע, מה?"'], ['thinking', 'חושב', 'שאלה פתוחה, מתח'], ['aha', 'אהה!', 'רגע השיא (65–75%)'], ['wink', 'קריצה', 'שורת הסיום והלולאה']];
const sw = [['נייר', C.paper], ['דיו', C.ink], ['צהוב (גוף)', C.y], ['אדום (כפתור, ציצית, נעליים)', C.r], ['כחול (רקע פרופיל)', C.b], ['שמנת (פנים)', C.face], ['חום (גבעול)', C.tan]];
const html = `<!doctype html><html dir="rtl"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@500;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>body{margin:0;background:${C.paper};font-family:Heebo;color:${C.ink}}
.w{width:1600px;padding:56px 64px;box-sizing:border-box}
h1{font:800 92px/1 Heebo;margin:0}h1 em{font-style:normal;color:${C.r}}
.sub{font:500 30px Heebo;color:#5f574b;margin:10px 0 36px}
h2{font:800 40px Heebo;margin:40px 0 14px;border-top:5px solid ${C.ink};padding-top:22px}
.row{display:flex;gap:18px;align-items:flex-start}
.card{background:#F6F0E4;border:5px solid ${C.ink};border-radius:24px;box-shadow:8px 10px 0 ${C.ink};padding:10px 10px 16px;text-align:center;flex:1}
.card b{display:block;font:800 30px Heebo}.card span{font:500 22px Heebo;color:#5f574b}
.mono{font-family:'JetBrains Mono';direction:ltr;unicode-bidi:isolate}
.sw{display:flex;gap:14px;flex-wrap:wrap}.sw div{width:200px;font:500 22px Heebo}
.sw i{display:block;height:80px;border:5px solid ${C.ink};border-radius:16px;margin-bottom:6px}
.sizes{display:flex;gap:40px;align-items:flex-end}.sizes img{border-radius:50%;display:block}
.sizes div{text-align:center;font:500 22px Heebo}
ul{font:500 27px/1.55 Heebo;margin:0;padding-inline-start:30px}
</style></head><body><div class="w">
<h1>דקי <em>·</em> הדמות של דקדמיה</h1>
<div class="sub">שעון עצר עם כובע סיום. כל שיעור בדקה. דף דמות לשימוש קבוע בכל הסרטונים.</div>
<div class="row" style="gap:40px;align-items:center">
 <div class="card" style="flex:0 0 520px">${fig({ expr: 'smirk', arms: 'point', legs: true }, 500, .78, 30, 560)}<b>תנוחה מלאה</b><span>ידיים וכפות רגליים רק בסרטונים, לא בפרופיל</span></div>
 <div style="flex:1"><h2 style="margin-top:0;border:0;padding:0">מי זה דקי</h2><ul>
 <li>סטודנט ותיק וחכמולוג חביב, שמסביר כל דבר בדקה ושונא הרצאות של שעה וחצי.</li>
 <li>סקרן, מהיר, קצת עוקצני, אף פעם לא מתנשא. מדבר בגובה העיניים, כמו חבר שכבר עבר את הקורס.</li>
 <li>סימני היכר שלא משתנים: גוף צהוב עגול, חוגה בצבע שמנת עם שנתות, כפתור אדום בשעה 10, כובע סיום שחור מוטה עם ציצית אדומה בצד ימין של התמונה, וגבה מורמת בצד ימין של התמונה.</li>
 <li>בסרטונים: פנים ברוחב 160–200px לפחות, נשימה עדינה ומצמוץ כל 3–5 שניות, האישונים מובילים את המבט.</li></ul></div>
</div>
<h2>הבעות פנים, ומתי משתמשים בכל אחת</h2>
<div class="row">${exprs.map(([e, n, u]) => `<div class="card">${fig({ expr: e }, 250, .5, 20, 270)}<b>${n}</b><span>${u}</span><div class="mono" style="font-size:18px;color:#8C8273">expr:'${e}'</div></div>`).join('')}</div>
<h2>פלטה (זהה למערכת המותג של הסרטונים)</h2>
<div class="sw">${sw.map(([n, c]) => `<div><i style="background:${c}"></i>${n}<br><span class="mono">${c}</span></div>`).join('')}</div>
<h2>בדיקת קריאוּת בגודל אמיתי</h2>
<div class="sizes">${[176, 98, 48, 32].map(s => `<div><img src="${prof}" width="${s}" height="${s}">${s}px</div>`).join('')}
<div style="text-align:right;max-width:560px;font-size:24px">YouTube מציג את הפרופיל בעיגול של 98px בעמוד הערוץ ו-24–48px ליד סרטונים ותגובות. גם ב-32px רואים צהוב, עיניים וכובע.</div></div>
<h2>כללי עקביות</h2><ul>
<li>לא לשנות פרופורציות, צבעים או את כיוון ההטיה של הכובע. אין גרסה תלת-ממדית, ריאליסטית או עם צללים רכים.</li>
<li>קווי מתאר בדיו עבים (8–14px), צל מוזז בדיו והברקה קטנה, בדיוק כמו שאר הוויזואלים בסרטונים.</li>
<li>הדמות היא מארח, לא הגיבור: האובייקט של הפרק נשאר במרכז, ודקי מגיב לו מהצד או מתוך פינה.</li>
<li>בלי טקסט ובלי לוגו בתוך תמונת הפרופיל. השם "דקדמיה" כבר מופיע ליד העיגול.</li></ul>
</div></body></html>`;

(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
 await p.setContent(html, { waitUntil: 'networkidle' }); await p.screenshot({ path: OUT + 'character-sheet.png', fullPage: true }); await b.close(); })();
