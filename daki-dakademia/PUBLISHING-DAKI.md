# פרסום סרטון של דקדמיה (אחרי הרינדור)

השלב הזה רץ אוטומטית מיד אחרי שהסרטון עבר את הבדיקות של הסקיל (render, mix, loudness, critique). אין עצירה לאישור אנושי בין השלבים, בהתאם ל-RUNBOOK.

## 1. העלאה לתיקיית הסרטונים בריפו

הסרטונים המוכנים נשמרים בריפו `merdok13443/skills` (ציבורי), בתוך תיקיית הסקיל:

```
daki-dakademia/videos/<course>/<unit>/<N.M name>.mp4
daki-dakademia/videos/<course>/<unit>/<N.M name>.json
```

- `<course>` ו-`<unit>` הם שמות התיקיות של הקורס והפרק כפי שהם ב-`videos/` של פרויקט העבודה (למשל `בדידה/1 לוגיקה פסוקית`), ו-`<N.M name>` הוא מספר הסרטון ושמו (למשל `1.1 פסוק וערך אמת`). אותו שם כמו ב-`out` ב-progress.json.
- רק הקובץ הסופי (mp4) וקובץ התיעוד (json). בלי מקורות, תסריטים, קבצי ביניים או גרסאות ניסוי. אלה נשארים בתיקיית הפרויקט.
- קובץ שכבר פורסם לא מוחלף. גרסה מתוקנת: `<N.M name> v2.mp4`.
- קובץ עד 100MB. `.gitignore` בריפו מתעלם מ-mp4 חוץ מ-`daki-dakademia/videos/`, לכן אין צורך ב-`git add -f`.

**בסשן ענן (claude.ai):** מושכים את main האחרון, פותחים ענף, מעתיקים את הקובץ, דוחפים ופותחים PR, וממזגים ל-main (לפי הכלל של הסשן לגבי ענף הפיתוח ו-PR):

```bash
git -C ~/skills fetch origin main && git -C ~/skills checkout -B <ענף-הסשן> origin/main
D=~/skills/daki-dakademia/videos/<course>/<unit>
mkdir -p "$D" && cp "<proj>/<N.M name>.mp4" "$D/"
git -C ~/skills add daki-dakademia/videos && git -C ~/skills commit -m "Add video <N.M>" && git -C ~/skills push -u origin <ענף-הסשן>
```

ואז PR למיזוג ל-main. מיזוג ל-main נחוץ כי הכתובת הישירה למטה היא של main.

**ב-Claude Code מקומי:** אותן פקודות, עם הרשאות ה-git של המחשב.

## 2. בדיקת הכתובת הישירה

הכתובת הישירה (זמינה מיד אחרי המיזוג ל-main), עם קידוד URL לשמות בעברית וריווחים:
`https://raw.githubusercontent.com/merdok13443/skills/main/daki-dakademia/videos/<course>/<unit>/<N.M name>.mp4`

```bash
curl -sIL "<url>" | grep -iE "^HTTP|content-length"
```

ממשיכים רק כשהתשובה האחרונה היא `200` וה-`content-length` שווה לגודל הקובץ המקומי. אם לא, מחכים 30 שניות ובודקים שוב, עד 3 פעמים.

הכתובת מוגשת כ-`application/octet-stream`. אם Buffer דוחה את הסרטון בגלל סוג הקובץ, מפעילים GitHub Pages בריפו (Settings > Pages > Deploy from a branch > `main` / `/ (root)` > Save) ומשתמשים בכתובת `https://merdok13443.github.io/skills/daki-dakademia/videos/...`, שמוגשת כ-`video/mp4`. מסשן ענן אי אפשר לבדוק את כתובת ה-Pages ישירות (הרשת חוסמת את github.io), אז בודקים אותה דרך הדפדפן של המשתמש.

## 3. טקסטים לפרסום

כותבים לפי `METADATA-DAKI.md`: טקסט נפרד לכל פלטפורמה (כותרת ותיאור ל-YouTube, כיתוב לאינסטגרם, כיתוב ו-title לטיקטוק), סביב מונח ראשי אחד, בלי לחשוף את ה-payoff.

## 4. פרסום ב-Buffer (מיד)

ארגון: "My organization". שלוש קריאות `create_post`, כל אחת עם `mode: "shareNow"`, `schedulingType: "automatic"` ו-`assets: [{ video: { url: "<כתובת מבדיקה 2>" } }]`:

| ערוץ | channelId | metadata |
|---|---|---|
| YouTube | `6b0482648541f09ecb7a3b7a` | `youtube: { type: "short", title, categoryId: "27", privacy: "public", madeForKids: false }` (27 = Education); `text` = תיאור YouTube |
| Instagram | `6b0482358541f09ecb7a3861` | `instagram: { type: "reel", shouldShareToFeed: true }`; `text` = כיתוב Instagram |
| TikTok | `6b0482798541f09ecb7a3ce4` | `tiktok: { title }`; `text` = כיתוב TikTok |

**מגבלת YouTube בתוכנית החינמית של Buffer:** 2 שורטים ביום לערוץ. לפני הפרסום בודקים ב-`list_posts` כמה פוסטים של YouTube נשלחו היום. אם כבר יש 2, מפרסמים ל-Instagram ול-TikTok כרגיל, וב-YouTube משתמשים ב-`addToQueue` (התור החינמי מוגבל ל-10 פוסטים לערוץ). אם גם התור מלא, לא מפרסמים ל-YouTube ומדווחים.

אם קריאה נכשלת, לא מנסים שוב יותר מפעם אחת. מדווחים מה נכשל ובאיזה ערוץ. פוסט שפורסם לא מוחקים ולא מפרסמים מחדש.

## 5. תיעוד

שומרים ליד הסרטון, באותה תיקייה בריפו, את `<N.M name>.json` ודוחפים (באותו ענף וקומיט או בקומיט נוסף עם PR):

```json
{
  "course": "<course>", "unit": "<unit>", "video": "<N.M>",
  "file": "<N.M name>.mp4", "url": "<הכתובת ששימשה>",
  "keyword": "<מונח ראשי>", "question": "<שאלה אמיתית או null>", "question_source": "<קישור או null>",
  "youtube": { "title": "...", "description": "..." },
  "instagram": { "caption": "..." },
  "tiktok": { "title": "...", "caption": "..." },
  "published_at": "<ISO>",
  "buffer": { "youtube": "<postId|queued|skipped>", "instagram": "<postId>", "tiktok": "<postId>" }
}
```

ומדווחים למשתמש בשורה אחת: מה פורסם, איפה, ומה נדחה או נכשל.
