# Hermes Crypto Prediction Bot

A production-ready backend Python project leveraging the [Hermes Agents framework](https://github.com/nousresearch/hermes-agent) to orchestrate a suite of specialized AI agents for cryptocurrency market research, technical prediction, and risk management.

## 🌟 Key Features

*   **Hermes Agent Orchestration**: A central `SupervisorAgent` coordinates tasks across multiple specialized worker agents, using LLMs (via OpenRouter) to resolve conflicts and explain rationales.
*   **Foundation Model Predictions**: Integrates the [Kronos](https://github.com/shiyu-coder/Kronos) model to analyze technical OHLCV data.
*   **Signal Fusion**: Combines technical model probabilities with real-world market odds (from Kalshi and Polymarket) using a pluggable consensus strategy.
*   **Kelly Sizing**: Computes precise Expected Value (EV) and applies Kelly criterion formulas for safe, mathematically-sound position recommendations.
*   **Probability Calibration**: Uses techniques like Platt Scaling to prevent model overconfidence before risking capital.
*   **Asynchronous & Telemetry**: Fully async pipeline powered by `asyncio` and `aiohttp`, with structured JSON telemetry logging.

## 🏗️ Architecture

The system operates on a decentralized, supervisor-worker pattern:

1.  **Supervisor Agent**: Orchestrates workflows, handles LLM-based reasoning, and manages final reporting.
2.  **Market Intelligence Agent**: Gathers and unifies odds from prediction markets (Kalshi, Polymarket).
3.  **Market Data Agent**: Fetches historical multi-timeframe OHLCV data from exchanges (e.g., Binance).
4.  **Prediction Agent**: Wraps the Kronos model pipeline (`FeaturePipeline -> WindowBuilder -> Kronos -> Postprocessor`).
5.  **Evaluation Agent**: Intercepts raw predictions and applies statistical calibration based on historical accuracy.
6.  **Signal Fusion Agent**: Unifies calibrated technical probabilities with fundamental market consensus.
7.  **Risk Agent**: Calculates expected value and the recommended Kelly position size.
8.  **Feedback Agent**: Updates Hermes' short-term memory and logs immutable metrics to a SQLite database.

## 📂 Project Structure

```text
app/
├── domain/             # Core business logic and Pydantic schemas (market, prediction, risk)
├── agents/             # Hermes-inspired worker agents (supervisor, risk, prediction, etc.)
├── services/           # External API integrations (Binance, Apify, Polymarket, Kronos, storage)
├── api/                # FastAPI application endpoints
├── cli/                # Command-line interfaces
├── config/             # Multi-profile configurations using pydantic-settings
├── telemetry/          # Structured JSON logging and observability
└── tests/              # Unit and integration tests
```

## 🚀 Getting Started

### Prerequisites

*   Python 3.11+
*   API Keys for OpenRouter (and optionally Binance, Apify, etc.)

### Installation

1.  Clone the repository and enter the project directory.
2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  Set up your environment variables. You can create a `.env` file in the root directory:

    ```env
    PROFILE=development
    OPENROUTER_API_KEY=your_openrouter_api_key
    BINANCE_API_KEY=your_binance_api_key
    BINANCE_API_SECRET=your_binance_api_secret
    APIFY_API_TOKEN=your_apify_api_token
    LOG_LEVEL=INFO
    ```

### Usage

**Running the CLI (Testing the workflow end-to-end):**

```bash
python main.py
```
*This will execute the supervisor workflow for BTC and ETH concurrently and log the JSON telemetry to the console.*

**Running the REST API (FastAPI Server):**

```bash
python main.py api
```
*The API will start on `http://0.0.0.0:8000`. You can test triggering workflows via the `/trigger-workflow` endpoint.*

## 🧪 Testing & Backtesting

The project includes a stubbed `BacktestingService` under `app/services/backtesting.py` to allow offline replay of historical bars for strategy validation without risking capital.

Run the test suite using `pytest` (once implemented in the `tests/` directory):
```bash
pytest
```

## 📜 License

[MIT License](LICENSE)
