# פרסום סרטון של דקדמיה (אחרי הרינדור)

השלב הזה רץ אוטומטית מיד אחרי שהסרטון עבר את ה-QA של ה-pipeline. אין עצירה לאישור אנושי. ההעלאה ל-YouTube רצה **בענן** ב-GitHub Actions של מאגר הסרטונים (סעיף "העלאה בענן" למטה), בלי המחשב של הבעלים, ואפשר להפעיל אותה גם מהטלפון. המחשב נדרש רק לקריינות (Gemini) ולהתקנה חד-פעמית. Instagram כשיחזור, על המחשב. אם הקריינות או ההעלאה בענן נכשלות, רושמים `waiting: publish` ומדווחים (`SKILL.md`, סעיף 1). Git: ענף מ-`dev` ו-PR ל-`dev`, אף פעם לא ישירות ל-`main`.

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

**חריגה זמנית (הבעלים, 2026-11-25, עד שיבטל): TikTok מדלגים ורושמים `skipped` ב-`published` וב-`publish-state.json`. YouTube ו-Instagram מפורסמים בענן (סעיף "העלאה בענן"); Instagram רק כשהבעלים מאשר את הפרסום שם, והחריגה "YouTube בלבד" הוסרה ל-Instagram באותו יום.** הסעיפים על Instagram ו-TikTok למטה נשארים לשימוש כשהבעלים יחזיר אותם.

**סרטון סיכום יחידה (`N.99`):** לפני כל פרסום `deliver.py verify-sheet` חייב להחזיר 200 לכתובת דף הסיכום (שהקישור אליו בתיאור); בלי זה לא מפרסמים אותו (`SUMMARY-VIDEOS-DAKI.md`).

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
- קצב לדקדמיה: סרטון אחד בשעה בלבד, בשעות הפעילות 10:00 עד 21:00 שעון ישראל (הבעלים, 2026-11-26; סעיף "שחרור בלי הבעלים"). `--daily-max` של `youtube_upload.py` אינו הגבלה של דקדמיה.
- אם אין הרשאות לאינסטגרם (`IG_ACCESS_TOKEN`), או כל עוד החריגה הזמנית בתוקף, רושמים `instagram: skipped` וממשיכים.
- TikTok: ידני, דרך TikTok Studio (אין סקריפט). זו היוצאת מהכלל "בלי אוטומציית דפדפן" של shorts-uploader: מעלים דרך חלון בחירת הקבצים ב-Studio בחשבון מחובר, לא בעוגיות ולא בכלי צד שלישי.
- אם קריאה נכשלת, לא מנסים שוב יותר מפעם אחת. מדווחים מה נכשל ובאיזו פלטפורמה. סרטון שפורסם לא מוחקים ולא מפרסמים מחדש.

## העלאה בענן (YouTube, ברירת המחדל מ-2026-11-25)

הסיבה: פרטי הגישה ליוטיוב היו רק על המחשב של הבעלים, ולכן אי אפשר היה לאשר ולהעלות מהטלפון. עכשיו ההעלאה רצה ב-GitHub Actions במאגר `merdok13443/dakademia-videos`, וה-workflow `Upload to YouTube` (`.github/workflows/upload-youtube.yml`) מריץ את `pipeline/publish_cloud.py`, עם אותו קוד העלאה כמו `shorts-uploader/scripts/youtube_upload.py` ואותן הגדרות קבועות: ציבורי (בבדיקה אפשר `private`/`unlisted`), לא לילדים, קטגוריה 27, עברית.

**הפעלה:**
- מהטלפון: אפליקציית GitHub > המאגר `dakademia-videos` > Actions > Upload to YouTube > Run workflow. שדות: `video` (למשל `discrete-math/u01-e03`), `privacy` (ברירת מחדל `public`), `dry_run`.
- מסשן: `mcp__github__actions_run_trigger` על `upload-youtube.yml`, ref `dev`, עם אותם שדות. **סרטון שציון התסריט שלו 95 ומעלה (ובלי תנאי סף שנכשל) והבנייה שלו עברה QA משוחרר בלי הבעלים, לפי סעיף "שחרור בלי הבעלים" למטה.** כל סרטון אחר: רק אחרי שהבעלים אישר במפורש את הסרטון (הודעה שלו בצ'אט, גם בצ'אט הפרויקט; הקואורדינטור מעביר אותה בציטוט), ואז מסמנים `owner_approved`. בלי אישור כזה לא מפעילים.
- שדה `platforms`: `youtube` (ברירת מחדל), `instagram` או `youtube,instagram`. Instagram מפרסם Reel מכתובת ה-raw המוצמדת ל-commit, עם `instagram.caption` מה-json (בדיוק 5 האשטגים; נכתב ב-`metadata.py` עם `ig_body`). אם אין כיתוב ב-json, הריצה נעצרת ואומרת זאת. TikTok לא נעשה כאן.
- הסרטון והטקסטים נלקחים מ-`dev` (`<name>.mp4` ו-`<name>.json`), לכן קודם ה-PR של הסרטון ממוזג.

**שחרור בלי הבעלים (הבעלים, 2026-11-26):** מעכשיו סרטון שציון התסריט שלו לפי `SCRIPT-RUBRIC.md` הוא **95 ומעלה, בלי תנאי סף שנכשל, ושהסרטון שנבנה מאותו תסריט עבר QA**, רשאי לעלות ל-YouTube ול-Instagram בלי שהבעלים אישר אותו. ארבעה תנאים, והסקריפט אוכף אותם:
1. **הציון שייך לתסריט שנבנה.** `deliver.py push --src <src>` רושם ב-`<name>.json` את `script_score` רק כשבקובץ הציונים (`courses/<slug>/state/script-scores.json`) יש ציון שה-`script_sha` שלו שווה ל-sha256 של `voice/script.json` שנבנה ממנו הסרטון. תסריט שתוקן אחרי הבנייה, או שלא נבדק, לא נותן ציון, והסרטון דורש אישור בעלים. (תסריטים מתוקנים ב-`03-script/revised/` צריכים קריינות ובנייה מחדש לפני שהציון שלהם חל.)
2. **`publish_cloud.py` מסרב** בלי `script_score` עם `pass` ו-`total` 95 ומעלה, אלא אם הועבר `--owner-approved` (שדה `owner_approved` ב-workflow, רק כשהבעלים אישר את הסרטון בצ'אט).
3. **סרטון אחד בשעה, ורק בשעות הפעילות 10:00 עד 21:00 שעון ישראל.** הסקריפט מסרב מחוץ לשעות, או כשסרטון אחר (YouTube או Instagram) עלה לפני פחות מ-60 דקות (`at` ב-`publish-state.json`). עקיפה רק ב-`--allow-outside-hours` (שדה `allow_outside_hours`) ובמילה מפורשת של הבעלים. ריצת `dry_run` רק מדווחת.
4. **סדר הקורס נשמר** (השמירה על הסדר, סעיף "סדר" ב-`publish_cloud.py`), ו-TikTok נשאר ידני.
סשן שמשחרר סרטון כך מדווח לבעלים אחרי ההעלאה (לא לפניה), ומריץ קודם `dry_run`. כשהציון מתחת ל-95, התסריט חוזר לכותב (`pipeline/README.md` שלב 3) ולא מחכה לאישור.

**מה הוא עושה:** בודק שם וקבצים, מדלג אם `publish-state.json` כבר מציין שהסרטון הועלה (אף פעם לא פעמיים), מתחבר עם הסוד, מעלה, רושם `youtube=uploaded` עם הכתובת ב-`publish-state.json` וב-`<name>.json` (וגם `skipped` לשתי הפלטפורמות האחרות), ועושה commit ישר ל-`dev` (לא ל-`main`). סיכום עם שורת `RESULT` מופיע בסיכום הריצה. `dry_run` בודק התחברות, קבצים וטקסטים ולא מעלה כלום.

**הסוד (חד-פעמי):** סוד המאגר `YT_TOKEN_JSON` = כל התוכן של `token_youtube.json` מתיקיית ה-uploader במחשב (ב-Windows: `Get-Content <תיקיית uploader>\token_youtube.json -Raw | Set-Clipboard` ואז הדבקה בשדה הסוד ב-Settings > Secrets and variables > Actions > New repository secret). הקובץ כולל את ה-client id וה-secret ואת ה-refresh token. הסוד מוצפן, לא מודפס בלוגים (המאגר ציבורי, ולכן **אסור** להדפיס אותו או לשים אותו בקובץ), ולא נקרא לעולם על ידי סשן. אם ההתחברות נכשלת (`YouTube login failed`), ה-refresh token בוטל או פג: יוצרים `token_youtube.json` חדש על המחשב (ראו README של shorts-uploader, ו-OAuth צריך להיות במצב In production) ומעדכנים את הסוד.

**Instagram (סוד שני, חד-פעמי):** סוד המאגר `IG_ACCESS_TOKEN` = תוכן `ig_token.txt` מתיקיית ה-uploader (ב-Windows: `Get-Content <תיקיית uploader>\ig_token.txt -Raw | Set-Clipboard`). ה-`IG_USER_ID` (`17841460444687086`, חשבון @dakademia.il) אינו סוד ונמצא ב-workflow. הטוקן של Instagram תקף כ-60 יום; כשהבדיקה נכשלת (`Instagram token check failed`), יוצרים טוקן חדש (README של shorts-uploader) ומעדכנים את הסוד. אי אפשר לערוך כיתוב אחרי פרסום. החריגה "YouTube בלבד" הוסרה ל-Instagram ב-2026-11-25 (הבעלים); TikTok נשאר דולג.

**קריינות בענן:** ה-workflow `Narration (Gemini voice)` באותו מאגר מריץ את `pipeline/voice.py` (בקשת Gemini אחת, יישור Whisper, הזרקת הפסקות, בדיקת כללים) על `work/<id>/voice/script.json` שנמצא ב-`dev`, ומחזיר את הקבצים ל-`work/<id>/voice/` ב-`dev`. הסוד `GEMINI_API_KEY` = `$env:GEMINI_API_KEY | Set-Clipboard` על המחשב, ואז הדבקה. אותם כללי מפתח: רק שלושת המודלים, רק לקריינות, בקשה אחת לסרטון (מקסימום 3 כולל ניסיונות חוזרים; `voice_stamp.json` מונע בקשה כפולה).

**סדר העלאה (חובה, הבעלים 2026-11-26):** מעלים לפי סדר הקורס בלבד (0.0, אחר כך יחידה ופרק עולים). `publish_cloud.py` מסרב להעלות פרק אם קיים פרק מוקדם יותר בקורס (קובץ mp4 ב-`dev`, גרסה `-vN` נחשבת לאותו פרק) שעדיין לא `uploaded` ב-YouTube או ב-Instagram לפי `publish-state.json`. ההודעה מפרטת איזה פרק חסר, גם ב-`dry_run`. TikTok ידני ולא נבדק. עוקפים רק בשדה `allow_out_of_order` ורק אחרי הודעה מפורשת של הבעלים. כשמעבירים פרק לארכיון הוא יוצא מ-`dev` ולכן לא חוסם; פרק שנבנה ולא נמסר ל-`dev` לא מוגן ממדלוג, ולכן מוסרים כל פרק מאושר ל-`dev` לפי הסדר ולא משאירים פרק תקוע.

**שינויים:** ההעלאה בענן אינה מחליפה את ההנחיות האחרות: קצב (עד 6 ביום), טקסטים לפי `METADATA-DAKI.md`, TikTok דולג (חריגה). ההרשאה היא `youtube.upload` בלבד, לכן אי אפשר לערוך סרטון קיים (למשל פרטי לציבורי) מהענן.

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

## 6. מפת הקורסים (ארטיפקט): מתעדכנת בכל מסירה, העלאה וציון

הארטיפקט "מפת הקורסים" (https://claude.ai/artifact/PBDSL8tPXbaPPdJwuchXnY) מציג את כל התוכנית (יחידות, סרטונים, סרטוני הסיכום N.99 והטריילר) ולצד כל סרטון שנבנה: סטטוס (הועלה / ממתין לבדיקה / בהפקה), קישור לבדיקה לגרסה האחרונה (קישור raw מוצמד ל-commit במאגר הסרטונים), קישורי YouTube, Instagram ו-TikTok כשיש, **וציון התסריט** (לפי `SCRIPT-RUBRIC.md`, עם פירוט הרכיבים והניכוי הגדול; בשיעורים מול רף 95, בפתיח, סיכום וטריילר "להערות בלבד"). הבעלים משתמש בו במקום לקבל רשימות קישורים וציונים בצ'אט, ולכן הוא חייב להיות עדכני.

**איך המידע נכנס (הכול בסקריפטים, בלי הקלדה ביד):**
- ציון: `rubric_score.py` (שלב 3) מוסיף אחרי כל דירוג את הציון ל-`courses/<slug>/state/script-scores.json` (הקורס והמזהה נלקחים מנתיב התיקייה, או `--course <slug> --id N.M`) **ומפיק בעצמו מחדש את דף המפה** ל-`queue/course-map.html` (דרך `course_map.py`, בלי שאף אחד יזכור). נשאר רק פרסום הדף בכלי ה-Artifact (והרישום `--mark-published`). `rubric_collect.py` בונה את כל הקובץ מחדש מתיקיות הסרטונים. העתק `course_map/scores/<slug>.json` ב-skills הוא תמונת מצב בלבד, והדף קורא קודם את קובץ ה-state.
- העלאה: `publish_cloud.py` (ובכל ריצה של ה-workflow `Upload to YouTube`) רושם את הפלטפורמה ב-`publish-state.json` ומדפיס `COURSE-MAP: ... republish` (גם בסיכום הריצה) כשעלה סרטון לאחת הרשתות.
- מסירה: `state.py done` מדפיס את אותה תזכורת.

**הגבלה אחת שאי אפשר לעקוף:** רק כלי ה-Artifact של סשן Claude יכול לפרסם את הארטיפקט (GitHub Actions אין לו גישה אליו, והדף עצמו לא יכול למשוך נתונים מהמאגר). לכן עדכון אוטומטי = הסקריפטים מעדכנים את הנתונים ומסמנים שהמפה ישנה, והסשן שרואה את השורה `COURSE-MAP:` מפרסם מחדש. העלאה שהופעלה מהטלפון (בלי סשן) נתפסת בבדיקה הבאה: `python pipeline/course_map.py --check` יוצא ב-1 כשהמפה הפורסמה לפני שינוי כלשהו, והוא רץ בתחילת כל ריצת הפקה, אחרי כל העלאה ואחרי כל דירוג.

**חובה, בכל אחד מהמקרים האלה** (מסירה ל-`dev` או גרסה חדשה `-vN`; העלאה או רישום ידני של פרסום; ציון חדש; סרטון שעבר לארכיון או סטטוס הפקה שהשתנה), אחרי שהמצב נרשם, מפיקים את הדף מחדש ומפרסמים אותו כגרסה חדשה של אותו ארטיפקט (אותה כתובת, לא ארטיפקט חדש):

```bash
python pipeline/course_map.py --out <scratch>/course-map.html     # קורא curriculum.json, progress.json, script-scores.json ואת origin/dev של מאגר הסרטונים
# כלי Artifact: publish עם url=<כתובת הארטיפקט> ו-file_path=<הקובץ> (לקרוא את הארטיפקט פעם אחת לפני הפרסום הראשון בסשן)
python pipeline/course_map.py --mark-published <scratch>/course-map.html   # רושם ב-queue/course-map-published.json שהמפה עדכנית
```

סשן בלי כלי Artifact או בלי גישת כתיבה לארטיפקט מציין זאת בדוח הסופי (`ארטיפקט המפה לא עודכן`) ולא מדלג בשקט. אין לערוך את ה-HTML ביד: משנים את `course_map/template.html` או את `pipeline/course_map.py`.

כללי הסטטוס (בסקריפט): הגרסה האחרונה היא ה-mp4 עם ה-commit החדש ביותר ב-`dev` (לא לפי שם הקובץ); `הועלה` = YouTube או Instagram רשומים כ-`uploaded` לגרסה הזאת; `ממתין לבדיקה` = ה-mp4 ב-`dev` ועוד לא הועלה; `בהפקה` = יש `work/uNN-eNN/` (קריינות) או `in_progress` במצב הקורס, בלי mp4. הקריינות ב-`work/` בלי שם קורס, ולכן היא נחשבת רק לקורס שסטטוסו `active` ב-`course.json`.
