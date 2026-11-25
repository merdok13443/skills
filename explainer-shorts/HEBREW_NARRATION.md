# Hebrew narration

Use this when the video is narrated in Hebrew. Kokoro (`engine/tts.py`) has no Hebrew voice, so Hebrew uses `engine/tts_he.py` instead. Everything after the voice step (timing.js, scene, render, mix) is the same as for English. The example project is `examples/he1`.

Tested on Windows 11, Python 3.11, on 2026-11-23. The numbers are in `research/hebrew-samples/results.txt`.

## Recommended: edge-tts (free, no key, online)

```
pip install edge-tts soundfile scipy numpy        # ffmpeg must be on PATH
python engine/tts_he.py he1                       # writes he1/voice.wav + he1/timing.json
sh engine/mktiming.sh he1
```

- **Voices:** `he-IL-HilaNeural` (female) is the default and recommended voice, and `script.json` / `tts_he.py` use it unless you set `"voice"`. The male alternative is `he-IL-AvriNeural`. These are the only two he-IL voices: `edge-tts --list-voices` shows no others, and Azure has none either.
- **Timing:** it returns real per-word timestamps, so no alignment step is needed. Both voices gave exact word marks for 7/7 lines in the he1 test.
- **Pace:** at `"rate": "-4%"`, the he1 script came out at 18.1 s / 106 wpm for Hila and 19.4 s / 99 wpm for Avri. For a 32-38 s Short, write about 60-70 Hebrew words, or set `"rate": "+0%"` for a little more speed.
- **Quality check:** a Whisper Hebrew transcription (ivrit-ai large-v3-turbo) of the Avri demo matched the script word for word. "80%" was read correctly as שמונים אחוז. The Hila demo was also correct; Whisper only spelled זוחל and סוללה slightly differently.
- **Caveats:** it uses Microsoft's Edge read-aloud endpoint, which is free but unofficial and can change. Keep the generated `voice.wav` with each project.

## Gemini TTS (Dakademia narration for Decky)

```
pip install google-genai>=2.25.0 soundfile scipy numpy
# key once, on the PC:  setx GEMINI_API_KEY "<key>"   (then open a new terminal)
python engine/tts_he.py <proj> --backend gemini
python engine/align_he.py <proj> && sh engine/mktiming.sh <proj>
```

**Standing rule (project owner, 2026-11-25):** the Gemini API key is used ONLY with the model `gemini-3.8-flash-tts` and ONLY to generate narration audio. No other model, no other use. `tts_he.py` hard-codes the model and exits if the script asks for another.

- **Limits:** one request per script line, spaced about 6.5 s apart (10 requests/minute). The Google Cloud project is capped at 50 requests per day for this model.
- **Voice:** default `Puck` (Upbeat). A/B candidates: `Sadachbia` (Lively), `Achird` (Friendly), `Fenrir` (Excitable). Pick once and keep it for the series.
- **Style (Decky):** young Israeli guy, quick, curious, a little cheeky, a friend who already passed the course; upbeat, slightly faster than normal speech, smiling, short punchy sentences, never a lecturer or announcer, a short pause before the punchline. Default text is `DECKY_STYLE` in `tts_he.py`; override with `"style"` in script.json.
- **Timing:** no word timestamps, so run `align_he.py` afterwards.
- **Output:** WAV, 24 kHz mono.

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

- `"text"` is shown as captions, and `"say"` (optional) is what the voice reads. With edge, keep the same number of words in both so the exact word marks still map 1:1.
- Edge reads digits and % correctly. For Piper, always spell out numbers, %, units and English words in Hebrew.
- Short lines with a comma or period at the end give natural pauses. Use `"pause"` for the dramatic silence before the payoff, just as in English.

## RTL captions and layout

- Copy `examples/he1/index.html`: `<html lang="he" dir="rtl">`, the Heebo font (`npm i @fontsource/heebo`, Hebrew + Latin subsets), and text blocks anchored with `right:` instead of `left:`.
- No `text-transform:uppercase` or letter-spacing on Hebrew text.
- Wrap numbers and English inside Hebrew text in `<bdi>` (for example `<bdi>80%</bdi>`), and give big number blocks `direction:ltr`.
- `buildCaptions` works unchanged: the karaoke highlight moves right to left.

## Other options researched (not tested here)

| Option | Hebrew | Cost / licence | Notes |
| --- | --- | --- | --- |
| Gemini TTS (Google AI Studio) | listed as supported (Cloud TTS docs call he-IL Preview) | free tier with an API key; paid is about $0.01 per Short | Probably more expressive; no word timestamps, so run `align_he.py`. The best candidate to A/B test next. |
| ElevenLabs v3 | supported (Multilingual v2 is not intelligible in Hebrew) | free plan has no commercial licence; Starter is $6/month | Best paid upgrade. Use `model_id="eleven_v3"`, `language_code="he"`. |
| Google Cloud Chirp 3 HD | he-IL supported | needs Cloud billing | No custom pronunciation for he-IL. |
| OpenAI TTS | reported American accent | paid; tts-1 retires 2027-01-06 | Not recommended. |
| Phonikud-TTS, Kokoro-Hebrew, MMS-TTS-heb | yes | non-commercial licences | Not usable for a monetised channel. |

Sources: https://danielrosehill-hebrew-tts-samples.static.hf.space/index.html (side-by-side Hebrew samples), https://github.com/rany2/edge-tts, https://aistudio.google.com/docs/speech-generation, https://elevenlabs.io/docs/overview/models, https://huggingface.co/thewh1teagle/piper-he-noa, https://github.com/thewh1teagle/phonikud
