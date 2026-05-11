"""
Orchestrator - Tools Module
Tool definitions and registry for LLM tool-calling
"""

import logging
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for tools available to the LLM"""

    def __init__(self):
        """Initialize tool registry"""
        self.tools = {}
        self.tool_functions = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""
        
        # Quant analysis tool
        self.register_tool(
            name='analyze_quant',
            description='Perform quantitative technical analysis on a stock',
            parameters={
                'ticker': {
                    'type': 'string',
                    'description': 'Stock ticker symbol (e.g., NVDA)'
                },
                'period': {
                    'type': 'string',
                    'description': 'Analysis period (1y, 6mo, 3mo, etc.)',
                    'default': '1y'
                }
            }
        )
        
        # Sentiment analysis tool
        self.register_tool(
            name='analyze_sentiment',
            description='Analyze market sentiment from news and social media',
            parameters={
                'ticker': {
                    'type': 'string',
                    'description': 'Stock ticker symbol'
                },
                'days': {
                    'type': 'integer',
                    'description': 'Number of days to look back',
                    'default': 7
                }
            }
        )
        
        # Risk analysis tool
        self.register_tool(
            name='analyze_risk',
            description='Assess portfolio and market risk',
            parameters={
                'ticker': {
                    'type': 'string',
                    'description': 'Stock ticker symbol'
                },
                'period': {
                    'type': 'string',
                    'description': 'Analysis period',
                    'default': '1y'
                }
            }
        )
        
        # Fetch macro data tool
        self.register_tool(
            name='fetch_macro_data',
            description='Fetch macroeconomic indicators (VIX, yield curve, etc.)',
            parameters={}
        )
        
        # Fetch news tool
        self.register_tool(
            name='fetch_news',
            description='Fetch recent news articles for a stock',
            parameters={
                'ticker': {
                    'type': 'string',
                    'description': 'Stock ticker symbol'
                },
                'days': {
                    'type': 'integer',
                    'description': 'Number of days to look back',
                    'default': 7
                }
            }
        )
        
        # Synthesize signals tool
        self.register_tool(
            name='synthesize_signals',
            description='Combine agent signals into a final trading signal',
            parameters={
                'quant_signal': {
                    'type': 'number',
                    'description': 'Quantitative signal [-1, 1]'
                },
                'sentiment_signal': {
                    'type': 'number',
                    'description': 'Sentiment signal [-1, 1]'
                },
                'risk_signal': {
                    'type': 'number',
                    'description': 'Risk signal [-1, 1]'
                }
            }
        )
        
        # Generate report tool
        self.register_tool(
            name='generate_report',
            description='Generate comprehensive trading analysis report',
            parameters={
                'ticker': {
                    'type': 'string',
                    'description': 'Stock ticker symbol'
                },
                'include_recommendations': {
                    'type': 'boolean',
                    'description': 'Include trading recommendations',
                    'default': True
                }
            }
        )

    def register_tool(self, name: str, description: str, 
                     parameters: Dict[str, Any], 
                     function: Optional[Callable] = None):
        """
        Register a tool
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Parameter schema
            function: Optional function to execute
        """
        self.tools[name] = {
            'name': name,
            'description': description,
            'parameters': parameters
        }
        
        if function:
            self.tool_functions[name] = function
        
        logger.info(f"Registered tool: {name}")

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get all registered tools
        
        Returns:
            List of tool definitions
        """
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tool
        
        Args:
            name: Tool name
            
        Returns:
            Tool definition or None
        """
        return self.tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            if name not in self.tool_functions:
                return {
                    'success': False,
                    'error': f'Tool {name} not implemented'
                }
            
            function = self.tool_functions[name]
            result = function(**kwargs)
            
            return {
                'success': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def register_function(self, name: str, function: Callable):
        """
        Register a function for a tool
        
        Args:
            name: Tool name
            function: Function to execute
        """
        if name not in self.tools:
            logger.warning(f"Tool {name} not registered, registering function anyway")
        
        self.tool_functions[name] = function
        logger.info(f"Registered function for tool: {name}")

    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get OpenAI-compatible tool schema
        
        Returns:
            Tool schema for LLM
        """
        tools = []
        
        for tool in self.tools.values():
            tool_schema = {
                'type': 'function',
                'function': {
                    'name': tool['name'],
                    'description': tool['description'],
                    'parameters': {
                        'type': 'object',
                        'properties': tool['parameters'],
                        'required': [
                            param for param, spec in tool['parameters'].items()
                            if 'default' not in spec
                        ]
                    }
                }
            }
            tools.append(tool_schema)
        
        return {'tools': tools}

    def list_tools(self) -> List[str]:
        """
        List all registered tool names
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tool_help(self, name: str) -> str:
        """
        Get help for a tool
        
        Args:
            name: Tool name
            
        Returns:
            Help string
        """
        tool = self.get_tool(name)
        if not tool:
            return f"Tool {name} not found"
        
        help_text = f"Tool: {tool['name']}\n"
        help_text += f"Description: {tool['description']}\n"
        help_text += "Parameters:\n"
        
        for param, spec in tool['parameters'].items():
            help_text += f"  - {param} ({spec.get('type', 'unknown')}): {spec.get('description', '')}\n"
        
        return help_text
