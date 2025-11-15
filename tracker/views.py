from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.safestring import mark_safe
import json
from datetime import timedelta
from .models import Mention, Alert
from .serializers import MentionSerializer, AlertSerializer
from .tasks import fetch_rss_feed
from .forms import RSSFeedForm

class MentionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mention.objects.order_by('-created_at')
    serializer_class = MentionSerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        limit = int(request.query_params.get('limit', 50))
        mentions = Mention.objects.filter(processed=True).order_by('-created_at')[:limit]
        serializer = self.get_serializer(mentions, many=True)
        return Response(serializer.data)

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.order_by('-created_at')
    serializer_class = AlertSerializer

def index(request):
    """Main index view - redirects to dashboard"""
    return redirect('dashboard')

def dashboard_view(request):
    """Dashboard with stats"""
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # Total mentions
    total_mentions = Mention.objects.count()
    mentions_24h = Mention.objects.filter(created_at__gte=last_24h).count()
    mentions_7d = Mention.objects.filter(created_at__gte=last_7d).count()
    
    # Sentiment breakdown
    sentiment_counts = Mention.objects.filter(processed=True).values('sentiment').annotate(
        count=Count('sentiment')
    )
    sentiment_dict = {s['sentiment'] or 'unknown': s['count'] for s in sentiment_counts}
    
    # Topic distribution
    topic_counts = Mention.objects.filter(
        processed=True, 
        topic__isnull=False
    ).exclude(topic='').values('topic').annotate(
        count=Count('topic')
    ).order_by('-count')[:10]
    
    # Alerts
    total_alerts = Alert.objects.count()
    unresolved_alerts = Alert.objects.filter(resolved=False).count()
    recent_alerts = Alert.objects.filter(created_at__gte=last_24h).count()
    
    # Hourly mentions for chart
    hourly_mentions = []
    for i in range(24):
        hour_start = last_24h + timedelta(hours=i)
        hour_end = hour_start + timedelta(hours=1)
        count = Mention.objects.filter(created_at__gte=hour_start, created_at__lt=hour_end).count()
        hourly_mentions.append({
            'hour': hour_start.hour,
            'count': count
        })
    
    # Sources breakdown
    source_counts = Mention.objects.values('source').annotate(
        count=Count('source')
    )
    
    sentiment_total = sentiment_dict.get('positive', 0) + sentiment_dict.get('negative', 0) + sentiment_dict.get('neutral', 0)
    
    context = {
        'total_mentions': total_mentions,
        'mentions_24h': mentions_24h,
        'mentions_7d': mentions_7d,
        'sentiment': {
            'positive': sentiment_dict.get('positive', 0),
            'negative': sentiment_dict.get('negative', 0),
            'neutral': sentiment_dict.get('neutral', 0),
            'total': sentiment_total,
        },
        'topics': list(topic_counts),
        'total_alerts': total_alerts,
        'unresolved_alerts': unresolved_alerts,
        'recent_alerts': recent_alerts,
        'hourly_mentions': mark_safe(json.dumps(hourly_mentions)),
        'sources': list(source_counts),
    }
    return render(request, 'tracker/dashboard.html', context)

def mentions_view(request):
    """Mentions list view with filtering"""
    filter_sentiment = request.GET.get('filter', 'all')
    limit = int(request.GET.get('limit', 100))
    
    mentions = Mention.objects.filter(processed=True).order_by('-created_at')
    
    if filter_sentiment != 'all':
        mentions = mentions.filter(sentiment=filter_sentiment)
    
    mentions = mentions[:limit]
    
    context = {
        'mentions': mentions,
        'current_filter': filter_sentiment,
    }
    return render(request, 'tracker/mentions.html', context)

def alerts_view(request):
    """Alerts view"""
    alerts = Alert.objects.order_by('-created_at')[:50]
    context = {
        'alerts': alerts,
    }
    return render(request, 'tracker/alerts.html', context)

def feeds_view(request):
    """RSS Feed Manager view"""
    if request.method == 'POST':
        form = RSSFeedForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                from tracker.tasks import is_celery_available
                import logging
                logger = logging.getLogger(__name__)
                
                if is_celery_available():
                    try:
                        fetch_rss_feed.delay(url)
                        messages.success(request, f'Fetch started for: {url}')
                    except Exception as celery_error:
                        logger.warning(f"Celery task failed, running synchronously: {celery_error}")
                        result = fetch_rss_feed(url)
                        messages.success(request, f'Feed processed (synchronous): {url}')
                else:
                    logger.debug("Celery/Redis not available - processing RSS feed synchronously")
                    result = fetch_rss_feed(url)
                    messages.success(request, f'Feed processed (synchronous): {url}')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error starting fetch: {e}", exc_info=True)
                messages.error(request, f'Error: {str(e)}')
            return redirect('feeds')
    else:
        form = RSSFeedForm()
    
    context = {
        'form': form,
        'default_feeds': [
            'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
            'https://feeds.bbci.co.uk/news/technology/rss.xml',
            'https://www.theguardian.com/technology/rss',
        ],
    }
    return render(request, 'tracker/feeds.html', context)

from rest_framework.views import APIView
class StartFetch(APIView):
    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'url required'}, status=400)
        try:
            # Check if Celery is available before trying to use it
            from tracker.tasks import is_celery_available
            import logging
            logger = logging.getLogger(__name__)
            
            if is_celery_available():
                try:
                    fetch_rss_feed.delay(url)
                    return Response({'status': 'fetch started', 'url': url})
                except Exception as celery_error:
                    # Fallback if Celery fails at runtime
                    logger.warning(f"Celery task failed, running synchronously: {celery_error}")
                    result = fetch_rss_feed(url)
                    return Response({'status': 'fetch completed (synchronous)', 'url': url, 'result': result})
            else:
                # Celery not available, run synchronously (only log once per request)
                logger.debug("Celery/Redis not available - processing RSS feed synchronously")
                result = fetch_rss_feed(url)
                return Response({'status': 'fetch completed (synchronous)', 'url': url, 'result': result})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error starting fetch: {e}", exc_info=True)
            return Response({'error': str(e)}, status=500)

class DashboardStats(APIView):
    def get(self, request):
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Total mentions
        total_mentions = Mention.objects.count()
        mentions_24h = Mention.objects.filter(created_at__gte=last_24h).count()
        mentions_7d = Mention.objects.filter(created_at__gte=last_7d).count()
        
        # Sentiment breakdown
        sentiment_counts = Mention.objects.filter(processed=True).values('sentiment').annotate(
            count=Count('sentiment')
        )
        sentiment_dict = {s['sentiment'] or 'unknown': s['count'] for s in sentiment_counts}
        
        # Topic distribution
        topic_counts = Mention.objects.filter(
            processed=True, 
            topic__isnull=False
        ).exclude(topic='').values('topic').annotate(
            count=Count('topic')
        ).order_by('-count')[:10]
        
        # Alerts
        total_alerts = Alert.objects.count()
        unresolved_alerts = Alert.objects.filter(resolved=False).count()
        recent_alerts = Alert.objects.filter(created_at__gte=last_24h).count()
        
        # Spikes detection (mentions per hour in last 24h)
        hourly_mentions = []
        for i in range(24):
            hour_start = last_24h + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            count = Mention.objects.filter(created_at__gte=hour_start, created_at__lt=hour_end).count()
            hourly_mentions.append({
                'hour': hour_start.hour,
                'count': count
            })
        
        # Sources breakdown
        source_counts = Mention.objects.values('source').annotate(
            count=Count('source')
        )
        
        return Response({
            'mentions': {
                'total': total_mentions,
                'last_24h': mentions_24h,
                'last_7d': mentions_7d,
            },
            'sentiment': {
                'positive': sentiment_dict.get('positive', 0),
                'negative': sentiment_dict.get('negative', 0),
                'neutral': sentiment_dict.get('neutral', 0),
            },
            'topics': list(topic_counts),
            'alerts': {
                'total': total_alerts,
                'unresolved': unresolved_alerts,
                'recent_24h': recent_alerts,
            },
            'hourly_mentions': hourly_mentions,
            'sources': list(source_counts),
        })
