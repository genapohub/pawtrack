/**
 * 管理后台 — 内容管理（公告/Banner）
 */
import { Card, Table, Tag, Button, message } from 'antd'

export default function ContentPage() {
  const notices = [
    { key: 1, title: 'v0.4.0 版本更新公告', scope: '全部用户', status: '已发布', tag: 'green' },
    { key: 2, title: 'Pro 会员 8 折活动', scope: '免费用户', status: '定时发布', tag: 'orange' },
  ]
  const banners = [
    { key: 1, name: '首页 Banner 1', link: '会员活动页', sort: 1 },
    { key: 2, name: '首页 Banner 2', link: '新用户引导', sort: 2 },
    { key: 3, name: '社交页 Banner', link: '碰头玩法介绍', sort: 3 },
  ]
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <Card title="📢 公告管理" extra={<Button size="small" type="primary">新建公告</Button>}>
        <Table size="small" rowKey="key"
          columns={[
            { title: '标题', dataIndex: 'title' },
            { title: '推送范围', dataIndex: 'scope' },
            { title: '状态', dataIndex: 'status', render: (v: string, r: any) => <Tag color={r.tag}>{v}</Tag> },
            { title: '操作', render: () => <a onClick={() => message.success('操作演示')}>置顶/下线</a> },
          ]}
          dataSource={notices} pagination={false} />
      </Card>
      <Card title="🖼️ Banner 管理" extra={<Button size="small" type="primary">新增 Banner</Button>}>
        <Table size="small" rowKey="key"
          columns={[
            { title: 'Banner', dataIndex: 'name' },
            { title: '链接', dataIndex: 'link' },
            { title: '排序', dataIndex: 'sort' },
            { title: '操作', render: () => <a onClick={() => message.success('排序调整演示')}>排序</a> },
          ]}
          dataSource={banners} pagination={false} />
      </Card>
    </div>
  )
}
