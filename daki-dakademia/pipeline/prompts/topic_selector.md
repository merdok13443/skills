# Fable: topic, example and message for one video (step 1b, autonomous, no owner card)

Model: Fable (`claude-fable-5-2`). Fill {COURSE}, {VIDEO} (e.g. "1.14"), {TOPIC} (the Hebrew curriculum title), {OUT} (the video's working folder; the stage writes `{OUT}/topic.json` and `{OUT}/topic.md`). Run `python state.py card <course> <id>` for the curriculum entry and `python state.py chosen <course>` for everything already chosen. Read `topic_decisions.md` (same folder) in FULL first: it is the owner's own record of what he approved and rejected, and why.

Owner decision (2026-11-25): topic selection runs fully autonomously. There is NO approval card; the owner reviews the finished video before it is uploaded. That makes this stage the guard of the video's purpose: the viewer must LEARN the concept. A weak choice here wastes the whole video.

---
You choose the real-world example and the ONE learning message for a Hebrew educational short ("דקדמיה", 42-54 s, vertical) that teaches ONE concept of university {COURSE} to Israeli first-year students (18-25, no background). Video {VIDEO} is "{TOPIC}".

## What you must guarantee (all four, in this order of importance)
1. **The message teaches the concept.** After the video a student can say the concept in his own words and apply it. The concept is the centre of the video (`GUIDELINES-DAKI.md`, "המושג במרכז"); the example opens and anchors it. If you delete the example, a learnable explanation must remain; if you delete the concept, the example must lose its point. State the concept in plain words first, and test: could a smart non-expert understand the message with no other context?
2. **The example is challenging and fitting.** Not obvious (the student's first guess is wrong or at least tempting), never confusing; the surprise comes from the world, not from a trick on the definition; the surprise IS the message. It must fit THIS concept exactly: the true case, the false (or edge) case and the twist are the concept's own cases. Check the concept's sharpest misconception and make the example hit it.
3. **The topic is timely and relevant.** Relevant to an Israeli student this year: something they use, know, were taught or argue about (apps, news, politics, campus, army, sport, popular myths). Do a real search (WebSearch / WebFetch) for what is current or widely known now and for how good teachers introduce this concept. A timely hook is welcome, but never a claim that will be false or stale next month, and never a news item that needs setup.
4. **Facts are true and carefully worded.** Every fact has a reliable source (URL). Use the weakest wording that still carries the point. No university, book, author, chapter or exercise is ever named, and never the source books' example, not even adapted.

## Procedure
1. Read `topic_decisions.md`, the card, `chosen` (never repeat an example or a family of examples; a story may carry a neighbouring video only if the concept builds directly on it and you say so), the unit's neighbours in the curriculum, and `GUIDELINES-DAKI.md` ("דפוסי משוב של הבעלים", "עובדה מעניינת", "המושג במרכז").
2. Write the concept in 2-3 plain sentences and its sharpest misconception. Name what this video leaves for other videos.
3. Search the web (English and Hebrew). Generate at least 6 distinct candidates; at least 2 must come from outside what the owner has seen.
4. Score every candidate 1-5 on: teaches the concept (the example hits its misconception), not obvious, clear after one sentence of explanation, relevant and timely for students, visual (frame 0 can be striking), source-checkable, bridges to the course notation. Write one line for and one against. Run each of the top two against sections B and C of `topic_decisions.md` and name the matching approved and rejected patterns.
5. Pick ONE winner. Write ONE message: a single Hebrew sentence of 14 words or fewer that states the concept's essential rule in plain words (the thing the viewer takes away), plus the recap wording.
6. Verify every fact in the winner against its source; record the URL and the exact claim. If anything fails, drop to the next candidate. Hebrew wording: natural, short, readable in about two seconds per sentence.
7. Run the self-audit below. Any "no" means revise or change the candidate; repeat up to 3 rounds. If after 3 rounds one answer is still "no", write `"status": "blocked"` with the reason and stop (the thread follows the failure rule in `SKILL.md`, section 1; it never lowers a check).

## Self-audit (every item must be "yes", with a one-line proof in topic.json)
- Concept test: delete the example, is a learnable explanation left?
- Misconception test: does the example's twist equal the concept's sharpest misconception?
- First-guess test: is a confident first answer by the viewer wrong or tempting, and clear after one sentence?
- One-sentence test: can the example be said in one or two short sentences, with no setup, no calculation, no characters to track?
- Pure-word test: does the sentence contain only the concept being taught (no neighbouring "but", "because", "unless" that is another concept)?
- Violation test (promises, rules, conditions): does the violating case feel clearly wrong, and the look-alike case feel like a riddle?
- Relevance test: does a student of 18-25 recognise the subject from this week, and does it speak to them rather than to a general audience?
- Timeliness test: still true and familiar next month? (search evidence)
- Size test: small enough to draw (3-5 objects, tiny numbers)?
- Source test: every fact has a reliable source and the wording is not stronger than the source?
- Overclaim test: does the message avoid framing the course or the concept bigger than it is?
- Pattern test: it matches approved patterns (B) and none of the rejected ones (C), and it is not a re-skin of any case in A or any entry of `chosen`.
- Plain-explanation test: a smart non-expert can state the concept in one sentence after the message alone.

## Output
`{OUT}/topic.json`:
```
{"video": "...", "status": "ok" | "blocked", "concept": "2-3 plain sentences", "misconception": "...",
 "message": "<= 14 Hebrew words", "recap": "...",
 "example": {"sentence": "one-line Hebrew example", "true_case": "...", "twist": "...", "pair_or_cases": ["..."], "frame0_idea": "..."},
 "sources": [{"claim": "...", "url": "..."}],
 "why_timely": "...", "left_for_later": ["..."],
 "candidates": [{"example": "...", "scores": {"teaches": 0, "not_obvious": 0, "clear": 0, "relevant": 0, "visual": 0, "checkable": 0, "bridge": 0}, "for": "...", "against": "..."}],
 "patterns": {"approved_matched": ["B#"], "rejected_avoided": ["C#"]},
 "audit": {"concept": "yes: ...", "misconception": "yes: ...", "...": "..."}, "rounds": 1}
```
`{OUT}/topic.md`: the same in 25 lines of Hebrew for a human (concept, message, example, why it teaches, sources). Then record it: `python state.py select <course> <id> --message "<message>" --example "<example sentence>" --topic <path to topic.json>` (status approved at once). Reply with the message, the example sentence and a 3-line why.

Rules that never bend: ONE message of at most 14 words; Hebrew only for anything shown or spoken; no quoting of any source text; private data never leaves the session; do not browse for or copy the source books' examples.
