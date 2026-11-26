# Configuration Guide

For normal OpenAI image creation or editing, use [`generate-image`](../../skills/generate-image/SKILL.md). The settings below apply only to explicitly authorized Replicate scripts, not to OpenCode's built-in image tool or the user's existing Codex login.

## Environment Variables

### REPLICATE_API_TOKEN (Required)

Your Replicate API authentication token.

**How to get it:**
1. Sign up at [replicate.com](https://replicate.com)
2. Navigate to [Account API Tokens](https://replicate.com/account/api-tokens)
3. Create a new token or copy existing one

**Setting the variable:**

```bash
# Linux/macOS
export REPLICATE_API_TOKEN="r8_your_token_here"

# Windows (PowerShell)
$env:REPLICATE_API_TOKEN="r8_your_token_here"

# Or create a .env file
echo "REPLICATE_API_TOKEN=r8_your_token_here" > .env
```

## OpenCode Skill Setup

Use the OpenCode skill loader to discover `generate-image` and
`art-gen-setup`. The setup skill resolves the collection root from its
loader-provided canonical skill directory and installs the Bun dependencies
with `bun install` only when setup is requested. The generation skill resolves
Replicate catalogs and scripts relative to its own canonical skill directory.
Media paths still resolve from the user's project working directory.

Replicate scripts require `REPLICATE_API_TOKEN` in the environment. Do not put a
live token in source control or in a skill prompt. A configured token does not
authorize a Replicate request. Follow `generate-image` for authorization and
execution; video always requires confirmation.

## Troubleshooting

### Script dependencies unavailable
- Use `art-gen-setup` when the user requests dependency setup or repair
- Verify Bun is installed and the setup completed successfully

### API errors
- Verify token is valid at replicate.com
- Check you have sufficient credits
- Review Replicate API status

### Script or reference path issues
- Resolve paths from the canonical directory supplied for the loaded skill
- Do not depend on the process working directory or a client-specific plugin variable
