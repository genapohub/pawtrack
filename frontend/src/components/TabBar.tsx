/**
 * 宠迹 PawTrack — TabBar 底部导航
 */
import React from 'react'

export type TabKey = 'home' | 'pets' | 'social' | 'device' | 'me'

interface TabBarProps {
  active: TabKey
  onChange: (tab: TabKey) => void
}

const TABS: { key: TabKey; icon: string; label: string }[] = [
  { key: 'home', icon: '📍', label: '首页' },
  { key: 'pets', icon: '🐾', label: '宠物' },
  { key: 'social', icon: '🤝', label: '社交' },
  { key: 'device', icon: '🔗', label: '设备' },
  { key: 'me', icon: '👤', label: '我的' }
]

export const TabBar: React.FC<TabBarProps> = ({ active, onChange }) => {
  return (
    <div className="tab-bar">
      {TABS.map(tab => (
        <button
          key={tab.key}
          className={`tab-item ${active === tab.key ? 'active' : ''}`}
          onClick={() => onChange(tab.key)}
        >
          <span className="tab-icon">{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  )
}
