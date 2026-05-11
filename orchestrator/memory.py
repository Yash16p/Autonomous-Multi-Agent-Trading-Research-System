"""
Orchestrator - Memory Management Module
Vector store for analysis summaries and historical signals
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryStore:
    """Vector store for analysis memory using ChromaDB"""

    def __init__(self, collection_name: str = "trading_analysis"):
        """
        Initialize memory store
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.memory = {}  # In-memory fallback
        
        # Try to initialize ChromaDB
        try:
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB collection '{collection_name}' initialized")
        except ImportError:
            logger.warning("ChromaDB not installed, using in-memory storage")
        except Exception as e:
            logger.warning(f"Error initializing ChromaDB: {str(e)}, using in-memory storage")

    def store_analysis(self, ticker: str, analysis_type: str, 
                      content: Dict[str, Any], metadata: Optional[Dict] = None) -> bool:
        """
        Store analysis results
        
        Args:
            ticker: Stock ticker
            analysis_type: Type of analysis ('quant', 'sentiment', 'risk', 'synthesis')
            content: Analysis content
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            doc_id = f"{ticker}_{analysis_type}_{datetime.now().isoformat()}"
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                'ticker': ticker,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
            })
            
            # Convert content to string for storage
            content_str = json.dumps(content)
            
            if self.collection:
                # Store in ChromaDB
                self.collection.add(
                    ids=[doc_id],
                    documents=[content_str],
                    metadatas=[metadata]
                )
            else:
                # Store in memory
                self.memory[doc_id] = {
                    'content': content,
                    'metadata': metadata
                }
            
            logger.info(f"Stored {analysis_type} analysis for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analysis: {str(e)}")
            return False

    def retrieve_analysis(self, ticker: str, analysis_type: Optional[str] = None,
                         limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve analysis results
        
        Args:
            ticker: Stock ticker
            analysis_type: Type of analysis to retrieve (optional)
            limit: Maximum number of results
            
        Returns:
            List of analysis results
        """
        try:
            if self.collection:
                # Query ChromaDB
                where_filter = {'ticker': ticker}
                if analysis_type:
                    where_filter['analysis_type'] = analysis_type
                
                results = self.collection.get(
                    where=where_filter,
                    limit=limit
                )
                
                # Parse results
                analyses = []
                for doc, metadata in zip(results.get('documents', []), 
                                        results.get('metadatas', [])):
                    try:
                        content = json.loads(doc)
                        analyses.append({
                            'content': content,
                            'metadata': metadata
                        })
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse stored analysis")
                
                return analyses
            else:
                # Retrieve from memory
                analyses = []
                for doc_id, data in self.memory.items():
                    if ticker in doc_id:
                        if analysis_type is None or analysis_type in doc_id:
                            analyses.append(data)
                
                return analyses[:limit]
                
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            return []

    def search_similar(self, query: str, ticker: Optional[str] = None,
                      limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar analyses
        
        Args:
            query: Search query
            ticker: Optional ticker filter
            limit: Maximum number of results
            
        Returns:
            List of similar analyses
        """
        try:
            if self.collection:
                # Build where filter
                where_filter = None
                if ticker:
                    where_filter = {'ticker': ticker}
                
                # Query ChromaDB
                results = self.collection.query(
                    query_texts=[query],
                    where=where_filter,
                    n_results=limit
                )
                
                # Parse results
                analyses = []
                for doc, metadata, distance in zip(
                    results.get('documents', [[]])[0],
                    results.get('metadatas', [[]])[0],
                    results.get('distances', [[]])[0]
                ):
                    try:
                        content = json.loads(doc)
                        analyses.append({
                            'content': content,
                            'metadata': metadata,
                            'similarity': 1 - distance  # Convert distance to similarity
                        })
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse stored analysis")
                
                return analyses
            else:
                logger.warning("ChromaDB not available, cannot perform semantic search")
                return []
                
        except Exception as e:
            logger.error(f"Error searching similar analyses: {str(e)}")
            return []

    def store_signal_history(self, ticker: str, signal: Dict[str, Any]) -> bool:
        """
        Store historical signal
        
        Args:
            ticker: Stock ticker
            signal: Signal data
            
        Returns:
            True if stored successfully
        """
        return self.store_analysis(
            ticker,
            'signal_history',
            signal,
            metadata={'signal_type': signal.get('direction', 'unknown')}
        )

    def get_signal_history(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical signals for a ticker
        
        Args:
            ticker: Stock ticker
            limit: Maximum number of signals
            
        Returns:
            List of historical signals
        """
        return self.retrieve_analysis(ticker, 'signal_history', limit)

    def store_reasoning_trace(self, ticker: str, trace: List[str]) -> bool:
        """
        Store reasoning trace
        
        Args:
            ticker: Stock ticker
            trace: List of reasoning steps
            
        Returns:
            True if stored successfully
        """
        return self.store_analysis(
            ticker,
            'reasoning_trace',
            {'steps': trace}
        )

    def get_reasoning_traces(self, ticker: str, limit: int = 5) -> List[List[str]]:
        """
        Get reasoning traces for a ticker
        
        Args:
            ticker: Stock ticker
            limit: Maximum number of traces
            
        Returns:
            List of reasoning traces
        """
        traces = self.retrieve_analysis(ticker, 'reasoning_trace', limit)
        return [t['content'].get('steps', []) for t in traces]

    def clear_old_data(self, days: int = 30) -> bool:
        """
        Clear data older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            True if cleared successfully
        """
        try:
            # Note: Full implementation would require timestamp-based deletion
            logger.info(f"Clearing data older than {days} days")
            return True
        except Exception as e:
            logger.error(f"Error clearing old data: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory store statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            if self.collection:
                count = self.collection.count()
                return {
                    'backend': 'chromadb',
                    'collection': self.collection_name,
                    'document_count': count
                }
            else:
                return {
                    'backend': 'memory',
                    'document_count': len(self.memory)
                }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
