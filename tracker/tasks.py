from celery import shared_task
from .models import Mention, Alert
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
from .nlp import analyze_text
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

# Cache for Celery availability check
_celery_available = None

def is_celery_available():
    """Check if Celery is available (Redis connection works)"""
    global _celery_available
    if _celery_available is not None:
        return _celery_available
    
    try:
        from celery import current_app
        # Try to get the broker connection
        broker = current_app.broker_connection()
        broker.ensure_connection(max_retries=1)
        broker.release()
        _celery_available = True
        return True
    except Exception:
        _celery_available = False
        return False

@shared_task
def fetch_rss_feed(url):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Fetching RSS feed: {url}")
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        # Try different XML parsers in order of preference
        soup = None
        parser_errors = []
        
        # Try lxml-xml (best for XML)
        try:
            soup = BeautifulSoup(resp.content, 'lxml-xml')
        except Exception as e:
            parser_errors.append(f"lxml-xml: {str(e)}")
        
        # Try xml parser (requires lxml)
        if soup is None:
            try:
                soup = BeautifulSoup(resp.content, 'xml')
            except Exception as e:
                parser_errors.append(f"xml: {str(e)}")
        
        # Fallback to html.parser (may not work perfectly for XML)
        if soup is None:
            try:
                soup = BeautifulSoup(resp.content, 'html.parser')
                logger.warning("Using html.parser for XML - may cause issues. Install lxml for better XML support.")
            except Exception as e:
                parser_errors.append(f"html.parser: {str(e)}")
                raise Exception(f"Could not parse XML. Parser errors: {parser_errors}. Please install lxml: pip install lxml")
        items = soup.find_all('item')
        
        created_count = 0
        for item in items[:30]:
            try:
                title = item.title.text if item.title else ''
                desc = item.description.text if item.description else ''
                pub = item.pubDate.text if item.pubDate else None
                
                # Parse date with proper fallback - parse_datetime can return None
                dt = None
                if pub:
                    try:
                        dt = parse_datetime(pub)
                    except (ValueError, TypeError):
                        dt = None
                
                # Ensure we always have a valid datetime
                if dt is None:
                    dt = timezone.now()
                
                text = f"{title}\n\n{desc}".strip()
                
                if not text:
                    continue
                    
                # Check for duplicates using the date
                mention_date = dt.date()
                
                if not Mention.objects.filter(text__icontains=text[:120], created_at__date=mention_date).exists():
                    m = Mention.objects.create(source='rss', text=text, created_at=dt)
                    
                    # Check Celery availability and process accordingly
                    if is_celery_available():
                        try:
                            process_mention.delay(m.id)
                        except Exception as celery_error:
                            # Fallback if Celery fails at runtime
                            logger.debug(f"Celery task failed for mention {m.id}, processing synchronously: {celery_error}")
                            process_mention(m.id)
                    else:
                        # Celery not available, process synchronously (only log once)
                        if _celery_available is False and created_count == 0:
                            logger.info("Celery/Redis not available - processing mentions synchronously. Start Redis for better performance.")
                        process_mention(m.id)
                    
                    created_count += 1
            except Exception as item_error:
                logger.warning(f"Error processing RSS item: {item_error}")
                continue
        
        logger.info(f"Created {created_count} new mentions from {url}")
        return {'status': 'success', 'created': created_count}
    except requests.RequestException as e:
        logger.error(f"RSS fetch error for {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching RSS feed {url}: {e}")
        raise

@shared_task
def process_mention(mention_id):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        m = Mention.objects.get(id=mention_id)
        result = analyze_text(m.text)
        # analyze_text returns (sentiment, score, topic_label, emb_bytes)
        if len(result) == 4:
            sentiment, score, topic, emb_bytes = result
        else:
            # Fallback for old signature
            sentiment, score, topic = result[:3]
        
        m.sentiment = sentiment
        m.sentiment_score = score
        m.topic = topic or 'general'
        m.processed = True
        m.save()

        # Check for negative sentiment spikes
        if sentiment == 'negative':
            window = timezone.now() - timezone.timedelta(minutes=10)
            neg_count = Mention.objects.filter(created_at__gte=window, sentiment='negative').count()
            if neg_count > 8:
                alert = Alert.objects.create(
                    mention=m, 
                    alert_type='negative_spike', 
                    description=f'{neg_count} negative mentions in last 10 minutes'
                )
                try:
                    broadcast_alert(alert)
                except Exception as alert_error:
                    logger.warning(f"Error broadcasting alert: {alert_error}")
        
        logger.debug(f"Processed mention {mention_id}: {sentiment} ({score:.2f})")
        return {'status': 'success', 'mention_id': mention_id, 'sentiment': sentiment}
    except Mention.DoesNotExist:
        logger.error(f"Mention {mention_id} not found")
        return {'status': 'error', 'message': 'Mention not found'}
    except Exception as e:
        logger.error(f"Error processing mention {mention_id}: {e}", exc_info=True)
        # Mark as processed to avoid infinite retries, but with error state
        try:
            m = Mention.objects.get(id=mention_id)
            m.processed = True
            m.sentiment = 'error'
            m.save()
        except:
            pass
        raise

def broadcast_alert(alert):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        layer = get_channel_layer()
        if layer is None:
            logger.warning("Channel layer not available, skipping alert broadcast")
            return
        
        payload = {
            'type': 'mention_alert',
            'data': {
                'id': alert.id,
                'alert_type': alert.alert_type,
                'description': alert.description,
                'mention_text': alert.mention.text[:200],
                'created_at': alert.created_at.isoformat(),
            }
        }
        async_to_sync(layer.group_send)('mentions', payload)
    except AttributeError as e:
        # Handle case where channel layer methods don't exist
        logger.warning(f"Channel layer method error, skipping alert broadcast: {e}")
    except Exception as e:
        logger.warning(f"Error broadcasting alert: {e}")
        # Don't raise - alerts can still be viewed via API even if WebSocket fails
