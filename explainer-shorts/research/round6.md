# Round 6 research: payoff, mechanism clarity, SFX density, seatbelt facts

Method note: Reddit/YouTube-comment threads did not surface via search snippets; findings below come from creator/industry articles, a LessWrong thread, research summaries, patents. Tags: [exp] = my synthesis.

## 1. Payoff and ending
- Close the curiosity gap inside the video; "open it too wide and the video reads as bait". Signpost the destination but keep "a little bit of mystery". https://www.descript.com/blog/article/the-youtubers-guide-to-the-curiosity-gap-how-to-keep-your-audiences-interest
- Treat the reveal as a moment on screen, not a static end frame; keep the same setup for before/after; then add ONE sentence on why it worked; close with a one-line rule. Avoid a "no proof ending" (never showing the method working). https://cursa.app/en/page/swipe-stopping-narrative-structures-for-short-form
- Loop techniques: callback to hook line, last frame matches first frame, audio continuity across the seam; combine at least two; put CTA in caption not voice; keep under ~25 s (vendor article, directional); breakers = hard stop, static final frame, over-explained ending, audio with a clear closing note. https://virvid.ai/blog/looping-structure-shorts-retention-2026
- Loop caveats: looping does not guarantee double watch time; since 31 Mar 2025 Shorts views count starts and replays; engaged views exclude loops. Example: Jake Fellman's tight arrowhead loop, 15M views in 48 h. https://vidiq.com/blog/post/double-youtube-watch-time-looping-shorts
- [exp] For our mechanism Shorts: final beat = the mechanism snapping shut on the thing the hook showed (e.g. belt jerked, pawl drops, hard stop), then the closing line reuses a hook word, and the first frame of the Short is the end frame state (belt half-out). Music tail stays unresolved/pad so the seam is soft.

## 2. Mechanism clarity
- Research: signaling (cues highlighting essential material) median d=0.70; segmenting into steps d=0.67; labels placed next to the part they name d=0.82. https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf
- Pace: every critical stage should hold a clear view for at least 1-2 s; a stage given "a quarter second" is not understood; the four-stroke animation praised for "one second per phase"; exaggerate small moving parts (cams, valves); mark unlabeled pivots. https://www.lesswrong.com/posts/ZiCvwLKreShtXuyiB/slower-animated-diagrams
- Jared Owen: builds animation first, then fits narration to it; takes real objects apart to learn them. https://www.blendernation.com/2018/11/19/meet-the-artist-jared-owen/
- Animation Processing Model: balance spatial and temporal information, clear instructional purpose, support perception. https://www.thecontentwrangler.com/p/exceptional-technical-animations
- Could not verify specific commenter praise for Animagraffs/Branch/Lesics/Mould; no source found. Do not claim it.
- [exp] Recipe: establish the whole part at rest, ghost/fade the housing, tint ONLY the moving part (one accent colour), run the event once at real speed then once slow (about 1 s per stage), label at the part (max 3 labels, 1-3 words), dim everything else.

## 3. SFX density
- "Fewer sounds and better sounds"; biggest problem is usually too much sound. https://sound-ideas.com/blogs/sound-ideas/avoiding-spectral-logjams
- Effects "at meaningful audio events, not on a timer"; example 20 s sequence with 6 whooshes+4 impacts+3 clicks vs 1 UI click + 1 major impact at the reveal, latter "possibly much stronger"; "the fiftieth one is part of the noise floor"; whoosh only when something moves, not on static cuts or sentence ends; vary repeats by pitch/timing/level; remove-50% test. https://www.overseeros.com/blog/youtube-sound-design
- "Some moments need emphasis. Others need space." https://www.motiontheagency.com/blog/sound-design-for-explainer-videos
- No source gives a hard per-10-s tolerance. [exp] Working budget: 2-3 SFX per 10 s, max 1 whoosh per 10 s, no regular spacing, silence before the payoff, one hero sound at the reveal. Foley (clicks, ratchet ticks, fabric) for physical events, synth only for transitions; both unsourced beyond the definitions in the overseeros article.

## 4. Seatbelt retractor fact check
- Pendulum (vehicle-sensitive): "The central operating element in this mechanism is a weighted pendulum." Sudden stop swings it forward; its pawl catches "a toothed ratchet gear attached to the spool." https://auto.howstuffworks.com/car-driving-safety/safety-regulatory-devices/seatbelt3.htm
- Centrifugal (webbing-sensitive): "a centrifugal clutch - a weighted pivoting lever mounted to the rotating spool." "When the spool spins slowly, the lever doesn't pivot at all." Fast spin flings the weighted end out, pushing a cam that pulls the pawl into the ratchet gear (same URL).
- Patent view of the vehicle sensor: pendulum tilts, lifts a lever, a pawl "is moved into blocking engagement with a ratchet wheel"; spring motor rewind releases it. https://patents.google.com/patent/US4015796A/en (note: this is a bell-on-post pendulum; ball-in-cup sensors exist in other patents but HowStuffWorks says neither uses a ball, so say "weighted pendulum").
- Wikipedia: "A webbing-sensitive lock is based on a centrifugal clutch"; "A vehicle-sensitive lock is based on a pendulum"; dual-sensing retractors use both. https://en.wikipedia.org/wiki/Seat_belt
- Thresholds (secondary source, avoid on screen): vehicle sensor about 0.7 g; webbing roughly 2-10 g; must not lock at 0.3 g or less. https://scienceinsights.org/why-do-seatbelts-lock-and-when-they-get-stuck/
- Misconceptions: "locks when pulled = broken" (it is working: fast pull trips the clutch; slow pull pays out); slope or tilt can hold the vehicle sensor locked; ALR child-seat mode locks at current length until unbuckled; hard braking or swerve can lock it too (same scienceinsights URL).
- Safe wording: "Two sensors, one ratchet. A weighted pendulum feels the car slow down. A weighted lever on the spool feels the belt being yanked. Either one drops a pawl into a toothed wheel, and the spool stops."
- Number (NHTSA): "If you buckle up in the front seat of a passenger car, you can reduce your risk of: Fatal injury by 45% (Kahane, 2015)." Also "Seat belt use in passenger vehicles saved an estimated 14,955 lives in 2017." https://www.nhtsa.gov/vehicle-safety/seat-belts
- IIHS: lap and shoulder belt "reduces the risk of fatal injury by 60% in an SUV, van or pickup and by 45% in a car"; NHTSA est. 20,443 lives saved in 2019. https://www.iihs.org/topics/seat-belts

## Rules to adopt for round 6
1. Write the final beat first; it must be a visible event (mechanism completing), then one "why" sentence, then a one-line rule.
2. Make the last frame near-identical to the first and reuse one hook word in the last line; CTA only in caption.
3. Seam audio: no closing chord; pad/ambience continues across the loop.
4. Mechanism shots: housing ghosted, one accent colour on the moving part, everything else dimmed; max 3 labels placed beside the part.
5. Hold every mechanism stage 1-2 s; show the event at real speed once, then slowed once.
6. SFX budget 2-3 per 10 s, at most one whoosh per 10 s, irregular spacing, silence just before the reveal, one hero sound at the payoff; run the remove-50% test.
7. Seatbelt script: say "weighted pendulum" and "weighted lever", never "ball"; use the exact NHTSA 45% wording with "Kahane, 2015" in the caption or description.
8. Preempt the misconception on screen: "Slow pull: it spools out. Fast yank: it locks. That is the design working."
