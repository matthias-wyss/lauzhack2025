# Specter  
**Hackathon LauzHack 2025 • 22–23 novembre 2025**

## Overview  
Specter is a web application that transforms raw brainstorming material into a complete, production-ready project using a multi-agent AI system.  
From a simple whiteboard photo and an accompanying audio explanation, the system generates:  
- a clean and structured project specification  
- an architecture proposal  
- modular, runnable code  
- documentation and artefacts ready for deployment

The goal is to bridge the gap between ideation and implementation in seconds, making early-stage prototyping dramatically faster.

## How It Works

### 1. Input Capture  
We use the **Logitech MX Brio** camera and microphone to obtain high-quality:  
- images of a whiteboard or sketch  
- audio describing the idea and constraints

These inputs feed the multi-agent pipeline.

### 2. Multi-Agent System  
The application relies on **Oracle’s Agent Spec** and **WayFlow** frameworks to orchestrate several specialized agents such as:  
- Vision analysis agent to interpret the whiteboard  
- Audio transcription and semantic extraction agent  
- Requirements extraction agent  
- Architecture and design agent  
- Code generation agent  
- Documentation/reporting agent

Each agent contributes a structured output to the pipeline, enabling clear separation of responsibilities and robust coordination.

### 3. AI Reasoning and Generation  
The agents are powered by **Gemini** (LLM + Vision LLM).  
Gemini handles:  
- reasoning over multimodal inputs  
- summarizing key ideas  
- designing system components  
- producing clean, idiomatic code  
- generating documentation tailored to the project’s structure

### 4. Output  
Specter produces **fully implemented, modular files** that already contain functions and code implementing the elements identified from the brainstorming session.  
These outputs include:  
- backend and frontend modules  
- reusable functions corresponding to brainstormed features  
- automatically generated documentation and developer notes  
- optional deployment scaffolding

## Tech Stack  
**Frontend**: Web app built for simplicity and rapid interaction  
**Backend**: Python API orchestrating the multi-agent pipeline  
**Agents**: Oracle Agent Spec + WayFlow  
**Models**: Gemini LLM and Gemini Vision  
**Hardware**: Logitech MX Brio (camera + microphone)  

## Why This Project?  
Hackathon teams often lose precious time translating ideas into code. Specter automates the early phase of project creation by transforming brainstorming sessions into fully functional, ready-to-use project scaffolds.  
The objective is to let teams build faster, iterate better, and focus on creativity rather than setup.

## Team  
Project developed during **LauzHack 2025** by:  
- Matthias Wyss  
- Yassine Wahidy  
- William Jallot  
- Lina Sadgal  

## Getting Started  
Coming soon after hackathon refinements.
