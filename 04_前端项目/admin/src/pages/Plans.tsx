/**
 * 管理后台 — 会员方案管理（三档方案）
 */
import { Card, Table, Tag, Button, message } from 'antd'

export default function PlansPage() {
  const data = [
    { key: 1, name: '免费版', month: 0, year: 0, devices: 1, refresh: '5分钟', share: '—', status: true },
    { key: 2, name: '基础版', month: 19.9, year: 199, devices: 3, refresh: '5秒', share: '—', status: true },
    { key: 3, name: 'Pro版', month: 29.9, year: 299, devices: 10, refresh: '5秒', share: '5人', status: true },
  ]
  const columns = [
    { title: '方案', dataIndex: 'name', render: (v: string) => <b>{v}</b> },
    { title: '月价', dataIndex: 'month', render: (v: number) => v === 0 ? '¥0' : `¥${v}` },
    { title: '年价', dataIndex: 'year', render: (v: number) => v === 0 ? '¥0' : `¥${v}` },
    { title: '设备上限', dataIndex: 'devices' },
    { title: '定位刷新', dataIndex: 'refresh' },
    { title: '家人共享', dataIndex: 'share' },
    { title: '状态', dataIndex: 'status', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '上架' : '下架'}</Tag> },
    { title: '操作', render: () => <a onClick={() => message.success('编辑功能演示')}>编辑</a> },
  ]
  return (
    <Card title="会员方案管理" extra={<Button size="small" type="primary">新增方案</Button>}>
      <Table size="small" rowKey="key" columns={columns} dataSource={data} pagination={false} />
      <div style={{ marginTop: 16, color: '#888', fontSize: 12 }}>价格变更需审批 · 审批记录保留 180 天</div>
    </Card>
  )
}
