# 🔍 AUTOVIZ: AI-Powered Data Visualization Tool

**Final Year Engineering Project – B.Tech AI & Data Science Branch**

AutoViz bridges the gap between **natural language** and **data visualization**. Users can ask questions in plain English, and AutoViz will automatically generate the appropriate chart in Apache Superset — no SQL or manual configuration required.

> Example:
> ```
> "Show me the total sales per category"
> ```
> ➜ AutoViz understands the request, determines the chart type, generates the chart configuration, and creates the visualization in Superset.

---

## 💡 Project Overview

AutoViz is an **AI-powered analytics assistant** that translates plain-English queries into fully functional Apache Superset charts using a local Large Language Model (LLM). It is designed to make data exploration intuitive for non-technical users.

---

## ⚙️ Key Components

- **ChartBuilderAgent**  
  Central agent that interprets user queries, selects chart types, and generates full Superset-compatible chart configurations using an LLM (like Mistral via Ollama).

- **SystemPromptGenerator**  
  Dynamically inspects the connected database and provides up-to-date schema context to the agent.

- **LLMHandler**  
  Interface for interacting with a local Ollama LLM instance.

- **ChartCreator**  
  Handles the API call to Apache Superset to create and display the chart.

---

## 🚀 Features

- Natural language to data visualization
- No need for SQL or chart-building skills
- Powered by fast, local LLMs (e.g., Mistral via Ollama)
- Direct integration with Apache Superset
- Modular and agent-based design for easy extension

---

## 📦 Requirements

- Python 3.9+
- Apache Superset (running and configured)
- Ollama with Mistral (or compatible local LLM)
- Required Python packages (see `requirements.txt`)


