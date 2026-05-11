"""
Basic functionality test
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    try:
        logger.info("Testing imports...")
        
        from agents.quant import QuantAgent
        logger.info("✓ QuantAgent imported")
        
        from agents.sentiment import SentimentAgent
        logger.info("✓ SentimentAgent imported")
        
        from agents.risk import RiskAgent
        logger.info("✓ RiskAgent imported")
        
        from pipeline import PipelineRunner
        logger.info("✓ PipelineRunner imported")
        
        from orchestrator import MemoryStore, ToolRegistry
        logger.info("✓ Orchestrator modules imported")
        
        return True
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        return False

def test_agent_initialization():
    """Test that agents can be initialized"""
    try:
        logger.info("\nTesting agent initialization...")
        
        from agents.quant import QuantAgent
        quant = QuantAgent('NVDA')
        logger.info("✓ QuantAgent initialized")
        
        from agents.sentiment import SentimentAgent
        sentiment = SentimentAgent('NVDA')
        logger.info("✓ SentimentAgent initialized")
        
        from agents.risk import RiskAgent
        risk = RiskAgent('NVDA')
        logger.info("✓ RiskAgent initialized")
        
        return True
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        return False

def test_pipeline_initialization():
    """Test that pipeline can be initialized"""
    try:
        logger.info("\nTesting pipeline initialization...")
        
        from pipeline import PipelineRunner
        runner = PipelineRunner('NVDA')
        logger.info("✓ PipelineRunner initialized")
        
        return True
    except Exception as e:
        logger.error(f"Pipeline initialization failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("BASIC FUNCTIONALITY TESTS")
    logger.info("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Agent Initialization", test_agent_initialization),
        ("Pipeline Initialization", test_pipeline_initialization),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("="*60)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
