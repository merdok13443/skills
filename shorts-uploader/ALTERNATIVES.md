# כלים קיימים מגיטהאב ומהרשת (חלופה לסקריפטים בתיקייה)

מבוסס על המחקר מ-25.11.2026. לא העתקתי קוד של צד שלישי לכאן. הקובץ מפנה למקור, כדי לכבד את הרישיונות (Postiz הוא AGPL-3.0).

## 1. Postiz (המומלץ אם רוצים לוח שנה ותזמון עם ממשק)
- https://github.com/gitroomhq/postiz-app , כ-41 אלף כוכבים, פעיל, AGPL-3.0.
- הפעלה עצמית בחינם (Docker, Postgres, Redis, Temporal). מדריך: https://docs.postiz.com
- חיבור ערוצים: אתה יוצר בעצמך אפליקציית Google (YouTube) ואפליקציית Meta (Instagram) ומכניס את ה-client id וה-secret ל-`.env`. מדריכים: https://docs.postiz.com/providers/youtube.md , https://docs.postiz.com/providers/instagram.md
- כולל MCP, CLI ו-API, שאפשר לחבר לקלוד.
- טיקטוק בהפעלה עצמית: הפוסטים נשארים פרטיים עד שטיקטוק מאשרת את האפליקציה שלך, ודחיות על שימוש אישי דווחו (https://github.com/gitroomhq/postiz-app/issues/2297).
- חלופה מתארחת: Postiz Cloud, כ-29 עד 99 דולר בחודש.

## 2. Upload-Post (מתארח, מכסה גם טיקטוק)
- MCP בקוד פתוח (MIT): https://github.com/Upload-Post/upload-post-mcp , ותוסף ל-Claude Code: https://www.upload-post.com/claude-code-plugin/
- חינמי: 10 העלאות בחודש ובלי טיקטוק. Basic בכ-16 עד 24 דולר בחודש: העלאות בלי הגבלה של הכלי וטיקטוק כלול (לפי הספק, ולא אימתתי).
- לפני אצווה, בדוק סרטון אחד בציבורי בטיקטוק.

## 3. Mixpost Lite (MIT)
- https://github.com/inovector/mixpost , כ-3.9 אלף כוכבים, Laravel. לא אימתתי אילו פלטפורמות כלולות בגרסה החינמית.

## לא מומלץ
- https://github.com/dreammis/social-auto-upload : אוטומציית דפדפן ועוגיות, סיכון נעילת חשבון.
- כל כלי שמבקש סיסמת טיקטוק או אינסטגרם.

## מתי מה
| צורך | בחירה |
|---|---|
| הכי חינמי, בלי שרת | הסקריפטים בתיקייה הזו (YouTube + Instagram) |
| ממשק ולוח שנה, ומוכנים להתקין שרת | Postiz בהפעלה עצמית |
| גם טיקטוק ציבורי ובלי טרחה | Upload-Post Basic |
