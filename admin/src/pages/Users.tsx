/**
 * 管理后台 — 用户管理（列表/编辑/封禁/导出）
 */
import { useEffect, useState } from 'react'
import { Table, Input, Select, Space, Button, Tag, Popconfirm, message, Modal, Form, InputNumber } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import { exportCSV } from '../utils/export'
import dayjs from 'dayjs'

export default function UsersPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(1)
  const [editOpen, setEditOpen] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form] = Form.useForm()

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

  const openEdit = (record: any) => {
    setEditing(record)
    form.setFieldsValue({
      nickname: record.nickname,
      member_level: record.member_level,
      points: record.points,
      status: record.status,
    })
    setEditOpen(true)
  }

  const submitEdit = async () => {
    try {
      const values = await form.validateFields()
      await api.users.edit(editing.id, values)
      message.success('用户已更新')
      setEditOpen(false)
      load()
    } catch (e: any) {
      if (e.errorFields) return // 表单校验错误
      message.error(e.message)
    }
  }

  const handleExport = () => {
    if (!data.length) {
      message.warning('当前无数据可导出')
      return
    }
    exportCSV('用户列表', [
      { title: 'ID', dataIndex: 'id' },
      { title: '昵称', dataIndex: 'nickname' },
      { title: '手机号', dataIndex: 'phone' },
      { title: '会员', dataIndex: 'member_level' },
      { title: '积分', dataIndex: 'points' },
      { title: '状态', dataIndex: 'status' },
      { title: '会员到期', dataIndex: 'member_expire_at' },
      { title: '注册时间', dataIndex: 'created_at' },
    ], data)
    message.success('已导出 CSV')
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
      render: (v: string) => v === 'blocked' ? <Tag color="red">已封禁</Tag> : v === 'deleted' ? <Tag color="default">已注销</Tag> : <Tag color="green">正常</Tag>
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
      title: '操作', width: 160, fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" onClick={() => openEdit(r)}>编辑</Button>
          {r.status !== 'deleted' && (
            <Popconfirm title={`确认${r.status === 'blocked' ? '解封' : '封禁'}该用户？`} onConfirm={() => toggleBan(r.id, r.status)}>
              <Button size="small" danger={r.status !== 'blocked'}>
                {r.status === 'blocked' ? '解封' : '封禁'}
              </Button>
            </Popconfirm>
          )}
        </Space>
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
          options={[{ value: 'active', label: '正常' }, { value: 'blocked', label: '已封禁' }, { value: 'deleted', label: '已注销' }]}
        />
        <Button onClick={load}>刷新</Button>
        <Button onClick={handleExport}>导出 CSV</Button>
      </Space>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        scroll={{ x: 1200 }}
        pagination={{
          current: page, total, pageSize: 10, showSizeChanger: false,
          onChange: (p) => setPage(p)
        }}
      />

      <Modal
        title={`编辑用户 #${editing?.id ?? ''}`}
        open={editOpen}
        onOk={submitEdit}
        onCancel={() => setEditOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="nickname" label="昵称" rules={[{ required: true, message: '请输入昵称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="member_level" label="会员等级">
            <Select options={[
              { value: 'free', label: '免费' },
              { value: 'basic', label: '基础' },
              { value: 'pro', label: 'Pro' },
            ]} />
          </Form.Item>
          <Form.Item name="points" label="积分">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select options={[
              { value: 'active', label: '正常' },
              { value: 'blocked', label: '已封禁' },
              { value: 'deleted', label: '已注销' },
            ]} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
