# פרסום סרטון של דקדמיה (אחרי הרינדור)

השלב הזה רץ אוטומטית מיד אחרי שהסרטון עבר את ה-QA של ה-pipeline. אין עצירה לאישור אנושי. ההעלאה ל-YouTube רצה **בענן** ב-GitHub Actions של מאגר הסרטונים (סעיף "העלאה בענן" למטה), בלי המחשב של הבעלים, ואפשר להפעיל אותה גם מהטלפון. המחשב נדרש רק לקריינות (Gemini) ולהתקנה חד-פעמית. Instagram כשיחזור, על המחשב. אם ההעלאה בענן נכשלת, רושמים `waiting: publish` ומדווחים (`SKILL.md`, סעיף 1). Git: ענף מ-`dev` ו-PR ל-`dev`, אף פעם לא ישירות ל-`main`.

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

**הפקודה (בענן או במחשב, אותה פקודה):** אם המאגר לא מחובר לסשן ענן, מחברים אותו קודם (`add_repo` עם `access: push`). ואז:

```bash
python pipeline/deliver.py push <src>/final.mp4 <uNN-eNN.json מ-metadata.py> --branch <thread-branch>
# then: PR <thread-branch> -> dev, merge it
```

הסקריפט משכפל את `dev`, יוצר את הענף, מעתיק את הקובץ בשם הנכון (קובץ זהה שכבר קיים נשאר; קובץ אחר באותו שם מקבל `-v2`, `-v3`), כותב את קובץ הטקסטים ליד הסרטון, רושם את הסרטון ב-`publish-state.json` (`add`) ודוחף. נשארות רק פתיחת ה-PR והמיזוג.

## 2. בדיקת הכתובת הישירה

הכתובת הישירה, מוצמדת ל-commit (לא נשברת אם ענף נמחק, ולא תלויה במיזוג ל-`main`):
`https://raw.githubusercontent.com/merdok13443/dakademia-videos/<sha>/<course-slug>/u01-e03.mp4`

```bash
python pipeline/deliver.py verify --name <course-slug>/u01-e03
```

הסקריפט לוקח את ה-sha של `dev` אחרי המיזוג, בונה את הכתובת ובודק אותה: ממשיכים רק כשהתשובה האחרונה היא `200` וה-`content-length` שווה לגודל הקובץ. אם לא, הוא מחכה 30 שניות ובודק שוב, עד 3 פעמים, ואז נכשל.

הכתובת מוגשת כ-`application/octet-stream`. אם הפלטפורמה דוחה את הסרטון בגלל סוג הקובץ, מבקשים מהבעלים להפעיל GitHub Pages במאגר (Settings > Pages > Deploy from a branch > `main` / `/ (root)` > Save; עובד רק לקבצים שכבר מוזגו ל-`main`) ומשתמשים ב-`https://merdok13443.github.io/dakademia-videos/<course-slug>/u01-e03.mp4`, שמוגש כ-`video/mp4`. מסשן ענן אי אפשר לבדוק את כתובת ה-Pages ישירות (הרשת חוסמת את github.io), אז בודקים אותה דרך הדפדפן של המשתמש.

## 3. טקסטים לפרסום

כותבים לפי `METADATA-DAKI.md`: טקסט נפרד לכל פלטפורמה (כרגע נדרש רק של YouTube; של אינסטגרם וטיקטוק כותבים כשהם חוזרים לפעולה) (כותרת ותיאור ל-YouTube, כיתוב לאינסטגרם, כיתוב ו-title לטיקטוק), סביב מונח ראשי אחד, בלי לחשוף את ה-payoff.

## 4. פרסום עם הסקיל shorts-uploader

**חריגה זמנית (הבעלים, 2026-11-25, עד שיבטל): מפרסמים רק ב-YouTube. Instagram ו-TikTok מדלגים, ורושמים `skipped` ב-`published` וב-`publish-state.json`.** הסעיפים על Instagram ו-TikTok למטה נשארים לשימוש כשהבעלים יחזיר אותם.

לא משתמשים ב-Buffer ולא באף כלי `mcp__Buffer__*`. הפרסום נעשה דרך ה-API הרשמי עם הסקיל `shorts-uploader` (מאגר `merdok13443/skills`), מתוך קובץ `queue.json`. ההתקנה החד-פעמית (Google Cloud ל-YouTube, אפליקציית Meta ל-Instagram) מתוארת ב-README של הסקיל.

**YouTube: ברירת המחדל היא ההעלאה בענן** (סעיף "העלאה בענן" למטה). המסלול על המחשב שלהלן נשאר ל-Instagram כשיחזור ולמקרה שהענן לא זמין.

**פקודה אחת לסרטון, על המחשב של הבעלים** (מתוך תיקיית ה-uploader, עם ה-venv שלה; סשן Remote Control מריץ רק אותה):

```bash
python <skills>/daki-dakademia/pipeline/publish_video.py --url <הכתובת מבדיקה 2> --uploader-dir . [--platforms youtube]
```

הסקריפט מוריד את הסרטון ואת קובץ הטקסטים מהכתובת המוצמדת, בונה תור של פריט אחד ומעלה עם אותו קוד של `youtube_upload.py` (אותם `client_secret.json`, `token_youtube.json` ו-`state.json`): ציבורי, לא לילדים, קטגוריה 27, עברית. סרטון שכבר הועלה לא עולה שוב, ונשמרת המגבלה היומית. Instagram רק כש-`instagram` ברשימת הפלטפורמות (כרגע לא, לפי החריגה הזמנית). ל-TikTok אין API חינמי ובטוח, ולכן הסקריפט מדפיס את הכותרת והכיתוב להעלאה ידנית. השורה האחרונה היא `RESULT {...}` עם המזהים, והם עוברים לסעיף 5. `--dry-run` בודק הכול בלי להעלות.

הסעיפים למטה מתארים את ההגדרות שהסקריפט מיישם.

- בתור: `file` הוא קובץ ה-mp4 המקומי (יחסית לתיקייה שממנה מריצים), `title` ו-`description` ל-YouTube, `caption` ל-Instagram, ו-`instagram_video_url` הוא הכתובת הישירה מבדיקה 2.
- `defaults.youtube`: `privacy: "public"`, `made_for_kids: false`, `category_id: "27"` (Education), `language: "he"`.
- YouTube: `python scripts/youtube_upload.py queue.json --dry-run`, ואז בלי `--dry-run`. ההתחברות הראשונה פותחת דפדפן, ולכן רצה על מחשב עם דפדפן (לא בענן). ההרשאה `youtube.upload` מעלה אבל לא עורכת סרטון קיים.
- Instagram: `python scripts/instagram_publish.py queue.json --dry-run`, ואז בלי. דורש חשבון Professional, `IG_USER_ID` ו-`IG_ACCESS_TOKEN`.
- קצב לדקדמיה: YouTube עד 6 ביום (`--daily-max 6`, ברירת המחדל של הסקריפט), עד שהבעלים מעלה אותו. מעלים בהדרגה.
- אם אין הרשאות לאינסטגרם (`IG_ACCESS_TOKEN`), או כל עוד החריגה הזמנית בתוקף, רושמים `instagram: skipped` וממשיכים.
- TikTok: ידני, דרך TikTok Studio (אין סקריפט). זו היוצאת מהכלל "בלי אוטומציית דפדפן" של shorts-uploader: מעלים דרך חלון בחירת הקבצים ב-Studio בחשבון מחובר, לא בעוגיות ולא בכלי צד שלישי.
- אם קריאה נכשלת, לא מנסים שוב יותר מפעם אחת. מדווחים מה נכשל ובאיזו פלטפורמה. סרטון שפורסם לא מוחקים ולא מפרסמים מחדש.

## העלאה בענן (YouTube, ברירת המחדל מ-2026-11-25)

הסיבה: פרטי הגישה ליוטיוב היו רק על המחשב של הבעלים, ולכן אי אפשר היה לאשר ולהעלות מהטלפון. עכשיו ההעלאה רצה ב-GitHub Actions במאגר `merdok13443/dakademia-videos`, וה-workflow `Upload to YouTube` (`.github/workflows/upload-youtube.yml`) מריץ את `pipeline/publish_cloud.py`, עם אותו קוד העלאה כמו `shorts-uploader/scripts/youtube_upload.py` ואותן הגדרות קבועות: ציבורי (בבדיקה אפשר `private`/`unlisted`), לא לילדים, קטגוריה 27, עברית.

**הפעלה:**
- מהטלפון: אפליקציית GitHub > המאגר `dakademia-videos` > Actions > Upload to YouTube > Run workflow. שדות: `video` (למשל `discrete-math/u01-e03`), `privacy` (ברירת מחדל `public`), `dry_run`.
- מסשן: `mcp__github__actions_run_trigger` על `upload-youtube.yml`, ref `dev`, עם אותם שדות, **רק אחרי שהבעלים אישר במפורש את הסרטון** (הודעה שלו בצ'אט, גם בצ'אט הפרויקט; הקואורדינטור מעביר אותה בציטוט). בלי אישור כזה לא מפעילים.
- הסרטון והטקסטים נלקחים מ-`dev` (`<name>.mp4` ו-`<name>.json`), לכן קודם ה-PR של הסרטון ממוזג.

**מה הוא עושה:** בודק שם וקבצים, מדלג אם `publish-state.json` כבר מציין שהסרטון הועלה (אף פעם לא פעמיים), מתחבר עם הסוד, מעלה, רושם `youtube=uploaded` עם הכתובת ב-`publish-state.json` וב-`<name>.json` (וגם `skipped` לשתי הפלטפורמות האחרות), ועושה commit ישר ל-`dev` (לא ל-`main`). סיכום עם שורת `RESULT` מופיע בסיכום הריצה. `dry_run` בודק התחברות, קבצים וטקסטים ולא מעלה כלום.

**הסוד (חד-פעמי):** סוד המאגר `YT_TOKEN_JSON` = כל התוכן של `token_youtube.json` מתיקיית ה-uploader במחשב (ב-Windows: `Get-Content <תיקיית uploader>\token_youtube.json -Raw | Set-Clipboard` ואז הדבקה בשדה הסוד ב-Settings > Secrets and variables > Actions > New repository secret). הקובץ כולל את ה-client id וה-secret ואת ה-refresh token. הסוד מוצפן, לא מודפס בלוגים (המאגר ציבורי, ולכן **אסור** להדפיס אותו או לשים אותו בקובץ), ולא נקרא לעולם על ידי סשן. אם ההתחברות נכשלת (`YouTube login failed`), ה-refresh token בוטל או פג: יוצרים `token_youtube.json` חדש על המחשב (ראו README של shorts-uploader, ו-OAuth צריך להיות במצב In production) ומעדכנים את הסוד.

**שינויים:** ההעלאה בענן אינה מחליפה את ההנחיות האחרות: קצב (עד 6 ביום), טקסטים לפי `METADATA-DAKI.md`, חריגת YouTube בלבד. ההרשאה היא `youtube.upload` בלבד, לכן אי אפשר לערוך סרטון קיים (למשל פרטי לציבורי) מהענן.

## 5. תיעוד

הקובץ `<course-slug>/u01-e03.json` נכתב ב-`metadata.py` ונדחף עם הסרטון. אחרי ההעלאה ממלאים בו את הכתובת והמזהים ומעדכנים את `publish-state.json` בפקודה אחת, ואז PR ל-`dev` ומיזוג:

```bash
python pipeline/deliver.py record --name <course-slug>/u01-e03 --url <URL> --youtube <id> --instagram skipped --tiktok skipped --branch <b> --package "<video folder>"
```

המבנה:

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
