import React, { useState } from 'react'
import Dashboard from './components/Dashboard'
import MentionsList from './components/MentionsList'
import Alerts from './components/Alerts'
import FeedManager from './components/FeedManager'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'mentions', label: 'Mentions', icon: '💬' },
    { id: 'alerts', label: 'Alerts', icon: '🚨' },
    { id: 'feeds', label: 'RSS Feeds', icon: '📡' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Brand Mention & Reputation Tracker</h1>
          <p className="text-sm text-gray-600 mt-1">Monitor brand mentions across multiple platforms in real-time</p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'mentions' && <MentionsList />}
        {activeTab === 'alerts' && <Alerts />}
        {activeTab === 'feeds' && <FeedManager />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Brand Mention Tracker - Real-time monitoring and sentiment analysis
          </p>
        </div>
      </footer>
    </div>
  )
}
