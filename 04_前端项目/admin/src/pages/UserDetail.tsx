/**
 * 管理后台 — 用户详情（宠物/设备/订单/报警 4 Tab）
 */
import { useState } from 'react'
import { Card, Tabs, Table, Descriptions, Tag, message } from 'antd'

export default function UserDetailPage() {
  const [userId] = useState(1)

  const petsColumns = [
    { title: '宠物', dataIndex: 'name' },
    { title: '类型', dataIndex: 'type', render: (v: string) => v === 'cat' ? '🐱 猫' : '🐶 狗' },
    { title: '围栏', dataIndex: 'fence', render: (v: string) => <Tag color={v?.includes('开') ? 'green' : 'default'}>{v || '未开启'}</Tag> },
  ]
  const petsData = [
    { key: 1, name: '旺财', type: 'dog', fence: '300m 已开启' },
    { key: 2, name: '咪咪', type: 'cat', fence: '100m 已开启' },
  ]

  const devicesColumns = [
    { title: 'SN', dataIndex: 'sn' },
    { title: '型号', dataIndex: 'model' },
    { title: '电量', dataIndex: 'battery', render: (v: number) => <Tag color={v < 20 ? 'red' : v < 50 ? 'orange' : 'green'}>{v}%</Tag> },
    { title: '状态', dataIndex: 'status', render: (v: string) => <Tag color={v === 'online' ? 'green' : 'default'}>{v === 'online' ? '在线' : '离线'}</Tag> },
  ]
  const devicesData = [
    { key: 1, sn: 'PT-DG-2026-0001', model: '狗狗定位器', battery: 86, status: 'online' },
    { key: 2, sn: 'PT-BL-2026-0007', model: '猫咪定位器', battery: 18, status: 'offline' },
  ]

  const ordersColumns = [
    { title: '订单号', dataIndex: 'order_no' },
    { title: '类型', dataIndex: 'type' },
    { title: '金额', dataIndex: 'amount', render: (v: number) => `¥${v}` },
    { title: '状态', dataIndex: 'status' },
  ]
  const ordersData = [
    { key: 1, order_no: 'PT20260809001', type: 'Pro 月付', amount: 29.9, status: '已支付' },
    { key: 2, order_no: 'PT20260801002', type: '基础 年付', amount: 199, status: '已支付' },
  ]

  const alarmsColumns = [
    { title: '时间', dataIndex: 'time' },
    { title: '类型', dataIndex: 'type' },
    { title: '状态', dataIndex: 'status', render: (v: string) => <Tag color={v === 'active' ? 'red' : 'green'}>{v === 'active' ? '待处理' : '已处理'}</Tag> },
  ]
  const alarmsData = [
    { key: 1, time: '08-09 12:30', type: '离开围栏', status: 'active' },
    { key: 2, time: '08-08 09:15', type: '低电量', status: 'handled' },
  ]

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Descriptions column={4} title="用户信息">
          <Descriptions.Item label="用户">张先生</Descriptions.Item>
          <Descriptions.Item label="手机号">138****8000</Descriptions.Item>
          <Descriptions.Item label="会员"><Tag color="default">免费版</Tag></Descriptions.Item>
          <Descriptions.Item label="注册时间">2026-07-01</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card>
        <Tabs defaultActiveKey="pets" items={[
          { key: 'pets', label: '宠物 (2)', children: <Table size="small" rowKey="key" columns={petsColumns} dataSource={petsData} pagination={false} /> },
          { key: 'devices', label: '设备 (2)', children: <Table size="small" rowKey="key" columns={devicesColumns} dataSource={devicesData} pagination={false} /> },
          { key: 'orders', label: '订单 (2)', children: <Table size="small" rowKey="key" columns={ordersColumns} dataSource={ordersData} pagination={false} /> },
          { key: 'alarms', label: '报警 (2)', children: <Table size="small" rowKey="key" columns={alarmsColumns} dataSource={alarmsData} pagination={false} /> },
        ]} />
      </Card>
    </div>
  )
}
