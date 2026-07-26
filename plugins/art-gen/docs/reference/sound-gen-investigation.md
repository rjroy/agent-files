# sound-gen Investigation Notes
# Created: 2026-06-22

## Goal
Build a "sound-gen" sibling to art-gen for generating sound effects via ElevenLabs API
instead of images via Replicate.

## Reference: art-gen (what we're mirroring)

Location: ~/Projects/writing/wyrd-gateway/art-gen/
Runtime: TypeScript / Bun
Pattern: CLI scripts in src/ that parse --flags, call API client, download output

Key files:
  src/replicate-client.ts   -- API abstraction (createPrediction, waitForCompletion, downloadFile)
  src/generate-image.ts     -- CLI entry point (--prompt, --output, --model, etc.)
  src/generate-video.ts     -- Another CLI entry point for video
  .claude-plugin/plugin.json -- Plugin manifest
  reference/image-models.md  -- Model catalog
  docs/reference/REPLICATE_API.md -- API docs

Art-gen is an MCP plugin with tools exposed to Claude Code. The MCP server bridges
Claude -> tool call -> Replicate API -> file save.

## ElevenLabs Sound Generation API

Endpoint: POST https://api.elevenlabs.io/v1/sound-generation
Auth: Bearer token from ELEVENLABS_API_KEY env var

Response is SYNC -- returns MP3 bytes directly in 200 body (no async polling like Replicate)

Request parameters (from OpenAPI spec):
  text              string   REQUIRED   The prompt that becomes a sound effect
  model_id          string            "eleven_text_to_sound_v2" (only model currently)
  duration_seconds  number/null       Auto-pick if null; range 0.5 - 30s
  prompt_influence  number/null       0.3 default; range 0-1. Higher = more prompt-adherent, less variation
  loop              boolean           false default; only for v2 model

Example request:
  POST /v1/sound-generation
  { "text": "Thunder rumbling in distance", "duration_seconds": 5 }


## Official Python SDK -- eleve labs (exists and is mature)

Package: elevenlabs on PyPI
Latest version: 2.53.0
Homepage: github.com/elevenlabs/elevenlabs-python
Summary: Full-featured official SDK with typed clients, streaming, async support

Sound generation via SDK:
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="YOUR_KEY")
audio = client.text_to_sound_effects.convert(
    text="Thunder rumbling in distance",
    duration_seconds=5,
)
# audio is bytes -- write to file directly
```

The SDK handles:
  - Auth (Bearer token in headers)
  - Request/response serialization
  - Retry logic and timeouts
  - Async variant: AsyncElevenLabs
  - Streaming support for TTS (probably not relevant for sound gen)

## Architectural Decision Points

### Option A: Direct HTTP calls from Bun (mirror art-gen style)
  Pro: Consistent with existing art-gen codebase (TypeScript/Bun, no extra deps)
  Pro: No Python venv to manage
  Con: ElevenLabs is sync (no polling needed), so replicate-client.ts pattern is overkill
  Con: Would need to handle MP3 binary response differently than Replicate URL-based output

### Option B: Use elevenlabs Python SDK (recommended if art-gen were Python)
  Pro: Full SDK with auth, retries, typed models, future-proof against API changes
  Pro: pip install elevenlabs -- one line dependency
  Con: art-gen is TypeScript/Bun, not Python -- creates tech stack mismatch

### Recommendation for Option A (staying consistent with art-gen)

Since art-gen uses Bun/TypeScript, sound-gen should too. But the client is simpler:
just ONE function instead of three (no polling needed):

```typescript
// elevenlabs-client.ts (roughly 25 lines total)
export async function generateSound(
    text: string,
    options: { duration_seconds?: number; prompt_influence?: number; loop?: boolean },
    fetchFn = globalThis.fetch
): Promise<Buffer> {
    const response = await fetchFn('https://api.elevenlabs.io/v1/sound-generation', {
        method: 'POST',
        headers: {
            'xi-api-key': process.env.ELEVENLABS_API_KEY, // ElevenLabs uses xi-api-key header
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text, ...options })
    });
    if (!response.ok) throw new Error(`ElevenLabs error: ${response.status}`);
    return Buffer.from(await response.arrayBuffer());
}
```

## What needs to be built (file inventory)

NEW files:
  src/elevenlabs-client.ts         -- Single POST call, returns Buffer (25-30 lines)
  src/generate-sound.ts            -- CLI entry point mirroring generate-image.ts (~100 lines)
  reference/sound-models.md        -- Model catalog (just one for now: eleven_text_to_sound_v2)
  docs/reference/ELEVENLABS_API.md -- API docs, pricing, limits

MODIFY existing:
  .claude-plugin/plugin.json       -- Add sound-gen tools to manifest
  package.json                     -- No new deps needed (uses built-in fetch)
  README.md                        -- Update description/features
  commands/                        -- Add sound-gen command(s)
  skills/                          -- Optionally add generate-sound skill

## Pricing (ElevenLabs)
Free tier: Limited credits for testing
Starter ($4/mo): Shared credit pool with TTS
Creator ($22/mo): More credits, higher limits
Sound gen draws from same credit pool as text-to-speech

## Estimated effort
1-2 hours of coding if cloning art-gen structure. The sync API makes it simpler than art-gen
(no polling state machine). Main work is adapting the CLI flag parsing and file saving pattern.
