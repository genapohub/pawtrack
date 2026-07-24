/**
 * 管理后台 — 订单管理
 */
import { useEffect, useState } from 'react'
import { Table, Select, Space, Button, Tag, Popconfirm, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { api } from '../api/client'
import dayjs from 'dayjs'

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
  pending: { label: '待支付', color: 'orange' },
  paid: { label: '已支付', color: 'green' },
  failed: { label: '失败', color: 'red' },
  cancelled: { label: '已取消', color: 'default' },
  refunded: { label: '已退款', color: 'purple' }
}

export default function OrdersPage() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(1)

  const load = async () => {
    setLoading(true)
    try {
      const resp: any = await api.orders.list({ status: status || undefined, page, size: 10 })
      setData(resp.data || [])
      setTotal(resp.pagination?.total || 0)
    } catch (e: any) {
      message.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, status])

  const refund = async (orderNo: string) => {
    try {
      await api.orders.refund(orderNo)
      message.success('退款已审批')
      load()
    } catch (e: any) {
      message.error(e.message)
    }
  }

  const columns: ColumnsType<any> = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '订单号', dataIndex: 'order_no', width: 200 },
    { title: '用户ID', dataIndex: 'user_id', width: 80 },
    { title: '类型', dataIndex: 'type', width: 100 },
    { title: '套餐', dataIndex: 'product_id', width: 120 },
    { title: '金额', dataIndex: 'amount', width: 90, render: (v: number) => `¥${v}` },
    { title: '渠道', dataIndex: 'pay_channel', width: 80, render: (v: string) => v || '—' },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (v: string) => <Tag color={STATUS_LABEL[v]?.color || 'default'}>{STATUS_LABEL[v]?.label || v}</Tag>
    },
    { title: '支付时间', dataIndex: 'paid_at', width: 160, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—' },
    { title: '下单时间', dataIndex: 'created_at', width: 160, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '—' },
    {
      title: '操作', width: 100, fixed: 'right',
      render: (_, r) => r.status === 'paid' ? (
        <Popconfirm title="确认退款？" onConfirm={() => refund(r.order_no)}>
          <Button size="small" danger>退款</Button>
        </Popconfirm>
      ) : '—'
    }
  ]

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>订单管理</h2>
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="状态筛选"
          allowClear
          style={{ width: 140 }}
          value={status || undefined}
          onChange={v => { setStatus(v || ''); setPage(1) }}
          options={Object.entries(STATUS_LABEL).map(([k, v]) => ({ value: k, label: v.label }))}
        />
        <Button onClick={load}>刷新</Button>
      </Space>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        scroll={{ x: 1300 }}
        pagination={{ current: page, total, pageSize: 10, showSizeChanger: false, onChange: (p) => setPage(p) }}
      />
    </>
  )
}
