# Round 5 research: viewer sentiment, hooks, audio, captions, battery topic

Legend: [exp] = my synthesis. Many hook/caption stats come from creator-tool blogs (vendor data, unverified) and are flagged as such.

## 1. What viewers/platforms punish (limited direct Reddit access; search snippets + articles)
- YouTube terminated 16 channels in Jan 2026 under "inauthentic content" (templated, mass-produced, little human input); enforcement looks at the last ~30 uploads channel-wide. Faceless channels get collateral damage. https://thenextweb.com/news/youtube-ai-slop-crackdown-faceless-creators-collateral-damage
- YouTube tests a 5-point viewer "AI slop" survey (March 2026). Same source.
- Common AI-Shorts mistakes: one template with swapped nouns trains viewers to skip the channel; flat narration on dramatic content "reads as parody"; scenes held longer than one sentence drop retention (cut every 2-4 s); caption typos/desync look sloppy; publishing unreviewed output. https://clippie.ai/blog/make-ai-shorts-go-viral-2026
- Kurzgesagt fan complaint (r/kurzgesagt mirror): the backlash was about oversimplified facts and missing nuance (e.g. exercise/calorie video), not about animation; critics also dislike "both sides" hedging and monetization framing. https://redlib.snake-cloud.ts.net/r/kurzgesagt/comments/1emntr6/both_sides_content_is_not_what_i_want_from
- Wider forum sentiment (not fetched, titles only): "Am I the only one who hates AI youtube videos?" https://forum.slowtwitch.com/t/am-i-the-only-one-who-hates-ai-youtube-videos/1297687
- [exp] Viewer trust failures cluster on: oversimplified-to-false claims, hooks promising more than delivered, and template sameness. Accuracy plus a concrete caveat is a differentiator.

## 2. Hooks (vendor data, treat as directional)
- Archetypes: curiosity gap, pattern interrupt, bold claim ("Everything you know about X is wrong"), relatable pain, visual shock. Claimed avg lift: visual shock +46%, curiosity gap +42%, pattern interrupt +38%, bold claim +35%, pain point +31%; combining curiosity gap + visual disruption +47%. https://dev.to/bulkdl/hook-engineering-the-science-of-the-first-3-seconds-in-short-form-video-2026-2jp9
- Scroll decision window claimed ~2.3 s on Shorts; first-3s retention <55% weak, 55-70% ok, >70% strong; 54-68% of views start muted, so hooks must work without sound. Same source.
- "Stop doing X" framing reported to beat "how to" (anecdotal). https://t.me/s/HookConfessions/11
- [exp] For this series: open with the visual contradiction (phone at 80% with a "why did it stop?" beat) plus one-line bold claim; the first line must be readable as caption with sound off.

## 3. Audio
- WCAG G56: background at least 20 dB below speech (accessibility benchmark). https://www.w3.org/WAI/WCAG22/Techniques/general/G56.html
- Creator guidance: dense educational narration 22-30 dB below, general faceless 18-24 dB, emotional 15-20 dB; optional extra 3-6 dB ducking; no vocals in the bed; judge music with voice, not solo; check on phone speaker; do not put impact SFX on key stats. https://www.overseeros.com/blog/background-music-volume-under-voiceover
- AI-Shorts guide: music bed 15-20 dB under VO. https://clippie.ai/blog/make-ai-shorts-go-viral-2026
- [exp] Target music about 20-24 dB under voice (RMS), duck 3 dB on speech, SFX sparse (max one per beat, none on the key number). Procedural bed should avoid mid-range lead melody (voice band 1-4 kHz); roll off there. Free sources were not verified this round.

## 4. Captions (vendor blogs)
- Word-highlight with full line visible: +18-23% watch time vs static; 1-2 word pop-in raises likes/shares but can hurt retention on long videos (fine under 30 s); full-sentence static is least engaging. Center (~60% from top) beats bottom third by ~10-15%; text height ~18-24% of screen height. https://dev.to/clamper_ai/how-ai-caption-styles-affect-watch-time-and-engagement-409i
- Caption errors/desync read as low effort; regenerate captions after final audio. https://clippie.ai/blog/make-ai-shorts-go-viral-2026
- Accessibility: keep high contrast, avoid covering key visuals. [exp]
- [exp] Use 3-5 word phrase chunks with active-word highlight, lower-center above the Shorts UI safe zone, never over the focal animation.

## 5. Topic: phone charging to 80%
TRUE:
- Heat and high voltage stress Li-ion; dwelling at full charge can be more stressful than cycling. At 25 C, 100% charge stored one year keeps ~80% capacity vs ~96% at 40% charge; at 60 C, 100% falls to 60% in 3 months. https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries
- Lowering charge voltage: 4.20 V = 300-500 cycles; 4.00 V = 850-1500; 3.92 V = 1200-2000 (less stored energy). Same source.
- No memory effect; no need for full discharges. Same source.
- Fast charge reaches 80% quickly, then slows (CV taper); Apple says software may limit charging above 80% when hot. https://www.apple.com/uk/batteries/why-lithium-ion/
- Optimized Battery Charging learns routine and delays charging past 80% until shortly before you need it. https://www.techradar.com/phones/should-you-stop-charging-your-phone-battery-to-100-percent-heres-what-experts-say
- A "100%" reading is not the chemical maximum; a buffer prevents true overcharging. Same source.
Misconceptions (to address one):
1. "Leaving it plugged in overnight overcharges/explodes it." False: charging stops; real issue is sitting at 100% plus heat. https://www.bgr.com/2169846/stop-believing-myths-charging-phone/
2. "Let it hit 0% first." Deep discharge is harmful; no memory. Same.
3. "Don't use the phone while charging." Light use fine; gaming adds heat. Same.
4. "Any cheap charger is fine." Poor regulation stresses cells. Same.
5. "Never go to 100%." Occasional 100% is fine (advice inherited from NiCd). TechRadar above.
- [exp] Best single misconception for 35 s: "overnight charging overcharges it" -> truth: the phone stops at 100% and then sits full and warm, which is what ages it; the 80% cap and Optimized Charging delay the full part. CC/CV can be one visual: steady current fills fast, then voltage holds and current tapers. Add a caveat: 80% costs ~10-20% runtime, so it matters for daily users who care about longevity, not a must.

## Rules to adopt for round 5
- Hook in the first 1.5 s: visual contradiction plus a readable bold-claim caption; must work muted.
- Address exactly one named misconception ("overnight charging overcharges it") and pay off the hook by second ~25.
- Cut visuals every 2-4 s; never hold a scene beyond one sentence.
- Music bed 20-24 dB under voice, extra 3 dB duck, no vocals/lead melody in 1-4 kHz, SFX sparse and never on key numbers; test on phone speaker.
- Captions: 3-5 word chunks, active word highlighted, lower-center in safe zone, proofread numbers, regenerate after final audio.
- Include one real figure with source on screen (e.g. 25 C: 80% vs 96% retained after a year) plus a one-line caveat to avoid the Kurzgesagt oversimplification trap.
- Vary structure between episodes (not noun-swap template) to avoid inauthentic-content flags; add a human-authored angle.
- Skip the claim "never charge to 100%"; say "avoid sitting full and hot".
