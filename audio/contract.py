"""Stable PCM contract shared by desktop and web audio transports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int
    channels: int = 1
    sample_width_bytes: int = 2  # PCM16


AUDIO_INPUT = AudioFormat(sample_rate=16_000)
AUDIO_OUTPUT = AudioFormat(sample_rate=24_000)
INPUT_CHUNK_SAMPLES = 1024
