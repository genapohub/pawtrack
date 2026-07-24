/**
 * 管理后台 — 宠物管理（只读列表）
 */
import { useEffect, useState } from 'react'
import { Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import dayjs from 'dayjs'

export default function PetsPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)

  const load = async () => {
    setLoading(true)
    try {
      const resp: any = await api.pets.list(page, 10)
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      message.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page])

  const columns: ColumnsType<any> = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '主人ID', dataIndex: 'user_id', width: 80 },
    { title: '名字', dataIndex: 'name', width: 100 },
    {
      title: '类型', dataIndex: 'type', width: 70,
      render: (v: string) => v === 'cat' ? <Tag color="orange">🐱 猫</Tag> : <Tag color="blue">🐶 狗</Tag>
    },
    { title: '品种', dataIndex: 'breed', width: 120 },
    { title: '性别', dataIndex: 'gender', width: 70 },
    {
      title: '围栏', width: 120,
      render: (_, r) => r.fence_enabled ? <Tag color="green">开启 {r.fence_radius}m</Tag> : <Tag>关闭</Tag>
    },
    { title: '状态', dataIndex: 'status', width: 80, render: (v: string) => <Tag>{v === 'active' ? '正常' : '已删'}</Tag> },
    { title: '创建时间', dataIndex: 'created_at', width: 160, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—' }
  ]

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>宠物管理</h2>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        scroll={{ x: 900 }}
        pagination={{ current: page, total, pageSize: 10, showSizeChanger: false, onChange: (p) => setPage(p) }}
      />
    </>
  )
}
