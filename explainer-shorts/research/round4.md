# Research round 4: viewers, craft, distribution (2026-11-23)

Reddit and HN were mostly unreachable from the research environment, so the sources are journalism, vendor studies, creator interviews and motion-design blogs. [exp] marks synthesis.

## What viewers punish (and what they reward)
- Sameness (same voice, structure and effects across videos), surface-level content, hallucinated facts and overly dramatic narration ([NPR](https://www.npr.org/2025/08/28/nx-s1-5493485/ai-slop-videos-youtube-tiktok), [404 Media](https://www.404media.co/ai-generated-boring-history-videos-are-flooding-youtube-and-drowning-out-real-history/)).
- In Kapwing's faceless-channel test, viewers rarely commented on the AI voice. They did call out wrong facts ([Kapwing](https://www.kapwing.com/resources/we-grew-a-faceless-youtube-channel-to-1000-subscribers/)).
- Voice quality matters more than whether the voice is AI or human. In one vendor study a high-quality AI voice scored 71% on retention quizzes, against 61% for a human voice ([TechSmith](https://techsmith.com/blog/ai-voices-avatars-in-training-videos)).
- Trust builders: accuracy, honesty about AI use, niche educational focus, and recurring characters or formats where each video still has a distinct concept.

## YouTube policy
- The "inauthentic content" policy (July 2025, clarified July 2026) targets templated, mass-produced content with only superficial differences. Series and recurring characters are allowed when each video has a distinct concept ([YouTube](https://support.google.com/youtube/answer/1311392), [Tubefilter](https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/)).
- Disclosure is required only for realistic synthetic content. Flat 2D animation with a TTS voice does not need the label ([YouTube](https://support.google.com/youtube/answer/14328491)).
- The risk for us is template sameness, so vary the hook type, metaphor, structure and length per video.

## Distribution and length
- Optimise first for viewed-vs-swiped (the hook), then % viewed (length + loop), then shares and subscribers per 1k views. Creator-reported targets: 70-80%+ viewed, 80-90%+ average viewed under 35 s ([1of10](https://1of10.com/blog/youtube-shorts-analytics/)).
- Top Shorts mostly run 25-35 s, and every second of slack costs about 3% ([Toptal compilation](https://www.toptal.com/creator/post/youtube-shorts-length)). Target 32-38 s.
- Visible physical objects, specific numbers and named things beat abstract concepts. Experiment and process topics perform well ([hackmd analysis](https://hackmd.io/@R1RqQ0E5TKGhW3BsooFBsw/SJeRwCjDWg)).
- Series: use a numbered tag, a consistent first-frame layout and a one-line tease, with no generic "subscribe" CTA [exp].

## Craft upgrades (ranked by impact/effort)
1. Use a different easing per element type, with overshoot, a 2-4 frame stagger and a settle ([Cursa](https://cursa.app/en/page/polish-pass-overlap-secondary-motion-and-subtle-texture)).
2. Constant slow camera push-in (1.00 to 1.06 per scene), with a harder push at the reveal.
3. Always-on idle on characters: breathing at 2-3% and a blink every 3-5 s.
4. Living grain, re-seeded every 2 frames at 4-6% opacity ([Codrops](https://tympanus.net/codrops/2019/02/19/svg-filter-effects-creating-texture-with-feturbulence/)).
5. Colour script: cool and desaturated for the problem, warm and saturated for the payoff, shifted through CSS variables ([Blender Studio](https://studio.blender.org/blog/color-scripting/)).
6. Line boil on characters only: feDisplacementMap scale 2-4, stepped on twos ([Visini](https://camillovisini.com/coding/simulating-hand-drawn-motion-with-svg-filters)).
7. Three parallax layers, with the background moving 10-30% of the foreground distance and blurred by 2-3 px.
8. On key beats: squash and stretch, a smear ghost, a particle burst and an impact-frame shake.

## Rules adopted for rounds 4-6
- Show a source tag on screen for the core claim.
- Every video has one original, counter-intuitive angle. No "X facts about Y".
- Use a recurring series tag ("EVERYDAY MYSTERIES #N") and keep the first-frame layout consistent, while the structure varies from video to video.
- End on the takeaway the hook promised, then loop. A 1-2 s content question is allowed. No subscribe pitch.
