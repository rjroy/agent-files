# Suno 5.0 Technical Formatting

## Core Requirements

**ALWAYS use Custom Mode** with three separate fields:
- **Lyrics Field:** All vocal content, structure, and performance cues
- **Style Field:** Musical blueprint, instrumentation, tempo, atmosphere
- **Excluded Styles:** Genres that break thematic atmosphere

## Lyrics Field Formatting

### Structure Headers
Use markdown headers on their own lines:
```
## Verse 1
Content here

## Chorus
More content

### Pre-Chorus
Subsection content
```

### Performance Tags - Single Narrative Philosophy
Use **single narrative descriptions** that combine multiple elements into flowing instructions:

```
[Acoustic guitar with soft string accompaniment]
[Whispered delivery with intimate reverb]
[Full orchestra with epic grandeur]
```

**Why Single Narrative Tags:**
- Each bracket creates a separate musical moment/pause in Suno
- Multiple tags cause processing gaps and extended intros
- Narrative format provides clearer direction than fragmented multi-tags
- Creates cohesive musical instructions Suno can process smoothly

**Examples:**
```
✗ [Heavy Guitars][Driving Drums][Rebellion] ← Creates gaps between elements
✓ [Heavy guitars with driving drums and rebellious energy] ← Single cohesive moment

✗ [Psychedelic][Floating][Atmosphere] ← Multiple pauses
✓ [Psychedelic floating atmosphere with dreamy textures] ← Single moment

✗ [Cold][Digital][Processing] ← Choppy
✓ [Cold digital processing with robotic precision] ← Narrative flow
```

### Voice Style Instructions
Voice/vocal processing using double brackets:
```
[[Warm analog voice]]
Lyrical content here

[[Bronze resonance vocals]]
More lyrics here
```

**Note:** The `(Voice style):` format from Suno 4.5 no longer works reliably. Use `[[voice style]]` instead.

### Parentheses Warning
In Suno 5.0, `(words)` behavior is inconsistent - sometimes read as lyrics, sometimes as style/processing. For reliable results:
- Use `[[voice style]]` for voice processing (not `(voice):`)
- Use `call // response` for call-and-response (not multi-line with parentheses)
- Only use `(repeated phrase)` for emphasis echoes where inconsistency is acceptable

## Style Field Blueprint

### Top-Anchor Approach
Suno V5 gives more weight to what appears first in the style field. **Front-load your most important creative intent** to lock in the style before the model processes the rest.

**Anchor with vocal character first, then genre, then instrumentation:**
```
Female vocalist, breathy and intimate, 90s R&B groove at 85 BPM. Opens with...
```

**What to include in the anchor (first 20-30 words):**
- Voice type and texture (female, raspy, warm, airy)
- Core mood (intimate, anthemic, wistful, defiant)
- Genre and era (90s R&B, folk-rock, 80s synthwave)
- BPM

**Why this works:** V5 responds best to "crisp, directive language" and tags are most impactful in the first 20-30 words. By anchoring your core sound at the start, subsequent instrumentation and arrangement details build on a solid foundation.

### Template Format
```
[Vocal character], [mood], [genre] at [BPM]. Opens with [instrumentation], [development through middle], [climactic resolution]. [Atmosphere]. [Emotional metaphor].
```

### Example
```
Female vocals with warm intimacy, wistful and yearning, folk ballad at 85 BPM. Opens with fingerpicked acoustic guitar, adding warm string section at verse 2, building to full folk arrangement with layered harmonies and church reverb at final chorus. Progression feels like personal confession becoming universal truth.
```

### Style Field: Order = Priority

**Maximum: 1,000 characters.** Detail is rewarded when purposeful.

In Suno 5.0, the order of elements in your style field indicates **priority** (what matters most), not timeline. The Top-Anchor approach puts your most important creative decisions first. Timeline information (when things change) comes after.

**Focus detail on:**
- Vocal character and how it evolves through the song
- Key arrangement transitions (when instruments enter/exit)
- Moments where the song's emotional arc shifts
- Genre blending and how styles interact

**Avoid filler phrases** that don't guide specific musical choices (e.g., "with professional production quality", "maintaining energy throughout").

**Structure your style field:**
1. **Anchor:** Vocal character + mood + genre + BPM + emotional metaphor
2. **Timeline:** When instruments/styles enter, exit, or transform
3. **Key moments:** Where cracks, shifts, or blends occur

**Integration Example:**
```
Female vocals with practiced warmth which transitions to emotional understanding. Polished Christmas electropop at 98 BPM intermixed with traditional acoustic carol music. Progression feels like watching a professional mask shatter mid-performance. Opens with synth pads, programmed sleigh bells, modern pop drums. Verse 2 introduces acoustic guitar. Then strings are added. Pre-chorus synth layers lightly mixed with acoustic instruments. Chorus has stadium-ready pop with layered harmonies, but the lead will crack at points. Bridge strips to solo piano and raw breaking vocals. Final chorus blends both electropop and acoustic carol music.
```

## Tempo Guidelines

### Standard: Single BPM
Most songs maintain consistent tempo:
```
"Folk ballad at 85 BPM with steady contemplative energy"
"Rock anthem at 135 BPM maintaining driving pace throughout"
```

### BPM Ranges
- **20-60 BPM:** Ambient, meditation, ballads
- **60-80 BPM:** Emotional ballads, laid-back hip-hop
- **80-120 BPM:** Pop, rock, country
- **120-160 BPM:** Dance, punk, energetic
- **160+ BPM:** Electronic, extreme genres

### Exceptional Tempo Changes
Only when narratively justified:
```
"Virelan clockwork starting at 100 BPM, mechanically winding down to 70 BPM as music box loses power"
```

**Use arrangement building instead of tempo escalation for musical progression.**

## Echo System

Use purposefully, not habitually. Most lines should have NO echo.

### Three Types

**Emphasis:** `(repeated phrase)`
```
The power will grow until the end (until the end)
```

**Call-and-Response:** `call // response`
```
Our love will always grow // Forever will I love
The battle cry rings out // We stand as one!
```

**Fragmented/Glitch:** `word // other word`
```
Gears go click // but data flows
Crown corrupts // while server grows
```

**Note:** The multi-line call-and-response format from Suno 4.5 no longer works reliably. Use `//` on a single line instead.

## Field Coordination

### Style Field Schedules Everything
List every instrument that appears anywhere in the song with timeline.

### Lyrics Field Triggers Scheduled Elements
`[Tags]` reference elements already planned in style field.

### Example Coordination

**Style Field:**
```
Folk ballad at 85 BPM maintaining steady energy. Solo acoustic guitar foundation, adding strings at verse 2, full folk arrangement with harmonies at final chorus.
```

**Lyrics Field:**
```
## Verse 1
[Solo acoustic guitar with contemplative pulse]
Opening lyrics...

## Verse 2
[Acoustic guitar with string section building emotion]
Building narrative...

## Final Chorus
[Full folk arrangement with layered harmonies]
Climactic resolution...
```

## Excluded Styles Field

Format as comma-separated list in code block:
```
Heavy metal, EDM, country, jazz fusion, dubstep, industrial techno, death metal, polka, disco, trap music, modern pop, electronic dance
```

Customize for each theme to prevent atmosphere-breaking genres.

## Quality Checkpoints

### Before Generating:
- ✓ Custom Mode with separated fields
- ✓ Style field uses Top-Anchor (vocal + mood + genre first)
- ✓ Single narrative tags (no multiple brackets)
- ✓ Voice styles use `[[voice style]]` format
- ✓ Call-and-response uses `call // response` format
- ✓ Style field schedules all instruments used in lyrics
- ✓ Single BPM unless narratively justified
- ✓ Echo usage is purposeful and minimal

### Success Indicators:
- No extended intros or gaps between sections
- Vocal entry happens as planned
- Arrangement follows timeline
- Clean field separation maintained
- tempo consistency

## Quick Fix Reference

**Top-Anchor:** Start style field with vocal + mood + genre + BPM
**Structure Headers:** Keep clean, no mixed content
**Performance Tags:** Single narrative descriptions only
**Voice Styles:** Use `[[voice style]]` format
**Call-and-Response:** Use `call // response` on single line
**Tempo:** Single BPM as default, justified changes only
**Coordination:** Style field plans, lyrics field triggers

Remember: These rules maximize Suno 5.0's capabilities. Single narrative tags eliminate processing gaps, `[[voice style]]` provides reliable voice processing, `//` format handles call-and-response correctly, consistent tempo provides musical stability, and proper field coordination ensures your vision translates accurately.