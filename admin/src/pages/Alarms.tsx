/**
 * 管理后台 — 报警管理
 */
import { useEffect, useState } from 'react'
import { Table, Select, Space, Button, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import dayjs from 'dayjs'

const TYPE_LABEL: Record<string, string> = {
  leave_fence: '离开围栏', leave_fence_cat: '猫咪离开围栏', enter_fence: '进入围栏',
  low_battery: '电量偏低', low_battery_critical: '电量严重不足',
  offline_warning: '设备离线', tamper_detected: '设备拆卸', fall_detected: '跌落检测'
}

export default function AlarmsPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(1)

  const load = async () => {
    setLoading(true)
    try {
      const resp: any = await api.alarms.list({ status: status || undefined, page, size: 10 })
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      message.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, status])

  const sevTag = (s: string) => s === 'high' ? <Tag color="red">高</Tag> : s === 'medium' ? <Tag color="orange">中</Tag> : <Tag>低</Tag>
  const statusTag = (s: string) => s === 'active' ? <Tag color="orange">待处理</Tag> : s === 'false_positive' ? <Tag>误报</Tag> : <Tag color="green">已处理</Tag>

  const columns: ColumnsType<any> = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '宠物ID', dataIndex: 'pet_id', width: 80 },
    { title: '用户ID', dataIndex: 'user_id', width: 80 },
    { title: '类型', dataIndex: 'type', width: 130, render: (v: string) => TYPE_LABEL[v] || v },
    { title: '严重程度', dataIndex: 'severity', width: 90, render: (v: string) => sevTag(v) },
    { title: '状态', dataIndex: 'status', width: 90, render: (v: string) => statusTag(v) },
    {
      title: '位置', width: 180,
      render: (_, r) => r.lat ? `${Number(r.lat).toFixed(5)}, ${Number(r.lng).toFixed(5)}` : '—'
    },
    { title: '处理时间', dataIndex: 'handled_at', width: 160, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—' },
    { title: '触发时间', dataIndex: 'created_at', width: 160, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—' }
  ]

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>报警管理</h2>
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="状态筛选"
          allowClear
          style={{ width: 140 }}
          value={status || undefined}
          onChange={v => { setStatus(v || ''); setPage(1) }}
          options={[{ value: 'active', label: '待处理' }, { value: 'handled', label: '已处理' }, { value: 'false_positive', label: '误报' }]}
        />
        <Button onClick={load}>刷新</Button>
      </Space>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        scroll={{ x: 1100 }}
        pagination={{ current: page, total, pageSize: 10, showSizeChanger: false, onChange: (p) => setPage(p) }}
      />
    </>
  )
}
