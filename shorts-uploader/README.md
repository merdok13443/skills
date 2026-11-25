# Shorts Uploader: העלאה המונית ליוטיוב ולאינסטגרם דרך ה-API הרשמי

חינמי, בלי תקרה של 2 ביום כמו ב-Buffer. טיקטוק מטופל ידנית (ראה למטה).
המחקר מתאריך 25.11.2026. הכללים של הפלטפורמות משתנים, ולכן לפני אצווה גדולה בדוק שוב את הקישורים בסוף הקובץ.

## מגבלות אמיתיות

| פלטפורמה | מה נמצא במקורות הרשמיים | ברירת המחדל בסקריפט |
|---|---|---|
| YouTube Data API v3 | `videos.insert` עולה יחידה אחת, בדלי נפרד של כ-100 קריאות ביום (שינוי מ-1.6.2026). הנעילה ל"פרטי" של פרויקטים לא מאומתים בוטלה ב-2.11.2026. קיימת גם שגיאה `uploadLimitExceeded`, מגבלה לכל ערוץ שאין לה מספר מפורסם | 10 ביום |
| Instagram Graph API | 50 עד 100 פרסומים ל-24 שעות (המסמכים של Meta סותרים). הסקריפט שואל את `content_publishing_limit` ומציג את המספר האמיתי שלך | 20 ביום |
| TikTok | ב-API, פוסטים של אפליקציה לא מאושרת נשארים פרטיים, והביקורת נדחית לרוב לשימוש אישי. אין סקריפט לטיקטוק | ידני |

ברירות המחדל נמוכות בכוונה כדי לא להיראות כספאם ולא להיתקל במגבלות לא מתועדות. אפשר להעלות עם `--daily-max`.

## התקנה

```bash
cd shorts-uploader
pip install -r requirements.txt
cp queue.example.json queue.json   # ערוך לפי הסרטונים שלך
```

### YouTube (חד פעמי, כ-10 דקות)
1. ב-[Google Cloud Console](https://console.cloud.google.com/) צור פרויקט והפעל **YouTube Data API v3**.
2. מסך ההסכמה (OAuth consent screen): סוג External, הוסף את המייל שלך כ-Test user.
3. צור OAuth client מסוג **Desktop app** והורד את `client_secret.json` לתיקייה הזו.
4. **חשוב:** במצב Testing ה-token פג אחרי 7 ימים. כדי למנוע זאת העבר את האפליקציה ל-**In production**. תראה אזהרת "unverified app" בהתחברות ראשונה, וזה צפוי לשימוש אישי בערוץ שלך.
5. הרצה ראשונה פותחת דפדפן להתחברות ויוצרת `token_youtube.json`.

### Instagram (חד פעמי, יותר מסורבל)
1. הפוך את החשבון ל-**Professional** (Creator או Business).
2. ב-[Meta for Developers](https://developers.facebook.com/) צור אפליקציה, והוסף את עצמך כ-admin/tester. לחשבון שלך מספיק Standard Access, בלי App Review.
3. הרשאות: `instagram_business_content_publish` (או `instagram_content_publish` יחד עם `pages_read_engagement`).
4. הפק access token ארוך טווח ואת ה-Instagram user id, והגדר:
   ```bash
   export IG_USER_ID=...
   export IG_ACCESS_TOKEN=...
   ```
5. **הסרטון חייב להיות בכתובת HTTPS ציבורית** (`instagram_video_url` בתור). אפשר bucket ציבורי (Cloudflare R2, S3 וכדומה) או כל אחסון שנותן קישור ישיר לקובץ. קישור של דף צפייה (Google Drive וכדומה) לא יעבוד.

## שימוש

```bash
python scripts/youtube_upload.py queue.json --dry-run     # בדיקה בלי להעלות
python scripts/youtube_upload.py queue.json --daily-max 10
python scripts/instagram_publish.py queue.json --dry-run
python scripts/instagram_publish.py queue.json --daily-max 20
python scripts/queue_status.py queue.json
```

- `state.json` נשמר אחרי כל סרטון. הרצה חוזרת מדלגת על מה שכבר הועלה, ולכן אפשר להריץ כל יום עד שהתור מסתיים.
- בין סרטונים יש המתנה אקראית (`--gap MIN MAX` בשניות).
- תזמון ביוטיוב: `publish_at` בפורמט RFC3339 (למשל `2026-12-01T16:00:00Z`). הסרטון יועלה כפרטי ויתפרסם בזמן שנקבע.
- סדר מומלץ: dry-run, אחר כך סרטון אחד אמיתי, ואז כל התור.

## תוכן לילדים (YouTube "made for kids")
- הסקריפט שולח תמיד `selfDeclaredMadeForKids` במפורש. ברירת המחדל בתור היא `false` (לא לילדים), כי התוכן שלנו מיועד לסטודנטים. סימון "לילדים" מכבה תגובות והתראות, ומומלץ לצד תוכן של ילדים. מסמנים `true` רק כשהתוכן באמת מיועד לילדים (מבחן ה-FTC) ובאישור מפורש של המשתמש.
- המשמעות: תגובות, מודעות מותאמות והתראות מבוטלות, וגם כרטיסים ומסכי סיום. תוכן שמיועד לילדי בית ספר נחשב ככזה.
- אם ההצהרה שגויה אפשר להיחשף לבעיות מול יוטיוב. אם יש ספק, התייעץ.
- באינסטגרם ובטיקטוק אין תווית כזו. הגיל המינימלי הוא 13, ולא אימתתי מקור רשמי שמתאר כללים ייעודיים לתוכן לילדים.

## סיכון חסימה: סדרה עם תבנית אחידה
במקורות שנבדקו, המדיניות מכוונת לתוכן מועתק, לסרטונים כמעט זהים עם הבדלים שטחיים, ולהעלאה חוזרת של אותו סרטון. סדרה מקורית עם פורמט עקבי לא מוזכרת כבעיה. כדי להיות בצד הבטוח, לכל סרטון נושא, תסריט וקריינות משלו, ולא מעלים את אותו סרטון פעמיים.

## טיקטוק
אין דרך חינמית ובטוחה להעלאה המונית דרך API. אפשרויות:
- מתזמן מובנה באתר TikTok Studio. במקורות לא נמצאה תקרה יומית מפורסמת, והבלוג הרשמי (2021) מדבר על תזמון של 15 דקות עד 10 ימים מראש. כדאי לנסות בפועל.
- שירות מתארח מאושר כמו Upload-Post (בתשלום, כ-16 עד 24 דולר בחודש, ללא אימות מצידי).
- לא מומלץ: כלי אוטומציית דפדפן עם עוגיות או סיסמה, כי הם מסכנים את החשבון.

## פתרון תקלות
- `quotaExceeded` / `uploadLimitExceeded`: הסקריפט עוצר, ממשיכים למחרת.
- Instagram `ERROR` בקונטיינר: בדוק שהקישור ציבורי, ישיר, MP4 (H.264/AAC), יחס 9:16 וגודל וכמות תווים בכיתוב בגבולות.
- ה-token של יוטיוב פג אחרי 7 ימים: האפליקציה עדיין במצב Testing, ראה שלב 4.

## מקורות
- https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits
- https://developers.google.com/youtube/v3/revision_history
- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.facebook.com/docs/instagram-platform/content-publishing/
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/content_publishing_limit
- https://developers.tiktok.com/doc/content-sharing-guidelines
- https://www.tiktok.com/business/es/blog/6940168110557102082

## הערות מהרצה אמיתית (2026-11-25)
- בנוסף ליצירת ה-client, צריך **להפעיל את YouTube Data API v3** בפרויקט (אחרת שגיאת 403), ולהוסיף את חשבון הערוץ כ-**Test user** (אחרת "access_denied").
- ההתחברות הראשונה פותחת דפדפן על localhost, ולכן חייבת לרוץ על מחשב עם דפדפן ולא בסביבת ענן.
- ההרשאה `youtube.upload` מאפשרת רק להעלות. לשינוי סרטון קיים (למשל מפרטי לציבורי) צריך הרשאת `youtube` נפרדת, או לשנות ב-Studio.
- אחרי הפריט האחרון יש המתנה אקראית של 1-4 דקות. אפשר לקצר עם `--gap 1 2`. בהרצה ברקע משתמשים ב-`python -u` כדי לראות לוג.
- `defaultLanguage` נקרא רק מ-`defaults.youtube.language`, לא מהפריט.
