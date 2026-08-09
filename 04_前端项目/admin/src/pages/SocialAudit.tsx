/**
 * 管理后台 — 碰头记录审核（异常标红/扣积分）
 */
import { Card, Table, Tag, Button, message } from 'antd'

export default function SocialAuditPage() {
  const data = [
    { key: 1, time: '08-09 11:00', from: '旺财', to: '可可', distance: '3m', points: 100, abnormal: '距离异常', color: 'red' },
    { key: 2, time: '08-08 20:30', from: '豆豆', to: '球球', distance: '120m', points: 100, abnormal: '频繁碰头', color: 'red' },
    { key: 3, time: '08-08 16:20', from: '咪咪', to: '团子', distance: '8m', points: 100, abnormal: '', color: 'green' },
  ]
  const columns = [
    { title: '时间', dataIndex: 'time' },
    { title: '发起方', dataIndex: 'from' },
    { title: '接收方', dataIndex: 'to' },
    { title: '距离', dataIndex: 'distance' },
    { title: '积分', dataIndex: 'points', render: (v: number) => `+${v}` },
    { title: '异常标记', dataIndex: 'abnormal', render: (v: string, r: any) => v ? <Tag color="red">{v}</Tag> : <Tag color="green">正常</Tag> },
    { title: '操作', render: (_: any, r: any) => r.abnormal
        ? <Button size="small" danger onClick={() => message.warning('已驳回并扣回积分 + 通知用户')}>审核不通过</Button>
        : <Button size="small" type="primary" onClick={() => message.success('已通过')}>通过</Button> },
  ]
  return (
    <Card title="碰头记录审核" extra={<Button size="small">导出</Button>}>
      <Table size="small" rowKey="key" columns={columns} dataSource={data} pagination={false} />
      <div style={{ marginTop: 16, color: '#888', fontSize: 12 }}>
        异常规则：相遇距离 &lt; 5m 标记异常 · 同对宠物 24h 内 ≥ 3 次标记频繁 · 审核不通过自动扣回积分并通知用户
      </div>
    </Card>
  )
}
