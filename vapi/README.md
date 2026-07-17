# Sarah — Safe Switch Voice Assistant (Vapi)

Sarah answers the Safe Switch support line: product questions, device setup
walkthroughs, basic app troubleshooting, and message-taking for James at
Strickland Technology.

## Files

| File | Purpose |
|------|---------|
| `SARAH_VAPI_PERSONA.md` | Governing persona doc — scope, guardrails, design decisions |
| `sarah-system-prompt.md` | The exact system prompt deployed to Vapi (source of truth) |
| `sarah-assistant.json` | Vapi assistant config template (`{{SYSTEM_PROMPT}}` is injected at deploy) |
| `deploy-sarah.sh` | Creates or updates the assistant via the Vapi API |

## Deploy

1. Get a **private API key** from the [Vapi dashboard](https://dashboard.vapi.ai)
   (Settings → API Keys). Never commit the key.
2. First deploy (creates the assistant and prints its id):

   ```bash
   VAPI_API_KEY=sk-... ./deploy-sarah.sh
   ```

3. Subsequent updates (edit `sarah-system-prompt.md` or `sarah-assistant.json`,
   then):

   ```bash
   VAPI_API_KEY=sk-... VAPI_ASSISTANT_ID=<id> ./deploy-sarah.sh
   ```

4. Attach a phone number to the assistant in the Vapi dashboard
   (Phone Numbers → Buy/Import → assign to "Sarah - Safe Switch Support"),
   or test in the browser from the assistant page.

## Configuration choices

- **Model**: OpenAI `gpt-4o` at temperature 0.4 — reliable instruction
  following for the guardrails, low latency for voice.
- **Voice**: ElevenLabs stock voice "Sarah" (`EXAVITQu4vr4xnSDxMaL`).
- **Transcriber**: Deepgram `nova-3`, English.
- **Limits**: 10-minute max call, 30-second silence timeout, call summaries
  enabled via `analysisPlan` (urgent safety reports are flagged).

## Editing the persona

Change behavior in `sarah-system-prompt.md`, keep `SARAH_VAPI_PERSONA.md` in
sync as the human-readable spec, then redeploy. The deploy script injects the
prompt file verbatim, so the JSON never needs hand-edited prompt text.
