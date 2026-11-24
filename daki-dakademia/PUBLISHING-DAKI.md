# פרסום סרטון של דקדמיה (אחרי הרינדור)

השלב הזה רץ אוטומטית מיד אחרי שהסרטון עבר את הבדיקות של הסקיל (render, mix, loudness, critique). אין עצירה לאישור אנושי בין השלבים, בהתאם ל-RUNBOOK.

## 1. העלאה למאגר הסרטונים

מאגר: `merdok13443/dakademia-videos` (ציבורי). מבנה ושמות קבצים לפי ה-README שלו:

```
<course-slug>/u<NN>-e<NN>.mp4
<course-slug>/u<NN>-e<NN>.json
```

- `course-slug` באנגלית, אותיות קטנות ומקפים (למשל `discrete-math`). מספרים בשתי ספרות.
- קובץ שכבר פורסם לא מוחלף. גרסה מתוקנת: `u01-e03-v2.mp4`.
- קובץ עד 100MB.

**בסשן ענן (claude.ai):** אם המאגר לא מחובר לסשן, מחברים אותו (`add_repo` עם `access: push`). ואז:

```bash
git clone --depth 1 https://github.com/merdok13443/dakademia-videos /tmp/dv
mkdir -p /tmp/dv/<course-slug>
cp <proj>/final.mp4 /tmp/dv/<course-slug>/u01-e03.mp4
cd /tmp/dv && git add -A && git commit -m "<course-slug> u01-e03" && git push origin main
```

**ב-Claude Code מקומי:** אותן פקודות, עם הרשאות ה-git של המחשב.

## 2. בדיקת הכתובת הישירה

הכתובת הישירה (זמינה מיד אחרי ה-push):
`https://raw.githubusercontent.com/merdok13443/dakademia-videos/main/<course-slug>/u01-e03.mp4`

```bash
curl -sIL "<url>" | grep -iE "^HTTP|content-length"
```

ממשיכים רק כשהתשובה האחרונה היא `200` וה-`content-length` שווה לגודל הקובץ המקומי. אם לא, מחכים 30 שניות ובודקים שוב, עד 3 פעמים.

הכתובת מוגשת כ-`application/octet-stream`. אם Buffer דוחה את הסרטון בגלל סוג הקובץ, מפעילים GitHub Pages במאגר (Settings > Pages > Deploy from a branch > `main` / `/ (root)` > Save) ומשתמשים ב-`https://merdok13443.github.io/dakademia-videos/<course-slug>/u01-e03.mp4`, שמוגש כ-`video/mp4`. מסשן ענן אי אפשר לבדוק את כתובת ה-Pages ישירות (הרשת חוסמת את github.io), אז בודקים אותה דרך הדפדפן של המשתמש.

## 3. טקסטים לפרסום (כותבים לבד, בעברית)

מתוך `script.json` ונושא הסרטון:

- **כותרת (YouTube):** עד 70 תווים. מתחילה בשאלה או בטענה המפתיעה של ה-hook, לא בשם הקורס. בלי קליקבייט שהסרטון לא מקיים. מסתיימת ב-` #shorts`.
- **כיתוב (Instagram, TikTok, תיאור YouTube):** 2-3 שורות. שורה 1: ה-hook במילים אחרות. שורה 2: מה לומדים, במשפט אחד. שורה 3: קריאה קצרה לפעולה ("שמרו לפני המבחן", "תייגו מישהו מהקורס").
- **האשטגים:** 5-8, בסוף הכיתוב. תמיד `#דקדמיה`, אחד לשם הקורס בעברית (למשל `#מתמטיקהבדידה`), 2-3 לנושא הספציפי, ו-2 כלליים מתוך `#סטודנטים #אוניברסיטה #לימודים #תואר #מבחנים`.
- אותם כללים כמו בסרטון: בלי שם של ספר, אוניברסיטה, מרצה או תרגיל.

## 4. פרסום ב-Buffer (מיד)

ארגון: "My organization". שלוש קריאות `create_post`, כל אחת עם `mode: "shareNow"`, `schedulingType: "automatic"` ו-`assets: [{ video: { url: "<כתובת מבדיקה 2>" } }]`:

| ערוץ | channelId | metadata |
|---|---|---|
| YouTube | `6b0482648541f09ecb7a3b7a` | `youtube: { type: "short", title, categoryId: "27", privacy: "public", madeForKids: false }` (27 = Education); `text` = הכיתוב |
| Instagram | `6b0482358541f09ecb7a3861` | `instagram: { type: "reel", shouldShareToFeed: true }`; `text` = כיתוב + האשטגים |
| TikTok | `6b0482798541f09ecb7a3ce4` | `tiktok: { title }`; `text` = כיתוב + האשטגים |

**מגבלת YouTube בתוכנית החינמית של Buffer:** 2 שורטים ביום לערוץ. לפני הפרסום בודקים ב-`list_posts` כמה פוסטים של YouTube נשלחו היום. אם כבר יש 2, מפרסמים ל-Instagram ול-TikTok כרגיל, וב-YouTube משתמשים ב-`addToQueue` (התור החינמי מוגבל ל-10 פוסטים לערוץ). אם גם התור מלא, לא מפרסמים ל-YouTube ומדווחים.

אם קריאה נכשלת, לא מנסים שוב יותר מפעם אחת. מדווחים מה נכשל ובאיזה ערוץ. פוסט שפורסם לא מוחקים ולא מפרסמים מחדש.

## 5. תיעוד

שומרים ליד הסרטון במאגר `<course-slug>/u01-e03.json` ודוחפים:

```json
{
  "course": "<course-slug>", "unit": 1, "episode": 3,
  "file": "u01-e03.mp4", "url": "<הכתובת ששימשה>",
  "title": "...", "caption": "...", "hashtags": ["#דקדמיה", "..."],
  "published_at": "<ISO>",
  "buffer": { "youtube": "<postId|queued|skipped>", "instagram": "<postId>", "tiktok": "<postId>" }
}
```

ומדווחים למשתמש בשורה אחת: מה פורסם, איפה, ומה נדחה או נכשל.
