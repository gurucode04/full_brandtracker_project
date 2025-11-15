from django import forms

class RSSFeedForm(forms.Form):
    url = forms.URLField(
        label='RSS Feed URL',
        widget=forms.URLInput(attrs={
            'class': 'flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter RSS feed URL (e.g., https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml)'
        }),
        required=True
    )

