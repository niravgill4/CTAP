# CTAP: Clinical Trial Attrition Predictor

> **Stop optimistic projections. Start diagnostic science.**

CTAP is a next-generation simulation insight engine designed to identify hidden structural biases and attrition risks in clinical trial protocols *before* a single patient enrolls. By combining **Patient Agent Swarms** with **GraphRAG-powered Knowledge Retrieval**, CTAP transforms static PDF protocols into dynamic, simulatable digital twins.

---

## 🚀 Key Capabilities

### 🧠 Patient Agent Swarm Simulation
Deploy 1,000+ high-fidelity patient agents, each with unique personas, clinical histories, and behavioral motivations. Watch them interact with your trial protocol in real-time to uncover exactly where and why participants are likely to drop out.

### 🕸️ GraphRAG Protocol Analysis
CTAP doesn't just read your protocol—it understands the relationships within it. Using a graph-based RAG architecture, the system maps inclusion/exclusion criteria against the Schedule of Assessments to identify "Patient Breaking Points."

### 🎮 Clinical Command Center
A premium, real-time dashboard providing:
- **Attrition Risk Heatmaps**: Visual identification of trial phases with the highest dropout probability.
- **Real-Time Sentiment Monitoring**: Watch the collective "mood" of your simulated cohort evolve as they face complex trial requirements.
- **Synthesis Reports**: Automated, LLM-generated insights detailing protocol flaws and optimization recommendations.

---

## 🛠️ Hybrid LLM Strategy

CTAP utilizes a performance-optimized multi-LLM architecture to ensure both speed and deep reasoning:
- **Phase 1 (Ontology Build)**: Powered by **Groq Cloud** (Llama 3.3 70B) for near-instant protocol parsing.
- **Phase 2-5 (Simulation & Synthesis)**: Powered by **Cerebras Cloud** (Llama 3.1 70B) for massive throughput during agent interactions.
- **Local Fallback**: Automatic failover to local **Ollama** models for maximum privacy and cost-efficiency.

---

## 📦 Getting Started

### Prerequisites
- **Node.js** (v18+)
- **Python** (v3.11 - v3.12)
- **uv** (Recommended for Python package management)

### Installation

1. **Clone the project** to your local machine.
2. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Add your API keys for Groq, Cerebras, and Zep
   ```
3. **Install Dependencies**:
   ```bash
   npm run setup:all
   ```
4. **Launch the Engine**:
   ```bash
   npm run dev
   ```

Visit `http://localhost:3000` to access the Command Center.

---

## 🏗️ Tech Stack

- **Frontend**: Vue 3, D3.js (Graph Visualization), Vanilla CSS (Premium Dark Theme).
- **Backend**: FastAPI, Pydantic, Python 3.12.
- **Memory/Graph**: [Zep](https://www.getzep.com/) for long-term agent memory and graph relationships.
- **Orchestration**: Custom multi-agent framework built for clinical accuracy.

---

## 📄 License & Credits
*Originally inspired by the MiroFish swarm intelligence engine. Redesigned and optimized for clinical trial simulation.*

**Strategic Support**: Powered by Advanced Agentic Research.
