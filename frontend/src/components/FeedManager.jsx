import React, { useState } from 'react'
import { API_BASE } from '../config'

const DEFAULT_FEEDS = [
  'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
  'https://feeds.bbci.co.uk/news/technology/rss.xml',
  'https://www.theguardian.com/technology/rss',
]

export default function FeedManager() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) {
      setMessage({ type: 'error', text: 'Please enter a valid RSS feed URL' })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const response = await fetch(`${API_BASE}/start-fetch/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: `Fetch started for: ${data.url}` })
        setUrl('')
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to start fetch' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  const handleQuickAdd = (feedUrl) => {
    setUrl(feedUrl)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">RSS Feed Manager</h2>
      
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter RSS feed URL (e.g., https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml)"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Adding...' : 'Add Feed'}
          </button>
        </div>
      </form>

      {message && (
        <div
          className={`mb-4 p-3 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-red-100 text-red-800 border border-red-300'
          }`}
        >
          {message.text}
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Quick Add Popular Feeds:</h3>
        <div className="flex flex-wrap gap-2">
          {DEFAULT_FEEDS.map((feedUrl, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickAdd(feedUrl)}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              {new URL(feedUrl).hostname}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> The system will fetch the latest items from the RSS feed and analyze them for sentiment and topics. 
          Processing may take a few moments.
        </p>
      </div>
    </div>
  )
}

