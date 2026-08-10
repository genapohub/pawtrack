/**
 * 管理后台 — 碰头记录审核（V2.0 对接后端真实接口）
 * GET /admin/meets → 列表（含异常自动标记）
 * PUT /admin/meets/{id}/audit → 通过/驳回（驳回自动扣回积分）
 */
import { useState, useEffect, useCallback } from 'react'
import { Card, Table, Tag, Button, message, Select } from 'antd'
import { api } from '../api/client'

export default function SocialAuditPage() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('')

  const fetchMeets = useCallback(async () => {
    setLoading(true)
    try {
      const res: any = await api.meets.list({ status: statusFilter || undefined!, page: 1, size: 50 })
      const items = (res.data?.items || res.items || []).map((m: any, idx: number) => ({
        key: m.id || idx,
        id: m.id,
        time: formatTime(m.created_at),
        from: m.from_pet || '-',
        to: m.to_pet || '-',
        distance: m.distance !== null ? `${m.distance}m` : '-',
        points: m.points || 0,
        abnormal: m.abnormal || '',
        color: m.color || 'green',
        status: m.status || '-'
      }))
      setData(items)
    } catch (e: any) {
      message.error(e.message || '加载碰头记录失败')
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => { fetchMeets() }, [fetchMeets])

  function formatTime(iso: string): string {
    if (!iso) return '-'
    const d = new Date(iso)
    const pad = (n: number) => String(n).padStart(2, '0')
    return `${d.getMonth() + 1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  }

  async function handleAudit(meetId: number, action: 'approve' | 'reject') {
    try {
      if (action === 'reject') {
        await api.meets.audit(meetId, 'reject')
        message.success('已驳回并自动扣回积分')
      } else {
        await api.meets.audit(meetId, 'approve')
        message.success('已通过')
      }
      fetchMeets()
    } catch (e: any) {
      message.error(e.message || '操作失败')
    }
  }

  const columns = [
    { title: '时间', dataIndex: 'time', width: 130 },
    { title: '发起方', dataIndex: 'from' },
    { title: '接收方', dataIndex: 'to' },
    { title: '距离', dataIndex: 'distance', width: 80 },
    { title: '积分', dataIndex: 'points', render: (v: number) => v > 0 ? `+${v}` : '-' },
    { title: '状态', dataIndex: 'status', render: (v: string) => {
      const map: Record<string, string> = { success: '已完成', confirmed: '进行中', pending: '待确认', failed: '已失败', cancelled: '已取消' }
      return <Tag color={v === 'success' ? 'green' : v === 'confirmed' ? 'blue' : 'default'}>{map[v] || v}</Tag>
    }},
    { title: '异常标记', dataIndex: 'abnormal', render: (v: string, r: any) =>
      v ? <Tag color="red">{v}</Tag> : <Tag color="green">正常</Tag> },
    { title: '操作', width: 140, render: (_: any, r: any) => (
      <div style={{ display: 'flex', gap: 8 }}>
        {r.abnormal ? (
          <Button size="small" danger onClick={() => handleAudit(r.id, 'reject')}>驳回</Button>
        ) : null}
        <Button size="small" type="primary" onClick={() => handleAudit(r.id, 'approve')}>通过</Button>
      </div>
    )}
  ]

  return (
    <Card title="碰头记录审核" extra={
      <Select
        placeholder="状态筛选"
        allowClear
        style={{ width: 120 }}
        size="small"
        value={statusFilter || undefined}
        onChange={(v) => setStatusFilter(v || '')}
        options={[
          { value: 'success', label: '已完成' },
          { value: 'confirmed', label: '进行中' },
          { value: 'pending', label: '待确认' },
          { value: 'failed', label: '已失败' },
        ]}
      />
    }>
      <Table size="small" rowKey="key" columns={columns} dataSource={data} loading={loading} pagination={false} />
      <div style={{ marginTop: 16, color: '#888', fontSize: 12 }}>
        异常自动判定规则：相遇距离 &lt; 5m 标记距离异常 · 同对宠物 24h ≥ 3 次标记频繁碰头 · 驳回自动扣回双方积分
      </div>
    </Card>
  )
}
