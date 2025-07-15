"""
ETAF v2 Core Scoring Logic
Main scoring function that orchestrates all ETAF components
"""

import logging
from typing import Dict, Any, Optional

from .rule_helpers import (
    score_temporal,
    score_operational, 
    score_specificity,
    score_source_intent
)

logger = logging.getLogger(__name__)

def score_etaf_v2(text, lang, metadata) -> dict:
    """
    Main ETAF v2 scoring function
    
    Args:
        text: Message text to analyze
        lang: Language code ('ar' or 'fa')
        metadata: Channel metadata dictionary
        spark_pipeline: Initialized Spark NLP pipeline
        
    Returns:
        Dictionary with etaf_score, level, components, and rationale
    """
    try:
        logger.info(f"Starting ETAF v2 scoring for {lang} text (length: {len(text)})")
        
        # Get global Spark pipeline (passed from main.py)
        global spark_pipeline
        
        # Process text through Spark NLP pipeline
        nlp_results = process_with_spark_nlp(text, lang, spark_pipeline)
        
        # Score each ETAF component
        temporal_score = score_temporal(text, nlp_results.get('pos_tags', []))
        operational_score = score_operational(text, nlp_results.get('tokens', []))
        specificity_score = score_specificity(nlp_results.get('entities', []))
        source_intent_score = score_source_intent(metadata or {}, nlp_results.get('entities', []))
        
        # Calculate total ETAF score
        total_score = temporal_score + operational_score + specificity_score + source_intent_score
        
        # Determine threat level
        threat_level = determine_threat_level(total_score)
        
        # Generate rationale
        rationale = generate_rationale(
            temporal_score, operational_score, specificity_score, source_intent_score,
            threat_level, nlp_results
        )
        
        result = {
            "etaf_score": total_score,
            "level": threat_level,
            "components": {
                "temporal": temporal_score,
                "operational": operational_score,
                "specificity": specificity_score,
                "source_intent": source_intent_score
            },
            "rationale": rationale
        }
        
        logger.info(f"ETAF v2 scoring completed: {total_score} ({threat_level})")
        return result
        
    except Exception as e:
        logger.error(f"ETAF v2 scoring failed: {str(e)}", exc_info=True)
        # Return minimum viable score on error
        return {
            "etaf_score": 50,
            "level": "Low",
            "components": {
                "temporal": 10,
                "operational": 15,
                "specificity": 15,
                "source_intent": 10
            },
            "rationale": f"Scoring error occurred: {str(e)}"
        }

def process_with_spark_nlp(text: str, lang: str, spark_pipeline) -> Dict[str, Any]:
    """
    Process text through Spark NLP pipeline
    
    Args:
        text: Input text
        lang: Language code
        spark_pipeline: Spark NLP pipeline
        
    Returns:
        Dictionary with NLP results (tokens, pos_tags, entities)
    """
    try:
        # Create Spark DataFrame from text
        from pyspark.sql import SparkSession
        spark = SparkSession.getActiveSession()
        
        if spark is None:
            # Initialize basic results if Spark not available
            return {
                'tokens': text.split(),
                'pos_tags': [],
                'entities': []
            }
        
        # Create DataFrame
        df = spark.createDataFrame([(text,)], ["text"])
        
        # Process through pipeline
        result_df = spark_pipeline.transform(df)
        
        # Extract results
        row = result_df.collect()[0]
        
        # Extract tokens
        tokens = []
        if hasattr(row, 'token') and row.token:
            tokens = [token.result for token in row.token]
        
        # Extract POS tags
        pos_tags = []
        if hasattr(row, 'pos') and row.pos:
            pos_tags = [(token.result, token.metadata.get('word', '')) for token in row.pos]
        
        # Extract named entities
        entities = []
        if hasattr(row, 'ner') and row.ner:
            entities = [
                {
                    'text': token.result,
                    'label': token.metadata.get('entity', 'O'),
                    'confidence': float(token.metadata.get('confidence', '0.0'))
                }
                for token in row.ner
                if token.metadata.get('entity', 'O') != 'O'
            ]
        
        return {
            'tokens': tokens,
            'pos_tags': pos_tags,
            'entities': entities
        }
        
    except Exception as e:
        logger.warning(f"Spark NLP processing failed: {str(e)}")
        # Return basic tokenization as fallback
        return {
            'tokens': text.split(),
            'pos_tags': [],
            'entities': []
        }

def determine_threat_level(total_score: int) -> str:
    """
    Determine threat level based on total ETAF score
    
    Args:
        total_score: Sum of all ETAF components (0-400)
        
    Returns:
        Threat level string
    """
    if total_score >= 300:
        return "Critical"
    elif total_score >= 200:
        return "High"
    elif total_score >= 100:
        return "Medium"
    else:
        return "Low"

def generate_rationale(temporal: int, operational: int, specificity: int, 
                      source_intent: int, level: str, nlp_results: Dict[str, Any]) -> str:
    """
    Generate human-readable rationale for the scoring decision
    
    Args:
        temporal: Temporal component score
        operational: Operational component score  
        specificity: Specificity component score
        source_intent: Source intent component score
        level: Determined threat level
        nlp_results: NLP processing results
        
    Returns:
        Rationale string
    """
    rationale_parts = []
    
    # Analyze highest scoring component
    scores = {
        'temporal': temporal,
        'operational': operational, 
        'specificity': specificity,
        'source_intent': source_intent
    }
    
    max_component = max(scores.keys(), key=lambda k: scores[k])
    max_score = scores[max_component]
    
    if max_score >= 70:
        if max_component == 'temporal':
            rationale_parts.append("Future-oriented threat indicators detected")
        elif max_component == 'operational':
            rationale_parts.append("Operational threat language identified")
        elif max_component == 'specificity':
            rationale_parts.append("High specificity with concrete details")
        elif max_component == 'source_intent':
            rationale_parts.append("Credible source with concerning intent")
    
    # Add entity information if available
    entities = nlp_results.get('entities', [])
    if entities:
        entity_types = list(set(entity['label'] for entity in entities))
        if entity_types:
            rationale_parts.append(f"Named entities detected: {', '.join(entity_types[:3])}")
    
    # Add level justification
    if level == "Critical":
        rationale_parts.append("Multiple high-confidence threat indicators")
    elif level == "High":
        rationale_parts.append("Significant threat potential identified")
    elif level == "Medium":
        rationale_parts.append("Moderate threat indicators present")
    else:
        rationale_parts.append("Limited threat indicators detected")
    
    return ". ".join(rationale_parts) if rationale_parts else f"{level} threat level based on component analysis"