import React, { useEffect, useState } from 'react'
import useSWR from 'swr'
import { API_BASE, WS_BASE } from '../config'

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

export default function Alerts() {
  const [realtimeAlerts, setRealtimeAlerts] = useState([])
  const { data: apiAlerts, error } = useSWR(
    `${API_BASE}/alerts/?ordering=-created_at`,
    fetcher,
    { refreshInterval: 10000 }
  )

  useEffect(() => {
    const wsUrl = `${WS_BASE}/mentions/`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data)
        setRealtimeAlerts((a) => [d, ...a].slice(0, 50))
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }
    
    ws.onopen = () => console.log('WebSocket connected')
    ws.onerror = (err) => console.error('WebSocket error:', err)
    ws.onclose = () => console.log('WebSocket closed')
    
    return () => ws.close()
  }, [])

  const allAlerts = [
    ...realtimeAlerts.map(a => ({ ...a, source: 'realtime' })),
    ...(apiAlerts?.results || apiAlerts || []).map(a => ({ ...a, source: 'api' }))
  ].slice(0, 50)

  const formatDate = (dateString) => {
    if (!dateString) return 'Just now'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    return date.toLocaleString()
  }

  const getAlertColor = (alertType) => {
    if (alertType?.includes('negative') || alertType?.includes('spike')) {
      return 'border-red-500 bg-red-50'
    }
    return 'border-yellow-500 bg-yellow-50'
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-red-500">Error loading alerts: {error.message}</div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold">Real-time Alerts</h2>
        <p className="text-sm text-gray-600">Live alerts for negative spikes and unusual activity</p>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {allAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No alerts yet. Alerts will appear here when negative sentiment spikes are detected.</p>
          </div>
        ) : (
          allAlerts.map((alert, i) => (
            <div
              key={alert.id || i}
              className={`p-4 border-l-4 rounded-lg shadow-sm ${getAlertColor(alert.alert_type)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-red-700 uppercase">
                    {alert.alert_type || 'Alert'}
                  </span>
                  {alert.source === 'realtime' && (
                    <span className="px-2 py-1 text-xs bg-green-500 text-white rounded-full animate-pulse">
                      LIVE
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-600">{formatDate(alert.created_at)}</span>
              </div>
              
              <div className="text-sm text-gray-700 mb-2">{alert.description}</div>
              
              {alert.mention_text && (
                <div className="mt-2 p-2 bg-white rounded border border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">Related Mention:</p>
                  <p className="text-xs text-gray-700 line-clamp-2">{alert.mention_text}</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
