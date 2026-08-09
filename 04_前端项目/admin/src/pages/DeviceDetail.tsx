/**
 * 管理后台 — 设备详情（信息/绑定历史/报警）
 */
import { Card, Descriptions, Table, Tag } from 'antd'

export default function DeviceDetailPage() {
  const alarmsColumns = [
    { title: '时间', dataIndex: 'time' },
    { title: '类型', dataIndex: 'type' },
    { title: '状态', dataIndex: 'status', render: (v: string) => <Tag color="green">{v}</Tag> },
  ]
  const alarmsData = [
    { key: 1, time: '08-09 12:30', type: '离开围栏', status: '已处理' },
    { key: 2, time: '08-08 09:15', type: '低电量', status: '已处理' },
  ]
  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Descriptions column={4} title="设备信息" bordered size="small">
          <Descriptions.Item label="SN">PT-DG-2026-0001</Descriptions.Item>
          <Descriptions.Item label="型号">狗狗定位器 GPS-4G</Descriptions.Item>
          <Descriptions.Item label="固件">v1.2.0 (最新)</Descriptions.Item>
          <Descriptions.Item label="电量"><Tag color="green">86%</Tag></Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color="green">● 在线</Tag></Descriptions.Item>
          <Descriptions.Item label="绑定宠物">旺财</Descriptions.Item>
          <Descriptions.Item label="绑定时间">2026-07-01</Descriptions.Item>
          <Descriptions.Item label="最后在线">刚刚</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="报警记录">
        <Table size="small" rowKey="key" columns={alarmsColumns} dataSource={alarmsData} pagination={false} />
      </Card>
    </div>
  )
}
