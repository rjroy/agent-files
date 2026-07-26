# Music Engine of Rowan

<img src="assets/logo.png" width="160" align="right" alt="Music Engine of Rowan">

A Claude Code plugin for songwriting and media generation targeting Suno AI. Produces lyrics, production design, cover art, and video hooks through a multi-agent pipeline with verbalized sampling at every creative stage.

## Commands

| Command | What it does |
|---------|--------------|
| `/music-engine-rowan:write-lyrics` | Full two-phase songwriting pipeline: concept → lyrics → production → review → Suno-formatted output |
| `/music-engine-rowan:get-image-prompt` | Generates k=3 image prompt samples for cover art, with theme-specific art style guidance |
| `/music-engine-rowan:get-video-prompt` | Generates k=3 motion prompt samples for animating a static image into a video hook |

## Songwriting Pipeline

`/write-lyrics` orchestrates eight agents in sequence:

```
Phase 1 (you + user)
  Concept Development → k=5 concepts → user selects → save concept-approved.md

Phase 2 (sub-agents)
  lyric-writer       → k=5 lyric approaches → sampling-curator → lyrics selected
  production-designer → k=5 production designs → sampling-curator → production selected
  song-reviewer      → fresh-eyes quality check → user approves fixes
  suno-formatter     → copy-paste ready Suno Custom Mode output

Optional
  cover-art-generator → image prompts via get-image-prompt → art-gen → final image
  hook-art-generator  → video prompts via get-video-prompt → art-gen → final video
  studio-prep         → per-segment style entries for Suno's studio editor
```

Each creative stage uses verbalized sampling: agents generate k=5 genuinely distinct approaches (not variations), then the `sampling-curator` auto-recommends and lets you select before the next stage runs. The song reviewer enters with no prior context from the creative process, which catches issues the creative agents missed while too close to the work.

## Themed Universes

Eight fictional worlds with distinct musical and visual identities:

| Theme | Sound | Setting |
|-------|-------|---------|
| **Telveran** | Haunting folk, memory-themed ballads | Reality shifts with collective memory |
| **Valdris** | Dark ambient, gothic rock | Ancient souls and spectral guardians |
| **Virelan** | Industrial folk, brass-heavy | Sacred steampunk, divine judgment through machinery |
| **Brightvale** | Theatrical pop, cabaret | Performance realm, authentic souls hiding behind facades |
| **Hope's Reach** | Ambient electronic, cosmic folk | Deep space vessel carrying humanity's musical heritage |
| **Trap Streets** | Urban folk, street poetry | Hidden pocket dimensions for the unwelcome |
| **Shattered Worlds** | Post-rock, ambient decay | Apocalyptic exploration of the mundane |
| **Insert Name** | Synthwave, introspective beats | Cyber world, personal development |

Themes are optional. Songs without a theme use universal concepts directly.

## Lens Transformations

Lenses reframe any theme (or no theme) into a different emotional register:

- **Work Empowerment** — High-energy motivational anthems for career and productivity
- **Epic** — Hero's journey structure for grand, transformational narratives
- **Lo-fi** — Warm, steady, background-compatible music for study or relaxation
- **Comedy** — Satirical and humorous takes on any subject
- **Universal Resonance** — Broad human experiences and timeless emotions

Combine freely: Epic + Telveran, Lo-fi + Hope's Reach, Comedy + Virelan.

## MIDI Lyric Analysis

If you have a MIDI file, the `midi-lyric-analyzer` skill extracts melodic motifs, phrase lengths, syllable counts, and stress patterns before writing begins. The resulting Lyrical Blueprint becomes a binding constraint for all five lyric samples, ensuring lyrics fit the melody naturally rather than fighting it.

Invoke from within the `/write-lyrics` flow when asked about MIDI sources.

## Skills

| Skill | Role |
|-------|------|
| `music-engine-reference` | Reference library: all theme files, lens files, theory modules, image guidance, video guidance. Loaded by commands, not interacted with directly. |
| `midi-lyric-analyzer` | Analyzes MIDI files and generates a Lyrical Blueprint for syllable-accurate lyric writing. |

## Output Files

Songs are saved to `song-[title-slug]-[YYYYMMDD]/concept-approved.md` in your working directory, with phase metadata tracking progress through the pipeline. Samples files (`lyrics-samples.md`, `production-samples.md`) are created and then deleted by the curator after selection.

Image and video prompt samples are written to the current directory as `image-prompt-samples-[concept-slug]-[date].md` and `video-prompt-samples-[concept-slug]-[date].md`.

## Dependencies

Cover art and video generation require the `art-gen-mcp` plugin, which provides `generate_image_replicate` and `generate_video_replicate` tools.
