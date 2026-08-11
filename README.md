# 🤖 Hello Friend

> Local personal AI assistant built with **LangChain + LangGraph**.

Hello Friend is a terminal-based personal AI assistant that can understand natural-language commands, automatically select tools, control browser/desktop applications, perform calculations, and search the web.

It supports **text and voice input** through the same agent pipeline.

---

## ✨ Features

- 🧠 LangChain tool-calling agent
- 🔄 LangGraph agent runtime and conversation state
- 💬 Text interaction
- 🎤 Voice interaction
- 🔑 Text + voice wake phrases
- ⚡ One-line wake + command
- 🗣️ NVIDIA Whisper STT
- 🎧 Automatic speech-end detection
- 🌐 Browser automation
- 🖥️ Desktop application control
- 🧮 Calculator
- 🔎 Web search
- 📰 News search
- 🌤️ Weather search
- ⚽ Sports search
- 🧠 Thread-based conversation memory
- 🔌 Multiple LLM providers

---

## 🔑 Wake Word

Supported wake phrases:

```text
hello friend
friend
````

### Two-step

```text
You: hello friend

Hello Friend: Yes, I'm listening.

You: open youtube
```

### One-line

```text
You: hello friend open youtube
```

or:

```text
You: friend open google
```

The wake detector separates:

```text
Wake phrase → hello friend
Command    → open youtube
```

---

## 🎤 Voice Pipeline

Voice input uses NVIDIA Whisper for speech-to-text.

```text
Microphone
    ↓
Speech / Silence Detection
    ↓
NVIDIA Whisper STT
    ↓
Text Transcript
    ↓
Wake Detector
    ↓
LangGraph Agent
    ↓
Tool
    ↓
Text Response
```

Voice and text ultimately use the **same agent**.

There is currently no voice output; responses are displayed as text.

---

## 🧠 Architecture

```text
                 ┌──────────────┐
                 │ Text Input   │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │ Unified Input│
                 │   Handler    │
                 └──────┬───────┘
                        │
Voice ──► NVIDIA STT ───┘
                        │
                        ▼
                  Wake Detector
                        │
                        ▼
                   AgentRunner
                        │
                     LangGraph
                        │
                    LangChain
                        │
                        ▼
                      Tools
```

---

## 🛠️ Tools

### Math

| Tool         | Purpose                   |
| ------------ | ------------------------- |
| `calculator` | Mathematical calculations |

### Browser

| Tool             | Purpose        |
| ---------------- | -------------- |
| `open_browser`   | Open browser   |
| `open_website`   | Open website   |
| `search_google`  | Google search  |
| `search_youtube` | YouTube search |

### System

| Tool                | Purpose                   |
| ------------------- | ------------------------- |
| `open_application`  | Open desktop application  |
| `close_application` | Close desktop application |

### Web

| Tool              | Purpose                 |
| ----------------- | ----------------------- |
| `web_search`      | General web research    |
| `fetch_webpage`   | Fetch webpage           |
| `extract_content` | Extract webpage content |
| `search_news`     | Search news             |
| `search_weather`  | Search weather          |
| `search_sports`   | Search sports           |

Tools use LangChain's standard:

```python
from langchain.tools import tool
```

There is no custom tool registry.

---

## 🔌 LLM Providers

Select the provider using `.env`:

```env
LLM_PROVIDER=nvidia
```

Supported:

```text
groq
ollama
nvidia
```

### Groq

```env
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

### Ollama

```env
OLLAMA_MODEL=gpt-oss:20b
OLLAMA_BASE_URL=http://localhost:11434
```

### NVIDIA

```env
NVIDIA_API_KEY=
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

---

## 🎙️ Voice Configuration

Example:

```env
INPUT_MODE=both
OUTPUT_MODE=text

STT_PROVIDER=nvidia
STT_MODEL=whisper-large-v3
STT_LANGUAGE=en

NVIDIA_RIVA_SERVER=grpc.nvcf.nvidia.com:443
NVIDIA_STT_FUNCTION_ID=b702f636-f60c-4a3d-a6f4-f3568c13bd7d

SAMPLE_RATE=16000

MIN_RECORD_SECONDS=0.8
MAX_RECORD_SECONDS=30

SILENCE_THRESHOLD=500
SILENCE_DURATION=1.2
START_TIMEOUT=10
```

Voice recording is not limited to a fixed 5-second command.

It records until speech ends, with `MAX_RECORD_SECONDS` acting as a safety limit.

---

## 🧠 Memory

LangGraph maintains conversation state using a `thread_id`.

Example:

```text
You: my name is Alex
You: what is my name?

Hello Friend: Alex
```

Current memory is process-local.

Persistent memory is planned.

---

## 📁 Project Structure

```text
src/
└── hello_friend/
    ├── agent/
    │   ├── graph.py
    │   └── ...
    │
    ├── core/
    │   ├── config.py
    │   ├── logging_setup.py
    │   └── runtime.py
    │
    ├── interface/
    │   ├── text.py
    │   ├── voice.py
    │   ├── unified.py
    │   └── wake.py
    │
    ├── llm/
    │   ├── providers/
    │   │   ├── groq.py
    │   │   ├── ollama.py
    │   │   └── nvidia.py
    │   └── ...
    │
    ├── memory/
    │
    ├── stt/
    │   └── nvidia.py
    │
    └── tools/
        ├── all.py
        ├── math/
        ├── browser/
        ├── system/
        └── web/
```

---

## 📦 Installation

### Create environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install

```bash
pip install -e .
```

Development:

```bash
pip install -e ".[dev]"
```

---

## 🔐 Environment

Create:

```text
.env
```

Example:

```env
APP_NAME=Hello Friend
LOG_LEVEL=INFO

INPUT_MODE=both
OUTPUT_MODE=text

LLM_PROVIDER=nvidia

NVIDIA_API_KEY=your_api_key
NVIDIA_MODEL=meta/llama-3.1-70b-instruct

STT_PROVIDER=nvidia
STT_MODEL=whisper-large-v3
STT_LANGUAGE=en

NVIDIA_RIVA_SERVER=grpc.nvcf.nvidia.com:443
NVIDIA_STT_FUNCTION_ID=b702f636-f60c-4a3d-a6f4-f3568c13bd7d

SAMPLE_RATE=16000
MIN_RECORD_SECONDS=0.8
MAX_RECORD_SECONDS=30
SILENCE_THRESHOLD=500
SILENCE_DURATION=1.2
START_TIMEOUT=10
```

Never commit `.env`.

---

## ▶️ Run

The complete project runs with:

```bash
python -m hello_friend
```

---

## 💬 Example Commands

```text
hello friend open youtube
```

```text
friend open google
```

```text
open calculator
```

```text
what is 25 * 17?
```

```text
search google LangGraph
```

```text
search youtube machine learning
```

```text
what is the weather in London?
```

```text
find today's football scores
```

```text
search the web for LangGraph
```

```text
what is today's AI news?
```

```text
my name is Alex
what is my name?
```

---

## 🧩 Add a Tool

Create a normal LangChain tool:

```python
from langchain.tools import tool

@tool
def example_tool(value: str) -> str:
    """Process a value."""
    return f"Result: {value}"
```

Export it through:

```text
tools/all.py
```

The LangChain agent can then select it automatically.

---

## 🛡️ Safety

Current system tools can open and close applications.

Future capabilities such as:

```text
file deletion
file modification
terminal commands
system configuration
```

should use an approval/policy layer before execution.

Planned flow:

```text
User
 ↓
Agent
 ↓
Tool Request
 ↓
Policy / Approval
 ↓
Execute
```

---

## 🗺️ Roadmap

### Completed

* [x] LangChain agent
* [x] LangGraph runtime
* [x] Tool calling
* [x] Calculator
* [x] Browser tools
* [x] Application tools
* [x] Web search
* [x] News
* [x] Weather
* [x] Sports
* [x] Conversation state
* [x] Text interface
* [x] Voice interface
* [x] Text wake
* [x] Voice wake
* [x] One-line wake + command
* [x] NVIDIA Whisper STT
* [x] Automatic speech-end detection

### Planned

* [ ] Persistent memory
* [ ] File/folder tools
* [ ] Clipboard tools
* [ ] Terminal/process tools
* [ ] Approval/policy system
* [ ] Better VAD
* [ ] Streaming STT
* [ ] Text-to-Speech
* [ ] Planner
* [ ] Multi-agent workflows
* [ ] Background tasks
* [ ] Scheduling
* [ ] Observability
* [ ] Evaluation

---

## 🧠 Philosophy

Hello Friend follows a simple architecture:

```text
Input
  ↓
Wake / Interaction Layer
  ↓
LangGraph Agent
  ↓
LangChain Tools
  ↓
Result
```

Voice does not create a second agent:

```text
Voice
 ↓
STT
 ↓
Text
 ↓
Same Agent
```

The goal is to keep the project:

**Simple · Readable · Debuggable · Modular · Extensible**

```

This version is **well below 250 lines** and reflects your current implementation rather than treating voice/wake as future work.
```
