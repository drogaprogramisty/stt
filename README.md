# stt - fast speech-to-text CLI for Apple Silicon 

> [!NOTE]  
> Also: Optimised for agentic usage with Claude Code, Codex, Open Code and more!

# Supported languages
English, and:
Bulgarian, Croatian, Czech, Danish, Dutch, Estonian, Finnish, French, German, Greek, Hungarian, Italian, Latvian, Lithuanian, Maltese, Polish, Portuguese, Romanian, Slovak, Slovenian, Spanish, Swedish, Russian, Ukrainian

# Speed

| Benchmark | Audio Total Duration | Processing Time | Speed Ratio |
|-----------|----------------|-----------------|-------------|
| First run (model load) | any | longer, 1.2GB to download | - |
| Single file (long) | 10m 39s | 8.19s | **78x real-time** |
| Single file (short) | 25s | 3.55s | **7x real-time** |
| Batch 100x (short) | 41m 40s | 19.79s | **126x real-time** |

**Notes:**
- Tested on Macbook Pro M4 Max, 128GB RAM

## Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.9+
- ffmpeg (`brew install ffmpeg`)

## Installation

```bash
pip install git+https://github.com/drogaprogramisty/stt

# or with uv
uv tool install git+https://github.com/drogaprogramisty/stt
```

## Output Formats

`txt` (default), `srt`, `vtt`, `json` (with timestamps)

## CLAUDE.md / AGENTS.md

Example plug-and-play .md paragraph so your favorite agent can use this amazing tool:

```markdown
## stt - Speech to Text

Transcribe audio/video files to text. Supports wav, mp3, m4a, mp4, etc.

stt audio.mp3                    # Creates audio.txt
stt video.mp4 -f srt             # Creates video.srt (subtitles)
stt recording.m4a -f json        # Creates recording.json (with timestamps)
stt *.wav -o transcripts/        # Batch process to directory
stt podcast.mp3 -o out.txt       # Custom output path
stt interview.m4a -f vtt -q      # Quiet mode, only prints output path (CLI usage)
stt -h                           # for help / all options
```
