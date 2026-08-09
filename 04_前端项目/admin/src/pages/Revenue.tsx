/**
 * 管理后台 — 收入统计（MRR/ARR/ARPU）
 */
import { Card, Statistic, Row, Col, Table, Button } from 'antd'

export default function RevenuePage() {
  const channelData = [
    { key: 1, channel: '微信支付', share: '65%' },
    { key: 2, channel: '支付宝', share: '25%' },
    { key: 3, channel: 'Apple', share: '10%' },
  ]
  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}><Card><Statistic title="MRR" value={128.6} precision={1} suffix="万" valueStyle={{ color: '#1677ff' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="ARR" value={1543} suffix="万" /></Card></Col>
        <Col span={6}><Card><Statistic title="ARPU" value={14.9} suffix="元" /></Card></Col>
        <Col span={6}><Card><Statistic title="付费转化率" value={8.2} suffix="%" /></Card></Col>
      </Row>
      <Row gutter={16}>
        <Col span={12}>
          <Card title="渠道分布" extra={<Button size="small">导出 Excel</Button>}>
            <Table size="small" rowKey="key" columns={[{ title: '渠道', dataIndex: 'channel' }, { title: '占比', dataIndex: 'share' }]} dataSource={channelData} pagination={false} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="收入趋势（近 7 个月）">
            {['25%', '40%', '35%', '58%', '50%', '75%', '100%'].map((h, i) => (
              <div key={i} style={{ display: 'inline-block', width: 40, height: 160, marginRight: 8, background: '#f0f1f5', borderRadius: 4, position: 'relative', verticalAlign: 'bottom' }}>
                <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: h, background: '#1677ff', borderRadius: 4 }} />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
