"""
Main Entry Point
Autonomous Trading Research System
"""

import logging
import argparse
import json
from pipeline import PipelineRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Autonomous Trading Research System'
    )
    
    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help='Stock ticker symbol (e.g., NVDA)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['analyze', 'trading', 'backtest'],
        default='analyze',
        help='Operation mode'
    )
    
    parser.add_argument(
        '--period',
        type=str,
        default='1y',
        help='Analysis period (1y, 6mo, 3mo, etc.)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'markdown', 'both'],
        default='json',
        help='Output format'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save output to file'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    logger.info(f"Starting analysis for {args.ticker}")
    
    runner = PipelineRunner(args.ticker)
    results = runner.run(quant_period=args.period)
    
    # Output results
    if args.output in ['json', 'both']:
        json_output = json.dumps(results, indent=2)
        print("\n" + "="*80)
        print("JSON OUTPUT")
        print("="*80)
        print(json_output)
        
        if args.save:
            filename = f"outputs/{args.ticker}_analysis.json"
            with open(filename, 'w') as f:
                f.write(json_output)
            logger.info(f"Saved JSON output to {filename}")
    
    if args.output in ['markdown', 'both']:
        md_output = runner.get_report_markdown()
        print("\n" + "="*80)
        print("MARKDOWN OUTPUT")
        print("="*80)
        print(md_output)
        
        if args.save:
            filename = f"outputs/{args.ticker}_analysis.md"
            with open(filename, 'w') as f:
                f.write(md_output)
            logger.info(f"Saved Markdown output to {filename}")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Ticker: {args.ticker}")
    print(f"Signal: {results.get('final_signal', 0.0):.2f}")
    print(f"Recommendation: {results.get('recommendation', {}).get('direction', 'HOLD')}")
    print(f"Confidence: {results.get('confidence', 0.0):.0%}")
    print("="*80)


if __name__ == '__main__':
    main()
