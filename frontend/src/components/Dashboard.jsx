import React, { useEffect, useState } from 'react'
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

export default function Dashboard() {
  const { data: stats, error, mutate } = useSWR(`${API_BASE}/dashboard-stats/`, fetcher, {
    refreshInterval: 30000
  })

  if (error) return <div className="text-red-500">Error loading dashboard: {error.message}</div>
  if (!stats) return <div className="text-gray-500">Loading dashboard...</div>

  const sentimentTotal = stats.sentiment.positive + stats.sentiment.negative + stats.sentiment.neutral
  const positivePercent = sentimentTotal > 0 ? ((stats.sentiment.positive / sentimentTotal) * 100).toFixed(1) : 0
  const negativePercent = sentimentTotal > 0 ? ((stats.sentiment.negative / sentimentTotal) * 100).toFixed(1) : 0
  const neutralPercent = sentimentTotal > 0 ? ((stats.sentiment.neutral / sentimentTotal) * 100).toFixed(1) : 0

  const maxHourlyCount = Math.max(...stats.hourly_mentions.map(h => h.count), 1)

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500">Total Mentions</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">{stats.mentions.total}</p>
          <p className="text-xs text-gray-500 mt-1">{stats.mentions.last_24h} in last 24h</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500">Positive</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">{stats.sentiment.positive}</p>
          <p className="text-xs text-gray-500 mt-1">{positivePercent}% of total</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
          <h3 className="text-sm font-medium text-gray-500">Negative</h3>
          <p className="text-3xl font-bold text-red-600 mt-2">{stats.sentiment.negative}</p>
          <p className="text-xs text-gray-500 mt-1">{negativePercent}% of total</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
          <h3 className="text-sm font-medium text-gray-500">Active Alerts</h3>
          <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.alerts.unresolved}</p>
          <p className="text-xs text-gray-500 mt-1">{stats.alerts.recent_24h} in last 24h</p>
        </div>
      </div>

      {/* Sentiment Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Sentiment Breakdown</h2>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-green-600 font-medium">Positive</span>
              <span>{stats.sentiment.positive} ({positivePercent}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-green-500 h-3 rounded-full transition-all"
                style={{ width: `${positivePercent}%` }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 font-medium">Neutral</span>
              <span>{stats.sentiment.neutral} ({neutralPercent}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gray-400 h-3 rounded-full transition-all"
                style={{ width: `${neutralPercent}%` }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-red-600 font-medium">Negative</span>
              <span>{stats.sentiment.negative} ({negativePercent}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-red-500 h-3 rounded-full transition-all"
                style={{ width: `${negativePercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Hourly Mentions Chart */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Mentions Over Last 24 Hours</h2>
        <div className="flex items-end justify-between h-48 space-x-1">
          {stats.hourly_mentions.map((hour, idx) => (
            <div key={idx} className="flex-1 flex flex-col items-center">
              <div 
                className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                style={{ height: `${(hour.count / maxHourlyCount) * 100}%` }}
                title={`${hour.count} mentions at ${hour.hour}:00`}
              />
              <span className="text-xs text-gray-500 mt-1">{hour.hour}:00</span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Topics */}
      {stats.topics && stats.topics.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">Top Topics</h2>
          <div className="space-y-2">
            {stats.topics.slice(0, 10).map((topic, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium text-gray-700">{topic.topic || 'Unknown'}</span>
                <span className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full">
                  {topic.count} mentions
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {stats.sources && stats.sources.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">Sources</h2>
          <div className="flex flex-wrap gap-2">
            {stats.sources.map((source, idx) => (
              <span 
                key={idx}
                className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {source.source}: {source.count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

