"""Provider-neutral audio contracts.

The existing Mark-LIII PCM16 audio path remains the reference transport:
16 kHz mono PCM input, 24 kHz mono PCM output, with 1024-sample input chunks.
The web UI already uses the same 16 kHz PCM transport, so provider work must
not change the browser audio contract.
"""

from .contract import AudioFormat, AUDIO_INPUT, AUDIO_OUTPUT, INPUT_CHUNK_SAMPLES

__all__ = ["AudioFormat", "AUDIO_INPUT", "AUDIO_OUTPUT", "INPUT_CHUNK_SAMPLES"]
