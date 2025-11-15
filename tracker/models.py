from django.db import models

class Mention(models.Model):
    source = models.CharField(max_length=50, default='rss')
    external_id = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    language = models.CharField(max_length=10, default='en')
    sentiment = models.CharField(max_length=20, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    topic = models.CharField(max_length=255, blank=True, null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.source} @ {self.created_at}: {self.text[:50]}"

class Alert(models.Model):
    mention = models.ForeignKey(Mention, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.alert_type} @ {self.created_at}"
