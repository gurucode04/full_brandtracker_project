import React, { useState } from 'react'
import useSWR from 'swr'
import { API_BASE } from '../config'

const fetcher = async (url) => {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Fetch error:', error)
    throw error
  }
}

export default function MentionsList() {
  const [filter, setFilter] = useState('all') // all, positive, negative, neutral
  const { data, error, mutate } = useSWR(
    `${API_BASE}/mentions/recent/?limit=100`,
    fetcher,
    { refreshInterval: 15000 }
  )

  if (error) return <div className="text-red-500">Error loading mentions: {error.message}</div>
  if (!data) return <div className="text-gray-500">Loading mentions...</div>

  const mentions = Array.isArray(data) ? data : (data.results || [])

  const filteredMentions = filter === 'all' 
    ? mentions 
    : mentions.filter(m => m.sentiment === filter)

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return 'bg-green-100 text-green-800 border-green-300'
      case 'negative': return 'bg-red-100 text-red-800 border-red-300'
      case 'neutral': return 'bg-gray-100 text-gray-800 border-gray-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Recent Mentions</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded text-sm font-medium ${
              filter === 'all' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('positive')}
            className={`px-4 py-2 rounded text-sm font-medium ${
              filter === 'positive' 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Positive
          </button>
          <button
            onClick={() => setFilter('neutral')}
            className={`px-4 py-2 rounded text-sm font-medium ${
              filter === 'neutral' 
                ? 'bg-gray-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Neutral
          </button>
          <button
            onClick={() => setFilter('negative')}
            className={`px-4 py-2 rounded text-sm font-medium ${
              filter === 'negative' 
                ? 'bg-red-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Negative
          </button>
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredMentions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No mentions found {filter !== 'all' && `with ${filter} sentiment`}
          </div>
        ) : (
          filteredMentions.map((mention) => (
            <div
              key={mention.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold border ${getSentimentColor(
                      mention.sentiment
                    )}`}
                  >
                    {mention.sentiment || 'Processing...'}
                  </span>
                  {mention.sentiment_score && (
                    <span className="text-xs text-gray-500">
                      {(mention.sentiment_score * 100).toFixed(0)}%
                    </span>
                  )}
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {mention.source}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {formatDate(mention.created_at)}
                </span>
              </div>
              
              <p className="text-sm text-gray-700 mb-2 line-clamp-3">
                {mention.text}
              </p>
              
              {mention.topic && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Topic:</span>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {mention.topic}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

