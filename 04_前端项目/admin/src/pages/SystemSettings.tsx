/**
 * 管理后台 — 系统设置（RBAC 权限 + 操作日志）
 */
import { Card, Table, Tag, Tabs, Button, message } from 'antd'

export default function SystemSettingsPage() {
  const roles = [
    { key: 1, role: '超管', desc: '全部权限（读写）', level: 'danger' },
    { key: 2, role: '运营', desc: '用户/宠物/设备/报警/内容（读写）', level: 'processing' },
    { key: 3, role: '客服', desc: '用户/宠物/设备（只读）+ 报警（读写）', level: 'default' },
    { key: 4, role: '财务', desc: '会员营收（只读）', level: 'warning' },
  ]
  const logs = [
    { key: 1, time: '08-09 11:02', user: 'admin', action: '封禁用户 138****5678' },
    { key: 2, time: '08-09 10:41', user: 'admin', action: '修改猫咪报警默认规则' },
    { key: 3, time: '08-08 22:15', user: 'ops_li', action: '导出订单报表' },
    { key: 4, time: '08-08 16:30', user: 'finance_w', action: '审批退款 PT20260807001' },
  ]
  return (
    <Card>
      <Tabs items={[
        {
          key: 'rbac', label: '🔐 角色权限 (RBAC)',
          children: <Table size="small" rowKey="key"
            columns={[
              { title: '角色', dataIndex: 'role', render: (v: string, r: any) => <Tag color={r.level}>{v}</Tag> },
              { title: '权限说明', dataIndex: 'desc' },
              { title: '操作', render: () => <a onClick={() => message.success('权限变更即时生效')}>编辑</a> },
            ]}
            dataSource={roles} pagination={false} />,
        },
        {
          key: 'logs', label: '📋 操作日志（保留 180 天）',
          children: (
            <div>
              <Table size="small" rowKey="key"
                columns={[
                  { title: '时间', dataIndex: 'time' },
                  { title: '操作人', dataIndex: 'user', render: (v: string) => <Tag color="blue">{v}</Tag> },
                  { title: '操作', dataIndex: 'action' },
                ]}
                dataSource={logs} pagination={false} />
              <Button size="small" style={{ marginTop: 12 }} onClick={() => message.success('日志已导出（不可编辑/删除）')}>导出日志</Button>
            </div>
          ),
        },
      ]} />
    </Card>
  )
}
