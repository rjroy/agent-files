# Initialize art-gen-mcp

Run this command to install dependencies for the art-gen-mcp scripts.

## Instructions

Resolve `..` from this command source directory, which is adjacent to the art-gen installation root.

```bash
cd .. && bun install
```

## Prerequisites

- **bun** is required. Install from https://bun.sh if not present.
- Run `bun --version` to verify installation.

## Verification

After installation, verify bun can find the scripts:

```bash
bun ../src/generate-image.ts --help 2>&1 || echo "Ready"
```
