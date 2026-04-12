# 🧠 Autonomous Multi-Agent Trading Research System

> **Built with OpenClaw-style agent architecture · Multi-agent · Tool-calling · Autonomous reasoning**

An AI-first system that autonomously researches stocks by orchestrating multiple specialized agents (Quant, Sentiment, Risk) and synthesizing their outputs into structured trade signals with reasoning traces.

---

## 🚀 Overview

This project implements an **OpenClaw-style multi-agent system** where an orchestrator dynamically plans, executes, and refines tasks using LLM-driven agents and tool-calling workflows.

Given a stock ticker (e.g., `NVDA`), the system:

1. Plans execution steps using an LLM
2. Delegates tasks to specialized agents
3. Uses tools (APIs, data sources) dynamically
4. Maintains memory across steps
5. Applies a critic loop for refinement
6. Produces a structured research report

---

## ⚙️ System Architecture

```
User Input (Ticker)
        ↓
🧠 Planner Agent (LLM)
        ↓
⚙️ Executor Loop (Tool + Agent Calls)
   ┌───────────────┬───────────────┬───────────────┐
   ↓               ↓               ↓
📊 Quant       📰 Sentiment     ⚠️ Risk
 Agent           Agent           Agent
   ↓               ↓               ↓
        🧠 Shared Memory (ChromaDB)
                    ↓
            🔍 Critic Agent
                    ↓
        📈 Final Synthesis Agent
                    ↓
     📄 Trade Signal + Reasoning Trace
```

---

## 🤖 Agents

### 📊 Quant Agent

* Fetches OHLCV data using `yfinance`
* Computes technical indicators:

  * RSI
  * MACD
  * Bollinger Bands
* Generates momentum-based signals

---

### 📰 Sentiment Agent

* Fetches news using `NewsAPI`
* Processes text using LLM (Claude / GPT)
* Outputs:

  * Sentiment (Bullish / Bearish / Neutral)
  * Confidence score
  * Key themes

---

### ⚠️ Risk Agent

* Computes:

  * Value at Risk (VaR)
  * Max Drawdown
* Integrates macro indicators via `FRED API`
* Flags risk exposure

---

## 🧠 Core Features

* ✅ Multi-agent system (Quant, Sentiment, Risk)
* ✅ Planner → Executor → Critic loop
* ✅ Dynamic tool-calling (OpenClaw-style)
* ✅ Memory using vector store (ChromaDB)
* ✅ LLM-based reasoning & synthesis
* ✅ Structured JSON outputs
* ✅ Autonomous multi-step task execution

---

## 🧰 Tech Stack

* **LLM**: Claude / GPT-4o-mini
* **Agent Framework**: OpenClaw-style (custom implementation)
* **Backend**: Python
* **Data Sources**:

  * yfinance (market data)
  * NewsAPI (news)
  * FRED API (macro)
* **Libraries**:

  * pandas, pandas-ta
  * chromadb
  * requests
* **Optional UI**: Streamlit

---

## 📦 Project Structure

```
trading-agent/
│
├── agents/
│   ├── planner.py
│   ├── executor.py
│   ├── quant_agent.py
│   ├── sentiment_agent.py
│   ├── risk_agent.py
│   ├── critic.py
│   ├── synthesizer.py
│   └── orchestrator.py
│
├── tools/
│   ├── market_data.py
│   ├── news_data.py
│   ├── macro_data.py
│   ├── registry.py
│   └── executor.py
│
├── memory/
│   └── vector_store.py
│
├── utils/
│   └── llm.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## 🔧 Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/your-username/trading-agent.git
cd trading-agent
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Setup Environment Variables

Create `.env`:

```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
NEWS_API_KEY=your_key
FRED_API_KEY=your_key
```

---

### 4. Run the System

```bash
python main.py
```

---

## 🧪 Example Run

**Input:**

```
NVDA
```

**Output (simplified):**

```json
{
  "final_signal": "bullish",
  "confidence": 0.82,
  "reasoning_trace": [
    "RSI indicates oversold recovery",
    "Positive earnings sentiment detected",
    "Low macro risk exposure"
  ]
}
```

---

## 🔁 Agent Workflow (OpenClaw Style)

This system follows an **agentic loop**:

1. **Planner** → decides execution steps
2. **Executor** → runs agents & tools
3. **Memory** → stores intermediate results
4. **Critic** → evaluates inconsistencies
5. **Synthesis** → generates final output

---

## 💡 Key Design Decisions

* **Tool abstraction** → each API wrapped as a callable tool
* **Stateful execution** → shared memory across agents
* **LLM-driven planning** → dynamic workflows instead of hardcoded pipelines
* **Separation of concerns** → agents, tools, memory isolated

---

## 📈 Future Improvements

* [ ] Real-time data via WebSockets (Polygon.io)
* [ ] Portfolio optimization agent
* [ ] Reinforcement learning for strategy tuning
* [ ] UI dashboard with Streamlit
* [ ] Backtesting engine

---

## 🎯 Resume One-Liner

> Built an OpenClaw-style multi-agent system that autonomously analyzes stocks by orchestrating quant, sentiment, and risk agents using tool-calling, memory, and reasoning-based workflows.

---

## 📹 Demo (Optional)

Add:

* Loom video walkthrough
* Example outputs
* Architecture explanation

---

## 🤝 Contributions

Open to improvements and extensions. Feel free to fork and build on top.


