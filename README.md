Hello Friend

Local personal AI assistant built with LangChain + LangGraph.

Runs in the terminal and automatically chooses tools for apps, browser actions, calculations, web research, weather, and sports.

python -m hello_friend

Stack

Python 3.11+

LangChain

LangGraph

Groq

Ollama

NVIDIA

Rich

httpx

numexpr

Structure

src/hello_friend/
├── agent/          # Agent + LangGraph
├── core/           # Config, logging, runtime
├── interface/      # Terminal UI
├── llm/            # Model + providers
│   └── providers/  # Groq, Ollama, NVIDIA
├── memory/         # Conversation memory
└── tools/
    ├── math/       # Calculator
    ├── browser/    # Browser actions
    ├── system/     # Open/close applications
    └── web/        # Search, news, weather, sports

Providers

Set the provider in .env:

LLM_PROVIDER=groq

Options:

LLM_PROVIDER=groq
LLM_PROVIDER=ollama
LLM_PROVIDER=nvidia

Example:

GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile

OLLAMA_MODEL=gpt-oss:20b
OLLAMA_BASE_URL=http://localhost:11434

Tools

Math

calculator — calculations

Browser

open_browser — open browser

open_website — open a website

search_google — Google search

search_youtube — YouTube search

System

open_application — open desktop apps

close_application — close desktop apps

Web

web_search — web research

fetch_webpage — fetch a URL

extract_content — extract page text

search_news — news

search_weather — weather

search_sports — football/sports

Tools use LangChain @tool; there is no custom tool registry.

Memory

LangGraph keeps conversation state using a thread_id.

> My name is Alex.
> What is my name?
Alex

Current memory is process-local. Persistent memory is planned.

Install

python -m venv .venv

Windows:

.venv\Scripts\activate

Linux/macOS:

source .venv/bin/activate

Then:

pip install -e .

Run

python -m hello_friend

Example:

> open youtube
> open calculator
> what is 25 * 17?
> what is the weather in London?
> find today's football scores
> my name is Alex
> what is my name?
> exit

Exit:

exit
quit
:q

Add a Tool

from langchain.tools import tool

@tool
def example_tool(value: str) -> str:
    return f"Result: {value}"

Export it and add it to tools/all.py.

Safety

Closing apps, deleting/writing files, or running commands should eventually use an approval/policy layer.

Roadmap

Persistent memory

File/folder tools

Process/terminal tools

Clipboard tools

Approval/policy system

Planner

Multi-agent workflows

Voice

Philosophy

Simple. Readable. Easy to debug. Easy to extend. Provider-independent. Safe.