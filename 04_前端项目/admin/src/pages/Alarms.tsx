/**
 * 管理后台 — 报警列表（对齐 209:1 / 210:1 / 211:1）
 */
import { useEffect, useState } from 'react'
import { Table, Button, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import { exportCSV } from '../utils/export'
import { PT } from '../styles/tokens'
import dayjs from 'dayjs'

const TYPE_LABEL: Record<string, string> = {
  leave_fence: '离开围栏', leave_fence_cat: '离开围栏', enter_fence: '进入围栏',
  low_battery: '低电量', low_battery_critical: '低电量',
  offline_warning: '设备离线', tamper_detected: '设备拆卸', fall_detected: '跌落检测'
}

export default function AlarmsPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const resp: any = await api.alarms.list({ page, size: 10 })
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      setData([])
      setError('报警列表拉取失败，请重试。不可用空列表代替失败态。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page])

  const statusTag = (s: string) => {
    if (s === 'active') return <Tag style={{ background: PT.warningSubtle, color: PT.warning, border: 0 }}>未处理</Tag>
    if (s === 'false_positive') return <Tag style={{ background: PT.bgMuted, color: PT.fg3, border: 0 }}>误报</Tag>
    return <Tag style={{ background: PT.successSubtle, color: PT.success, border: 0 }}>已处理</Tag>
  }

  const columns: ColumnsType<any> = [
    {
      title: '时间', dataIndex: 'created_at', width: 140,
      render: (v: string) => v ? dayjs(v).format('MM-DD HH:mm') : '—',
    },
    {
      title: '宠物 / 设备',
      render: (_, r) => `${r.pet_name || '宠物'}${r.device_sn ? ' / ' + r.device_sn : ''}`,
    },
    { title: '类型', dataIndex: 'type', render: (v: string) => TYPE_LABEL[v] || v },
    { title: '状态', dataIndex: 'status', width: 100, render: (v: string) => statusTag(v) },
    { title: '示意地址', dataIndex: 'address', render: (v: string) => v || '—' },
  ]

  return (
    <>
      <p className="pt-page-note">状态用词与小程序一致：离开围栏、进入围栏、低电量、设备离线、设备拆卸。地址为示意。</p>
      <div style={{ marginBottom: 16 }}>
        <Button onClick={load} style={{ marginRight: 8 }}>刷新</Button>
        <Button onClick={() => {
          if (!data.length) return
          exportCSV('报警列表（Mock 示意）', [
            { title: '时间', dataIndex: 'created_at' },
            { title: '宠物', dataIndex: 'pet_name' },
            { title: '类型', dataIndex: 'type' },
            { title: '状态', dataIndex: 'status' },
            { title: '示意地址', dataIndex: 'address' },
          ], data)
        }}>导出 CSV（示意）</Button>
      </div>
      {error ? (
        <div style={{ background: PT.dangerSubtle, color: PT.danger, borderRadius: 14, padding: 16, marginBottom: 16 }}>
          <div style={{ marginBottom: 12 }}>{error}</div>
          <Button type="primary" onClick={load}>重新加载</Button>
        </div>
      ) : (
        <Table
          rowKey="id"
          columns={columns}
          dataSource={data}
          loading={loading}
          locale={{ emptyText: '暂无报警。这是空列表，不是加载失败。' }}
          pagination={{ current: page, total, pageSize: 10, showSizeChanger: false, onChange: (p) => setPage(p) }}
        />
      )}
    </>
  )
}
