# ⚙️ JARVIS-LIII — Provider-Agnostic WUI Fork

This repository is a personal, non-commercial fork of [FatihMakes/Mark-LIII](https://github.com/FatihMakes/Mark-LIII).

The original Mark-LIII functionality remains the reference implementation for JARVIS's agent, tools, memory, desktop control and realtime audio behavior. This fork is being evolved toward a provider-agnostic JARVIS architecture with a first-class Web UI.

## Current architecture work

### Provider-neutral LLM layer

`providers/` defines a small vendor-neutral contract so the JARVIS core does not need to know which LLM vendor is active.

The first concrete adapter is `OpenAICompatibleProvider`, which can target compatible gateways such as OpenRouter, OpenAI-compatible local servers, vLLM, LM Studio, llama.cpp servers and compatible hosted providers.

Example configurations are in `config/providers.example.json`.

### Audio is a stable contract

The Web UI audio path is **not being replaced**. The existing Mark-LIII remote dashboard already captures microphone audio as mono PCM16 at 16 kHz and sends it in 1024-sample chunks to `/ws/phone-audio`. The new architecture treats that transport as a compatibility contract rather than tying it to a specific LLM vendor.

The original desktop audio path remains untouched while the provider layer is extracted. Realtime audio providers will be added as separate adapters, allowing Gemini Live to remain available without making Gemini a requirement for every LLM task.

Reference constants:

- input: 16 kHz / mono / PCM16
- output: 24 kHz / mono / PCM16
- input chunk: 1024 samples

### Target architecture

```text
                         JARVIS WUI
                    chat + HUD + microphone
                              │
                         WebSocket/API
                              │
                       ┌──────▼──────┐
                       │ JARVIS Core │
                       │ agent/tools │
                       │ memory/etc. │
                       └──────┬──────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
          LLM layer       Voice layer      Vision layer
             │                │                │
       ┌─────┼─────┐     ┌────┼────┐           │
     Gemini OpenAI Ollama  STT TTS Realtime    ...
       OpenRouter / custom
```

The important design rule is that **LLM, STT, TTS and realtime voice are separate capabilities**. A future configuration can therefore use a cloud LLM with local speech recognition, a local LLM with cloud TTS, or a dedicated realtime provider.

## Original Mark-LIII capabilities

Mark-LIII remains the functional baseline: wake word, realtime voice, audio device selection, reactive HUD, memory, plugins/actions, vision, desktop/system control, remote dashboard and the other capabilities documented below from the upstream project.

[Original project](https://github.com/FatihMakes/Mark-LIII)

## License

The upstream project is licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. This fork preserves the upstream attribution and is intended for personal, non-commercial use. Commercial redistribution or commercial use requires the appropriate permission from the copyright holder.

---

## Upstream documentation

# ⚙️ MARK LIII (53)
### The Ultimate Cross-Platform Personal AI Assistant — By FatihMakes

A real-time voice AI that can hear, see, understand, and control your computer — on any OS. Supports Windows, macOS, and Linux. Built on the Gemini Live API for native audio streaming.

## ✨ Overview

MARK LIII is the hands-free & scalable release. Say **"Hey Jarvis"** and it wakes; stay quiet and it slips back to sleep on its own. Every skill — bundled or drop-in — describes itself in its own file, so adding a tool is a one-file operation and the core stays lean.

## 🚀 Capabilities

| Feature | Description |
|---|---|
| 🎙️ Wake Word | Local **"Hey Jarvis"** detection with automatic sleep/wake |
| ⚡ Instant Acknowledgment | Immediate short acknowledgement for longer tasks |
| 🧩 Self-Describing Skills | Auto-discovered actions and plugins |
| 🧠 Recallable Memory | Persistent searchable memory |
| 👁️ Memory Panel | Inspect and manage stored facts |
| ↩️ Undo | Reverse supported assistant actions |
| 🎧 Audio Device Picker | Select microphone and speakers |
| 🔗 Session Continuity | Preserve conversation state across reconnects |
| 🧩 Plugin System | Drop-in Python plugins |
| 🎙️ Real-time Voice | Low-latency voice conversation |
| 🎨 Live Theming | Runtime HUD customization |
| 〰️ Reactive HUD | Audio-reactive waveform and reactor |
| 🎙️ Voice Picker | Multiple native voices |
| ♾️ Unlimited Sessions | Long-running conversations |
| 🖥️ System Control | OS and desktop control |
| 👁️ Visual Awareness | Screen and webcam vision |
| 🧠 Persistent Memory | Cross-session personal context |
| ⌨️ Hybrid Input | Keyboard + voice |
| 🌅 Morning Briefing | Contextual first-boot briefing |
| 🔔 Proactive Monitoring | Background topic monitoring |
| 📊 Hardware Monitoring | CPU/RAM/GPU/temperature telemetry |
| 🌤️ Weather | Live weather reports |
| 🔍 Multi-Mode Web Search | Search/news/research/price/compare |
| ⏰ Smart Reminders | Native OS reminders |
| ✈️ Flight Finder | Flight lookup |
| 🎮 Game Updater | Steam/Epic update support |
| 📂 File Processor | Local file processing |
| 💻 Code Helper | Coding assistance |
| 🌐 Browser Control | Browser automation |
| 📨 Messaging | Messaging integrations |
| 🎬 YouTube Control | YouTube control |
| 🖱️ Desktop Control | Desktop/window automation |
| 📱 Remote Dashboard | Phone control via QR pairing |
| ⚡ Auto-Start | OS startup integration |
| 📋 Clipboard Intelligence | Clipboard assistance |
| 🪪 Assistant Customization | Name/voice/color configuration |
