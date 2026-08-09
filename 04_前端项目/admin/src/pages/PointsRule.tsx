/**
 * 管理后台 — 积分规则配置
 */
import { Card, Descriptions, InputNumber, Button, message } from 'antd'

export default function PointsRulePage() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <Card title="获取规则">
        <Descriptions column={1} size="small">
          <Descriptions.Item label="碰头成功"><InputNumber size="small" defaultValue={100} min={0} /> 积分</Descriptions.Item>
          <Descriptions.Item label="邀请好友"><InputNumber size="small" defaultValue={50} min={0} /> 积分/人</Descriptions.Item>
          <Descriptions.Item label="每日签到"><InputNumber size="small" defaultValue={5} min={0} /> 积分</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="消费与过期">
        <Descriptions column={1} size="small">
          <Descriptions.Item label="兑换比例"><InputNumber size="small" defaultValue={100} min={0} /> 积分 = ¥1</Descriptions.Item>
          <Descriptions.Item label="有效期">12 个月（滚动）</Descriptions.Item>
          <Descriptions.Item label="过期提醒">提前 30 天通知</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card style={{ gridColumn: '1 / -1' }}>
        <Button type="primary" onClick={() => message.success('积分规则已保存（实时生效）')}>保存规则</Button>
      </Card>
    </div>
  )
}
