# פרסום סרטון של דקדמיה (אחרי הרינדור)

השלב הזה רץ אוטומטית מיד אחרי שהסרטון עבר את ה-QA של ה-pipeline. אין עצירה לאישור אנושי. ההעלאה ל-YouTube רצה על המחשב של הבעלים (Instagram כשיחזור); אם הוא לא זמין, רושמים `waiting: publish` ומדווחים (`SKILL.md`, סעיף 1). Git: ענף מ-`dev` ו-PR ל-`dev`, אף פעם לא ישירות ל-`main`.

## 1. העלאה למאגר הסרטונים

מאגר: `merdok13443/dakademia-videos` (ציבורי). מבנה ושמות קבצים לפי ה-README שלו:

```
<course-slug>/u<NN>-e<NN>.mp4
<course-slug>/u<NN>-e<NN>.json
```

- `course-slug` באנגלית, אותיות קטנות ומקפים (למשל `discrete-math`). מספרים בשתי ספרות.
- קובץ שכבר פורסם לא מוחלף. גרסה מתוקנת: `u01-e03-v2.mp4`.
- קובץ עד 100MB.
- מיפוי: סרטון `N.M` ביחידה N הוא `u<NN>-e<MM>` (למשל 1.3 בבדידה הוא `discrete-math/u01-e03.mp4`). הקובץ הוא רק ה-mp4 הסופי (והתיעוד json), בלי מקורות, תסריטים או גרסאות ניסוי.

**בסשן ענן (claude.ai):** אם המאגר לא מחובר לסשן, מחברים אותו (`add_repo` עם `access: push`). ואז:

```bash
git clone --depth 1 -b dev https://github.com/merdok13443/dakademia-videos /tmp/dv
cd /tmp/dv && git checkout -b <thread-branch>
mkdir -p <course-slug> && cp <proj>/final.mp4 <course-slug>/u01-e03.mp4
git add -A && git commit -m "<course-slug> u01-e03" && git push -u origin <thread-branch>
# PR to dev, merge it, then: git rev-parse HEAD  -> <sha> for the direct link
```

**ב-Claude Code מקומי:** אותן פקודות, עם הרשאות ה-git של המחשב.

## 2. בדיקת הכתובת הישירה

הכתובת הישירה, מוצמדת ל-commit (לא נשברת אם ענף נמחק, ולא תלויה במיזוג ל-`main`):
`https://raw.githubusercontent.com/merdok13443/dakademia-videos/<sha>/<course-slug>/u01-e03.mp4`

```bash
curl -sIL "<url>" | grep -iE "^HTTP|content-length"
```

ממשיכים רק כשהתשובה האחרונה היא `200` וה-`content-length` שווה לגודל הקובץ המקומי. אם לא, מחכים 30 שניות ובודקים שוב, עד 3 פעמים.

הכתובת מוגשת כ-`application/octet-stream`. אם הפלטפורמה דוחה את הסרטון בגלל סוג הקובץ, מבקשים מהבעלים להפעיל GitHub Pages במאגר (Settings > Pages > Deploy from a branch > `main` / `/ (root)` > Save; עובד רק לקבצים שכבר מוזגו ל-`main`) ומשתמשים ב-`https://merdok13443.github.io/dakademia-videos/<course-slug>/u01-e03.mp4`, שמוגש כ-`video/mp4`. מסשן ענן אי אפשר לבדוק את כתובת ה-Pages ישירות (הרשת חוסמת את github.io), אז בודקים אותה דרך הדפדפן של המשתמש.

## 3. טקסטים לפרסום

כותבים לפי `METADATA-DAKI.md`: טקסט נפרד לכל פלטפורמה (כרגע נדרש רק של YouTube; של אינסטגרם וטיקטוק כותבים כשהם חוזרים לפעולה) (כותרת ותיאור ל-YouTube, כיתוב לאינסטגרם, כיתוב ו-title לטיקטוק), סביב מונח ראשי אחד, בלי לחשוף את ה-payoff.

## 4. פרסום עם הסקיל shorts-uploader

**חריגה זמנית (הבעלים, 2026-11-25, עד שיבטל): מפרסמים רק ב-YouTube. Instagram ו-TikTok מדלגים, ורושמים `skipped` ב-`published` וב-`publish-state.json`.** הסעיפים על Instagram ו-TikTok למטה נשארים לשימוש כשהבעלים יחזיר אותם.

לא משתמשים ב-Buffer ולא באף כלי `mcp__Buffer__*`. הפרסום נעשה דרך ה-API הרשמי עם הסקיל `shorts-uploader` (מאגר `merdok13443/skills`), מתוך קובץ `queue.json`. ההתקנה החד-פעמית (Google Cloud ל-YouTube, אפליקציית Meta ל-Instagram) מתוארת ב-README של הסקיל.

- בתור: `file` הוא קובץ ה-mp4 המקומי (יחסית לתיקייה שממנה מריצים), `title` ו-`description` ל-YouTube, `caption` ל-Instagram, ו-`instagram_video_url` הוא הכתובת הישירה מבדיקה 2.
- `defaults.youtube`: `privacy: "public"`, `made_for_kids: false`, `category_id: "27"` (Education), `language: "he"`.
- YouTube: `python scripts/youtube_upload.py queue.json --dry-run`, ואז בלי `--dry-run`. ההתחברות הראשונה פותחת דפדפן, ולכן רצה על מחשב עם דפדפן (לא בענן). ההרשאה `youtube.upload` מעלה אבל לא עורכת סרטון קיים.
- Instagram: `python scripts/instagram_publish.py queue.json --dry-run`, ואז בלי. דורש חשבון Professional, `IG_USER_ID` ו-`IG_ACCESS_TOKEN`.
- קצב לדקדמיה: YouTube עד 6 ביום (`--daily-max 6`, ברירת המחדל של הסקריפט), עד שהבעלים מעלה אותו. מעלים בהדרגה.
- אם אין הרשאות לאינסטגרם (`IG_ACCESS_TOKEN`), או כל עוד החריגה הזמנית בתוקף, רושמים `instagram: skipped` וממשיכים.
- TikTok: ידני, דרך TikTok Studio (אין סקריפט). זו היוצאת מהכלל "בלי אוטומציית דפדפן" של shorts-uploader: מעלים דרך חלון בחירת הקבצים ב-Studio בחשבון מחובר, לא בעוגיות ולא בכלי צד שלישי.
- אם קריאה נכשלת, לא מנסים שוב יותר מפעם אחת. מדווחים מה נכשל ובאיזו פלטפורמה. סרטון שפורסם לא מוחקים ולא מפרסמים מחדש.

## 5. תיעוד

שומרים ליד הסרטון במאגר `<course-slug>/u01-e03.json` ודוחפים:

```json
{
  "course": "<course-slug>", "unit": 1, "episode": 3,
  "file": "u01-e03.mp4", "url": "<הכתובת ששימשה>",
  "keyword": "<מונח ראשי>", "question": "<שאלה אמיתית או null>", "question_source": "<קישור או null>",
  "youtube": { "title": "...", "description": "..." },
  "instagram": { "caption": "..." },
  "tiktok": { "title": "...", "caption": "..." },
  "published_at": "<ISO>",
  "published": { "youtube": "<videoId|skipped>", "instagram": "<mediaId|skipped>", "tiktok": "manual|skipped" }
}
```

מעתיקים את אותו `u01-e03.json` ל-`07-publish/metadata.json` בתיקיית הסרטון בפרויקט, ואת הרשומה של הסרטון מ-`publish-state.json` ל-`07-publish/state.json`, ומוסיפים את הקישורים ל-README שלה (`pipeline/VIDEO-PACKAGE.md`).

ומדווחים למשתמש בשורה אחת: מה פורסם, איפה, ומה נדחה או נכשל.

## הגדרת קהל ב-YouTube (חובה)
תמיד "לא מיועד לילדים" (`made_for_kids: false` ב-shorts-uploader). הקהל שלנו הוא סטודנטים. לפי YouTube, סימון לילדים מכבה תגובות, התראות, מודעות מותאמות, כרטיסים ומסכי סיום (הרשימה המלאה ב-`shorts-uploader/README.md`), והסרטון מומלץ בעיקר לצד סרטוני ילדים. הצהרה לא מדויקת עלולה לגרור בעיות מול YouTube. הסימון לא חוסם צפייה של ילדים. אם משתמש מבקש "לילדים", מציגים לו את ההשלכות ומקבלים אישור מפורש, ורק אז משנים. מקורות: support.google.com/youtube/answer/9527654, 9632097, 10774223.
