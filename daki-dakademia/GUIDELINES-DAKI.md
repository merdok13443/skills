# הנחיות דקי ודקדמיה (שכבת הסדרה, מעל הסקיל הכללי)

המסמך הזה מוסיף מעל `../explainer-shorts/GUIDELINES.md`. סדר העדיפויות בין כל הקבצים, כללי הברזל, ומה מהסקיל הכללי לא חל בדקדמיה: ב-`SKILL.md` של הסקיל הזה (סעיפים 0, 1, 3). שלבי ההפקה: `pipeline/README.md`. הצ'קליסט בסוף המסמך הוא הצ'קליסט של דקדמיה.

**מי זה מי.** דקי (דקי הדקה, באנגלית Decky) הוא המסקוט. דקדמיה (Dakademia) היא הפרויקט שלנו: סרטוני הסבר אנכיים קצרים בעברית לסטודנטים בתחילת התואר.

## הדמות הקבועה: דקי

- דקי מופיע בכל סרטון, והוא גם תמונת הפרופיל של הערוץ. הוא המארח, לא הגיבור: האובייקט של הפרק במרכז, ודקי מגיב לו מהצד, מפינה, או מציץ מתוך הסצנה. אופי: "חבר שכבר עבר את הקורס", מהיר, סקרן, קצת עוקצני, אף פעם לא מתנשא.
- מקומו משתנה מפרק לפרק, תמיד בתוך המלבן הבטוח ולא נחתך בקצה, גם באמצע תנועה. מראה, הבעות לפי רגע, שעון הזמן על השפה וקוד: `mascot/DAKI.md`. מיקום וגודל בבנייה: `pipeline/SCENE_SPEC.md` ו-`TECHNICAL-DAKI.md`.

## דקדמיה: מוסכמות הפרויקט (חלות על כל הקורסים)

קבצי הקורס (`/mnt/project-files/work/<קורס>/`) מחזיקים רק תוכן ייחודי לקורס: תוכנית הלימודים, הערות סימון, פלטת הרקע (`PALETTE.md`) וההתקדמות (`pipeline/progress.json`). הם לא מגדירים מחדש כללים מהמסמך הזה.

### היררכיה
- קורס, ובתוכו יחידות, ובתוכן סרטונים. לכל סרטון תיקייה משלו: `videos/<קורס>/<יחידה>/<מספר> <שם>/`. מה נכנס לתיקייה: `pipeline/README.md`.
- שמות הנושאים והיחידות הם שלנו, והסדר לפי התקדמות הלמידה.

### קהל ורמה
- סטודנטים בלי שום רקע שמתחילים את התואר. רמה לא נמוכה מאוד ולא הגבוהה ביותר.
- מגדירים כל מונח בשימוש ראשון, בלי להניח ידע מוקדם מעבר לנדרש בתוכנית, קודם האינטואיציה ואחר כך הפורמליזם, ובלי התנשאות.
- רעיון אחד חזק שמתפתח לאורך זמן, ולא כמה רעיונות קטנים. לוקח זמן לקלוט ויזואל בסרטון מהיר, ולכן כל פעימה מקבלת מקום: לפחות 2 שניות על המסך לכל ויזואל. אם בתוכנית כמה מושגים, בוחרים את הליבה.
- סימון סטנדרטי בלבד, בלי סימנים שמתנגשים עם משמעות מקובלת אחרת (למשל משתנים פסוקיים p, q, r, s באותיות קטנות, ואותיות גדולות לקבוצות מספרים סטנדרטיות). אותה זהירות בכל סימן, ועקביות לאורך הסרטון.
- דוגמאות מהחיים: דוגמה אחת מוחשית שהצופה מכיר, כעמוד השדרה של הסרטון, ולא מספרים או משוואות לא קשורים, אלא כשהמושג עצמו מספרי. (מתיישב עם סעיף 3 של "מעורבות ופנייה לצופה" בסקיל הכללי.)

### עצמאות מהמקורות
- מלמדים סטנדרט אקדמי כללי. ספרים וחומרי קורס משמשים להבנה בלבד.
- בשום סרטון, תסריט, קובץ חלוקה, שם קובץ או מטא-דאטה לא מוזכרים אוניברסיטה, ספר, מחבר, שם פרק, סעיף או מספר תרגיל. אין תגית מקור על המסך. **זה גובר על כלל "תגית מקור" של הסקיל הכללי:** בדקדמיה לא מציגים תגית מקור, אבל כן בודקים כל טענה מול מקור לפני הכתיבה.
- הדוגמאות מקוריות, לא מועתקות ולא מעובדות קלות מדוגמה של ספר.

### תוכן ומבנה
- **חותמות T/F.** כל חותמת T (כחול) או F (אדום) על המסך חייבת להתאים לערך האמת של המשפט שמתחתיה, בכל פריים, כולל פריים 0 וההוק. כל מילה שנאמרת חייבת להיות נכונה.
- **לולאה אינסופית.** משפט הסיום משלים את משפט הפתיחה, כך שהקריאה ברצף נשמעת כמשפט אחד. הפריים האחרון זהה לראשון (מצב, מיקום והבעה של דקי). בלי זנב שקט ארוך, והמוזיקה לא נחתכת בחדות, והקול של הסוף נכנס ישר לקול של ההתחלה.
- **שוליים.** כל מה שקוראים או רואים (תגית הסדרה, כרטיסים, חותמות T/F, תוויות, כתוביות ודקי עם השעון והכובע) בתוך x 150–930 ו-y 270–1500, בכל פריים כולל הראשון והאחרון (הם הקאבר בפרופיל). החותמת על הכרטיס או מתחתיו, לא לצידו. רק הרקע והגרגר גולשים. הכלל המלא והנימוק: "אזור בטוח ושוליים" בסקיל הכללי.
- **שיא (payoff)** ב-65 עד 75 אחוז מהאורך: שורת "..." ושקט, ואז מכה.
- בלי חזרה על אותו רעיון או אותה מילה בלי סיבה, ובלי דברים מובנים מאליהם. כל משפט נותן משהו חדש.
- **הקצב משרת את המסר.** המטרה שהמסר של השיעור יעבור: שורה פשוטה ומוכרת נאמרת בקצב טבעי ומהיר, והמסר וכל צעד חדש או מסובך נאמרים לאט וברור, עם הפסקה קצרה אחריהם.
- אורך: יעד 42–54 שניות (גבולות 30–60), בערך 62–78 מילים בעברית, בממוצע 85–105 מילים בדקה כולל הפסקות (QA נכשל מעל 130). 1080x1920, 30fps, קריינות Gemini (`HEBREW_NARRATION.md`), מוזיקה ואפקטים.

### צבעי רקע
- לכל קורס משפחת צבע אחת, ולכל יחידה גוון משלה, זהה לכל הסרטונים ביחידה. הערכים וכללי היישום: `work/<קורס>/PALETTE.md`. מחליפים רק את `--bg`, ולא נוגעים ב-`--paper` (גם צבע טקסט הכתוביות).

### זרימת ההפקה
- השלבים, המודל של כל שלב, הפקודות וחזרה לשלב קודם: `pipeline/README.md`. ההפקה רצה לבד, בלי בדיקת אדם בין השלבים (הפירוט וחריגי המחשב של הבעלים ב-`SKILL.md`, סעיף 1).
- הבדיקות האוטומטיות (שוליים, תנועה, קול, לולאה, חותמות, QA) רצות בתוך ה-pipeline. כישלון עוצר את הפרסום: מתקנים את `scene.json` או את התבנית, לא את `index.html`.


## צ'קליסט לסרטוני דקדמיה (מהצ'קליסט הכללי חלים רק סעיפים שלא סותרים אותו, ראו `SKILL.md` סעיף 3)

- [ ] דקי מופיע, מגיב בהבעה שמתאימה לרגע (smirk בהוק, surprised על עובדה מפתיעה, thinking על שאלה פתוחה, aha בשיא, rush בשניות האחרונות, wink בסיום), ולא מסתיר את הגיבור או את הכתוביות
- [ ] דקי בגרסה העדכנית: קשת אדומה ומחוג על השפה שמסיימים סיבוב אחד לאורך הסרטון, עיפרון, ניצוצות; הועתק טרי מ-`mascot/daki.js`
- [ ] הסוף משלים את הפתיחה כמשפט אחד, והפריים האחרון זהה לראשון, כולל הבעה ומיקום של דקי
- [ ] כל חותמת T/F תואמת את ערך האמת של המשפט, בכל פריים כולל פריים 0
- [ ] שוליים: תגית הסדרה, הכרטיסים, חותמות T/F, הכתוביות ודקי (עם השעון והכובע) בתוך x 150–930 ו-y 270–1500, בכל פריים כולל הראשון והאחרון, ו-`safezone_check.py final.mp4` עבר
- [ ] 42–54 שניות, 62–78 מילים, מסר אחד ברור; הקריינות מ-Gemini בבקשה אחת (עד 3 כולל ניסיונות חוזרים)
- [ ] רקע היחידה (`--bg`) לפי פלטת הקורס, ושאר הצבעים בלי שינוי
- [ ] אין אזכור של ספר, אוניברסיטה, מחבר, פרק או תרגיל, ואין תגית מקור על המסך; הדוגמאות מקוריות
- [ ] מונחים מוגדרים בשימוש ראשון, סימון סטנדרטי ועקבי, רעיון אחד חזק עם מקום לכל פעימה (2 שניות לפחות לכל ויזואל)


## Teaching quality rules (owner feedback on 1.1 v2, 2026-11-25)
- **The example decides the video.** It is chosen by a dedicated Opus step (`pipeline/prompts/example_researcher.md`) that researches and scores 4-5 candidates. It must be a real everyday scene the student has lived (group chat, lecturer's announcement, campus app, exam...), never a gimmick like codes or locks, and it must show both sides of the idea in the same scene.
- **Not the obvious** (owner, 2026-11-25): the example has a moment that challenges the student a little (their first guess is wrong), and stays relatable and clear. After the everyday example come 2-4 tiny examples in math notation that show exactly what the concept is, in our own numbers. The 8 example tests (a sentence not a scene, a known subject, surprise from the world not the definition, the surprise is the message, a clean pair, a reliable source, short Hebrew, a math bridge) are in `pipeline/prompts/example_researcher.md`.
- **Opus high + a visual hook** (owner, 2026-11-25): choosing the example and writing the script always run on Opus at high effort, and that step also designs the visual hook: a striking frame 0 (the example as a bold picture plus the topic tag) or an attention-grabbing effect in the first second. Frame 0 still equals the last frame (loop).
- **The message lands quickly** (owner, 2026-11-25): the main message comes early in the video, not necessarily by second 4. In Dakademia this replaces the hard "topic spoken by second 4" rule of the general skill (GUIDELINES.md, rule 2): the topic is still shown large from frame 0 and said as early as is natural; the build only warns when it is said after second 4.
- **One learning message** (<= 14 words) stated plainly, followed by a real pause (a line with pause >= 0.6) and repeated once as the recap. At most two supporting ideas; everything else waits for a later video. If a student cannot say the message after the video, the video failed.
- **Pace follows difficulty** (owner decision 2026-11-25): brisk on simple, familiar lines, slower and clear with a short pause on the message and on new or tricky steps, not slow everywhere. Limits: 62-78 words in 42-54 s. `voice_rules.py` (also run by qa.py) fails above 130 wpm and checks the message line exists in `script.md` ("המסר:") and is spoken.
- **Finished animation:** nothing is ever cropped by the frame edge, the stamp pops in and out in place (never flies in from outside the frame), two stamps close together chain instead of teleporting, and every stamp lands exactly on its target. `pipeline/motion_check.py` checks this on every frame before the render.
