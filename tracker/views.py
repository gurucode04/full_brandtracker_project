from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Mention, Alert
from .serializers import MentionSerializer, AlertSerializer
from .tasks import fetch_rss_feed
from .utils import get_built_assets

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
    css_file, js_file = get_built_assets()
    context = {
        'css_file': css_file,
        'js_file': js_file,
    }
    return render(request, 'tracker/index.html', context)

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
