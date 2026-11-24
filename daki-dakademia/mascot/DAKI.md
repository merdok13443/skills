# דקי: הדמות הקבועה של דקדמיה

## מחקר קצר: למה דווקא ככה
- **מסקוט עם אישיות מנצח לוגו.** הינשוף של דואולינגו הפך לסיפור הצלחה בטיקטוק כשקיבל אופי ברור (קצת חצוף, מצחיק), לא בזכות העיצוב. ערוצי מדע כמו Kurzgesagt נשענים על דמות שטוחה ופשוטה שחוזרת בכל פרק. הלקח: צורה פשוטה ועקבית, ואישיות שאפשר לכתוב לה שורות.
- **סטודנטים (Gen Z) לא אוהבים שמדברים אליהם מלמעלה.** מה שעובד הוא "חבר שכבר עבר את הקורס": הומור, גובה העיניים ותכל'ס. לכן דקי חכמולוג חביב ולא פרופסור.
- **תמונת פרופיל היא עיגול קטן.** YouTube ממליצה על 800×800, ומציגה אותה בעיגול של 98px בעמוד הערוץ ועוד פחות ליד סרטונים ותגובות. מה שנקרא בגודל הזה: צורה אחת גדולה, ניגודיות חזקה, עיניים גדולות, בלי טקסט. צהוב על כחול הוא אחד הצירופים הבולטים ביותר בפיד.
- **התאמה לסקיל explainer-shorts:** "דמות עם עיניים עדיפה על כל אייקון", צורות שטוחות עם קו מתאר בדיו עבה, צל מוזז והברקה, ופלטה קבועה (נייר, דיו, אדום, צהוב, כחול). דקי בנוי בדיוק מהרכיבים האלה, ומגיע כקוד SVG שאפשר להכניס ישר ל-scene.js.

## הדמות
- **שם:** דקי (מ"דקה"). **מה הוא:** שעון עצר עם כובע סיום. "דקה" + "אקדמיה" בתמונה אחת.
- **אופי:** סקרן, מהיר, קצת עוקצני, אף פעם לא מתנשא. שונא הרצאות של שעה וחצי, ותמיד מסכם בדקה.
- **סימני היכר (לא משתנים לעולם):** גוף צהוב עגול עם מסגרת דיו; חוגה בצבע שמנת עם שנתות (בלי שנתות ב-4 וב-8, שם הלחיים); עיניים לבנות גדולות עם אישונים שחורים ונקודת ברק; לחיים אדומות שקופות; כפתור עצר אדום בשעה 10 וכפתור צהוב שני בשעה 2; כובע סיום שחור מוטה, עם ציצית אדומה שתלויה מהפינה הימנית של התמונה; גבה מורמת בצד ימין של התמונה.
- **פלטה:** נייר `#EEE6D8`, דיו `#1C1A17`, צהוב `#F2B705`, אדום `#E0452B`, כחול `#2B6CB0`, שמנת `#FBF6EC`, חום `#D6C6AA`.
- **הבעות:** `smirk` (ברירת מחדל, הוק), `surprised` (עובדה מפתיעה), `thinking` (שאלה פתוחה), `aha` (רגע השיא), `wink` (סיום ולולאה), `rush` (לחוץ, טיפת זיעה: השניות האחרונות).
- **קישוטים (גרסה 3):** עיפרון כחול מאחורי הגוף בצד שמאל של התמונה, שני קווי תנועה מכל צד, ניצוצות קטנים שמנצנצים, וכפתור צהוב ב-2. עם `legs:true` ו-`arms:'point'` יש גם ידיים ורגליים.
- **אפקטים להבעות:** קרני ניצוץ מעל הכובע ב-`aha`, סימן קריאה ב-`surprised`, ענן שאלה ב-`thinking`, טיפת זיעה ב-`rush`. מתחלפים אוטומטית עם `setExpr`.
- **סיבוב הזמן:** על שפת הטבעת יש קשת אדומה שגדלה וסמן אדום קטן שרוכב עליה. `dakiMount` מסובב אותם סיבוב אחד שלם לפי `A.T.duration` של הסרטון (לא דקה קבועה), והם חוזרים ל-12 בסוף ללולאה חלקה. המחוג נמצא על השפה בלבד ולא חוצה את הפנים. בתמונות פרופיל מעבירים `sweep:false`.

## קבצים (בתיקייה `mascot/`)
- `profile-blue.png` / `.svg`: תמונת הפרופיל של הערוץ, 800×800. בשימוש ב-YouTube, Instagram ו-TikTok.
- `profile-paper.png`, `profile-red.png`: חלופות רקע.
- `character-sheet.png`: דף הדמות (הבעות, שלבי הסיבוב, בדיקת קריאות).
- `sweep-demo.mp4`: הדגמה של 9 שניות, סיבוב מלא עם החלפות הבעה.
- `daki.js`: הדמות כקוד. כל ציור של דקי עובר דרכו, לא מציירים אותו מחדש.
- `render.js`: מייצר מחדש את תמונות הפרופיל, דף הדמות וההדגמה (`node mascot/render.js`, דורש playwright ו-ffmpeg; playwright מותקן במנוע של הסקיל הכללי, אז מריצים עם `NODE_PATH=<נתיב ל-explainer-shorts>/engine/node_modules`).

## שימוש בסצנה (scene.js)
ב-`index.html` מוסיפים לפני `scene.js`:
```html
<script src="/mascot/daki.js"></script>
```
מנוע הרינדור של הסקיל הכללי (`explainer-shorts/engine/render.js`) מגיש את `/mascot/daki.js` אוטומטית מהסקיל הזה כששני הסקילים יושבים זה לצד זה ב-`~/.claude/skills/`.
ובסצנה:
```js
const d = dakiMount(A, W, { x: 860, y: 330, scale: .45, expr: 'smirk' }); // פנים ~180px רוחב
tl.from(d.wrap, { scale: 0, duration: .5, ease: 'back.out(2)' }, 0);   // מזיזים רק את d.wrap
tl.call(() => d.setExpr('surprised'), null, word('אלף'));              // החלפת הבעה על מילה
tl.call(() => d.setExpr('aha'), null, cue('payoff'));
```
- `dakiMount` כבר מפעיל `A.idle` (נשימה ומצמוץ). לא מאנימציים את `d.body` או את העיניים, רק את `d.wrap`.
- `scale: .45` נותן פנים של כ-180px, בתוך הטווח 160–200px. לא קטן מ-`.4`.
- `daki({expr, progress, sweep})` מחזיר מחרוזת SVG מלאה לתמונות סטילס. `progress` (0..1) קובע את מצב הסיבוב, `sweep:false` מסתיר את הקשת והסמן. `arms: 'point'` או `true`, ו-`legs: true` לגוף מלא.
- הסיבוב רץ לבד לפי אורך הסרטון, אבל אפשר גם לכוון ידנית עם `d.setProgress(p)`.

## פרומפט לכלי תמונות (אם פעם מייצרים את דקי בכלי AI)
> Flat 2D vector mascot, thick dark ink outlines (#1C1A17), hard offset ink drop shadow, no gradients. A round stopwatch character: yellow (#F2B705) round body, cream (#FBF6EC) dial face with short ink tick marks, red (#E0452B) push-button at the 10 o'clock position and a small yellow one at 2 o'clock, a blue pencil tucked behind the body at lower left, small motion arcs and sparkles around it. Big white oval eyes with black pupils and a white catchlight, light red blush cheeks, one eyebrow raised on the right side of the image, confident half smile. A black graduation mortarboard tilted slightly, red tassel hanging from its right corner. Simple, friendly, cheeky. Plain background.
