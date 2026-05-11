# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-...
NEWS_API_KEY=your_newsapi_key
FRED_API_KEY=your_fred_key
```

### 3. Run Your First Analysis
```bash
python main.py --ticker NVDA
```

## Common Commands

### Analyze a Stock
```bash
python main.py --ticker AAPL
```

### Custom Analysis Period
```bash
python main.py --ticker TSLA --period 6mo
```

### Get Markdown Report
```bash
python main.py --ticker GOOGL --output markdown
```

### Save Results to File
```bash
python main.py --ticker MSFT --save
```

### Get Both JSON and Markdown
```bash
python main.py --ticker META --output both --save
```

## Python API

### Basic Usage
```python
from pipeline import PipelineRunner

# Create runner
runner = PipelineRunner('NVDA')

# Run analysis
results = runner.run()

# Get recommendation
print(runner.get_recommendation())  # BUY, SELL, or HOLD

# Get signal strength
print(runner.get_signal())  # -1.0 to 1.0

# Get full report
print(runner.get_report_json())
```

### Advanced Usage
```python
from pipeline import PipelineRunner

runner = PipelineRunner('NVDA')

# Custom parameters
results = runner.run(
    quant_period='3mo',      # Shorter period
    sentiment_days=14,        # More recent news
    rl_weights={              # Custom weights
        'quant': 0.5,
        'sentiment': 0.3,
        'risk': 0.2
    }
)

# Access individual components
quant_signal = results['component_signals']['quant']
sentiment_signal = results['component_signals']['sentiment']
risk_signal = results['component_signals']['risk']

# Get detailed report
report = results['report']
print(report['executive_summary'])
print(report['risk_disclosure'])
```

## Understanding the Output

### Signal Values
- **1.0**: Extremely bullish
- **0.3 to 1.0**: Bullish (BUY)
- **-0.3 to 0.3**: Neutral (HOLD)
- **-1.0 to -0.3**: Bearish (SELL)
- **-1.0**: Extremely bearish

### Confidence
- **0.9-1.0**: Very high confidence
- **0.7-0.9**: High confidence
- **0.5-0.7**: Moderate confidence
- **<0.5**: Low confidence

### Component Signals
- **Quant**: Technical analysis signal
- **Sentiment**: News and sentiment signal
- **Risk**: Risk assessment signal

## Troubleshooting

### "No module named 'yfinance'"
```bash
pip install yfinance
```

### "ANTHROPIC_API_KEY not set"
Make sure you've created `.env` file and added your key:
```bash
cp .env.example .env
# Edit .env with your key
```

### "No news found for ticker"
This is normal for some tickers. The system will still provide quant and risk analysis.

### "FRED_API_KEY not set"
Optional - the system will use default macro values if not provided.

## API Keys

### Get Free API Keys

**Anthropic (Claude)**
- Sign up: https://console.anthropic.com
- Free tier available

**NewsAPI**
- Sign up: https://newsapi.org
- Free tier: 100 requests/day

**FRED (Federal Reserve)**
- Sign up: https://fredaccount.stlouisfed.org
- Free tier: Unlimited

**yfinance**
- No key needed - free data

## Example Workflows

### Analyze Multiple Stocks
```bash
for ticker in NVDA TSLA AAPL MSFT GOOGL; do
    python main.py --ticker $ticker --save
done
```

### Daily Analysis Script
```python
from pipeline import PipelineRunner
import json
from datetime import datetime

tickers = ['NVDA', 'TSLA', 'AAPL']

for ticker in tickers:
    runner = PipelineRunner(ticker)
    results = runner.run()
    
    # Save with timestamp
    filename = f"outputs/{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"{ticker}: {runner.get_recommendation()}")
```

### Portfolio Analysis
```python
from pipeline import PipelineRunner

portfolio = {
    'NVDA': 0.3,   # 30% weight
    'TSLA': 0.3,   # 30% weight
    'AAPL': 0.4    # 40% weight
}

total_signal = 0
for ticker, weight in portfolio.items():
    runner = PipelineRunner(ticker)
    results = runner.run()
    signal = results['final_signal']
    total_signal += signal * weight
    print(f"{ticker}: {signal:.2f}")

print(f"Portfolio Signal: {total_signal:.2f}")
```

## Output Files

When using `--save`, files are created in `outputs/`:
- `{TICKER}_analysis.json` - Full JSON report
- `{TICKER}_analysis.md` - Markdown report

## Next Steps

1. **Explore the Code**: Check out `agents/` to understand how each agent works
2. **Customize Weights**: Modify signal weights in `pipeline/synthesizer.py`
3. **Add Indicators**: Add new technical indicators in `agents/quant/indicators.py`
4. **Extend Themes**: Add sentiment themes in `agents/sentiment/news_fetcher.py`
5. **Build UI**: Create Streamlit dashboard in `app/main.py`

## Performance Tips

- **Faster Analysis**: Use shorter periods (`--period 3mo`)
- **Cached Data**: Results are cached in ChromaDB
- **Parallel Execution**: Agents run in parallel (when implemented)
- **Batch Processing**: Analyze multiple tickers in a loop

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review IMPLEMENTATION.md for architecture details
3. Check agent-specific files for implementation details
4. Review error messages in logs

## What's Next?

The system is ready for:
- ✅ Live market analysis
- ✅ Portfolio monitoring
- ✅ Signal generation
- ✅ Risk assessment
- ⏳ RL optimization (coming soon)
- ⏳ Real-time trading (coming soon)
- ⏳ Backtesting (coming soon)

Happy trading! 📈
