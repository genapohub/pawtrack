# -*- coding: utf-8 -*-
"""宠迹后台管理 UI 原型生成器 — 15 屏"""
import os

OUT_ADMIN = "/Users/macos/Downloads/工作相关/宠迹/03_设计文档/UI原型_V2.1/admin"

ADMIN_PAGES = [
# ── 登录 ──────────────────────────────────────────
dict(f="a1-login.html", title="A1 后台登录", module="系统",
  prd="📋 后台入口：管理员账号登录（RBAC 角色区分权限）",
  body="""<div class="login-wrap">
  <div class="login-box">
    <div class="login-logo">🐾 宠迹管理后台</div>
    <div class="login-sub">PawTrack Admin Console</div>
    <input class="inp" placeholder="管理员账号" value="admin">
    <input class="inp" type="password" placeholder="密码" value="••••••••">
    <button class="btn-main">登 录</button>
    <div class="login-tip">默认账号 admin · 支持 RBAC 4 角色</div>
  </div>
</div>"""),
# ── 数据概览 ──────────────────────────────────────
dict(f="a2-dashboard.html", title="A2 数据概览 Dashboard", module="数据概览",
  prd="📋 PRD 4.2.1：核心指标卡 DAU/MAU/设备在线率/报警率/收入趋势（7/30/90天切换）；报警热力图；实时监控 10 秒刷新",
  body="""<div class="page">
  <div class="p-head"><h2>数据概览</h2><div class="seg"><span class="on">7天</span><span>30天</span><span>90天</span></div><button class="btn-sm">导出</button></div>
  <div class="kpi-grid">
    <div class="kpi"><div class="k-l">DAU</div><div class="k-v">12,846</div><div class="k-d up">▲ 12.4%</div></div>
    <div class="kpi"><div class="k-l">MAU</div><div class="k-v">86,320</div><div class="k-d up">▲ 8.1%</div></div>
    <div class="kpi"><div class="k-l">设备在线率</div><div class="k-v">96.2%</div><div class="k-d up">▲ 1.3%</div></div>
    <div class="kpi"><div class="k-l">报警率</div><div class="k-v">2.8%</div><div class="k-d down">▼ 0.4%</div></div>
    <div class="kpi"><div class="k-l">收入 (MRR)</div><div class="k-v">¥128.6万</div><div class="k-d up">▲ 15.7%</div></div>
  </div>
  <div class="row2">
    <div class="panel"><div class="p-t">收入趋势</div><div class="chart-line"><div class="bar" style="height:30%"></div><div class="bar" style="height:45%"></div><div class="bar" style="height:38%"></div><div class="bar" style="height:62%"></div><div class="bar" style="height:55%"></div><div class="bar" style="height:78%"></div><div class="bar" style="height:90%"></div></div></div>
    <div class="panel"><div class="p-t">实时监控 <span class="live">● LIVE 10s</span></div><div class="live-row"><span>在线设备</span><b>3,842</b></div><div class="live-row"><span>活跃用户</span><b>1,256</b></div><div class="live-row"><span>今日报警</span><b class="warn">28</b></div></div>
  </div>
  <div class="panel"><div class="p-t">报警热力图 <span class="sub">按时间/类型筛选</span></div><div class="heat-map"><span style="left:15%;top:30%;opacity:.2"></span><span style="left:30%;top:60%;opacity:.5"></span><span style="left:55%;top:25%;opacity:.9"></span><span style="left:70%;top:55%;opacity:.35"></span><span style="left:45%;top:70%;opacity:.15"></span></div></div>
</div>"""),
# ── 用户管理 ──────────────────────────────────────
dict(f="a3-user-list.html", title="A3 用户列表", module="用户管理",
  prd="📋 PRD 4.2.2：多维筛选+批量操作+封禁/解封；封禁即时生效，前端拦截登录",
  body="""<div class="page">
  <div class="p-head"><h2>用户管理</h2><button class="btn-sm warn">批量封禁</button><button class="btn-sm">导出 CSV</button></div>
  <div class="filter-bar"><input class="inp sm" placeholder="搜索手机号/昵称"><select class="sel"><option>全部会员等级</option></select><select class="sel"><option>全部状态</option></select><button class="btn-sm">查询</button></div>
  <table class="tbl">
    <tr><th><input type="checkbox"></th><th>用户</th><th>手机号</th><th>会员</th><th>宠物</th><th>设备</th><th>状态</th><th>注册时间</th><th>操作</th></tr>
    <tr><td><input type="checkbox"></td><td>张先生</td><td>138****8000</td><td><span class="tag free">免费</span></td><td>2</td><td>2</td><td><span class="st ok">正常</span></td><td>2026-07-01</td><td><a>详情</a> <a class="red">封禁</a></td></tr>
    <tr><td><input type="checkbox"></td><td>李女士</td><td>139****1234</td><td><span class="tag pro">Pro</span></td><td>3</td><td>3</td><td><span class="st ok">正常</span></td><td>2026-06-15</td><td><a>详情</a> <a class="red">封禁</a></td></tr>
    <tr><td><input type="checkbox"></td><td>王先生</td><td>137****5678</td><td><span class="tag basic">基础</span></td><td>1</td><td>1</td><td><span class="st ban">已封禁</span></td><td>2026-05-20</td><td><a>详情</a> <a>解封</a></td></tr>
  </table>
  <div class="pager">共 8,632 条 · <span class="cur">1</span> 2 3 ... 288</div>
</div>"""),
dict(f="a4-user-detail.html", title="A4 用户详情", module="用户管理",
  prd="📋 PRD 4.2.2：宠物/设备/订单/报警 4 个 Tab，关联数据联动展示",
  body="""<div class="page">
  <div class="p-head"><h2>用户详情 <span class="sub">138****8000</span></h2><button class="btn-sm warn">封禁用户</button></div>
  <div class="panel"><div class="user-info"><span class="avatar">🐾</span><div><b>张先生</b><div class="sub">注册于 2026-07-01 · 会员：免费版</div></div><span class="tag free">免费</span></div></div>
  <div class="tabs"><span class="on">宠物 (2)</span><span>设备 (2)</span><span>订单 (5)</span><span>报警 (12)</span></div>
  <div class="panel">
    <table class="tbl">
      <tr><th>宠物</th><th>类型</th><th>绑定设备</th><th>围栏</th><th>状态</th></tr>
      <tr><td>旺财</td><td>🐶 狗</td><td>PT-DG-2026-0001</td><td>300m 开启</td><td><span class="st ok">正常</span></td></tr>
      <tr><td>咪咪</td><td>🐱 猫</td><td>PT-BL-2026-0007</td><td>100m 开启</td><td><span class="st warn">低电量</span></td></tr>
    </table>
  </div>
</div>"""),
# ── 设备管理 ──────────────────────────────────────
dict(f="a5-device-list.html", title="A5 设备列表", module="设备管理",
  prd="📋 PRD 4.2.3：在线/离线/低电量状态筛选；支持固件批量推送",
  body="""<div class="page">
  <div class="p-head"><h2>设备管理</h2><button class="btn-sm">固件批量推送</button></div>
  <div class="filter-bar"><select class="sel"><option>全部状态</option></select><select class="sel"><option>全部型号</option></select><input class="inp sm" placeholder="搜索 SN"><button class="btn-sm">查询</button></div>
  <table class="tbl">
    <tr><th>SN</th><th>型号</th><th>绑定宠物</th><th>电量</th><th>固件</th><th>状态</th><th>最后在线</th><th>操作</th></tr>
    <tr><td>PT-DG-2026-0001</td><td>狗狗定位器</td><td>旺财</td><td>86%</td><td>v1.2.0</td><td><span class="st ok">在线</span></td><td>刚刚</td><td><a>详情</a></td></tr>
    <tr><td>PT-BL-2026-0007</td><td>猫咪定位器</td><td>咪咪</td><td>18%</td><td>v1.1.0</td><td><span class="st warn">低电量</span></td><td>2分钟前</td><td><a>详情</a></td></tr>
    <tr><td>PT-DG-2026-0034</td><td>狗狗定位器</td><td>—</td><td>—</td><td>v1.0.0</td><td><span class="st ban">离线</span></td><td>3小时前</td><td><a>详情</a></td></tr>
  </table>
  <div class="pager">共 4,215 台</div>
</div>"""),
dict(f="a6-device-detail.html", title="A6 设备详情", module="设备管理",
  prd="📋 PRD 4.2.3：绑定历史+定位轨迹+报警记录+固件日志；设备异常标红高亮",
  body="""<div class="page">
  <div class="p-head"><h2>设备详情 <span class="sub">PT-DG-2026-0001</span></h2><button class="btn-sm">推送固件</button></div>
  <div class="row2">
    <div class="panel"><div class="p-t">设备信息</div>
      <div class="kv"><span>型号</span><b>狗狗定位器 GPS-4G</b></div>
      <div class="kv"><span>固件</span><b>v1.2.0 (最新)</b></div>
      <div class="kv"><span>电量</span><b class="ok">86%</b></div>
      <div class="kv"><span>状态</span><b class="ok">● 在线</b></div>
      <div class="kv"><span>绑定宠物</span><b>旺财</b></div>
    </div>
    <div class="panel"><div class="p-t">绑定历史</div>
      <div class="log-row2"><span>2026-07-01 绑定 → 旺财</span></div>
      <div class="log-row2"><span>2026-06-28 解绑 ← 前用户</span></div>
    </div>
  </div>
  <div class="panel"><div class="p-t">报警记录</div>
    <table class="tbl">
      <tr><th>时间</th><th>类型</th><th>位置</th><th>状态</th></tr>
      <tr><td>08-09 12:30</td><td>离开围栏</td><td>金水区</td><td><span class="st warn">已处理</span></td></tr>
      <tr class="row-warn"><td>08-08 09:15</td><td>低电量</td><td>—</td><td><span class="st warn">已处理</span></td></tr>
    </table>
  </div>
</div>"""),
# ── 报警管理 ──────────────────────────────────────
dict(f="a7-alarm-rule.html", title="A7 报警规则配置", module="报警管理",
  prd="📋 PRD 4.2.4：猫/狗独立默认规则，支持自定义覆盖；变更后前端下次报警生效",
  body="""<div class="page">
  <div class="p-head"><h2>报警规则配置</h2><button class="btn-sm">保存规则</button></div>
  <div class="row2">
    <div class="panel"><div class="p-t">🐱 猫咪默认规则</div>
      <div class="kv"><span>围栏半径</span><b>100m（楼栋范围）</b></div>
      <div class="kv"><span>离开报警</span><b class="ok">立即报警 · 高优先级</b></div>
      <div class="kv"><span>进入提醒</span><b>开启</b></div>
      <div class="kv"><span>低电量阈值</span><b>20%</b></div>
    </div>
    <div class="panel"><div class="p-t">🐶 狗狗默认规则</div>
      <div class="kv"><span>围栏半径</span><b>300m（小区范围）</b></div>
      <div class="kv"><span>离开报警</span><b>可选开启 · 中优先级</b></div>
      <div class="kv"><span>进入提醒</span><b>关闭</b></div>
      <div class="kv"><span>低电量阈值</span><b>20%</b></div>
    </div>
  </div>
  <div class="panel"><div class="p-t">自定义覆盖</div>
    <table class="tbl"><tr><th>用户</th><th>宠物</th><th>自定义规则</th><th>生效</th></tr>
    <tr><td>李女士</td><td>团子</td><td>围栏 500m / 低电量 25%</td><td>下次报警生效</td></tr></table>
  </div>
</div>"""),
dict(f="a8-alarm-list.html", title="A8 报警记录", module="报警管理",
  prd="📋 PRD 4.2.4：按类型/时间/状态筛选；误报可标记，用于优化算法",
  body="""<div class="page">
  <div class="p-head"><h2>报警记录</h2><button class="btn-sm">导出</button></div>
  <div class="filter-bar"><select class="sel"><option>全部类型</option></select><select class="sel"><option>全部状态</option></select><input class="inp sm" placeholder="开始日期"><input class="inp sm" placeholder="结束日期"><button class="btn-sm">查询</button></div>
  <table class="tbl">
    <tr><th>时间</th><th>类型</th><th>用户</th><th>宠物</th><th>位置</th><th>状态</th><th>操作</th></tr>
    <tr><td>08-09 12:30</td><td>🏃 离开围栏</td><td>张先生</td><td>旺财</td><td>金水区 XX路</td><td><span class="st warn">已处理</span></td><td><a>详情</a> <a>标记误报</a></td></tr>
    <tr><td>08-09 09:15</td><td>🔋 低电量</td><td>李女士</td><td>咪咪</td><td>—</td><td><span class="st ok">已确认</span></td><td><a>详情</a></td></tr>
    <tr><td>08-08 22:40</td><td>📡 设备离线</td><td>王先生</td><td>豆豆</td><td>—</td><td><span class="st ok">误报</span></td><td><a>详情</a></td></tr>
  </table>
  <div class="pager">共 1,284 条</div>
</div>"""),
# ── 社交管理 ──────────────────────────────────────
dict(f="a9-social-audit.html", title="A9 碰头记录审核", module="社交管理",
  prd="📋 PRD 4.2.5：异常碰头标红（距离<50m/频繁碰头）；审核不通过扣积分+通知用户",
  body="""<div class="page">
  <div class="p-head"><h2>碰头记录审核</h2><button class="btn-sm">导出</button></div>
  <div class="filter-bar"><select class="sel"><option>全部状态</option></select><select class="sel"><option>全部异常标记</option></select><button class="btn-sm">查询</button></div>
  <table class="tbl">
    <tr><th>时间</th><th>发起方</th><th>接收方</th><th>距离</th><th>积分</th><th>异常标记</th><th>操作</th></tr>
    <tr class="row-warn"><td>08-09 11:00</td><td>旺财</td><td>可可</td><td>3m</td><td>+100</td><td><span class="tag red">距离异常</span></td><td><a class="red">审核不通过</a></td></tr>
    <tr class="row-warn"><td>08-08 20:30</td><td>豆豆</td><td>球球</td><td>120m</td><td>+100</td><td><span class="tag red">频繁碰头</span></td><td><a class="red">审核不通过</a></td></tr>
    <tr><td>08-08 16:20</td><td>咪咪</td><td>团子</td><td>8m</td><td>+100</td><td>—</td><td><a>通过</a></td></tr>
  </table>
  <div class="panel"><div class="p-t">异常规则</div><div class="sub">· 相遇距离 &lt; 5m 标记异常 · 同对宠物 24h 内 ≥ 3 次标记频繁 · 审核不通过自动扣回积分并通知</div></div>
</div>"""),
dict(f="a10-points-rule.html", title="A10 积分规则配置", module="社交管理",
  prd="📋 PRD 4.2.5：获取/消费规则+过期策略；变更实时生效",
  body="""<div class="page">
  <div class="p-head"><h2>积分规则配置</h2><button class="btn-sm">保存</button></div>
  <div class="row2">
    <div class="panel"><div class="p-t">获取规则</div>
      <div class="kv"><span>碰头成功</span><b>+100</b></div>
      <div class="kv"><span>邀请好友</span><b>+50 / 人</b></div>
      <div class="kv"><span>每日签到</span><b>+5</b></div>
      <div class="kv"><span>活动奖励</span><b>可配置</b></div>
    </div>
    <div class="panel"><div class="p-t">消费与过期</div>
      <div class="kv"><span>兑换比例</span><b>100 积分 = ¥1</b></div>
      <div class="kv"><span>有效期</span><b>12 个月（滚动）</b></div>
      <div class="kv"><span>过期提醒</span><b>提前 30 天通知</b></div>
      <div class="kv"><span>异常回滚</span><b>自动 + 通知用户</b></div>
    </div>
  </div>
</div>"""),
# ── 会员与营收 ────────────────────────────────────
dict(f="a11-plan-manage.html", title="A11 会员方案管理", module="会员与营收",
  prd="📋 PRD 4.2.6：三档方案+功能对比；价格变更需审批",
  body="""<div class="page">
  <div class="p-head"><h2>会员方案管理</h2><button class="btn-sm">新增方案</button></div>
  <table class="tbl">
    <tr><th>方案</th><th>月价</th><th>年价</th><th>设备上限</th><th>定位刷新</th><th>家人共享</th><th>状态</th><th>操作</th></tr>
    <tr><td>免费版</td><td>¥0</td><td>¥0</td><td>1</td><td>5分钟</td><td>—</td><td><span class="st ok">上架</span></td><td><a>编辑</a></td></tr>
    <tr><td>基础版</td><td>¥19.9</td><td>¥199</td><td>3</td><td>5秒</td><td>—</td><td><span class="st ok">上架</span></td><td><a>编辑</a></td></tr>
    <tr><td>Pro版</td><td>¥29.9</td><td>¥299</td><td>10</td><td>5秒</td><td>5人</td><td><span class="st ok">上架</span></td><td><a>编辑</a></td></tr>
  </table>
  <div class="panel"><div class="p-t">待审批变更</div>
    <div class="kv"><span>2026-08-07 基础版月价 ¥19.9 → ¥21.9</span><b><a>审批</a> <a class="red">驳回</a></b></div>
  </div>
</div>"""),
dict(f="a12-order-list.html", title="A12 订单列表", module="会员与营收",
  prd="📋 PRD 4.2.6：按状态/类型筛选；退款需审批+通知用户",
  body="""<div class="page">
  <div class="p-head"><h2>订单列表</h2><button class="btn-sm">导出 Excel</button></div>
  <div class="filter-bar"><select class="sel"><option>全部状态</option></select><select class="sel"><option>全部类型</option></select><input class="inp sm" placeholder="订单号"><button class="btn-sm">查询</button></div>
  <table class="tbl">
    <tr><th>订单号</th><th>用户</th><th>类型</th><th>金额</th><th>渠道</th><th>状态</th><th>时间</th><th>操作</th></tr>
    <tr><td>PT20260809001</td><td>张先生</td><td>Pro 月付</td><td>¥29.9</td><td>微信</td><td><span class="st ok">已支付</span></td><td>08-09 10:20</td><td><a>详情</a></td></tr>
    <tr><td>PT20260808002</td><td>李女士</td><td>基础 年付</td><td>¥199</td><td>支付宝</td><td><span class="st ok">已支付</span></td><td>08-08 15:40</td><td><a>详情</a></td></tr>
    <tr><td>PT20260807001</td><td>王先生</td><td>Pro 月付</td><td>¥29.9</td><td>微信</td><td><span class="st ban">退款申请</span></td><td>08-07 09:12</td><td><a class="red">审批退款</a></td></tr>
  </table>
  <div class="pager">共 5,320 条</div>
</div>"""),
dict(f="a13-revenue.html", title="A13 收入统计", module="会员与营收",
  prd="📋 PRD 4.2.6：MRR/ARR/ARPU+收入趋势+渠道分布；支持导出 Excel",
  body="""<div class="page">
  <div class="p-head"><h2>收入统计</h2><div class="seg"><span class="on">月</span><span>季</span><span>年</span></div><button class="btn-sm">导出 Excel</button></div>
  <div class="kpi-grid">
    <div class="kpi"><div class="k-l">MRR</div><div class="k-v">¥128.6万</div><div class="k-d up">▲ 15.7%</div></div>
    <div class="kpi"><div class="k-l">ARR</div><div class="k-v">¥1,543万</div><div class="k-d up">▲ 12.3%</div></div>
    <div class="kpi"><div class="k-l">ARPU</div><div class="k-v">¥14.9</div><div class="k-d up">▲ 6.8%</div></div>
    <div class="kpi"><div class="k-l">付费转化率</div><div class="k-v">8.2%</div><div class="k-d up">▲ 1.1%</div></div>
  </div>
  <div class="row2">
    <div class="panel"><div class="p-t">收入趋势</div><div class="chart-line"><div class="bar" style="height:25%"></div><div class="bar" style="height:40%"></div><div class="bar" style="height:35%"></div><div class="bar" style="height:58%"></div><div class="bar" style="height:50%"></div><div class="bar" style="height:75%"></div><div class="bar" style="height:100%"></div></div></div>
    <div class="panel"><div class="p-t">渠道分布</div>
      <div class="ch-row"><span>微信支付</span><div class="ch-bar"><div class="ch-fill wx" style="width:65%"></div></div><b>65%</b></div>
      <div class="ch-row"><span>支付宝</span><div class="ch-bar"><div class="ch-fill ali" style="width:25%"></div></div><b>25%</b></div>
      <div class="ch-row"><span>Apple</span><div class="ch-bar"><div class="ch-fill ap" style="width:10%"></div></div><b>10%</b></div>
    </div>
  </div>
</div>"""),
# ── 内容管理 ──────────────────────────────────────
dict(f="a14-content.html", title="A14 内容管理", module="内容管理",
  prd="📋 PRD 4.2.7：公告定时发布+推送范围+置顶/下线；Banner 配置+链接+排序",
  body="""<div class="page">
  <div class="p-head"><h2>内容管理</h2><button class="btn-sm">新建公告</button></div>
  <div class="row2">
    <div class="panel"><div class="p-t">📢 公告管理</div>
      <table class="tbl">
        <tr><th>标题</th><th>推送范围</th><th>发布状态</th><th>操作</th></tr>
        <tr><td>v0.4.0 版本更新公告</td><td>全部用户</td><td><span class="st ok">已发布</span></td><td><a>置顶</a> <a>下线</a></td></tr>
        <tr><td>Pro 会员 8 折活动</td><td>免费用户</td><td><span class="st warn">定时 08-10 09:00</span></td><td><a>编辑</a></td></tr>
      </table>
    </div>
    <div class="panel"><div class="p-t">🖼️ Banner 管理</div>
      <div class="banner-row"><span>📸 首页 Banner 1</span><b>会员活动页</b><a>编辑</a> <a>排序↑</a></div>
      <div class="banner-row"><span>📸 首页 Banner 2</span><b>新用户引导</b><a>编辑</a> <a>排序↑</a></div>
      <div class="banner-row"><span>📸 社交页 Banner</span><b>碰头玩法介绍</b><a>编辑</a></div>
    </div>
  </div>
</div>"""),
# ── 系统设置 ──────────────────────────────────────
dict(f="a15-system.html", title="A15 系统设置", module="系统设置",
  prd="📋 PRD 4.2.8：RBAC 权限模型 4 种角色；操作日志全量审计保留 180 天，不可编辑/删除，支持导出",
  body="""<div class="page">
  <div class="p-head"><h2>系统设置</h2></div>
  <div class="row2">
    <div class="panel"><div class="p-t">🔐 角色权限 (RBAC)</div>
      <table class="tbl">
        <tr><th>角色</th><th>数据概览</th><th>用户</th><th>宠物</th><th>设备</th><th>报警</th><th>营收</th><th>系统</th></tr>
        <tr><td>超管</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
        <tr><td>运营</td><td>只读</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>—</td><td>—</td></tr>
        <tr><td>客服</td><td>—</td><td>只读</td><td>只读</td><td>只读</td><td>✅</td><td>—</td><td>—</td></tr>
        <tr><td>财务</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>只读</td><td>—</td></tr>
      </table>
    </div>
    <div class="panel"><div class="p-t">📋 操作日志 <span class="sub">保留 180 天</span></div>
      <div class="log-row2"><span>08-09 11:02</span><b>admin</b><i>封禁用户 138****5678</i></div>
      <div class="log-row2"><span>08-09 10:41</span><b>admin</b><i>修改猫咪报警默认规则</i></div>
      <div class="log-row2"><span>08-08 22:15</span><b>ops_li</b><i>导出订单报表</i></div>
      <div class="log-row2"><span>08-08 16:30</span><b>finance_w</b><i>审批退款 PT20260807001</i></div>
      <button class="btn-sm" style="margin-top:12px">导出日志</button>
    </div>
  </div>
</div>"""),
]

ADMIN_CSS = """
  * { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system,'PingFang SC',sans-serif; }
  body { background:#e8eaee; display:flex; justify-content:center; align-items:center; min-height:100vh; }
  .stage { display:flex; gap:32px; align-items:center; }
  .meta { width:300px; }
  .meta h1 { font-size:20px; margin-bottom:12px; }
  .meta .tag { display:inline-block; background:#3D6CF5; color:#fff; font-size:12px; padding:3px 10px; border-radius:999px; margin-bottom:10px; }
  .meta p { font-size:13px; color:#555; line-height:1.8; }
  .meta .nav { margin-top:16px; font-size:13px; }
  .meta .nav a { color:#3D6CF5; text-decoration:none; margin-right:12px; }
  .prd-ref { margin-top:16px; background:#FFF7ED; border-left:3px solid #F59E0B; padding:12px; border-radius:6px; font-size:12px; color:#92400E; line-height:1.7; }
  .screen { width:1080px; height:680px; background:#F5F6FA; border-radius:16px; overflow:hidden; box-shadow:0 20px 60px rgba(0,0,0,.3); display:flex; }
  .sidebar { width:190px; background:#1F2430; color:#fff; padding:18px 0; flex-shrink:0; }
  .sb-logo { padding:6px 22px 18px; font-size:16px; font-weight:700; border-bottom:1px solid rgba(255,255,255,.1); margin-bottom:14px; }
  .sb-item { padding:11px 22px; font-size:13px; color:#9CA3AF; cursor:pointer; }
  .sb-item.on { background:rgba(61,108,245,.2); color:#fff; border-left:3px solid #3D6CF5; }
  .main { flex:1; overflow-y:auto; padding:20px 24px; }
  .p-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
  .p-head h2 { font-size:18px; }
  .sub { font-size:12px; color:#999; font-weight:400; margin-left:8px; }
  .btn-sm { background:#3D6CF5; color:#fff; border:none; border-radius:8px; padding:8px 16px; font-size:12px; cursor:pointer; }
  .btn-sm.warn { background:#F59E0B; }
  .kpi-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:16px; }
  .kpi { background:#fff; border-radius:12px; padding:16px; }
  .k-l { font-size:12px; color:#888; }
  .k-v { font-size:24px; font-weight:800; margin:6px 0; }
  .k-d { font-size:11px; }
  .k-d.up { color:#22C55E; } .k-d.down { color:#EF4444; }
  .row2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
  .panel { background:#fff; border-radius:12px; padding:16px; margin-bottom:14px; }
  .p-t { font-size:14px; font-weight:700; margin-bottom:12px; }
  .p-t .live { font-size:10px; color:#EF4444; background:#FEF2F2; padding:2px 8px; border-radius:999px; margin-left:8px; }
  .chart-line { display:flex; align-items:flex-end; gap:8px; height:140px; }
  .bar { flex:1; background:linear-gradient(180deg,#5B8CFF,#3D6CF5); border-radius:4px 4px 0 0; min-height:8px; }
  .live-row { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #F3F4F6; font-size:13px; }
  .live-row b { font-size:18px; }
  .live-row .warn { color:#EF4444; }
  .heat-map { height:150px; background:linear-gradient(135deg,#EAF2EA,#F0F1F5); border-radius:8px; position:relative; }
  .heat-map span { position:absolute; width:46px; height:46px; border-radius:50%; background:#EF4444; }
  .filter-bar { display:flex; gap:10px; margin-bottom:14px; align-items:center; }
  .inp { background:#fff; border:1px solid #E5E7EB; border-radius:8px; padding:9px 14px; font-size:13px; outline:none; }
  .inp.sm { width:180px; }
  .sel { background:#fff; border:1px solid #E5E7EB; border-radius:8px; padding:9px 12px; font-size:13px; }
  .tbl { width:100%; border-collapse:collapse; font-size:13px; }
  .tbl th { background:#F8F9FB; padding:10px; text-align:left; font-size:12px; color:#666; }
  .tbl td { padding:10px; border-bottom:1px solid #F3F4F6; }
  .tbl a { color:#3D6CF5; text-decoration:none; margin-right:10px; cursor:pointer; }
  .tbl a.red { color:#EF4444; }
  .tag { font-size:11px; padding:3px 10px; border-radius:999px; }
  .tag.free { background:#F3F4F6; color:#666; } .tag.basic { background:#EEF2FF; color:#3D6CF5; } .tag.pro { background:#FFFBEB; color:#F59E0B; }
  .tag.red { background:#FEF2F2; color:#EF4444; }
  .st { font-size:11px; padding:3px 10px; border-radius:999px; }
  .st.ok { background:#F0FDF4; color:#22C55E; } .st.warn { background:#FFFBEB; color:#F59E0B; } .st.ban { background:#FEF2F2; color:#EF4444; }
  .pager { font-size:12px; color:#888; padding:12px 0; text-align:right; }
  .pager .cur { color:#3D6CF5; font-weight:700; }
  .seg { display:flex; background:#F0F1F5; border-radius:8px; padding:3px; }
  .seg span { padding:6px 16px; font-size:12px; border-radius:6px; color:#888; }
  .seg span.on { background:#fff; color:#3D6CF5; font-weight:600; }
  .user-info { display:flex; align-items:center; gap:14px; }
  .avatar { width:52px; height:52px; border-radius:50%; background:#EEF2FF; display:flex; align-items:center; justify-content:center; font-size:24px; }
  .tabs { display:flex; gap:6px; margin-bottom:14px; }
  .tabs span { padding:8px 18px; font-size:13px; color:#888; background:#fff; border-radius:8px; cursor:pointer; }
  .tabs span.on { background:#3D6CF5; color:#fff; font-weight:600; }
  .kv { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #F3F4F6; font-size:13px; }
  .kv span { color:#888; } .kv b.ok { color:#22C55E; }
  .log-row2 { display:flex; gap:10px; padding:9px 0; border-bottom:1px solid #F3F4F6; font-size:12px; }
  .log-row2 span { color:#999; } .log-row2 b { color:#3D6CF5; } .log-row2 i { font-style:normal; }
  .row-warn td { background:#FFFBF5; }
  .ch-row { display:flex; align-items:center; gap:10px; padding:9px 0; font-size:12px; }
  .ch-bar { flex:1; height:10px; background:#F0F1F5; border-radius:999px; }
  .ch-fill { height:100%; border-radius:999px; }
  .ch-fill.wx { background:#07C160; } .ch-fill.ali { background:#1677FF; } .ch-fill.ap { background:#555; }
  .banner-row { display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid #F3F4F6; font-size:13px; }
  .banner-row a { color:#3D6CF5; text-decoration:none; }
  .login-wrap { width:100%; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#1F2430,#2D3550); }
  .login-box { background:#fff; border-radius:16px; padding:40px; width:340px; text-align:center; }
  .login-logo { font-size:20px; font-weight:800; }
  .login-sub { font-size:12px; color:#999; margin:6px 0 24px; }
  .login-box .inp { width:100%; margin-bottom:14px; }
  .btn-main { width:100%; background:linear-gradient(135deg,#5B8CFF,#3D6CF5); color:#fff; border:none; border-radius:10px; padding:12px; font-size:15px; font-weight:600; }
  .login-tip { font-size:11px; color:#aaa; margin-top:12px; }
"""

ADMIN_JS = """
<script>
(function(){
  var MOD_MAP = {
    '数据概览':'a2-dashboard.html','用户':'a3-user-list.html','设备':'a5-device-list.html',
    '报警':'a7-alarm-rule.html','社交':'a9-social-audit.html','会员':'a11-plan-manage.html',
    '内容':'a14-content.html','系统':'a15-system.html'
  };
  function showTip(msg){
    var t=document.createElement('div');
    t.style.cssText='position:fixed;left:50%;bottom:30px;transform:translateX(-50%);background:rgba(31,35,41,.92);color:#fff;padding:10px 20px;border-radius:999px;font-size:13px;z-index:9999';
    t.textContent=msg;document.body.appendChild(t);
    setTimeout(function(){t.style.opacity='0';setTimeout(function(){t.remove()},300)},1600);
  }
  document.querySelectorAll('.sb-item').forEach(function(el){
    el.addEventListener('click',function(){
      var txt=el.textContent||'';
      for(var k in MOD_MAP){
        if(txt.indexOf(k)>-1){location.href=MOD_MAP[k];return;}
      }
    });
  });
  document.querySelectorAll('.tbl a,.btn-sm,.banner-row a,.kv a,.seg span,.tabs span,.filter-bar .inp,.filter-bar .sel').forEach(function(el){
    el.addEventListener('click',function(e){
      e.stopPropagation();
      var tag=el.tagName;
      if(tag==='A'){showTip('原型演示：操作未绑定');}
    });
  });
})();
</script>
"""

def build_admin():
    prev_f = None
    for i, p in enumerate(ADMIN_PAGES):
        prev_link = f"<a href='{ADMIN_PAGES[i-1]['f']}'>← 上一屏</a>" if i > 0 else ""
        next_link = f"<a href='{ADMIN_PAGES[i+1]['f']}'>下一屏 →</a>" if i < len(ADMIN_PAGES)-1 else ""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p['title']} — 宠迹后台原型</title>
<style>{ADMIN_CSS}</style>
</head>
<body>
<div class="stage">
  <div class="meta">
    <span class="tag">后台 · {p['module']}</span>
    <h1>{p['title']}</h1>
    <div class="prd-ref">{p['prd']}</div>
    <div class="nav">{prev_link}{next_link}</div>
  </div>
  <div class="screen">
    <div class="sidebar">
      <div class="sb-logo">🐾 宠迹管理</div>
      <div class="sb-item {'on' if p['module']=='数据概览' else ''}">📊 数据概览</div>
      <div class="sb-item {'on' if p['module']=='用户管理' else ''}">👥 用户管理</div>
      <div class="sb-item {'on' if p['module']=='设备管理' else ''}">📡 设备管理</div>
      <div class="sb-item {'on' if p['module']=='报警管理' else ''}">🔔 报警管理</div>
      <div class="sb-item {'on' if p['module']=='社交管理' else ''}">🐾 社交管理</div>
      <div class="sb-item {'on' if p['module']=='会员与营收' else ''}">💰 会员与营收</div>
      <div class="sb-item {'on' if p['module']=='内容管理' else ''}">📢 内容管理</div>
      <div class="sb-item {'on' if p['module']=='系统设置' else ''}">⚙️ 系统设置</div>
    </div>
    <div class="main">
{p['body']}
    </div>
  </div>
</div>
{ADMIN_JS}
</body>
</html>"""
        with open(os.path.join(OUT_ADMIN, p['f']), 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ {p['f']}")

build_admin()
