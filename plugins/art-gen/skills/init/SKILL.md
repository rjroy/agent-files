---
name: init
description: Install dependencies for the art-gen scripts. Requires bun.
---

# Initialize art-gen-mcp

Run this command to install dependencies for the art-gen-mcp scripts.

## Instructions

```bash
cd ${PLUGIN_ROOT} && bun install
```

## Prerequisites

- **bun** is required. Install from https://bun.sh if not present.
- Run `bun --version` to verify installation.

## Verification

After installation, verify bun can find the scripts:

```bash
bun ${PLUGIN_ROOT}/src/generate-image.ts --help 2>&1 || echo "Ready"
```
