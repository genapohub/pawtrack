/**
 * 管理后台 — 用户管理
 */
import { useEffect, useState } from 'react'
import { Table, Input, Select, Space, Button, Tag, Popconfirm, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import dayjs from 'dayjs'

export default function UsersPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(1)

  const load = async () => {
    setLoading(true)
    try {
      const resp: any = await api.users.list({ keyword: keyword || undefined, status: status || undefined, page, size: 10 })
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      message.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, status])

  const toggleBan = async (userId: number, current: string) => {
    const action = current === 'blocked' ? 'unban' : 'ban'
    try {
      await api.users.ban(userId, action)
      message.success(action === 'ban' ? '已封禁' : '已解封')
      load()
    } catch (e: any) {
      message.error(e.message)
    }
  }

  const columns: ColumnsType<any> = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '昵称', dataIndex: 'nickname', width: 120 },
    { title: '手机号', dataIndex: 'phone', width: 140 },
    {
      title: '会员', dataIndex: 'member_level', width: 90,
      render: (v: string) => v === 'pro' ? <Tag color="purple">Pro</Tag> : v === 'basic' ? <Tag color="blue">基础</Tag> : <Tag>免费</Tag>
    },
    { title: '积分', dataIndex: 'points', width: 80 },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (v: string) => v === 'blocked' ? <Tag color="red">已封禁</Tag> : <Tag color="green">正常</Tag>
    },
    {
      title: '会员到期', dataIndex: 'member_expire_at', width: 160,
      render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—'
    },
    {
      title: '注册时间', dataIndex: 'created_at', width: 160,
      render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—'
    },
    {
      title: '操作', width: 100, fixed: 'right',
      render: (_, r) => (
        <Popconfirm title={`确认${r.status === 'blocked' ? '解封' : '封禁'}该用户？`} onConfirm={() => toggleBan(r.id, r.status)}>
          <Button size="small" danger={r.status !== 'blocked'}>
            {r.status === 'blocked' ? '解封' : '封禁'}
          </Button>
        </Popconfirm>
      )
    }
  ]

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>用户管理</h2>
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search
          placeholder="搜索手机号/昵称"
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
          options={[{ value: 'active', label: '正常' }, { value: 'blocked', label: '已封禁' }]}
        />
        <Button onClick={load}>刷新</Button>
      </Space>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        scroll={{ x: 1100 }}
        pagination={{
          current: page, total, pageSize: 10, showSizeChanger: false,
          onChange: (p) => setPage(p)
        }}
      />
    </>
  )
}
