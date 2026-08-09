/**
 * 管理后台 — 报警规则配置（猫/狗独立默认规则）
 */
import { Card, Descriptions, Switch, Table, Button, Tag, message } from 'antd'

export default function AlarmRulesPage() {
  const overrides = [
    { key: 1, user: '李女士', pet: '团子', rule: '围栏 500m / 低电量 25%', status: true },
  ]
  const overridesColumns = [
    { title: '用户', dataIndex: 'user' },
    { title: '宠物', dataIndex: 'pet' },
    { title: '自定义规则', dataIndex: 'rule' },
    { title: '生效', dataIndex: 'status', render: (v: boolean) => <Switch checked={v} size="small" /> },
  ]
  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card title="🐱 猫咪默认规则">
          <Descriptions column={1} size="small">
            <Descriptions.Item label="围栏半径">100m（楼栋范围）</Descriptions.Item>
            <Descriptions.Item label="离开报警"><Tag color="red">立即报警 · 高优先级</Tag></Descriptions.Item>
            <Descriptions.Item label="进入提醒"><Switch checked size="small" /></Descriptions.Item>
            <Descriptions.Item label="低电量阈值">20%</Descriptions.Item>
          </Descriptions>
        </Card>
        <Card title="🐶 狗狗默认规则">
          <Descriptions column={1} size="small">
            <Descriptions.Item label="围栏半径">300m（小区范围）</Descriptions.Item>
            <Descriptions.Item label="离开报警"><Tag color="orange">可选开启 · 中优先级</Tag></Descriptions.Item>
            <Descriptions.Item label="进入提醒"><Switch size="small" /></Descriptions.Item>
            <Descriptions.Item label="低电量阈值">20%</Descriptions.Item>
          </Descriptions>
        </Card>
      </div>
      <Card title="自定义覆盖" extra={<Button type="primary" size="small" onClick={() => message.success('规则已保存（下次报警生效）')}>保存规则</Button>}>
        <Table size="small" rowKey="key" columns={overridesColumns} dataSource={overrides} pagination={false} />
      </Card>
    </div>
  )
}
