/**
 * 管理后台 — 设备管理
 */
import { useEffect, useState } from 'react'
import { Table, Input, Select, Space, Button, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import dayjs from 'dayjs'

export default function DevicesPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(1)

  const load = async () => {
    setLoading(true)
    try {
      const resp: any = await api.devices.list({ keyword: keyword || undefined, status: status || undefined, page, size: 10 })
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      message.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, status])

  const statusTag = (s: string) => {
    if (s === 'online') return <Tag color="green">在线</Tag>
    if (s === 'low_battery') return <Tag color="orange">低电量</Tag>
    return <Tag>离线</Tag>
  }

  const columns: ColumnsType<any> = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: 'SN', dataIndex: 'sn', width: 180 },
    { title: '主人ID', dataIndex: 'user_id', width: 80 },
    { title: '宠物ID', dataIndex: 'pet_id', width: 80, render: (v) => v || '—' },
    { title: '硬件类型', dataIndex: 'hardware_type', width: 90, render: (v) => v === 'cat' ? '🐱' : '🐶' },
    { title: '固件', dataIndex: 'firmware_version', width: 90 },
    {
      title: '电量', dataIndex: 'battery_level', width: 80,
      render: (v: number) => v <= 20 ? <Tag color="red">{v}%</Tag> : v <= 40 ? <Tag color="orange">{v}%</Tag> : <span>{v}%</span>
    },
    { title: '状态', dataIndex: 'status', width: 90, render: (v: string) => statusTag(v) },
    { title: '最后在线', dataIndex: 'last_online_at', width: 160, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—' }
  ]

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>设备管理</h2>
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search
          placeholder="搜索设备 SN"
          allowClear
          value={keyword}
          onChange={e => setKeyword(e.target.value)}
          onSearch={() => { setPage(1); load() }}
          style={{ width: 240 }}
        />
        <Select
          placeholder="状态筛选"
          allowClear
          style={{ width: 140 }}
          value={status || undefined}
          onChange={v => { setStatus(v || ''); setPage(1) }}
          options={[{ value: 'online', label: '在线' }, { value: 'offline', label: '离线' }, { value: 'low_battery', label: '低电量' }]}
        />
        <Button onClick={load}>刷新</Button>
      </Space>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        scroll={{ x: 1000 }}
        pagination={{ current: page, total, pageSize: 10, showSizeChanger: false, onChange: (p) => setPage(p) }}
      />
    </>
  )
}
