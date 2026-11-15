import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './index.css'
import { PT } from './styles/tokens'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: PT.accent,
          colorSuccess: PT.success,
          colorWarning: PT.warning,
          colorError: PT.danger,
          colorBgBase: PT.bg,
          colorBgContainer: PT.surface,
          colorBgLayout: PT.bg,
          colorBorder: PT.border,
          colorText: PT.fg,
          colorTextSecondary: PT.fg2,
          colorTextTertiary: PT.fg3,
          borderRadius: PT.radiusMd,
          fontFamily: PT.font,
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>
)
