/**
 * 管理后台 — 设备详情
 */
import { Card, Descriptions, Table, Tag } from 'antd'
import { PT } from '../styles/tokens'

export default function DeviceDetailPage() {
  const alarmsColumns = [
    { title: '时间', dataIndex: 'time' },
    { title: '类型', dataIndex: 'type' },
    { title: '状态', dataIndex: 'status', render: (v: string) => (
      <Tag style={{ background: PT.successSubtle, color: PT.success, border: 0 }}>{v}</Tag>
    ) },
  ]
  const alarmsData = [
    { key: 1, time: '今天 14:02', type: '离开围栏', status: '已处理' },
    { key: 2, time: '昨天 21:18', type: '低电量', status: '已处理' },
  ]
  return (
    <div>
      <Card style={{ marginBottom: 16, background: PT.surface, borderColor: PT.border }}>
        <Descriptions column={4} title="设备信息" bordered size="small">
          <Descriptions.Item label="SN">PT-A10086</Descriptions.Item>
          <Descriptions.Item label="型号">定位器</Descriptions.Item>
          <Descriptions.Item label="固件">v0.1.0</Descriptions.Item>
          <Descriptions.Item label="电量"><Tag style={{ background: PT.successSubtle, color: PT.success, border: 0 }}>72%</Tag></Descriptions.Item>
          <Descriptions.Item label="状态"><Tag style={{ background: PT.successSubtle, color: PT.success, border: 0 }}>在线</Tag></Descriptions.Item>
          <Descriptions.Item label="绑定宠物">橘子 · 猫</Descriptions.Item>
          <Descriptions.Item label="绑定时间">2026-08-01</Descriptions.Item>
          <Descriptions.Item label="最后位置">31.230, 121.473</Descriptions.Item>
          <Descriptions.Item label="固件状态">固件已是最新，暂无可升级版本。</Descriptions.Item>
          <Descriptions.Item label="最后上报">今天 14:02</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="报警记录" style={{ background: PT.surface, borderColor: PT.border }}>
        <Table size="small" rowKey="key" columns={alarmsColumns} dataSource={alarmsData} pagination={false} />
      </Card>
    </div>
  )
}
