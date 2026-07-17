#!/usr/bin/env bash
# Deploy the Sarah assistant to Vapi.
#
# Usage:
#   VAPI_API_KEY=... ./deploy-sarah.sh                    # create a new assistant
#   VAPI_API_KEY=... VAPI_ASSISTANT_ID=... ./deploy-sarah.sh   # update existing
#
# Requires: curl, jq

set -euo pipefail

cd "$(dirname "$0")"

if [[ -z "${VAPI_API_KEY:-}" ]]; then
  echo "ERROR: VAPI_API_KEY is not set. Get a private key from https://dashboard.vapi.ai" >&2
  exit 1
fi

command -v jq >/dev/null || { echo "ERROR: jq is required" >&2; exit 1; }

# Inject the system prompt from sarah-system-prompt.md into the config template.
PAYLOAD=$(jq --rawfile prompt sarah-system-prompt.md \
  '.model.messages[0].content = $prompt' sarah-assistant.json)

if [[ -n "${VAPI_ASSISTANT_ID:-}" ]]; then
  echo "Updating existing assistant ${VAPI_ASSISTANT_ID}..."
  RESPONSE=$(curl -sS -X PATCH "https://api.vapi.ai/assistant/${VAPI_ASSISTANT_ID}" \
    -H "Authorization: Bearer ${VAPI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
else
  echo "Creating new assistant..."
  RESPONSE=$(curl -sS -X POST "https://api.vapi.ai/assistant" \
    -H "Authorization: Bearer ${VAPI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
fi

ASSISTANT_ID=$(echo "$RESPONSE" | jq -r '.id // empty')

if [[ -z "$ASSISTANT_ID" ]]; then
  echo "ERROR: Vapi API did not return an assistant id. Response:" >&2
  echo "$RESPONSE" | jq . >&2 || echo "$RESPONSE" >&2
  exit 1
fi

echo "OK: assistant id ${ASSISTANT_ID}"
echo "Manage it at https://dashboard.vapi.ai/assistants/${ASSISTANT_ID}"
echo
echo "To update later, run:"
echo "  VAPI_API_KEY=... VAPI_ASSISTANT_ID=${ASSISTANT_ID} ./deploy-sarah.sh"
