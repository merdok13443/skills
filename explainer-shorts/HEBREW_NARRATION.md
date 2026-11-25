# Hebrew narration

**Dakademia (Decky): Gemini TTS only, see "Gemini TTS: the fixed voice of Decky" below. edge-tts and Piper are for other series and are never used for Dakademia.**

Use this when the video is narrated in Hebrew. Kokoro (`engine/tts.py`) has no Hebrew voice, so Hebrew uses `engine/tts_he.py` instead. Everything after the voice step (timing.js, scene, render, mix) is the same as for English. The example project is `examples/he1`.

Tested on Windows 11, Python 3.11, on 2026-11-23. The numbers are in `research/hebrew-samples/results.txt`.

## edge-tts (free, no key, online; general default for other series, not Dakademia)

```
pip install edge-tts soundfile scipy numpy        # ffmpeg must be on PATH
python engine/tts_he.py he1                       # writes he1/voice.wav + he1/timing.json
sh engine/mktiming.sh he1
```

- **Voices:** `he-IL-HilaNeural` (female) is the default and recommended voice, and `script.json` / `tts_he.py` use it unless you set `"voice"`. The male alternative is `he-IL-AvriNeural`. These are the only two he-IL voices: `edge-tts --list-voices` shows no others, and Azure has none either.
- **Timing:** it returns real per-word timestamps, so no alignment step is needed. Both voices gave exact word marks for 7/7 lines in the he1 test.
- **Pace:** at `"rate": "-4%"`, the he1 script came out at 18.1 s / 106 wpm for Hila and 19.4 s / 99 wpm for Avri. For a general 32-38 s Short, write about 60-70 Hebrew words. (Dakademia's word budget is in the daki-dakademia skill.)
- **Quality check:** a Whisper Hebrew transcription (ivrit-ai large-v3-turbo) of the Avri demo matched the script word for word. "80%" was read correctly as שמונים אחוז. The Hila demo was also correct; Whisper only spelled זוחל and סוללה slightly differently.
- **Caveats:** it uses Microsoft's Edge read-aloud endpoint, which is free but unofficial and can change. Keep the generated `voice.wav` with each project.

## Gemini TTS: the fixed voice of Decky (דקי)

This is the locked, stable voice of the mascot Decky for every Dakademia video. Heard and approved by the project owner on 2026-11-25 ("sounds great, energetic"); the sample was 10.49 s. Pace rule (owner, 2026-11-25): the lesson's message must come across, so speed follows how hard the line is (the style prompt below says this instead of "slightly faster than normal speech").

**Standing rule (project owner, 2026-11-25):** the Gemini API key is used ONLY with these TTS models: `gemini-3.8-flash-tts` (default and the one that produced the approved voice), `gemini-3.8-flash-lite-tts`, `gemini-3.1-flash-tts`, and ONLY to generate narration audio. No other model, no other use. `tts_he.py` keeps this allowlist and exits if the script asks for anything else.

```
pip install "google-genai>=2.25.0" soundfile scipy numpy
# key once, on the PC (then open a new terminal):  setx GEMINI_API_KEY "<key>"
python engine/tts_he.py <proj> --backend gemini      # ONE request for the whole script
python engine/align_he.py <proj> && sh engine/mktiming.sh <proj>   # required after a whole take
```

### How it was done (what made it work)
1. **Model:** `gemini-3.8-flash-tts` through the Interactions API (`client.interactions.create`), WAV output, 24 kHz mono.
2. **API version v1beta is mandatory.** `genai.Client(api_key=..., http_options={'api_version': 'v1beta'})`. With the SDK default every TTS model answered `404 Model ... not found` (we lost four requests to it on 2026-11-25). Same fix as in a Google forum report; env alternative `GOOGLE_GENAI_API_VERSION=v1beta`.
3. **Billing:** the AI Studio project of the key must be on a paid tier with a prepay credit balance above zero, otherwise the call returns `402 RESOURCE_EXHAUSTED: Your prepayment credits are depleted`. The project has a monthly spend cap set in AI Studio, Spend page (5 ILS at the time of writing), and the Google Cloud project dakademia-515807 has a daily quota cap of 50 requests for this model.
4. **Voice:** prebuilt voice `Puck` (Upbeat). Alternatives to A/B only if the owner asks: `Sadachbia`, `Achird`, `Fenrir`.
5. **Style:** put delivery in the `style` annotation (`speech_metadata`), never in the text (the text is read verbatim). The fixed prompt is `DECKY_STYLE` in `engine/tts_he.py`; copy it here if it changes:

> Decky, a young native Israeli guy (a sabra), lively, quick, curious and a little cheeky, talking to a friend who just started university. Authentic everyday Israeli Hebrew: Tel Aviv casual rhythm and intonation, natural Israeli stress and melody, as if recorded on a voice note between friends, not a foreign speaker and not a textbook reader. Upbeat and energetic, smiling while speaking. The pace serves understanding: brisk and natural on simple, familiar lines; slower and very clear, with a short pause, on the key message and on any step that is new or tricky, so a first-year student follows every word. Short punchy sentences with expressive rises and falls. A touch of the confident, clear delivery of an Israeli prime-time TV newscaster, but warmer and more playful. A brief pause before the punchline and a spark of excitement on the aha moment. Never monotone, never robotic, never an announcer.

   (Format 2, below, builds this same voice in a fixed structure plus a line-by-line delivery map; the prompt quoted here is what `--legacy` scripts still send.)

   **Fun fact line (owner, 2026-11-25):** when the script has a fun fact, its line carries `"emphasis":"funfact"` in `script.json` and the previous line has `pause` >= 0.6. `tts_he.py` (`style_for`) then adds one instruction to the SAME style annotation (no extra request): say that sentence clearly slower, with emphasis and wonder, stressing the surprising word or number. The sentence is quoted inside the style only; the text stays verbatim.

   The approved sample used the earlier wording of this prompt (young Israeli guy plus classic newscaster qualities, no real person named). The version above pushes the Israeli accent harder, which is the owner's top priority, and keeps the energy. **Never name or imitate a real person in the prompt.** Describe qualities instead.
6. **Budget: ONE request per video (project owner, 2026-11-25).** The daily quota is small, so `tts_he.py --backend gemini` defaults to `--mode whole`: the whole script goes in a single request (lines joined by newlines, `<short pause>` after lines whose `pause` is 0.5 or more). At most 3 requests per video including retries; `--mode lines` (one request per line) is refused for scripts of more than 3 lines (no override). `timing.json` records `requests`, and the Dakademia QA fails a video that used more than 3. A whole take has no line boundaries, so `align_he.py` (Whisper on the PC) is required afterwards; until it ran, `timing.json` carries `"needs_align": true`.

### Unified narration format (format 2; owner, 2026-11-25)
One fixed structure for every Dakademia narration: the same voice definition every time, and per line a delivery tone, a stress word and inline markers, so the narration has many pauses, emphasis and a moving melody like the best recent videos. It is still ONE request per video (one text, one `speech_metadata.style`), the same three allowed models, the same voice. `engine/narration_format.py` builds the request from `script.json`; `pipeline/voice.py` checks it before any request. A script without `"format": 2` is the old format and still works with `--legacy` (re-takes of earlier videos only); new scripts use format 2.

**What the request looks like** (Interactions API, as in section "How it was done"):
1. `text` = the transcript, verbatim, one line per script line, with the markers turned into tags and the line's `pause` turned into a closing tag (>= 0.5 s `<short pause>`, >= 1.0 s `<long pause>`; never two tags in a row).
2. `speech_metadata.style` = the style annotation, always built in this order (the model reads it, never says it):
   - **Voice (fixed, same words in every video; changed only on the owner's request):** identity (Decky, a young native Israeli guy), sound (authentic everyday Tel Aviv Hebrew, a voice note between friends, upbeat, warm, smiling), pace rule (brisk on familiar lines, slow and clear on the message and on anything new or tricky) and movement rule (never the same contour on two lines in a row; questions rise and hang; conclusions fall with confidence; the surprising word gets a small lift and a smile; real silence after an important line).
   - **Line by line:** every line whose tone is hook, ask, message, reveal, funfact, recap or loop is named by its first words (caption text, no niqqud) and gets its tone direction, plus `land on "<word>"` when the line has a `stress` word. Lines with tone brisk or build are described once in a closing sentence.
   - A closing guard: do not change, add or skip any word, never read the directions aloud.
   The whole annotation stays under 2200 characters (the check fails above it), because long style blocks make the voice drift.

**Per line in `script.json` (format 2):**
```
{"id": "msg", "text": "...", "say": "... {p} ...", "pause": 1.0, "target": 5.6, "tone": "message", "stress": "אמת"}
```
| tone | use for | delivery |
|---|---|---|
| `hook` | the opening question | a teasing question, rising and hanging |
| `ask` | a question to the viewer inside the video | really asking, rising, a beat to guess |
| `brisk` | simple, familiar lines | quick, light, casual |
| `build` | steps toward the point | steady and clear, leaning toward the point |
| `message` | THE message line (and the payoff) | slow, clear, warm and certain, a falling end, then silence |
| `reveal` | the answer or twist | a beat of silence, then the answer lands with a lift and a smile |
| `funfact` | the fun-fact line (replaces `"emphasis":"funfact"`, which still works) | clearly slower, with wonder, a beat before the surprising word or number |
| `recap` | the plain recap | relaxed, confident, a bit quicker, winding up |
| `loop` | the last line | open, light, unfinished, flowing into the first line |

**Inline markers in `say`** (not words: they do not count toward the "same number of words as `text`"; never in `text`, never as raw tags): `{p}` short pause, `{P}` long pause, `{breath}`, `{chuckle}`, `{gasp}`, `{sigh}`. The tool writes them as `<short pause>` etc. for the 3.8 models and as `[short pause]` etc. for `gemini-3.1-flash-tts` (square brackets, per Google's 3.1 docs). Tags are English even in a Hebrew text. Put a marker where a person would take a breath: before an answer inside a line (`... {p} אמת או שקר?`), before the surprising word, after a definition. Only human vocalisations and pauses, no sound-effect tags. Hebrew has no capital letters: emphasis comes from `stress`, from position (a colon or a comma before the key word), from short sentences and from the pause before it.

**Minimums, checked before any request** (`narration_format.check`): every line has a valid tone; one line has tone `message`; at least 5 different tones in the script; no 3 lines in a row with the same tone; at least 6 pauses (lines with `pause` >= 0.5 plus inline markers); at least 2 inline markers (warning); no unknown or adjacent markers; stress words are in their line; the last line is `loop` (warning).

**How it was researched** (2026-11-25, all from public pages; the 3.8 specifics come from Google's current speech-generation page):
- Google's page for the 3.8 models: the `text` field is a strict verbatim transcript; sustained delivery (emotion, pace, volume) goes in `speech_metadata.style`; point-in-time events go in inline tags (`<short pause>`, `<long pause>`, `<breath>`, `<laugh>`, `<sigh>`, `<gasp>`, `<chuckle>`, `<whispers>`, ...); tags are English even for non-English text; pace and emphasis also come from punctuation (commas, dashes, ellipses); keep style short and reuse the same style across turns for a stable baseline; avoid meta-instructions such as "keep the same timbre".
- Google's blog for 3.1: tags in square brackets, two tags never adjacent, a tag needs text or punctuation around it, "accents are triggered by style prompts".
- Practitioner guides for 3.1 (a Google AI developer article and a LiveKit guide): a named persona, a concrete scene, a pace note and an accent note work better than adjectives; "flatness" words such as quiet, monotone or no rush make the voice crash; do not quote transcript words in the notes of a prompt that is part of the text; keep the tags consistent with the register of the scene.
What we took: the fixed persona block (consistency), tags only for pauses and breaths (reliable, official), delivery as plain-language direction in the style field (not in the text), punctuation and pauses for rhythm, and a ceiling on the style length. What we did NOT take: the "audio profile / scene / director's notes" headers (made for 3.1, where the style is part of the text and the headers were read aloud in some reports); here the style is a separate field that is never spoken.

**Check on the first video that uses it** (not provable from the cloud, no key there): `align_he.py` already transcribes the take and fails if a script word is missing or an extra word was said, which catches a style or a tag read aloud. Listen once for: `<long pause>` length (`inject_pauses.py` only ever adds silence, never cuts it, so a pause longer than wanted shows in `fit_check.py`), and whether the line map's quoted first words leak into the speech. If one does, shorten the stress words or drop `stress` for that line; record the result here.

### Text rules for the voice (applied automatically by `prepare_voice_text` in `tts_he.py`)
- **Numbers are always Hebrew words, never digits.** The script converts `80%` to `שמונים אחוז`, `3.14` to `שלוש נקודה אחת ארבע`, `ו-17` to `ושבע עשרה`, up to 9999. It uses the feminine/abstract counting forms, so for a counted noun of another gender, or a bigger number, write the words yourself in the line's `"say"` field. The script exits with an error if a digit or the Latin name reaches the voice.
- **The name is spelled דקי in Hebrew letters, never "Daki" or "Decky" in Latin, and pronounced like "דקה" (DA-ka, stress on the first syllable).** The script replaces `דקי` with the niqqud form `דַּקִּי` before sending (override with `"name_say"` in script.json). If the owner reports a wrong stress on the name, try `דָּקִי` or `דֶּקִי` in `"name_say"` and record the winner here.
- Prefer short sentences, commas for breath. In format 2 write pauses and breaths as the markers `{p}`, `{P}`, `{breath}` in `say` (see "Unified narration format"); raw `<tags>` are only for legacy scripts.

### Timing and checks
Gemini returns no word timestamps, so `align_he.py` is required afterwards. Its Whisper transcript is also the automatic voice check: every word of the script is heard, numbers are read as words, and the name is דקי. Accent and energy are fixed by the locked voice and style prompt; change them only on the owner's request.

## Offline fallback: Piper + noa

```
pip install piper-tts huggingface_hub
hf download thewh1teagle/piper-he-noa he_IL-noa-medium.onnx he_IL-noa-medium.onnx.json --local-dir tts/he
python engine/tts_he.py he1 --backend piper
pip install faster-whisper && python engine/align_he.py he1      # word timings (Piper gives none)
sh engine/mktiming.sh he1
```

- **Model:** about 77 MB, CPU only, fast. Licence: CC-BY-4.0, so commercial use is allowed with credit ("voice: piper-he-noa by thewh1teagle").
- **Timing:** without alignment, word timings are estimates (0/7 exact). `align_he.py` matched 24/32 words and interpolated the rest. It downloads the 1.5 GB `ivrit-ai/whisper-large-v3-turbo-ct2` model on first run, and the first run took about 11 minutes on CPU including the download. Try `--model small` for a quicker run.
- **Quality:** noticeably weaker than edge. Whisper heard נטען as "ניתן", באג as "בא", and שנים as "שאנים". It skipped "80%" entirely.
- **Fixes:** write numbers and symbols out in words in a `"say"` field, for example `"say": "... עד שמונים אחוז,"`; that fixed the 80% problem. Adding nikud did not help Piper and made some words worse (it dropped the ה in הטלפון). Prefer respelling over nikud.

## Writing Hebrew scripts (any backend)

- `"text"` is shown as captions, and `"say"` (optional) is what the voice reads. Keep the same number of words in both (any backend), so the word times still map 1:1 to the captions.
- Edge reads digits and % correctly. For Piper and Gemini, numbers, %, units and English words are always Hebrew words (Gemini: enforced by `tts_he.py`).
- Short lines with a comma or period at the end give natural pauses. Use `"pause"` for the dramatic silence before the payoff, just as in English.

## RTL captions and layout

- General engine: copy `examples/he1/index.html`: `<html lang="he" dir="rtl">`, the Heebo font (`npm i @fontsource/heebo`, Hebrew + Latin subsets), and text blocks anchored with `right:` instead of `left:`.
- No `text-transform:uppercase` or letter-spacing on Hebrew text.
- Wrap numbers and English inside Hebrew text in `<bdi>` (for example `<bdi>80%</bdi>`), and give big number blocks `direction:ltr`.
- `buildCaptions` works unchanged: the karaoke highlight moves right to left.

## Other options researched (not tested here; Gemini is now in use, see above)

| Option | Hebrew | Cost / licence | Notes |
| --- | --- | --- | --- |
| ElevenLabs v3 | supported (Multilingual v2 is not intelligible in Hebrew) | free plan has no commercial licence; Starter is $6/month | Best paid upgrade. Use `model_id="eleven_v3"`, `language_code="he"`. |
| Google Cloud Chirp 3 HD | he-IL supported | needs Cloud billing | No custom pronunciation for he-IL. |
| OpenAI TTS | reported American accent | paid; tts-1 retires 2027-01-06 | Not recommended. |
| Phonikud-TTS, Kokoro-Hebrew, MMS-TTS-heb | yes | non-commercial licences | Not usable for a monetised channel. |

Sources: https://danielrosehill-hebrew-tts-samples.static.hf.space/index.html (side-by-side Hebrew samples), https://github.com/rany2/edge-tts, https://aistudio.google.com/docs/speech-generation, https://elevenlabs.io/docs/overview/models, https://huggingface.co/thewh1teagle/piper-he-noa, https://github.com/thewh1teagle/phonikud
