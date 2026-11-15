/**
 * 管理后台 — 数据概览页
 */
import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Spin, message } from 'antd'
import {
  UserOutlined, ApiOutlined, BellOutlined,
  ShoppingCartOutlined, DollarOutlined, CheckCircleOutlined, ThunderboltOutlined
} from '@ant-design/icons'
import { api } from '../api/client'

export default function DashboardPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.dashboard().then(resp => setData(resp.data)).catch(e => message.error(e.message)).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin />
  if (!data) return null

  const cards = [
    { title: '注册用户', value: data.users, icon: <UserOutlined />, color: 'var(--pt-accent)' },
    { title: '宠物档案', value: data.pets, icon: <UserOutlined />, color: 'var(--pt-warning)' },
    { title: '设备总数', value: data.devices, icon: <ApiOutlined />, color: 'var(--pt-accent)' },
    { title: '在线设备', value: data.online_devices, icon: <ThunderboltOutlined />, color: 'var(--pt-success)' },
    { title: '待处理报警', value: data.active_alarms, icon: <BellOutlined />, color: 'var(--pt-danger)' },
    { title: '今日报警', value: data.today_alarms, icon: <BellOutlined />, color: 'var(--pt-warning)' },
    { title: '已支付订单', value: data.paid_orders, icon: <ShoppingCartOutlined />, color: 'var(--pt-accent)' },
    { title: '累计营收', value: data.revenue, prefix: '¥', precision: 2, icon: <DollarOutlined />, color: 'var(--pt-success)' },
    { title: '碰头总数', value: data.meets, icon: <CheckCircleOutlined />, color: 'var(--pt-accent)' },
    { title: '成功碰头', value: data.success_meets, icon: <CheckCircleOutlined />, color: 'var(--pt-success)' },
    { title: '活跃订阅', value: data.active_subs, icon: <ShoppingCartOutlined />, color: 'var(--pt-accent)' }
  ]

  return (
    <>
      <h2 style={{ marginBottom: 8 }}>数据概览</h2>
      <p className="pt-page-note">数据概览中的订单与营收来自本地 Mock，不得理解为真实营收或已到账。</p>
      <Row gutter={[16, 16]}>
        {cards.map((c, i) => (
          <Col xs={12} sm={8} md={6} key={i}>
            <Card>
              <Statistic
                title={c.title}
                value={c.value}
                prefix={c.prefix}
                precision={c.precision}
                valueStyle={{ color: c.color }}
              />
              <div style={{ marginTop: 8, color: c.color, fontSize: 20 }}>{c.icon}</div>
            </Card>
          </Col>
        ))}
      </Row>
    </>
  )
}
