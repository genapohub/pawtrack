/**
 * 管理后台 — 设备列表（对齐 205:1 / 206:1 / 207:1）
 */
import { useEffect, useState } from 'react'
import { Table, Button, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import { exportCSV } from '../utils/export'
import { PT } from '../styles/tokens'
import dayjs from 'dayjs'

export default function DevicesPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const resp: any = await api.devices.list({ page, size: 10 })
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      setData([])
      setError('设备列表拉取失败，请重试。当前为本地服务失败态，不是硬件掉线统计。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page])

  const statusTag = (s: string) => {
    if (s === 'online') return <Tag style={{ background: PT.successSubtle, color: PT.success, border: 0 }}>在线</Tag>
    if (s === 'low_battery') return <Tag style={{ background: PT.warningSubtle, color: PT.warning, border: 0 }}>低电</Tag>
    return <Tag style={{ background: PT.bgMuted, color: PT.fg3, border: 0 }}>离线</Tag>
  }

  const petLabel = (r: any) => {
    if (!r.pet_id && !r.pet_name) return '未绑定'
    const kind = r.pet_type === 'cat' || r.hardware_type === 'cat' ? '猫' : r.pet_type === 'dog' || r.hardware_type === 'dog' ? '狗' : ''
    const name = r.pet_name || '已绑定'
    return kind ? `${name} · ${kind}` : name
  }

  const columns: ColumnsType<any> = [
    { title: 'SN', dataIndex: 'sn' },
    { title: '绑定宠物', render: (_, r) => petLabel(r) },
    { title: '状态', dataIndex: 'status', width: 100, render: (v: string) => statusTag(v) },
    { title: '电量', dataIndex: 'battery_level', width: 90, render: (v: number | null) => v == null ? '—' : `${v}%` },
    {
      title: '最后上报（示意）',
      dataIndex: 'last_online_at',
      render: (v: string, r) => {
        if (!v) return '—'
        const label = dayjs(v).format('HH:mm')
        if (r.status === 'offline') return `昨天 ${label}（超过 30 分钟无上报）`
        return `今天 ${label}`
      }
    },
  ]

  return (
    <>
      <p className="pt-page-note">列表中的 SN、在线、电量均为 Mock，用词与小程序一致（在线 / 离线 / 低电）。</p>
      <div style={{ marginBottom: 16 }}>
        <Button onClick={load} style={{ marginRight: 8 }}>刷新</Button>
        <Button onClick={() => {
          if (!data.length) return
          exportCSV('设备列表（Mock 示意）', [
            { title: 'SN', dataIndex: 'sn' },
            { title: '绑定宠物', dataIndex: 'pet_name' },
            { title: '状态', dataIndex: 'status' },
            { title: '电量', dataIndex: 'battery_level' },
            { title: '最后上报', dataIndex: 'last_online_at' },
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
          locale={{ emptyText: '暂无数据。这是空列表，不是加载失败。' }}
          pagination={{ current: page, total, pageSize: 10, showSizeChanger: false, onChange: (p) => setPage(p) }}
        />
      )}
    </>
  )
}
