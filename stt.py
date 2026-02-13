#!/usr/bin/env python3
"""Speech-to-text CLI tool."""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path
from typing import Any

from huggingface_hub import try_to_load_from_cache
from parakeet_mlx import from_pretrained

MODEL_ID = "mlx-community/parakeet-tdt-0.6b-v3"


def is_model_cached() -> bool:
    """Check if model is already downloaded."""
    result = try_to_load_from_cache(MODEL_ID, "config.json")
    return isinstance(result, str) and Path(result).exists()

EXTENSION_MAP = {
    "txt": ".txt",
    "srt": ".srt",
    "vtt": ".vtt",
    "json": ".json",
}


def expand_paths(patterns: list[str]) -> list[Path]:
    """Expand glob patterns and return list of file paths."""
    paths = []
    for pattern in patterns:
        if any(c in pattern for c in "*?["):
            expanded = glob.glob(pattern)
            paths.extend(Path(p).resolve() for p in sorted(expanded))
        else:
            paths.append(Path(pattern).resolve())
    return paths


def get_unique_output_path(base_path: Path) -> Path:
    """Return a unique path by adding numeric suffix if file exists."""
    if not base_path.exists():
        return base_path

    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}-{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def get_output_path(input_path: Path, output: str | None, fmt: str) -> Path:
    """Determine the output file path."""
    ext = EXTENSION_MAP.get(fmt, ".txt")

    if output:
        output_path = Path(output)
        if output_path.is_dir():
            output_path = output_path / f"{input_path.stem}{ext}"
    else:
        output_path = input_path.parent / f"{input_path.stem}{ext}"

    return get_unique_output_path(output_path)


def transcribe(input_path: Path, output_path: Path, fmt: str, quiet: bool, model: Any) -> bool:
    """Run transcription using parakeet-mlx."""
    try:
        if not quiet:
            print(f"Processing {input_path.name}...", file=sys.stderr)

        result = model.transcribe(str(input_path))
    except Exception as e:
        if not quiet:
            print(f"Error: Transcription failed for {input_path.name}: {e}", file=sys.stderr)
        return False

    content = format_output(result, fmt)
    output_path.write_text(content)
    print(output_path)
    return True


def format_output(result: Any, fmt: str) -> str:
    """Format transcription result based on output format."""
    if fmt == "txt":
        return result.text

    if fmt == "json":
        import json
        return json.dumps({
            "text": result.text,
            "sentences": [
                {"text": s.text, "start": s.start, "end": s.end}
                for s in result.sentences
            ]
        }, indent=2, ensure_ascii=False)

    if fmt in ("srt", "vtt"):
        lines = []
        if fmt == "vtt":
            lines.append("WEBVTT\n")

        for i, sentence in enumerate(result.sentences, 1):
            start = format_timestamp(sentence.start, fmt)
            end = format_timestamp(sentence.end, fmt)
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(sentence.text)
            lines.append("")

        return "\n".join(lines)

    return result.text


def format_timestamp(seconds: float, fmt: str) -> str:
    """Format seconds to SRT/VTT timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    if fmt == "srt":
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    else:  # vtt
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio to text",
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="Path(s) to audio file(s), supports glob patterns (e.g., *.mp3)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output path (file for single input, directory for multiple)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "srt", "vtt", "json"],
        default="txt",
        help="Output format (default: txt)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except the output file path",
    )

    args = parser.parse_args()

    input_paths = expand_paths(args.input)

    if not input_paths:
        if not args.quiet:
            print("Error: No matching files found", file=sys.stderr)
        sys.exit(1)

    # Validate all input files exist
    missing = [p for p in input_paths if not p.exists()]
    if missing:
        if not args.quiet:
            for p in missing:
                print(f"Error: Input file not found: {p}", file=sys.stderr)
        sys.exit(1)

    # For multiple files, output must be a directory (or not specified)
    if len(input_paths) > 1 and args.output and not Path(args.output).is_dir():
        if not args.quiet:
            print("Error: Output must be a directory when processing multiple files", file=sys.stderr)
        sys.exit(1)

    # Load model once for batch processing
    if not args.quiet and not is_model_cached():
        print(f"Model not found locally. Downloading {MODEL_ID}...", file=sys.stderr)
    model = from_pretrained(MODEL_ID)

    success = True
    for input_path in input_paths:
        output_path = get_output_path(input_path, args.output, args.format)
        if not transcribe(input_path, output_path, args.format, args.quiet, model):
            success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
