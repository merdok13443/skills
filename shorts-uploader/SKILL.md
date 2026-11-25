---
name: shorts-uploader
description: Bulk-upload original vertical shorts to YouTube Shorts and Instagram Reels through the official APIs (free, no third-party scheduler or daily cap), from a queue file, with safe pacing, resume and the YouTube made-for-kids flag. TikTok is covered as manual/TikTok Studio only.
---

# Shorts Uploader (YouTube + Instagram, official APIs)

Use when the user wants to publish many finished shorts (from `explainer-shorts` or any other source) to YouTube Shorts and Instagram Reels without a paid scheduler.

## Read first
- `README.md` (Hebrew): full setup, usage, limits, kids setting, pacing, troubleshooting.
- `queue.example.json`: format of the upload queue.
- `ALTERNATIVES.md` (Hebrew): existing GitHub tools (Postiz, Upload-Post MCP, Mixpost) with setup pointers, when to prefer each, and what to avoid.

## What it does
- `scripts/youtube_upload.py`: resumable upload with `videos.insert`, from the queue, public/unlisted/private or scheduled (`publishAt`), `selfDeclaredMadeForKids` set explicitly, `#Shorts` added, state file so reruns skip finished items.
- `scripts/instagram_publish.py`: Graph API Reels publishing (create container, poll until FINISHED, publish), checks `content_publishing_limit` first, state file.
- `scripts/queue_status.py`: shows what is done / pending / failed.

## Rules for the agent
1. Never ask for or store passwords. Auth is OAuth (YouTube) and a long-lived token (Instagram), kept in local files that are in `.gitignore`. Never commit `client_secret.json`, `token.json`, `.env`, `state.json`.
2. Always dry-run first (`--dry-run`), then one real video, then the batch.
3. Pace: default 6 uploads/day for YouTube (the user will raise it gradually) and 20/day for Instagram, with random gaps, far below the official ceilings (see README, "limits"). A series skill may set a lower cadence.
4. Kids flag: the default is `false` (not made for kids); set `true` only when the content is actually directed at children and the user confirms explicitly. Why: README, "made for kids".
5. TikTok: no safe free bulk API. Use TikTok Studio's own scheduler (web, "Schedule video") or manual upload. Do not use cookie/browser-automation tools on the user's main account (the only exception: the manual TikTok Studio upload on the owner's PC, see README).
6. Limits change. Before a large batch re-check the official pages linked in README.
7. After every finished video that is approved for publishing, try all three platforms: YouTube (required), Instagram and TikTok (best-effort, not mandatory). Always report the status of each one. Before writing a caption, check what the video is actually about.
8. Keep a persistent publish state: `publish-state.json` (plus the generated `PUBLISH-STATE.md`) in the videos repo. Update it with `scripts/publish_state.py` (`add` when a video is ready, `set <video> <platform> <status> --url ...` after each upload attempt). It must always show which videos exist and where each one is already up. Statuses: pending, uploaded, under_review, failed, skipped, unknown.
