# Configuration Guide

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
with `bun install`. The generation skill resolves model catalogs and scripts
relative to its own canonical skill directory; it does not depend on the
process working directory, a provider-specific plugin root, or MCP client configuration.

Generation scripts require `REPLICATE_API_TOKEN` in the environment. Do not
put a live token in source control or in a skill prompt. Image, edit, and
background-removal requests use the selected script and model; video
generation can incur charges and requires user confirmation before execution.

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
