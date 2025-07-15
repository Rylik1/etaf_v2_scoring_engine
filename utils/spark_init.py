"""
Spark NLP Initialization for ETAF v2
Configures and initializes Spark NLP pipeline for Arabic and Farsi processing
"""

import logging
import os
from typing import Optional

try:
    from pyspark.sql import SparkSession
    from sparknlp.base import *
    from sparknlp.annotator import *
    from sparknlp import start, Pipeline
    SPARK_NLP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Spark NLP not available: {e}")
    SPARK_NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

def initialize_spark_nlp() -> Optional[object]:
    """
    Initialize Spark NLP pipeline for Arabic and Farsi text processing
    
    Returns:
        Fitted pipeline object or None if initialization fails
    """
    if not SPARK_NLP_AVAILABLE:
        logger.error("Spark NLP dependencies not available")
        return None
    
    try:
        logger.info("Starting Spark NLP session...")
        
        # Start Spark NLP session
        spark = start(
            gpu=False,  # CPU-only for Railway compatibility
            memory="4g",  # Adjust based on Railway memory limits
            log_level="WARN"  # Reduce log verbosity
        )
        
        logger.info("Spark session started successfully")
        
        # Create pipeline for multilingual processing
        pipeline = create_multilingual_pipeline()
        
        # Create empty DataFrame for pipeline fitting
        empty_df = spark.createDataFrame([[""]]).toDF("text")
        
        logger.info("Fitting Spark NLP pipeline...")
        fitted_pipeline = pipeline.fit(empty_df)
        
        logger.info("Spark NLP pipeline initialized successfully")
        return fitted_pipeline
        
    except Exception as e:
        logger.error(f"Failed to initialize Spark NLP: {str(e)}")
        return None

def create_multilingual_pipeline():
    """
    Create a multilingual NLP pipeline for Arabic and Farsi
    
    Returns:
        Spark NLP Pipeline object
    """
    try:
        # Document assembler - converts text to document
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        
        # Sentence detector
        sentence_detector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_xx", "xx") \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")
        
        # Tokenizer for multilingual text
        tokenizer = Tokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")
        
        # Word embeddings - using multilingual model
        try:
            word_embeddings = WordEmbeddingsModel.pretrained("glove_100d", "xx") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("embeddings")
        except:
            logger.warning("Could not load multilingual embeddings, using basic tokenization")
            word_embeddings = None
        
        # POS tagger for multilingual text
        try:
            pos_tagger = PerceptronModel.pretrained("pos_ud_gsd", "xx") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("pos")
        except:
            logger.warning("Could not load multilingual POS tagger")
            pos_tagger = None
        
        # Named Entity Recognition - multilingual
        try:
            ner_model = NerDLModel.pretrained("ner_ud_gsd_glove_840B_300d", "xx") \
                .setInputCols(["sentence", "token", "embeddings"]) \
                .setOutputCol("ner")
            
            # NER converter to extract entities
            ner_converter = NerConverter() \
                .setInputCols(["sentence", "token", "ner"]) \
                .setOutputCol("entities")
        except:
            logger.warning("Could not load multilingual NER model")
            ner_model = None
            ner_converter = None
        
        # Build pipeline with available components
        stages = [document_assembler, sentence_detector, tokenizer]
        
        if word_embeddings:
            stages.append(word_embeddings)
        
        if pos_tagger:
            stages.append(pos_tagger)
        
        if ner_model and ner_converter and word_embeddings:
            stages.extend([ner_model, ner_converter])
        
        pipeline = Pipeline(stages=stages)
        
        logger.info(f"Created pipeline with {len(stages)} stages")
        return pipeline
        
    except Exception as e:
        logger.error(f"Failed to create pipeline: {str(e)}")
        # Return minimal pipeline as fallback
        return Pipeline(stages=[
            DocumentAssembler().setInputCol("text").setOutputCol("document"),
            Tokenizer().setInputCols(["document"]).setOutputCol("token")
        ])

def create_arabic_specific_pipeline():
    """
    Create Arabic-specific NLP pipeline (fallback option)
    
    Returns:
        Spark NLP Pipeline object optimized for Arabic
    """
    try:
        # Document assembler
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        
        # Arabic sentence detector
        sentence_detector = SentenceDetectorDLModel.pretrained("sentence_detector_dl", "ar") \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")
        
        # Arabic tokenizer
        tokenizer = Tokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")
        
        # Arabic word embeddings
        word_embeddings = WordEmbeddingsModel.pretrained("arabic_w2v_cc_300d", "ar") \
            .setInputCols(["sentence", "token"]) \
            .setOutputCol("embeddings")
        
        # Arabic NER
        ner_model = NerDLModel.pretrained("arabic_ner_cc_300d", "ar") \
            .setInputCols(["sentence", "token", "embeddings"]) \
            .setOutputCol("ner")
        
        ner_converter = NerConverter() \
            .setInputCols(["sentence", "token", "ner"]) \
            .setOutputCol("entities")
        
        pipeline = Pipeline(stages=[
            document_assembler,
            sentence_detector, 
            tokenizer,
            word_embeddings,
            ner_model,
            ner_converter
        ])
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Failed to create Arabic pipeline: {str(e)}")
        raise e

def create_farsi_specific_pipeline():
    """
    Create Farsi-specific NLP pipeline (fallback option)
    
    Returns:
        Spark NLP Pipeline object optimized for Farsi
    """
    try:
        # Document assembler
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        
        # Farsi sentence detector
        sentence_detector = SentenceDetectorDLModel.pretrained("sentence_detector_dl", "fa") \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")
        
        # Farsi tokenizer
        tokenizer = Tokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")
        
        # Farsi word embeddings
        word_embeddings = WordEmbeddingsModel.pretrained("persian_w2v_cc_300d", "fa") \
            .setInputCols(["sentence", "token"]) \
            .setOutputCol("embeddings")
        
        # Farsi NER
        ner_model = NerDLModel.pretrained("persian_ner_cc_300d", "fa") \
            .setInputCols(["sentence", "token", "embeddings"]) \
            .setOutputCol("ner")
        
        ner_converter = NerConverter() \
            .setInputCols(["sentence", "token", "ner"]) \
            .setOutputCol("entities")
        
        pipeline = Pipeline(stages=[
            document_assembler,
            sentence_detector,
            tokenizer, 
            word_embeddings,
            ner_model,
            ner_converter
        ])
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Failed to create Farsi pipeline: {str(e)}")
        raise e