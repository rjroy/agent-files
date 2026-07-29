# Music Engine Reference

Repository of reference materials for the Suno AI 5.0 songwriting system. This skill provides access to themed universes, lens transformations, theory modules, and image generation guidance for the music-engine-rowan plugin.

## Purpose

This skill serves as the reference library for music creation commands and workflows. When invoked, it makes available all theme files, theory modules, lens transformations, and supporting materials needed for the two-phase songwriting system.

## When to Invoke

This skill should be invoked by music engine commands (like `/write-lyrics`) to access reference materials. It is NOT intended for direct user interaction but rather as a resource repository that other commands can utilize.

Commands should invoke this skill using:
```
Skill tool with command: "music-engine-rowan:music-engine-reference"
```

## Available Reference Materials

### Core System Architecture

**`music/base.md`** - Master system architecture and two-phase workflow
- Unified Suno 5.0 songwriting system
- Two-phase creation workflow (Concept Development → Song Execution)
- Core requirements and quality standards
- Quick start commands and error prevention

### Theory Modules (Load Contextually During Workflow)

**`music/theory/theory-story-and-representation.md`**
- Story development frameworks
- Character authenticity guidelines
- Cultural sensitivity and representation
- Load during: Phase 1 (Concept Development)

**`music/theory/theory-lyrical-craft.md`**
- Classical poetic patterns and meter
- Natural speech method
- Cross-genre techniques
- Echo system implementation
- Load during: Phase 2A (Lyrical Craft)

**`music/theory/theory-production-atmosphere.md`**
- Blueprint Method timeline design
- Atmospheric coordination
- Progressive complexity staging
- Transition logic
- Load during: Phase 2B (Production Design)

**`music/theory/theory-suno-formatting.md`**
- Custom Mode field separation rules
- Bracket/parentheses formatting
- BPM tempo markings (no Italian terms)
- Timeline coordination
- Load during: Phase 2C (Technical Implementation)

**`music/theory/theory-genre-reference.md`**
- Comprehensive genre, style, and structural tag reference
- 300+ genres organized by category and alphabetically
- Style descriptors for modifying genre feel
- Structural tags for song sections
- Load during: Phase 2B (Production Design) or Genre exploration

### Themed Universes

**`music/themes/theme-telveran.md`**
- Memory-shifting folk realm where reality bends to collective memory
- Musical signature: Haunting folk, mystical acoustic, memory-themed ballads

**`music/themes/theme-valdris.md`**
- Gothic mystical realm of ancient souls and spectral guardians
- Musical signature: Dark ambient, gothic rock, ethereal mysticism

**`music/themes/theme-virelan.md`**
- Sacred steampunk world of divine judgment through machinery
- Musical signature: Industrial folk, mechanical rhythms, brass-heavy arrangements

**`music/themes/theme-brightvale.md`**
- Performance realm where survival depends on authentic souls hiding beneath glittering facades
- Musical signature: Theatrical pop, cabaret, dramatic performance styles

**`music/themes/theme-hope_s-reach.md`**
- Deep space vessel carrying humanity's musical heritage between stars
- Musical signature: Ambient electronic, space-themed synthwave, cosmic folk

**`music/themes/theme-the-trap-streets.md`**
- Hidden pocket dimensions for the unwelcome, built from raw authenticity
- Musical signature: Urban folk, street poetry, underground sounds

**`music/themes/theme-shattered-worlds.md`**
- Apocalyptic exploration of the meaning of the mundane
- Musical signature: Post-rock, ambient decay, reflective soundscapes

**`music/themes/theme-insert-name.md`**
- Cyber world exploration of personal development
- Musical signature: Synthwave, electronic, introspective beats

**`music/themes/instrument-bank.md`**
- Comprehensive instrument reference for production design
- Organized by category (strings, brass, percussion, etc.)

### Cross-Universe Lens Transformations

**`music/lens/lens-work-empowerment.md`**
- Transform any universe into high-energy motivational anthems
- Apply to: Career growth, productivity, professional development themes

**`music/lens/lens-epic.md`**
- Apply legendary storytelling structure to any universe for grand narratives
- Apply to: Hero's journey, transformation arcs, momentous achievements

**`music/lens/lens-lo-fi.md`**
- Convert any universe into warm, steady, background-compatible music
- Apply to: Study music, relaxation, ambient listening

**`music/lens/lens-comedy.md`**
- Comedy transformation for any universe
- Apply to: Satirical, humorous, or lighthearted storytelling

**`music/lens/lens-universal-resonance.md`**
- Universal resonance transformation across themes
- Apply to: Broad human experiences, timeless emotions

### Framework Extensions

**`music/framework/framework-saga.md`**
- Extended framework for saga-style multi-song narratives
- Multi-chapter storytelling structures
- Character development across songs

### Songwriter Personas

**`music/songwriters/songwriter-lyra.md`**
- Songwriter persona reference
- Creative voice and approach guidelines
- Style characteristics

### Image Generation Resources

**`images/base.md`**
- Core image generation guidance for song cover art
- Integration with art-gen MCP
- Prompt construction guidelines

**`images/Suno Theme Art Styles Guide.md`**
- Visual style guidelines for each themed universe
- Art direction for cover art generation
- Thematic visual elements

### Video Generation Resources

**`video/video-prompting-guide.md`**
- Best practices for AI video generation prompts
- Image-to-video workflow guidance
- Camera movement terminology and techniques
- Model-specific notes (Minimax, Kling, PixVerse, WAN)
- Motion prompt construction guidelines

## File Organization

```
music-engine-reference/
├── music/
│   ├── base.md                    # Core system architecture
│   ├── theory/                    # Theory modules
│   │   ├── theory-story-and-representation.md
│   │   ├── theory-lyrical-craft.md
│   │   ├── theory-production-atmosphere.md
│   │   ├── theory-suno-formatting.md
│   │   └── theory-genre-reference.md
│   ├── themes/                    # Themed universes
│   │   ├── theme-telveran.md
│   │   ├── theme-valdris.md
│   │   ├── theme-virelan.md
│   │   ├── theme-brightvale.md
│   │   ├── theme-hope_s-reach.md
│   │   ├── theme-the-trap-streets.md
│   │   ├── theme-shattered-worlds.md
│   │   ├── theme-insert-name.md
│   │   └── instrument-bank.md
│   ├── lens/                      # Lens transformations
│   │   ├── lens-work-empowerment.md
│   │   ├── lens-epic.md
│   │   ├── lens-lo-fi.md
│   │   ├── lens-comedy.md
│   │   └── lens-universal-resonance.md
│   ├── framework/                 # Extended frameworks
│   │   └── framework-saga.md
│   └── songwriters/               # Songwriter personas
│       └── songwriter-lyra.md
├── images/                        # Image generation
│   ├── base.md
│   └── Suno Theme Art Styles Guide.md
└── video/                         # Video generation
    └── video-prompting-guide.md
```

## Usage Pattern

When a command like `/write-lyrics` is invoked:

1. **Command invokes this skill** to load it into context
2. **Command accesses reference files** from this skill's directory
3. **Theory modules loaded contextually** during the two-phase workflow:
   - Phase 1: Load base.md + theme/lens + story theory
   - Phase 2A: Load lyrical craft theory
   - Phase 2B: Load production atmosphere theory
   - Phase 2C: Load formatting theory
4. **Drop previous modules** when moving to next step

## Integration with Commands

Commands should reference files using relative paths from this skill directory:

```markdown
Load the master system:
- Read `music/base.md` from music-engine-reference skill

Load theme files:
- Read `music/themes/theme-telveran.md` from music-engine-reference skill

Load theory modules:
- Read `music/theory/theory-lyrical-craft.md` from music-engine-reference skill
```

## Maintenance Notes

- All reference materials are stored within this skill directory
- Files use markdown format with descriptive frontmatter where applicable
- Theory modules are designed for contextual loading (not all at once)
- Themed universes maintain consistent structure (world, musical signature, visual identity)
- Lens transformations are universe-agnostic and can be applied to any theme

## External Resources

- **art-gen MCP**: Used by cover-art-generator agent for image generation

---

This skill is a passive reference library. It should be invoked by commands to access materials, not presented directly to users. Commands handle user interaction and workflow orchestration.
