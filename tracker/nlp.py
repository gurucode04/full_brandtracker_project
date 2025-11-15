# tracker/nlp.py - transformer-based NLP with lightweight fallback
import pickle
import os
import logging

logger = logging.getLogger(__name__)

# Check if we should use lightweight NLP (TextBlob) instead of transformers
USE_LIGHTWEIGHT_NLP = os.environ.get('USE_LIGHTWEIGHT_NLP', 'false').lower() == 'true'

# Try to import heavy ML libraries, fallback to TextBlob if not available
_sentiment = None
_embedder = None
_topic_model = None
_transformers_available = False
_sentence_transformers_available = False
_bertopic_available = False

try:
    from transformers import pipeline
    _transformers_available = True
except ImportError:
    logger.warning("transformers not available, will use TextBlob fallback")

try:
    from sentence_transformers import SentenceTransformer
    _sentence_transformers_available = True
except ImportError:
    logger.warning("sentence-transformers not available")

try:
    from bertopic import BERTopic
    _bertopic_available = True
except ImportError:
    logger.warning("bertopic not available")

# Import lightweight fallback
try:
    from textblob import TextBlob
    _textblob_available = True
except ImportError:
    _textblob_available = False
    logger.warning("TextBlob not available - sentiment analysis will be basic")

import numpy as np

SENTIMENT_MODEL_NAME = os.environ.get('SENTIMENT_MODEL','distilbert-base-uncased-finetuned-sst-2-english')
EMBED_MODEL_NAME = os.environ.get('EMBED_MODEL','all-MiniLM-L6-v2')

def _get_sentiment_pipeline():
    global _sentiment
    if _sentiment is None:
        if USE_LIGHTWEIGHT_NLP or not _transformers_available:
            _sentiment = 'textblob'  # Use TextBlob
            logger.info("Using TextBlob for sentiment analysis (lightweight mode)")
        else:
            try:
                _sentiment = pipeline('text-classification', model=SENTIMENT_MODEL_NAME, truncation=True)
                logger.info(f"Loaded sentiment model: {SENTIMENT_MODEL_NAME}")
            except Exception as e:
                logger.warning(f"Error loading sentiment model, falling back to TextBlob: {e}")
                _sentiment = 'textblob'
    return _sentiment

def _get_embedder():
    global _embedder
    if _embedder is None:
        if USE_LIGHTWEIGHT_NLP or not _sentence_transformers_available:
            _embedder = None  # Skip embeddings in lightweight mode
            logger.info("Skipping embeddings in lightweight mode")
        else:
            try:
                _embedder = SentenceTransformer(EMBED_MODEL_NAME)
                logger.info(f"Loaded embedding model: {EMBED_MODEL_NAME}")
            except Exception as e:
                logger.warning(f"Error loading embedding model: {e}")
                _embedder = None
    return _embedder

def encode_text(text):
    if USE_LIGHTWEIGHT_NLP or not _sentence_transformers_available:
        logger.warning("encode_text called but embeddings not available in lightweight mode")
        return np.array([])
    embedder = _get_embedder()
    if embedder is None:
        return np.array([])
    emb = embedder.encode(text, show_progress_bar=False)
    return np.array(emb)

def analyze_text(text, use_topic=True):
    text = (text or '').strip()
    if not text:
        return 'neutral', 0.0, 'general', None
    
    # Sentiment analysis
    sentiment = 'neutral'
    score = 0.0
    
    try:
        sentiment_pipeline = _get_sentiment_pipeline()
        
        if sentiment_pipeline == 'textblob' or not _transformers_available:
            # Use lightweight TextBlob fallback
            if _textblob_available:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                score = abs(polarity)
                if polarity > 0.1:
                    sentiment = 'positive'
                elif polarity < -0.1:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
            else:
                # Basic keyword-based fallback
                text_lower = text.lower()
                positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'fantastic']
                negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointed']
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                if pos_count > neg_count:
                    sentiment = 'positive'
                    score = 0.6
                elif neg_count > pos_count:
                    sentiment = 'negative'
                    score = 0.6
                else:
                    sentiment = 'neutral'
                    score = 0.5
        else:
            # Use transformers
            res = sentiment_pipeline(text[:512])[0]
            label = res.get('label','')
            score = float(res.get('score',0.0))
            if label.lower() in ['positive','pos']:
                sentiment = 'positive'
            elif label.lower() in ['negative','neg']:
                sentiment = 'negative'
            else:
                sentiment = 'positive' if score>0.6 else ('negative' if score<0.4 else 'neutral')
    except Exception as e:
        logger.warning(f"Sentiment analysis error: {e}")
        sentiment, score = 'neutral', 0.0

    # Embeddings (skip in lightweight mode)
    emb_bytes = None
    if not USE_LIGHTWEIGHT_NLP and _sentence_transformers_available:
        try:
            embedder = _get_embedder()
            if embedder is not None:
                emb = embedder.encode(text, show_progress_bar=False)
                emb_bytes = pickle.dumps(np.array(emb))
        except Exception:
            emb_bytes = None

    # Topic modeling (skip in lightweight mode)
    topic_label = 'general'
    global _topic_model
    if use_topic and _topic_model is not None and not USE_LIGHTWEIGHT_NLP and _bertopic_available:
        try:
            topics, probs = _topic_model.transform([text])
            t = topics[0]
            topic_info = _topic_model.get_topic(t)
            if isinstance(topic_info, list):
                topic_label = ' '.join([w for w,_ in topic_info[:5]])
            else:
                topic_label = str(topic_info)
        except Exception:
            topic_label = 'general'
    
    return sentiment, score, topic_label, emb_bytes

def fit_topic_model(texts, n_components=5):
    global _topic_model
    if USE_LIGHTWEIGHT_NLP or not _bertopic_available or not _sentence_transformers_available:
        logger.warning("Topic modeling not available in lightweight mode")
        return None
    try:
        embedder = _get_embedder()
        if embedder is None:
            logger.warning("Embedder not available for topic modeling")
            return None
        embeddings = embedder.encode(texts, show_progress_bar=True)
        topic_model = BERTopic(n_components=n_components, calculate_probabilities=False, verbose=False)
        topics, probs = topic_model.fit_transform(texts, embeddings)
        _topic_model = topic_model
        logger.info(f"Fitted topic model with {n_components} components")
        return topic_model
    except Exception as e:
        logger.error(f"Error fitting topic model: {e}")
        raise

def save_topic_model(path):
    global _topic_model
    if _topic_model is None:
        raise RuntimeError('topic model not fitted')
    _topic_model.save(path)

def load_topic_model(path):
    global _topic_model
    _topic_model = BERTopic.load(path)
    return _topic_model
