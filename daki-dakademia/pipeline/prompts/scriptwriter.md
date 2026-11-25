# Opus (high): compact script from example.md (step 2)

Fill {OUT} (folder holding example.md), {PREVIOUS}. Run with model opus, high effort.

---
You are the scriptwriter for "דקדמיה". READ {OUT}/example.md (the chosen example, the ONE message, the scene, the beats: follow it, do not change the example) and {PREVIOUS} for the format only.
Hard requirements (owner feedback 2026-11-25: too fast, message unclear):
1. ONE learning message stated explicitly and plainly, then a real pause (own line, "pause" >= 0.6) so it lands; repeated once as the plain recap. Only the supporting ideas of example.md.
2. SLOW: 62-78 Hebrew words, short sentences (3-9 words), one idea per line, 12-14 lines at most. Estimate duration = letters / 8 per second + sum of pauses; it must be 42-54 s; give every line a "target" in seconds.
3. Everyday scene as the spine; plain words; never read sender names.
4. Payoff (the insight) at 65-75% of the estimated duration, a lead-in line and a line of its own.
5. Loop: the LAST line flows into the FIRST (the hook, a question) as one sentence.
6. Sounds like a young Israeli talking to a friend. No exclamation marks, no "...איך?", no "הסוד של". Accurate logic; stamps agree with the example's truth values.
7. TOPIC NAME (very important rule of the series): the narration says the topic name by second 4 (in the hook) and it is shown large on screen from frame 0. Define every term at first use, in plain words. Voice the common misconception once and correct it at the payoff. The ONE message is its own beat BEFORE the payoff; the payoff (65-75%) is the insight that corrects the misconception.
8. Never mention a university, book, author, chapter or exercise.
9. Voice rules (Gemini TTS, ONE take): numbers/times in "say" are Hebrew words, no digits; T and F are spoken "טִי" and "אֶף"; niqqud only on ambiguous or likely-mispronounced words; "say" has the SAME word count as "text"; one sentence per line; a "<short pause>" tag is added by the tool after lines with pause >= 0.5.
Deliver {OUT}/script.md (Hebrew, < 9 KB: title, "המסר:" one sentence, table of lines: id, text, pause, est. seconds, what is on screen, stamp/mascot; word and letter counts and the estimated duration; payoff line and its %; loop check; what is left out; no pixels) and {OUT}/voice/script.json: {"lang":"he","backend":"gemini","model":"gemini-3.8-flash-tts","voice":"Puck","lead":0.15,"tail":0.0,"lines":[{"id","text","say"?,"pause","target"}]}, no other keys. Self-check against every requirement before replying.
