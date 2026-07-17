# Sarah — Vapi Voice Assistant

Sarah is the phone assistant for the Sarlls Safe Switch project. This folder contains everything needed to deploy her on [Vapi](https://vapi.ai).

## Files

| File | Purpose |
|---|---|
| `SARAH-VAPI-PERSONA.md` | Governing persona document — the source of truth for Sarah's identity, knowledge, and conversation rules. Edit this first, then sync changes into the JSON system prompt. |
| `sarah-assistant.json` | Ready-to-deploy Vapi assistant configuration (model, voice, transcriber, call behavior). |

## Deploy

### Option A — Vapi Dashboard
1. Go to [dashboard.vapi.ai](https://dashboard.vapi.ai) → **Assistants** → **Create Assistant**.
2. Copy the values from `sarah-assistant.json` into the corresponding fields (or use the JSON import if available on your plan).
3. Attach a phone number under **Phone Numbers** and set Sarah as the inbound assistant.

### Option B — Vapi API
```bash
curl https://api.vapi.ai/assistant \
  -X POST \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @sarah-assistant.json
```
The response includes the assistant `id`. To update later, `PATCH https://api.vapi.ai/assistant/{id}` with the changed fields.

## Configuration Notes

- **Model:** `claude-opus-4-8` (Anthropic provider). Note that Opus 4.8 does not accept `temperature`/`top_p` — the config intentionally omits them. If call latency matters more than answer quality, `claude-haiku-4-5` is the low-latency swap.
- **Voice:** ElevenLabs "sarah" voice. Swap `voice.voiceId` for any voice available in your ElevenLabs/Vapi account.
- **Transcriber:** Deepgram Nova-2, English (US).
- **Call limits:** 30 s silence timeout, 10 min max duration.
- **Analysis:** each call produces a summary and a pass/fail success evaluation (visible in the Vapi call logs) so James can scan callbacks quickly.

## Keeping the persona in sync

`SARAH-VAPI-PERSONA.md` is the human-readable master. The `model.messages[0].content` field in `sarah-assistant.json` is a condensed, speech-optimized version of it. When you change the persona doc, update the JSON system prompt to match and re-deploy (PATCH or re-import).

## Test checklist

After deploying, call the number and verify:
1. Sarah answers with the greeting and identifies herself.
2. Ask "what is the Safe Switch?" — expect a short, plain-language answer.
3. Ask about an order status — expect an offer to take a message (she must not invent tracking info).
4. Ask for the WiFi password — expect a polite refusal directing you to the setup card.
5. Say "that's all, goodbye" — expect a thank-you and the call to end.
