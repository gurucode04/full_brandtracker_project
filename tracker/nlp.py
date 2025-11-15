# tracker/nlp.py - transformer-based NLP
import pickle
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from bertopic import BERTopic
import os
import logging

logger = logging.getLogger(__name__)

SENTIMENT_MODEL_NAME = os.environ.get('SENTIMENT_MODEL','distilbert-base-uncased-finetuned-sst-2-english')
EMBED_MODEL_NAME = os.environ.get('EMBED_MODEL','all-MiniLM-L6-v2')

_sentiment = None
_embedder = None
_topic_model = None

def _get_sentiment_pipeline():
    global _sentiment
    if _sentiment is None:
        try:
            _sentiment = pipeline('text-classification', model=SENTIMENT_MODEL_NAME, truncation=True)
            logger.info(f"Loaded sentiment model: {SENTIMENT_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            raise
    return _sentiment

def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            _embedder = SentenceTransformer(EMBED_MODEL_NAME)
            logger.info(f"Loaded embedding model: {EMBED_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    return _embedder

def encode_text(text):
    embedder = _get_embedder()
    emb = embedder.encode(text, show_progress_bar=False)
    return np.array(emb)

def analyze_text(text, use_topic=True):
    text = (text or '').strip()
    if not text:
        return 'neutral', 0.0, 'general', None
    
    # Sentiment analysis
    try:
        sentiment_pipeline = _get_sentiment_pipeline()
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

    try:
        emb = encode_text(text)
        emb_bytes = pickle.dumps(emb)
    except Exception:
        emb_bytes = None

    topic_label = 'general'
    global _topic_model
    if use_topic and _topic_model is not None:
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
    try:
        embedder = _get_embedder()
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
