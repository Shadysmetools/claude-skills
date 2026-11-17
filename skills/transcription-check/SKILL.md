---
name: transcription-check
description: Shadow audit of your app's stored speech-to-text transcripts. Cuts audio clips with ffmpeg, re-transcribes them with Whisper as the "ears", and has Claude judge stored text vs what was actually said (wrong language, translation, invented content, accuracy), then reports agreement with your production verifier. Trigger - "/transcription-check [YYYY-MM-DD]", a scheduled transcription-check routine, or "run the transcription check".
---

# /transcription-check

Claude cannot hear audio. So: **ffmpeg cuts the clip, Whisper hears it, Claude judges.**

This is a **shadow** of whatever verifier your product already runs (or the first verifier, if you
have none). It does not replace it. Label its KPI **"Transcript consistency (Claude, text-only),
unverified"** until it has been calibrated against human spot-listens. Accuracy first: never present
it as verified accuracy.

## Inputs (configurable)
- `CLIPS_SOURCE`: where today's sample comes from: a JSON/CSV export or a DB query returning
  `{ clip_id, media_url_or_path, start_s, end_s, stored_text, prod_verdict? }`.
- `OUT_DIR`: default `./transcription-check/<day>/`.
- `WHISPER_API_KEY` (env) for a hosted Whisper endpoint, or a local `whisper` / `faster-whisper` install.
- `LANGS`: the languages you expect (e.g. `ar,en`).
- Spend cap per run (default $0.05).

## Steps
1. **Prep** (read-only on production):
   - Load the clip list for `[day]` (default today, UTC). If your production verifier has not run
     yet and you are shadowing it, stop and say so.
   - Cut each window: `ffmpeg -ss <start> -to <end> -i <media> -ac 1 -ar 16000 -c:a libopus <OUT_DIR>/clips/<clip_id>.ogg`
   - Transcribe each clip twice: language auto-detect, and forced to each expected language.
   - Write `<OUT_DIR>/bundle.json` with `stored_text`, `whisper_auto`, `whisper_forced`, `prod_verdict`.
2. **Judge** each clip by comparing `stored_text` with both Whisper runs:
   - **fail** if any of:
     - wrong language or script (e.g. Arabic speech stored as Spanish);
     - translation (speech in one language stored in another);
     - invented content: a sentence or more that neither Whisper run heard and that is not explained
       by Whisper dropping one language of a code-switch;
     - accuracy below 70.
   - **needs-listen**: evidence conflicts and text alone cannot decide. Name the .ogg file.
   - **pass**: otherwise. Code-switched speech that matches is correct; dropped fillers are fine.
   - Known Whisper limits (don't blame the stored text): auto-detect drops the minority language of a
     code-switch; forcing English on non-English speech translates it.
   - Record `accuracy_0_100`, flags, a short note with quoted evidence, and `agree` (your verdict vs `prod_verdict`).
3. **Report**: write `verdicts.json` and `report.md` with pass / fail / needs-listen counts, the
   Claude-vs-production agreement (N/M), every disagreement with its clip path, and side findings
   (e.g. the same speech recorded twice).
4. **History**: append to `transcription-check/history.csv`:
   `day,clips,claude_pass,claude_fail,needs_listen,prod_pass,agree,whisper_usd`
5. **Failures**: a clip that both Claude and the production verifier fail is a real bug candidate ->
   file it with your normal bug process (search for duplicates first). A Claude-only fail goes on the
   human needs-listen list, not on a bug board.

## Rules
- Never print secrets.
- No production writes.
- No extra LLM API spend: Claude judges inside the Claude Code session.
- Customer transcript text and audio stay in local files. Never commit them or post them to chats.
