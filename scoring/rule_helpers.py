"""
ETAF v2 Rule-based Helper Functions
Individual scoring functions for each ETAF component
"""

import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Arabic threat keywords for operational scoring
ARABIC_OPERATIONAL_KEYWORDS = [
    'هجوم', 'اعتداء', 'ضربة', 'قصف', 'تفجير', 'انفجار',
    'قتل', 'اغتيال', 'تصفية', 'إعدام', 'ذبح',
    'تدمير', 'هدم', 'حرق', 'تخريب',
    'أمر', 'توجيه', 'تعليمات', 'خطة', 'عملية',
    'استهداف', 'مهاجمة', 'ضرب', 'قنص'
]

# Farsi threat keywords for operational scoring  
FARSI_OPERATIONAL_KEYWORDS = [
    'حمله', 'تجاوز', 'ضربه', 'بمباران', 'انفجار',
    'کشتن', 'ترور', 'اعدام', 'سر بریدن',
    'تخریب', 'ویران', 'سوزاندن', 'نابودی',
    'دستور', 'هدایت', 'دستورالعمل', 'نقشه', 'عملیات',
    'هدف گیری', 'حمله کردن', 'زدن', 'تک تیراندازی'
]

# Temporal indicators for future-looking threats
ARABIC_TEMPORAL_KEYWORDS = [
    'غداً', 'بكرة', 'الأسبوع القادم', 'الشهر القادم', 'قريباً', 'سوف', 'سنقوم',
    'سيتم', 'مقبل', 'قادم', 'مستقبل', 'لاحقاً', 'فيما بعد'
]

FARSI_TEMPORAL_KEYWORDS = [
    'فردا', 'هفته آینده', 'ماه آینده', 'به زودی', 'خواهیم', 'انجام خواهد',
    'آینده', 'بعدی', 'آتی', 'بعداً', 'در آینده'
]

# Location keywords for specificity scoring
ARABIC_LOCATIONS = [
    'بغداد', 'البصرة', 'الموصل', 'كربلاء', 'النجف', 'أربيل', 'السليمانية',
    'الفلوجة', 'الرمادي', 'تكريت', 'كركوك', 'ديالى', 'صلاح الدين',
    'العراق', 'سوريا', 'لبنان', 'فلسطين', 'اليمن', 'إيران'
]

FARSI_LOCATIONS = [
    'تهران', 'اصفهان', 'مشهد', 'شیراز', 'تبریز', 'کرج', 'اهواز',
    'قم', 'کرمانشاه', 'ارومیه', 'رشت', 'زاهدان', 'همدان',
    'ایران', 'عراق', 'سوریه', 'لبنان', 'فلسطین', 'یمن'
]

def score_temporal(text, pos_tags):
    """
    Score temporal component (0-100)
    Looks for future-oriented verbs, dates, and temporal expressions
    
    Args:
        text: Input text
        pos_tags: POS tag results from Spark NLP
        
    Returns:
        Temporal score (0-100)
    """
    try:
        score = 0
        text_lower = text.lower()
        
        # Detect language from text characteristics
        lang = 'fa' if any(char in text for char in 'پچجحخکگی') else 'ar'
        
        # Select appropriate temporal keywords
        temporal_keywords = ARABIC_TEMPORAL_KEYWORDS if lang == 'ar' else FARSI_TEMPORAL_KEYWORDS
        
        # Check for temporal keywords
        for keyword in temporal_keywords:
            if keyword in text_lower:
                score += 15
                logger.debug(f"Temporal keyword found: {keyword}")
        
        # Check for future tense verbs in POS tags
        future_verbs = 0
        for tag, word in pos_tags:
            if 'VERB' in tag.upper() and any(marker in word for marker in ['سوف', 'سن', 'سي', 'خواه']):
                future_verbs += 1
        
        score += min(future_verbs * 10, 30)
        
        # Check for specific dates/times
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # Date formats
            r'\d{1,2}:\d{2}',                   # Time formats
            r'(يوم|شهر|أسبوع|ساعة|دقيقة)',      # Arabic time units
            r'(روز|ماه|هفته|ساعت|دقیقه)'        # Farsi time units
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text):
                score += 10
                break
        
        # Check for urgency indicators
        urgency_words = ['عاجل', 'فوري', 'سريع', 'فوراً'] if lang == 'ar' else ['فوری', 'سریع', 'زود', 'سریعاً']
        for word in urgency_words:
            if word in text_lower:
                score += 20
                break
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Temporal scoring error: {str(e)}")
        return 10  # Default low score on error

def score_operational(text, verbs):
    """
    Score operational component (0-100)
    Identifies militant verbs, commands, and operational language
    
    Args:
        text: Input text
        verbs: Verb tokens from Spark NLP
        
    Returns:
        Operational score (0-100)
    """
    try:
        score = 0
        text_lower = text.lower()
        
        # Detect language from text characteristics
        lang = 'fa' if any(char in text for char in 'پچجحخکگی') else 'ar'
        
        # Select appropriate operational keywords
        operational_keywords = ARABIC_OPERATIONAL_KEYWORDS if lang == 'ar' else FARSI_OPERATIONAL_KEYWORDS
        
        # Count operational keywords
        keyword_count = 0
        for keyword in operational_keywords:
            if keyword in text_lower:
                keyword_count += 1
                logger.debug(f"Operational keyword found: {keyword}")
        
        score += min(keyword_count * 20, 60)
        
        # Check for command structures
        command_indicators = ['أمر', 'توجيه', 'تعليمات'] if lang == 'ar' else ['دستور', 'فرمان', 'تعلیمات']
        for indicator in command_indicators:
            if indicator in text_lower:
                score += 15
                break
        
        # Check for weapon mentions
        weapons = ['سلاح', 'قنبلة', 'صاروخ', 'رصاصة'] if lang == 'ar' else ['سلاح', 'بمب', 'موشک', 'گلوله']
        for weapon in weapons:
            if weapon in text_lower:
                score += 20
                break
        
        # Check for military terminology
        military_terms = ['عسكري', 'جندي', 'قوات', 'جيش'] if lang == 'ar' else ['نظامی', 'سرباز', 'نیرو', 'ارتش']
        for term in military_terms:
            if term in text_lower:
                score += 10
                break
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Operational scoring error: {str(e)}")
        return 15  # Default low score on error

def score_specificity(ner_results):
    """
    Score specificity component (0-100)
    Evaluates presence of specific locations, people, timestamps
    
    Args:
        ner_results: Named entity recognition results from Spark NLP
        
    Returns:
        Specificity score (0-100)
    """
    try:
        score = 0
        
        # Extract entities and text from ner_results
        if isinstance(ner_results, list):
            entities = ner_results
            text = ' '.join([e.get('text', '') for e in entities if e.get('text')])
        else:
            entities = ner_results.get('entities', [])
            text = ner_results.get('text', '')
            
        text_lower = text.lower()
        
        # Detect language from text characteristics
        lang = 'fa' if any(char in text for char in 'پچجحخکگی') else 'ar'
        
        # Score based on named entities
        location_entities = 0
        person_entities = 0
        organization_entities = 0
        
        for entity in entities:
            label = entity.get('label', '').upper()
            confidence = entity.get('confidence', 0.0)
            
            # Only consider high-confidence entities
            if confidence >= 0.5:
                if 'LOC' in label or 'GPE' in label:
                    location_entities += 1
                elif 'PER' in label:
                    person_entities += 1
                elif 'ORG' in label:
                    organization_entities += 1
        
        # Score entity types
        score += min(location_entities * 15, 45)
        score += min(person_entities * 10, 30)
        score += min(organization_entities * 10, 25)
        
        # Check for specific locations manually
        locations = ARABIC_LOCATIONS if lang == 'ar' else FARSI_LOCATIONS
        location_mentions = sum(1 for loc in locations if loc in text_lower)
        score += min(location_mentions * 10, 30)
        
        # Check for specific numbers/quantities
        number_patterns = [
            r'\d+\s*(كيلو|متر|طن|جرام)',  # Arabic units
            r'\d+\s*(کیلو|متر|تن|گرم)',   # Farsi units
            r'\d+\s*(شخص|فرد|نفر)',      # Person counts
            r'\d+:\d+',                   # Time stamps
            r'\$\d+|\d+\s*دولار'          # Money amounts
        ]
        
        for pattern in number_patterns:
            if re.search(pattern, text):
                score += 15
                break
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Specificity scoring error: {str(e)}")
        return 20  # Default low score on error

def score_source_intent(metadata, entities):
    """
    Score source intent component (0-100)
    Evaluates channel credibility and historical context
    
    Args:
        metadata: Channel metadata dictionary
        entities: Named entities for additional context
        
    Returns:
        Source intent score (0-100)
    """
    try:
        score = 30  # Base score for any source
        
        # Check source reliability indicators
        source_name = metadata.get('source', '').lower()
        
        # High-credibility sources
        credible_sources = [
            'sabereen', 'qassam', 'hezbollah', 'resistance',
            'صابرین', 'قسام', 'حزب الله', 'مقاومة'
        ]
        
        if any(cred in source_name for cred in credible_sources):
            score += 25
            logger.debug(f"Credible source detected: {source_name}")
        
        # Check verification status
        if metadata.get('verified', False):
            score += 15
        
        # Check follower count (higher = more credible)
        follower_count = metadata.get('follower_count', 0)
        if follower_count > 100000:
            score += 20
        elif follower_count > 10000:
            score += 10
        elif follower_count > 1000:
            score += 5
        
        # Check historical accuracy
        historical_accuracy = metadata.get('historical_accuracy', 0.0)
        if historical_accuracy >= 0.8:
            score += 15
        elif historical_accuracy >= 0.6:
            score += 10
        elif historical_accuracy >= 0.4:
            score += 5
        
        # Check if entities mention known threat actors
        threat_actors = ['isis', 'qaeda', 'hamas', 'hezbollah', 'داعش', 'القاعدة', 'حماس']
        for entity in entities:
            entity_text = entity.get('text', '').lower()
            if any(actor in entity_text for actor in threat_actors):
                score += 15
                break
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Source intent scoring error: {str(e)}")
        return 25  # Default moderate score on error