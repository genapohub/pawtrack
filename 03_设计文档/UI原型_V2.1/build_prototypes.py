# -*- coding: utf-8 -*-
"""宠迹 UI 原型批量生成器 — 统一外壳 + 页面内容数据驱动"""
import os, re

OUT_MOBILE = "/Users/macos/Downloads/工作相关/宠迹/03_设计文档/UI原型_V2.1/mobile"
OUT_ADMIN = "/Users/macos/Downloads/工作相关/宠迹/03_设计文档/UI原型_V2.1/admin"

# ═══════════════════════════════════════════════
# 移动端页面定义 (S3-S26)
# ═══════════════════════════════════════════════
MOBILE_PAGES = [
# ── Flow 1 注册激活 ──────────────────────────────
dict(f="s3-add-pet.html", tag="P0 · Flow 1 注册激活", title="S3 添加宠物", prev="s2-map.html", next="s4-bind-device.html",
  prd="📋 PRD 参考：S3 添加宠物（P0）— 选择猫/狗 + 品种 + 名称；猫/狗选择影响默认设置（猫默认开报警）",
  body="""<div class="logo-sm">🐾 添加宠物</div>
  <div class="card">
    <div class="field"><label>宠物名称</label><input placeholder="如：旺财" value="旺财"></div>
    <div class="field"><label>宠物类型</label>
      <div class="type-row">
        <div class="type active">🐱 猫咪<span>BLE+WiFi 室内定位</span></div>
        <div class="type">🐶 狗狗<span>GPS+4G 户外定位</span></div>
      </div>
    </div>
    <div class="field"><label>品种</label><input placeholder="如：金毛" value="金毛"></div>
    <div class="field"><label>性别</label>
      <div class="pill-row"><span class="pill">未知</span><span class="pill active">男孩</span><span class="pill">女孩</span></div>
    </div>
    <div class="field"><label>体重 (kg)</label><input placeholder="如：25.5" value="25.5"></div>
    <div class="field"><label>安全围栏</label>
      <div class="switch-row"><span>开启电子围栏 <i>默认：猫100m / 狗300m</i></span><div class="switch on"></div></div>
    </div>
    <button class="primary-btn">下一步：绑定定位器</button>
  </div>"""),
dict(f="s4-bind-device.html", tag="P0 · Flow 1 注册激活", title="S4 绑定定位器", prev="s3-add-pet.html", next="s5-pet-list.html",
  prd="📋 PRD 参考：S4 绑定定位器（P0）— 扫码配对 + 绑定成功结果页，成功后展示设备状态+引导下一步",
  body="""<div class="logo-sm">📡 绑定定位器</div>
  <div class="card center">
    <div class="scan-box">▣ 扫码区域<br><span>将定位器机身二维码放入框内</span></div>
    <div class="divider"><span></span><i>或手动输入</i><span></span></div>
    <div class="field"><label>设备序列号 SN</label><input placeholder="设备机身或包装盒 SN 码" value="PT-DG-2026-0001"></div>
    <div class="field"><label>激活码</label><input placeholder="购买时随附激活码" value="**** 4521"></div>
    <button class="primary-btn">绑定到 旺财</button>
  </div>"""),
# ── Flow 2 定位与状态 ────────────────────────────
dict(f="s5-pet-list.html", tag="P0 · Flow 2 定位与状态", title="S5 宠物列表 Tab", prev="s4-bind-device.html", next="s6-pet-detail.html",
  prd="📋 PRD 参考：S5 宠物列表Tab（P0）— 宠物卡片列表+状态标签；狗狗显示「在家/户外玩耍」，猫咪显示「宅家」",
  body="""<div class="topbar"><b>我的宠物</b><span class="plus">＋</span></div>
  <div class="card pet-card-row">
    <div class="pet-avatar dog">🐶</div>
    <div><div class="pet-name">旺财 <i>金毛 · 2岁</i></div><div class="pet-sub">📍 在家 · 30秒前</div></div>
    <span class="badge green">在家</span>
  </div>
  <div class="card pet-card-row">
    <div class="pet-avatar cat">🐱</div>
    <div><div class="pet-name">咪咪 <i>布偶猫 · 1岁</i></div><div class="pet-sub">📍 宅家 · 2分钟前</div></div>
    <span class="badge blue">宅家</span>
  </div>
  <div class="card pet-card-row" style="opacity:.5">
    <div class="pet-avatar">🐶</div>
    <div><div class="pet-name">豆豆 <i>柯基 · 3岁</i></div><div class="pet-sub">📍 户外玩耍 · 5分钟前</div></div>
    <span class="badge orange">户外</span>
  </div>
  <div class="tip">💡 免费版最多添加 3 只宠物，升级会员解锁更多</div>"""),
dict(f="s6-pet-detail.html", tag="P0 · Flow 2 定位与状态", title="S6 宠物详情", prev="s5-pet-list.html", next="s7-history.html",
  prd="📋 PRD 参考：S6 宠物详情（P0）— 宠物信息+报警设置入口+Pro入口；含设备状态、电量、报警快捷入口、Pro对比",
  body="""<div class="navbar-sm"><span class="back">‹</span>旺财 <span class="edit">编辑</span></div>
  <div class="hero dog-bg">
    <div class="big-avatar">🐶</div>
    <div class="hero-name">旺财 <i>金毛 · 2岁 · 25.5kg</i></div>
    <div class="hero-status"><span class="badge green">● 在线</span><span class="badge">🔋 86%</span></div>
  </div>
  <div class="card grid-2">
    <div class="cell">📍 实时位置<span>郑州市金水区</span></div>
    <div class="cell">🛡️ 安全围栏<span>已开启 · 300m</span></div>
    <div class="cell">🗺️ 历史轨迹<span>今天 2.3km</span></div>
    <div class="cell">📡 设备状态<span>PT-DG-2026-0001</span></div>
  </div>
  <div class="card menu">
    <div class="menu-item">🛡️ 报警设置 <span>›</span></div>
    <div class="menu-item">📖 历史轨迹 <span>›</span></div>
    <div class="menu-item">💎 升级 Pro <span class="pro-tag">对比功能</span><span>›</span></div>
    <div class="menu-item">🔔 设备状态提醒 <span>›</span></div>
  </div>"""),
dict(f="s7-history.html", tag="P0 · Flow 2 定位与状态", title="S7 历史轨迹", prev="s6-pet-detail.html", next="s8-nearby.html",
  prd="📋 PRD 参考：S7 历史轨迹（P0）— 时间轴选择+轨迹回放；免费7天/会员无限，触发订阅转化",
  body="""<div class="navbar-sm"><span class="back">‹</span>历史轨迹</div>
  <div class="date-bar"><span class="date active">今天</span><span class="date">昨天</span><span class="date">近7天</span><span class="date pro">全部 🔒</span></div>
  <div class="map-mini">
    <div class="track" style="left:20%;top:70%;width:18%"></div>
    <div class="track" style="left:36%;top:30%;width:22%"></div>
    <div class="track" style="left:56%;top:30%;width:14%"></div>
    <div class="track" style="left:68%;top:45%;width:20%"></div>
    <div class="dot start"></div><div class="dot end"></div>
  </div>
  <div class="card stat-row">
    <div>总距离<span class="num">2.3km</span></div>
    <div>时长<span class="num">1h 45m</span></div>
    <div>步数<span class="num">3,856</span></div>
  </div>
  <div class="upgrade-banner">🔒 历史轨迹仅保留 7 天<br><button class="mini-btn">升级 Pro 解锁全部轨迹</button></div>"""),
dict(f="s8-nearby.html", tag="P1 · Flow 2 定位与状态", title="S8 附近宠物", prev="s7-history.html", next="s9-alarm-settings.html",
  prd="📋 PRD 参考：S8 附近宠物（P1）— 地图展示附近其他宠物位置；受隐私设置控制，仅显示开放可见的宠物",
  body="""<div class="topbar"><b>附近宠物</b><span class="filter">筛选 ▾</span></div>
  <div class="map-list">
    <div class="map-mini wide">
      <div class="pin-sm dog" style="left:25%;top:35%">🐶</div>
      <div class="pin-sm cat" style="left:55%;top:60%">🐱</div>
      <div class="pin-sm dog" style="left:75%;top:25%">🐶</div>
      <div class="pin-sm me" style="left:40%;top:50%">📍</div>
    </div>
  </div>
  <div class="card nearby-row">
    <div class="pet-avatar dog">🐶</div>
    <div><div class="pet-name">可可 <i>柯基</i></div><div class="pet-sub">距离 350m · 活跃</div></div>
    <span class="meet-btn">打招呼</span>
  </div>
  <div class="card nearby-row">
    <div class="pet-avatar cat">🐱</div>
    <div><div class="pet-name">团子 <i>英短</i></div><div class="pet-sub">距离 800m · 宅家</div></div>
    <span class="meet-btn gray">打招呼</span>
  </div>
  <div class="tip">🔒 位置可见性受对方隐私设置控制</div>"""),
# ── Flow 3 安全报警 ──────────────────────────────
dict(f="s9-alarm-settings.html", tag="P0 · Flow 3 安全报警", title="S9 报警设置", prev="s8-nearby.html", next="s10-fence-custom.html",
  prd="📋 PRD 参考：S9 报警设置（P0）— 围栏报警开关+范围设置入口；猫默认开启(100m)，狗默认关闭(可选300m)",
  body="""<div class="navbar-sm"><span class="back">‹</span>报警设置</div>
  <div class="card">
    <div class="switch-row"><span>电子围栏报警<i>宠物离开设定范围时提醒</i></span><div class="switch on"></div></div>
    <div class="field"><label>围栏半径</label>
      <div class="slider-row"><span>100m</span><div class="slider"><div class="slider-fill" style="width:33%"></div><div class="knob" style="left:33%"></div></div><span>500m</span></div>
      <div class="range-value">当前：<b>300m</b>（狗默认）</div>
    </div>
    <div class="switch-row"><span>进入围栏提醒<i>宠物回到安全区域时通知</i></span><div class="switch"></div></div>
    <div class="switch-row"><span>低电量提醒<i>电量低于 20% 时通知</i></span><div class="switch on"></div></div>
    <div class="switch-row"><span>设备离线提醒<i>离线超过 30 分钟通知</i></span><div class="switch on"></div></div>
    <button class="primary-btn">保存设置</button>
  </div>
  <div class="card rule-note">
    <div class="rule-title">🐱 猫咪默认规则</div>
    <p>围栏 100m（楼栋范围）· 离开立即报警 · 高优先级推送</p>
    <div class="rule-title">🐶 狗狗默认规则</div>
    <p>围栏 300m（小区范围）· 可选开启 · 中优先级推送</p>
  </div>"""),
dict(f="s10-fence-custom.html", tag="P0 · Flow 3 安全报警", title="S10 围栏自定义", prev="s9-alarm-settings.html", next="s11-alarm-notify.html",
  prd="📋 PRD 参考：S10 围栏自定义（P0）— 地图拖拽编辑围栏范围；拖拽圆心调整位置，滑块调整半径，实时预览",
  body="""<div class="navbar-sm"><span class="back">‹</span>自定义围栏</div>
  <div class="fence-editor">
    <div class="map-mini wide">
      <div class="fence-circle" style="left:50%;top:50%"><div class="fence-handle c"></div><div class="fence-handle e"></div></div>
      <div class="pin-sm dog" style="left:50%;top:50%">🐶</div>
    </div>
    <div class="edit-hint">拖拽中心点移动位置 · 拖拽边缘点调整范围</div>
  </div>
  <div class="card">
    <div class="field"><label>围栏半径</label>
      <div class="slider-row"><span>50m</span><div class="slider"><div class="slider-fill" style="width:60%"></div><div class="knob" style="left:60%"></div></div><span>1000m</span></div>
      <div class="range-value">当前：<b>300m</b></div>
    </div>
    <button class="primary-btn">保存围栏</button>
  </div>"""),
dict(f="s11-alarm-notify.html", tag="P0 · Flow 3 安全报警", title="S11 报警通知", prev="s10-fence-custom.html", next="s12-device-status.html",
  prd="📋 PRD 参考：S11 报警通知（P0）— Push+App内通知+紧急联系人；猫咪离开围栏立即报警，狗狗仅开启后报警",
  body="""<div class="navbar-sm"><span class="back">‹</span>报警通知</div>
  <div class="card">
    <div class="switch-row"><span>Push 推送通知</span><div class="switch on"></div></div>
    <div class="switch-row"><span>App 内弹窗提醒</span><div class="switch on"></div></div>
    <div class="field"><label>紧急联系人</label><input placeholder="添加紧急联系人手机号" value="张先生 138****8000"></div>
    <div class="field"><label>短信通知（紧急报警时）</label><input placeholder="添加短信接收号码"></div>
  </div>
  <div class="card alarm-demo">
    <div class="demo-title">🔔 报警推送预览</div>
    <div class="demo-bubble">【紧急】旺财已离开安全区域！<br>当前位置：郑州市金水区 · 12:30<br><span class="demo-link">点击查看实时位置 ›</span></div>
    <div class="demo-bubble blue">【提醒】咪咪电量不足 20%，请及时充电<br><span class="demo-link">查看设备状态 ›</span></div>
  </div>"""),
dict(f="s12-device-status.html", tag="P0 · Flow 3 安全报警", title="S12 设备状态提醒", prev="s11-alarm-notify.html", next="s13-social-home.html",
  prd="📋 PRD 参考：S12 设备状态提醒（P0）— 低电量/离线/拆卸预警；电量<20%预警，离线>30min报警，拆卸检测立即报警",
  body="""<div class="navbar-sm"><span class="back">‹</span>设备状态</div>
  <div class="card device-card">
    <div class="dev-head">
      <div class="dev-icon">📡</div>
      <div><div class="pet-name">PT-DG-2026-0001 <i>狗狗定位器</i></div><div class="pet-sub">固件 v1.2.0 · 绑定 旺财</div></div>
      <span class="badge green">在线</span>
    </div>
    <div class="battery-row"><span>🔋 电量</span><div class="battery-bar"><div class="battery-fill ok" style="width:86%"></div></div><b>86%</b></div>
  </div>
  <div class="card warn-list">
    <div class="warn-item orange"><span>⚠️ 低电量预警</span><i>电量 < 20% 触发</i><b>已开启</b></div>
    <div class="warn-item red"><span>🚨 离线报警</span><i>离线 > 30 分钟触发</i><b>已开启</b></div>
    <div class="warn-item red"><span>⚠️ 拆卸检测</span><i>检测到拆卸立即报警</i><b>已开启</b></div>
    <div class="warn-item gray"><span>🔄 固件升级</span><i>当前 v1.2.0 最新</i><b>检查更新</b></div>
  </div>
  <div class="card"> <div class="switch-row"><span>设备状态异常时短信提醒</span><div class="switch on"></div></div></div>"""),
# ── Flow 4 社交碰头 ──────────────────────────────
dict(f="s13-social-home.html", tag="P2 · Flow 4 社交碰头", title="S13 社交首页", prev="s12-device-status.html", next="s14-friend-list.html",
  prd="📋 PRD 参考：S13 社交首页（P2）— 寻找好朋狗入口+碰头入口；显示附近活跃狗狗数量+待碰头请求",
  body="""<div class="navbar-sm"><span class="back">‹</span>宠物社交</div>
  <div class="hero dog-bg">
    <div class="big-avatar">🐶🤝🐶</div>
    <div class="hero-name">好朋狗</div>
    <div class="hero-status"><span class="badge green">附近 12 只活跃狗狗</span></div>
  </div>
  <div class="card menu">
    <div class="menu-item">🐾 寻找好朋狗 <span class="badge orange">NEW</span><span>›</span></div>
    <div class="menu-item">🤝 发起碰头 <span>›</span></div>
    <div class="menu-item">📅 碰头记录 <span class="badge blue">2 条待确认</span><span>›</span></div>
  </div>
  <div class="card">
    <div class="demo-title">📥 待处理碰头请求</div>
    <div class="nearby-row" style="padding:8px 0">
      <div class="pet-avatar dog">🐶</div>
      <div><div class="pet-name">可可的主人</div><div class="pet-sub">距离 120m · 5分钟前</div></div>
      <span class="meet-btn">接受</span><span class="meet-btn gray">拒绝</span>
    </div>
  </div>"""),
dict(f="s14-friend-list.html", tag="P2 · Flow 4 社交碰头", title="S14 好朋狗列表", prev="s13-social-home.html", next="s15-meet-start.html",
  prd="📋 PRD 参考：S14 好朋狗列表（P2）— 匹配结果+距离+匹配度；按品种/距离/活跃度筛选，显示匹配度百分比",
  body="""<div class="navbar-sm"><span class="back">‹</span>好朋狗匹配</div>
  <div class="filter-bar"><span class="f active">综合</span><span class="f">品种</span><span class="f">距离</span><span class="f">活跃度</span></div>
  <div class="card nearby-row">
    <div class="pet-avatar dog">🐶</div>
    <div><div class="pet-name">可可 <i>柯基 · 2岁</i></div>
    <div class="pet-sub">距离 350m · 活跃 · 匹配度</div>
    <div class="match-bar"><div class="match-fill" style="width:92%"></div></div></div>
    <div><div class="match-num">92%</div><span class="meet-btn">打招呼</span></div>
  </div>
  <div class="card nearby-row">
    <div class="pet-avatar dog">🐶</div>
    <div><div class="pet-name">豆豆 <i>金毛 · 3岁</i></div>
    <div class="pet-sub">距离 800m · 活跃 · 匹配度</div>
    <div class="match-bar"><div class="match-fill" style="width:78%"></div></div></div>
    <div><div class="match-num">78%</div><span class="meet-btn gray">打招呼</span></div>
  </div>
  <div class="card nearby-row">
    <div class="pet-avatar dog">🐶</div>
    <div><div class="pet-name">球球 <i>柴犬 · 1岁</i></div>
    <div class="pet-sub">距离 1.2km · 一般 · 匹配度</div>
    <div class="match-bar"><div class="match-fill" style="width:65%"></div></div></div>
    <div><div class="match-num">65%</div><span class="meet-btn gray">打招呼</span></div>
  </div>"""),
dict(f="s15-meet-start.html", tag="P2 · Flow 4 社交碰头", title="S15 碰头开始", prev="s14-friend-list.html", next="s16-meet-seeking.html",
  prd="📋 PRD 参考：S15 碰头开始（P2）— 发起碰头请求+距离校验；双方距离>50m才可发起，对方确认后开始",
  body="""<div class="navbar-sm"><span class="back">‹</span>发起碰头</div>
  <div class="card center" style="padding:28px 18px">
    <div class="big-avatar">🤝</div>
    <div class="hero-name" style="margin-top:10px">与 可可 碰头</div>
    <div class="pet-sub">双方距离：<b style="color:#3D6CF5">350m</b>（需 > 50m 才可发起）</div>
    <div class="check">✅ 距离校验通过</div>
    <button class="primary-btn" style="margin-top:18px">发送碰头邀请</button>
    <div class="tip" style="margin-top:12px">对方确认后自动开始 · 碰头成功各得 100 积分</div>
  </div>"""),
dict(f="s16-meet-seeking.html", tag="P2 · Flow 4 社交碰头", title="S16 碰头寻找中", prev="s15-meet-start.html", next="s17-meet-success.html",
  prd="📋 PRD 参考：S16 碰头寻找中（P2）— 实时距离倒计时+导航；显示当前距离，<5m时触发碰头确认弹窗",
  body="""<div class="navbar-sm"><span class="back">‹</span>碰头进行中</div>
  <div class="map-mini wide">
    <div class="pin-sm me" style="left:30%;top:50%">📍</div>
    <div class="pin-sm dog" style="left:70%;top:50%">🐶</div>
    <div class="meet-line"></div>
    <div class="dist-badge">距离 12m</div>
  </div>
  <div class="card center">
    <div class="countdown">⏱ 剩余时间 04:32</div>
    <div class="dist-num">12<b>m</b></div>
    <div class="pet-sub">接近中 · 小于 5m 时触发确认</div>
    <button class="primary-btn" style="margin-top:16px">🧭 打开导航</button>
  </div>"""),
dict(f="s17-meet-success.html", tag="P2 · Flow 4 社交碰头", title="S17 碰头成功", prev="s16-meet-seeking.html", next="s18-pro-entry.html",
  prd="📋 PRD 参考：S17 碰头成功（P2）— 双方确认+积分奖励；双方确认后各得100积分，展示碰头记录卡",
  body="""<div class="card center" style="padding:36px 18px;margin-top:20px">
    <div class="success-circle">🎉</div>
    <div class="hero-name" style="margin-top:12px">碰头成功！</div>
    <div class="pet-sub">旺财 与 可可 完成首次碰头</div>
    <div class="points-gain">+100 <span>积分</span></div>
    <div class="record-card">
      <div>🤝 碰头记录</div>
      <div class="pet-sub">2026-08-09 12:30 · 金水区市民公园</div>
      <div class="pet-sub">用时 4 分钟 · 距离相遇 5m</div>
    </div>
    <button class="primary-btn" style="margin-top:18px">查看碰头记录</button>
  </div>"""),
# ── Flow 5 商业变现 ──────────────────────────────
dict(f="s18-pro-entry.html", tag="P0 · Flow 5 商业变现", title="S18 Pro 入口", prev="s17-meet-success.html", next="s19-membership.html",
  prd="📋 PRD 参考：S18 Pro入口（P0）— 多触点入口（地图/宠物详情/轨迹/我的）；功能限制时触发升级提示，展示免费vs会员对比",
  body="""<div class="card center" style="margin-top:16px">
    <div class="lock-icon">🔒</div>
    <div class="hero-name">功能升级提示</div>
    <div class="pet-sub" style="margin-top:6px">历史轨迹已超过 7 天免费保留期</div>
    <button class="primary-btn" style="margin-top:16px">升级解锁全部轨迹</button>
    <div class="link" style="margin-top:10px">查看免费 vs 会员对比 ›</div>
  </div>
  <div class="card">
    <div class="demo-title">免费 vs Pro 对比</div>
    <table class="cmp-table">
      <tr><th>功能</th><th>免费版</th><th>Pro 版</th></tr>
      <tr><td>定位刷新</td><td>5 分钟/次</td><td class="hi">5 秒/次</td></tr>
      <tr><td>历史轨迹</td><td>7 天</td><td class="hi">无限</td></tr>
      <tr><td>设备数量</td><td>1 台</td><td class="hi">10 台</td></tr>
      <tr><td>家人共享</td><td>—</td><td class="hi">5 人</td></tr>
      <tr><td>优先客服</td><td>—</td><td class="hi">✓</td></tr>
    </table>
  </div>"""),
dict(f="s19-membership.html", tag="P0 · Flow 5 商业变现", title="S19 会员订阅", prev="s18-pro-entry.html", next="s20-points-shop.html",
  prd="📋 PRD 参考：S19 会员订阅（P0）— 三档定价+功能对比；基础版19.9/月、Pro版29.9/月，年付优惠约17%",
  body="""<div class="navbar-sm"><span class="back">‹</span>会员中心</div>
  <div class="hero dog-bg">
    <div class="big-avatar">💎</div>
    <div class="hero-name">升级 Pro 会员</div>
    <div class="hero-status"><span class="badge">当前：免费版</span></div>
  </div>
  <div class="plan-card plan-pro">
    <div><div class="plan-name">Pro 版 <span class="hot">推荐</span></div><div class="pet-sub">10 台设备 · 轨迹无限 · 家人共享</div></div>
    <div class="plan-price">¥29.9<span>/月</span></div>
  </div>
  <div class="plan-card">
    <div><div class="plan-name">基础版</div><div class="pet-sub">3 台设备 · 轨迹无限</div></div>
    <div class="plan-price">¥19.9<span>/月</span></div>
  </div>
  <div class="plan-card">
    <div><div class="plan-name">Pro 年付 <span class="save">省17%</span></div><div class="pet-sub">¥299/年 · 相当于 ¥24.9/月</div></div>
    <div class="plan-price red">¥299<span>/年</span></div>
  </div>
  <div class="card"><div class="demo-title">📊 三档对比</div>
    <table class="cmp-table">
      <tr><th>功能</th><th>免费</th><th>基础</th><th>Pro</th></tr>
      <tr><td>定位刷新</td><td>5分钟</td><td class="hi">5秒</td><td class="hi">5秒</td></tr>
      <tr><td>设备</td><td>1台</td><td class="hi">3台</td><td class="hi">10台</td></tr>
      <tr><td>家人共享</td><td>—</td><td>—</td><td class="hi">5人</td></tr>
    </table>
  </div>
  <div class="card center"><button class="primary-btn">立即开通 Pro</button><div class="tip">支持微信支付 · 模拟支付演示</div></div>"""),
dict(f="s20-points-shop.html", tag="P1 · Flow 5 商业变现", title="S20 积分商城", prev="s19-membership.html", next="s21-points-detail.html",
  prd="📋 PRD 参考：S20 积分商城（P1）— 积分兑换宠物用品/优惠券；积分来源：碰头+邀请+签到+活动，12月过期",
  body="""<div class="navbar-sm"><span class="back">‹</span>积分商城</div>
  <div class="hero dog-bg" style="padding:20px">
    <div class="hero-name">🪙 我的积分 <span style="color:#F59E0B">1,280</span></div>
    <div class="hero-status"><span class="badge orange">12月31日过期</span></div>
  </div>
  <div class="shop-grid">
    <div class="shop-item"><div class="shop-icon">🦴</div><div class="shop-name">磨牙棒</div><div class="shop-pts">200 积分</div><button class="ex-btn">兑换</button></div>
    <div class="shop-item"><div class="shop-icon">🎫</div><div class="shop-name">会员8折券</div><div class="shop-pts">500 积分</div><button class="ex-btn">兑换</button></div>
    <div class="shop-item"><div class="shop-icon">🐟</div><div class="shop-name">猫罐头</div><div class="shop-pts">300 积分</div><button class="ex-btn">兑换</button></div>
    <div class="shop-item"><div class="shop-icon">🧶</div><div class="shop-name">逗猫棒</div><div class="shop-pts">150 积分</div><button class="ex-btn">兑换</button></div>
  </div>"""),
dict(f="s21-points-detail.html", tag="P1 · Flow 5 商业变现", title="S21 积分明细", prev="s20-points-shop.html", next="s22-profile.html",
  prd="📋 PRD 参考：S21 积分明细（P1）— 积分收支记录；按时间排序，显示获取/消费/过期记录",
  body="""<div class="navbar-sm"><span class="back">‹</span>积分明细</div>
  <div class="card center" style="padding:24px">
    <div class="pts-total">1,280</div>
    <div class="pet-sub">当前可用积分</div>
  </div>
  <div class="card">
    <div class="log-row"><span>🤝 碰头奖励</span><i>08-09 12:30</i><b class="plus">+100</b></div>
    <div class="log-row"><span>📅 每日签到</span><i>08-09 09:00</i><b class="plus">+5</b></div>
    <div class="log-row"><span>🎁 邀请好友成功</span><i>08-08 20:15</i><b class="plus">+50</b></div>
    <div class="log-row"><span>🛒 兑换磨牙棒</span><i>08-05 14:30</i><b class="minus">-200</b></div>
    <div class="log-row"><span>⏰ 积分过期</span><i>07-31 00:00</i><b class="minus">-60</b></div>
  </div>"""),
# ── Flow 6 个人中心 ──────────────────────────────
dict(f="s22-profile.html", tag="P0 · Flow 6 个人中心", title="S22 个人中心", prev="s21-points-detail.html", next="s23-notify-settings.html",
  prd="📋 PRD 参考：S22 个人中心（P0）— 用户信息+会员卡+功能入口；含通知设置、邀请好友、设备管理、设置入口",
  body="""<div class="card profile-card">
    <div class="avatar-lg">🐾</div>
    <div><div class="hero-name" style="font-size:17px">张先生</div><div class="pet-sub">138****8000</div></div>
    <span class="vip-card">免费版 ›</span>
  </div>
  <div class="card menu">
    <div class="menu-item">💎 会员中心 <span>›</span></div>
    <div class="menu-item">🪙 我的积分 <span class="badge blue">1,280</span><span>›</span></div>
    <div class="menu-item">🎁 邀请好友 <span class="badge orange">+50积分/人</span><span>›</span></div>
    <div class="menu-item">📡 设备管理 <span>›</span></div>
    <div class="menu-item">🔔 通知设置 <span>›</span></div>
    <div class="menu-item">⚙️ 设置 <span>›</span></div>
  </div>"""),
dict(f="s23-notify-settings.html", tag="P0 · Flow 6 个人中心", title="S23 通知设置", prev="s22-profile.html", next="s24-invite.html",
  prd="📋 PRD 参考：S23 通知设置（P0）— 系统消息开关；独立于报警设置，控制活动/社交/营销推送",
  body="""<div class="navbar-sm"><span class="back">‹</span>通知设置</div>
  <div class="card">
    <div class="demo-title">推送类型</div>
    <div class="switch-row"><span>系统消息<i>设备绑定/固件升级等</i></span><div class="switch on"></div></div>
    <div class="switch-row"><span>社交互动<i>碰头邀请/好友动态</i></span><div class="switch on"></div></div>
    <div class="switch-row"><span>营销活动<i>会员优惠/积分到期提醒</i></span><div class="switch"></div></div>
  </div>
  <div class="card">
    <div class="demo-title">免打扰时段</div>
    <div class="switch-row"><span>开启免打扰</span><div class="switch"></div></div>
    <div class="field" style="margin-top:12px"><label>时段</label><input placeholder="22:00 - 08:00"></div>
  </div>"""),
dict(f="s24-invite.html", tag="P1 · Flow 6 个人中心", title="S24 邀请好友", prev="s23-notify-settings.html", next="s25-device-manage.html",
  prd="📋 PRD 参考：S24 邀请好友（P1）— 邀请码+分享+记录+积分奖励；每成功邀请1人各得50积分",
  body="""<div class="navbar-sm"><span class="back">‹</span>邀请好友</div>
  <div class="card center" style="padding:28px">
    <div class="big-avatar">🎁</div>
    <div class="hero-name" style="margin-top:8px">邀请好友，各得 50 积分</div>
    <div class="invite-code">PAWTRACK-<b>2026</b></div>
    <button class="primary-btn">分享给好友</button>
  </div>
  <div class="card">
    <div class="demo-title">邀请记录</div>
    <div class="log-row"><span>👤 李雷</span><i>08-08 已注册</i><b class="plus">+50</b></div>
    <div class="log-row"><span>👤 韩梅梅</span><i>08-06 已注册</i><b class="plus">+50</b></div>
  </div>"""),
dict(f="s25-device-manage.html", tag="P0 · Flow 6 个人中心", title="S25 设备管理", prev="s24-invite.html", next="s26-settings.html",
  prd="📋 PRD 参考：S25 设备管理（P0）— 设备列表+绑定/解绑+固件升级；显示设备状态、电量、固件版本",
  body="""<div class="navbar-sm"><span class="back">‹</span>设备管理 <span class="plus">＋</span></div>
  <div class="card">
    <div class="dev-head">
      <div class="dev-icon">📡</div>
      <div><div class="pet-name">PT-DG-2026-0001</div><div class="pet-sub">狗狗定位器 · 绑定 旺财</div></div>
      <span class="badge green">在线</span>
    </div>
    <div class="battery-row"><span>🔋</span><div class="battery-bar"><div class="battery-fill ok" style="width:86%"></div></div><b>86%</b></div>
    <div class="btn-row">
      <button class="outline-btn">🔔 查找设备</button>
      <button class="outline-btn">🔄 固件升级</button>
      <button class="outline-btn red">解绑</button>
    </div>
  </div>
  <div class="card">
    <div class="dev-head">
      <div class="dev-icon cat">🐱</div>
      <div><div class="pet-name">PT-BL-2026-0007</div><div class="pet-sub">猫咪定位器 · 绑定 咪咪</div></div>
      <span class="badge orange">低电量</span>
    </div>
    <div class="battery-row"><span>🔋</span><div class="battery-bar"><div class="battery-fill warn" style="width:18%"></div></div><b>18%</b></div>
  </div>"""),
dict(f="s26-settings.html", tag="P0 · Flow 6 个人中心", title="S26 设置", prev="s25-device-manage.html", next="s1-login.html",
  prd="📋 PRD 参考：S26 设置（P0）— 账号/隐私/通用/关于；隐私设置控制位置可见性，支持退出登录",
  body="""<div class="navbar-sm"><span class="back">‹</span>设置</div>
  <div class="card">
    <div class="demo-title">账号</div>
    <div class="menu-item">手机号 <span>138****8000 ›</span></div>
    <div class="menu-item">修改密码 <span>›</span></div>
  </div>
  <div class="card">
    <div class="demo-title">隐私</div>
    <div class="menu-item">位置可见性 <span>仅好友可见 ›</span></div>
    <div class="menu-item">附近宠物展示 <span>开启 ›</span></div>
    <div class="menu-item">碰头匹配 <span>参与 ›</span></div>
  </div>
  <div class="card">
    <div class="demo-title">通用</div>
    <div class="menu-item">通知设置 <span>›</span></div>
    <div class="menu-item">关于宠迹 <span>v0.4.0 ›</span></div>
  </div>
  <div class="card center"><button class="danger-btn">退出登录</button></div>"""),
]

# ═══════════════════════════════════════════════
# 生成函数
# ═══════════════════════════════════════════════
MOBILE_CSS = """
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
  .phone { width:375px; height:780px; background:#F6F7FB; border-radius:40px; overflow:hidden; box-shadow:0 20px 60px rgba(0,0,0,.25); position:relative; border:8px solid #1c1c1e; display:flex; flex-direction:column; }
  .statusbar { height:40px; background:transparent; display:flex; align-items:center; justify-content:space-between; padding:0 24px; font-size:13px; font-weight:600; color:#1c1c1e; flex-shrink:0; }
  .content { flex:1; overflow-y:auto; padding:8px 16px 24px; }
  .logo-sm { text-align:center; font-size:19px; font-weight:700; padding:18px 0 14px; }
  .card { background:#fff; border-radius:16px; padding:18px; margin-bottom:14px; box-shadow:0 2px 10px rgba(0,0,0,.04); }
  .card.center { text-align:center; }
  .field { margin-bottom:16px; }
  .field label { display:block; font-size:12px; color:#888; margin-bottom:6px; }
  .field input { width:100%; background:#F6F7FB; border:none; border-radius:10px; padding:13px 14px; font-size:14px; outline:none; }
  .primary-btn { width:100%; background:linear-gradient(135deg,#5B8CFF,#3D6CF5); color:#fff; border:none; border-radius:24px; padding:14px; font-size:15px; font-weight:600; cursor:pointer; margin-top:6px; }
  .type-row { display:flex; gap:10px; }
  .type { flex:1; background:#F6F7FB; border:2px solid transparent; border-radius:12px; padding:14px 10px; text-align:center; font-size:14px; font-weight:600; }
  .type span { display:block; font-size:10px; color:#999; font-weight:400; margin-top:4px; }
  .type.active { border-color:#3D6CF5; background:#EEF2FF; color:#3D6CF5; }
  .pill-row { display:flex; gap:10px; }
  .pill { padding:9px 22px; background:#F6F7FB; border-radius:999px; font-size:13px; color:#666; }
  .pill.active { background:#3D6CF5; color:#fff; font-weight:600; }
  .switch-row { display:flex; align-items:center; justify-content:space-between; padding:11px 0; border-bottom:1px solid #F3F4F6; }
  .switch-row:last-child { border-bottom:none; }
  .switch-row span { font-size:14px; font-weight:600; }
  .switch-row i { display:block; font-size:11px; color:#999; font-style:normal; font-weight:400; margin-top:2px; }
  .switch { width:48px; height:28px; border-radius:999px; background:#D1D5DB; position:relative; flex-shrink:0; transition:.2s; }
  .switch::after { content:''; position:absolute; width:22px; height:22px; border-radius:50%; background:#fff; top:3px; left:3px; transition:.2s; }
  .switch.on { background:#3D6CF5; }
  .switch.on::after { left:23px; }
  .slider-row { display:flex; align-items:center; gap:10px; font-size:11px; color:#999; }
  .slider { flex:1; height:6px; background:#E5E7EB; border-radius:999px; position:relative; }
  .slider-fill { position:absolute; height:100%; background:#3D6CF5; border-radius:999px; }
  .knob { position:absolute; top:50%; transform:translate(-50%,-50%); width:18px; height:18px; background:#fff; border:3px solid #3D6CF5; border-radius:50%; }
  .range-value { text-align:center; font-size:13px; color:#666; margin-top:8px; }
  .divider { display:flex; align-items:center; gap:12px; margin:20px 0; }
  .divider span { flex:1; height:1px; background:#E5E7EB; }
  .divider i { font-size:12px; color:#999; font-style:normal; }
  .scan-box { height:180px; border:2px dashed #3D6CF5; border-radius:16px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#3D6CF5; font-size:22px; margin-bottom:6px; }
  .scan-box span { font-size:11px; color:#999; font-weight:400; margin-top:8px; }
  .topbar { display:flex; align-items:center; justify-content:space-between; padding:14px 4px 10px; font-size:18px; }
  .plus { width:30px; height:30px; background:#3D6CF5; color:#fff; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:18px; }
  .pet-avatar { width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:26px; flex-shrink:0; }
  .pet-avatar.dog { background:#EFF6FF; } .pet-avatar.cat { background:#FFF7ED; }
  .pet-card-row { display:flex; align-items:center; gap:14px; }
  .pet-name { font-size:15px; font-weight:700; }
  .pet-name i { font-size:12px; color:#999; font-weight:400; }
  .pet-sub { font-size:12px; color:#888; margin-top:3px; }
  .badge { font-size:11px; padding:4px 10px; border-radius:999px; background:#F3F4F6; color:#666; }
  .badge.green { background:#F0FDF4; color:#22C55E; } .badge.blue { background:#EEF2FF; color:#3D6CF5; } .badge.orange { background:#FFF7ED; color:#F59E0B; }
  .tip { text-align:center; font-size:11px; color:#aaa; padding:8px 0; }
  .navbar-sm { display:flex; align-items:center; justify-content:space-between; padding:14px 8px; font-size:16px; font-weight:700; }
  .navbar-sm .back { font-size:22px; font-weight:400; color:#333; }
  .hero { text-align:center; padding:26px 16px; border-radius:0 0 24px 24px; margin-bottom:14px; }
  .hero.dog-bg { background:linear-gradient(180deg,#EFF6FF,#fff); } .hero.cat-bg { background:linear-gradient(180deg,#FFF7ED,#fff); }
  .big-avatar { font-size:58px; }
  .hero-name { font-size:19px; font-weight:700; margin-top:6px; }
  .hero-name i { font-size:12px; color:#888; font-weight:400; }
  .hero-status { margin-top:10px; display:flex; gap:8px; justify-content:center; }
  .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .cell { font-size:13px; font-weight:600; }
  .cell span { display:block; font-size:12px; color:#888; font-weight:400; margin-top:4px; }
  .menu { padding:6px 18px; }
  .menu-item { display:flex; align-items:center; justify-content:space-between; padding:14px 0; border-bottom:1px solid #F3F4F6; font-size:14px; font-weight:600; }
  .menu-item:last-child { border-bottom:none; }
  .pro-tag { font-size:10px; color:#F59E0B; background:#FFFBEB; padding:2px 8px; border-radius:999px; margin-left:6px; }
  .date-bar { display:flex; gap:10px; padding:4px 4px 14px; }
  .date { font-size:13px; padding:8px 16px; background:#F0F1F5; border-radius:999px; color:#666; }
  .date.active { background:#3D6CF5; color:#fff; font-weight:600; }
  .date.pro { color:#F59E0B; }
  .map-mini { position:relative; height:200px; background:#EAF2EA; border-radius:16px; margin-bottom:14px; overflow:hidden; }
  .map-mini.wide { height:180px; }
  .track { position:absolute; height:4px; background:#3D6CF5; border-radius:4px; transform:rotate(0deg); }
  .dot { position:absolute; width:10px; height:10px; border-radius:50%; }
  .dot.start { background:#22C55E; } .dot.end { background:#EF4444; }
  .stat-row { display:flex; text-align:center; }
  .stat-row div { flex:1; font-size:12px; color:#888; }
  .stat-row .num { display:block; font-size:18px; font-weight:700; color:#1F2329; margin-top:4px; }
  .upgrade-banner { background:linear-gradient(135deg,#FBBF24,#F59E0B); color:#fff; border-radius:16px; padding:18px; text-align:center; font-size:14px; font-weight:600; }
  .mini-btn { background:#fff; color:#F59E0B; border:none; border-radius:999px; padding:8px 20px; font-size:13px; font-weight:600; margin-top:10px; }
  .filter { font-size:13px; color:#666; }
  .nearby-row { display:flex; align-items:center; gap:14px; }
  .meet-btn { font-size:13px; font-weight:600; color:#fff; background:#3D6CF5; padding:8px 18px; border-radius:999px; }
  .meet-btn.gray { background:#F3F4F6; color:#999; }
  .pin-sm { position:absolute; transform:translate(-50%,-100%); font-size:24px; }
  .pin-sm.me { font-size:20px; }
  .slider2 { flex:1; }
  .battery-row { display:flex; align-items:center; gap:10px; margin-top:14px; font-size:13px; }
  .battery-bar { flex:1; height:10px; background:#F0F1F5; border-radius:999px; overflow:hidden; }
  .battery-fill { height:100%; border-radius:999px; }
  .battery-fill.ok { background:#22C55E; } .battery-fill.warn { background:#F59E0B; } .battery-fill.low { background:#EF4444; }
  .warn-item { display:flex; align-items:center; gap:10px; padding:12px 0; border-bottom:1px solid #F3F4F6; font-size:13px; }
  .warn-item:last-child { border-bottom:none; }
  .warn-item span { font-weight:600; flex:1; }
  .warn-item i { font-size:11px; color:#999; flex:1; font-style:normal; }
  .warn-item b { font-size:12px; }
  .warn-item.orange b { color:#F59E0B; } .warn-item.red b { color:#EF4444; } .warn-item.gray b { color:#999; }
  .dev-head { display:flex; align-items:center; gap:12px; }
  .dev-icon { width:46px; height:46px; border-radius:12px; background:#EEF2FF; display:flex; align-items:center; justify-content:center; font-size:22px; }
  .fence-editor { position:relative; }
  .fence-circle { position:absolute; transform:translate(-50%,-50%); width:160px; height:160px; border:2px dashed rgba(61,108,245,.6); border-radius:50%; }
  .fence-handle { position:absolute; width:18px; height:18px; border-radius:50%; background:#3D6CF5; border:3px solid #fff; box-shadow:0 2px 6px rgba(0,0,0,.2); }
  .fence-handle.c { top:50%; left:50%; transform:translate(-50%,-50%); }
  .fence-handle.e { top:50%; right:-9px; transform:translateY(-50%); }
  .edit-hint { text-align:center; font-size:11px; color:#999; padding:8px 0; }
  .rule-title { font-size:13px; font-weight:700; margin:10px 0 4px; }
  .rule-note p { font-size:12px; color:#666; line-height:1.6; }
  .demo-title { font-size:14px; font-weight:700; margin-bottom:12px; }
  .demo-bubble { background:#F0FDF4; border:1px solid #D1FAE5; border-radius:12px; padding:12px 14px; font-size:13px; line-height:1.7; margin-bottom:10px; }
  .demo-bubble.blue { background:#EEF2FF; border-color:#C7D2FE; }
  .demo-link { color:#3D6CF5; font-weight:600; }
  .filter-bar { display:flex; gap:8px; padding:4px 4px 14px; }
  .f { font-size:13px; padding:8px 18px; background:#F0F1F5; border-radius:999px; color:#666; }
  .f.active { background:#3D6CF5; color:#fff; font-weight:600; }
  .match-bar { width:120px; height:6px; background:#F0F1F5; border-radius:999px; margin-top:6px; overflow:hidden; }
  .match-fill { height:100%; background:linear-gradient(90deg,#22C55E,#3D6CF5); border-radius:999px; }
  .match-num { font-size:16px; font-weight:700; color:#3D6CF5; text-align:center; margin-bottom:6px; }
  .check { display:inline-block; margin-top:12px; font-size:12px; color:#22C55E; background:#F0FDF4; padding:6px 14px; border-radius:999px; font-weight:600; }
  .meet-line { position:absolute; top:50%; left:32%; width:36%; height:3px; background:linear-gradient(90deg,#3D6CF5,#22C55E); border-radius:3px; }
  .dist-badge { position:absolute; top:16px; right:16px; background:#fff; border-radius:999px; padding:6px 14px; font-size:13px; font-weight:700; color:#3D6CF5; box-shadow:0 2px 8px rgba(0,0,0,.15); }
  .countdown { font-size:14px; color:#666; }
  .dist-num { font-size:56px; font-weight:800; color:#3D6CF5; }
  .dist-num b { font-size:20px; font-weight:600; }
  .success-circle { width:96px; height:96px; border-radius:50%; background:#F0FDF4; display:flex; align-items:center; justify-content:center; font-size:44px; margin:0 auto; }
  .points-gain { margin-top:12px; font-size:32px; font-weight:800; color:#F59E0B; }
  .points-gain span { font-size:14px; font-weight:400; color:#999; }
  .record-card { background:#F6F7FB; border-radius:12px; padding:14px; margin-top:16px; font-size:14px; font-weight:600; text-align:left; }
  .lock-icon { font-size:44px; }
  .link { font-size:13px; color:#3D6CF5; font-weight:600; }
  .cmp-table { width:100%; border-collapse:collapse; font-size:13px; margin-top:8px; }
  .cmp-table th { background:#F8F9FB; padding:10px 8px; font-size:12px; color:#666; text-align:center; }
  .cmp-table td { padding:10px 8px; text-align:center; border-bottom:1px solid #F3F4F6; }
  .cmp-table .hi { color:#3D6CF5; font-weight:700; }
  .plan-card { display:flex; align-items:center; justify-content:space-between; background:#fff; border-radius:16px; padding:18px; margin-bottom:12px; box-shadow:0 2px 10px rgba(0,0,0,.04); }
  .plan-card.plan-pro { border:2px solid #F59E0B; }
  .plan-name { font-size:16px; font-weight:700; }
  .plan-price { font-size:24px; font-weight:800; color:#1F2329; }
  .plan-price span { font-size:12px; font-weight:400; color:#999; }
  .plan-price.red { color:#EF4444; }
  .hot { font-size:10px; background:#F59E0B; color:#fff; padding:2px 8px; border-radius:999px; vertical-align:middle; }
  .save { font-size:10px; background:#F0FDF4; color:#22C55E; padding:2px 8px; border-radius:999px; vertical-align:middle; }
  .shop-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .shop-item { background:#fff; border-radius:16px; padding:16px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,.04); }
  .shop-icon { font-size:38px; }
  .shop-name { font-size:13px; font-weight:600; margin-top:8px; }
  .shop-pts { font-size:12px; color:#F59E0B; margin-top:4px; }
  .ex-btn { margin-top:10px; width:100%; background:#EEF2FF; color:#3D6CF5; border:none; border-radius:999px; padding:8px; font-size:13px; font-weight:600; }
  .pts-total { font-size:44px; font-weight:800; color:#F59E0B; }
  .log-row { display:flex; align-items:center; gap:10px; padding:13px 0; border-bottom:1px solid #F3F4F6; font-size:14px; }
  .log-row:last-child { border-bottom:none; }
  .log-row span { flex:1; font-weight:600; }
  .log-row i { font-size:11px; color:#999; font-style:normal; }
  .log-row b { font-size:14px; }
  .log-row b.plus { color:#3D6CF5; } .log-row b.minus { color:#9CA3AF; }
  .profile-card { display:flex; align-items:center; gap:14px; }
  .avatar-lg { width:64px; height:64px; border-radius:50%; background:#EEF2FF; display:flex; align-items:center; justify-content:center; font-size:30px; }
  .vip-card { background:linear-gradient(135deg,#FBBF24,#F59E0B); color:#fff; font-size:12px; font-weight:600; padding:8px 16px; border-radius:999px; }
  .invite-code { background:#F6F7FB; border:2px dashed #3D6CF5; border-radius:12px; padding:14px 30px; font-size:20px; letter-spacing:3px; color:#3D6CF5; margin:16px 0; font-weight:700; }
  .btn-row { display:flex; gap:10px; margin-top:16px; }
  .outline-btn { flex:1; border:1.5px solid #3D6CF5; color:#3D6CF5; background:#fff; border-radius:10px; padding:10px; font-size:13px; font-weight:600; }
  .outline-btn.red { border-color:#EF4444; color:#EF4444; }
  .danger-btn { width:100%; background:#FEF2F2; color:#EF4444; border:none; border-radius:24px; padding:14px; font-size:15px; font-weight:600; }
  .dev-icon.cat { background:#FFF7ED; }
"""

# ═══════════════════════════════════════════════
# 移动端交互脚本：入口点击 → 关键词匹配跳转对应屏
# ═══════════════════════════════════════════════
MOBILE_JS = """
<script>
(function(){
  var NAV_MAP = {
    '会员中心':'s19-membership.html','立即开通':'s19-membership.html','升级 Pro':'s19-membership.html','Pro':'s19-membership.html',
    '积分商城':'s20-points-shop.html','我的积分':'s20-points-shop.html',
    '积分明细':'s21-points-detail.html','邀请好友':'s24-invite.html',
    '设备管理':'s25-device-manage.html','查找设备':'s25-device-manage.html','固件':'s25-device-manage.html',
    '通知设置':'s23-notify-settings.html','免打扰':'s23-notify-settings.html',
    '设置':'s26-settings.html','退出登录':'s26-settings.html',
    '历史轨迹':'s7-history.html','附近宠物':'s8-nearby.html',
    '报警设置':'s9-alarm-settings.html','电子围栏报警':'s9-alarm-settings.html',
    '自定义围栏':'s10-fence-custom.html','围栏':'s10-fence-custom.html',
    '报警通知':'s11-alarm-notify.html','设备状态':'s12-device-status.html',
    '宠物社交':'s13-social-home.html','发起碰头':'s15-meet-start.html','碰头记录':'s13-social-home.html',
    '好朋狗':'s14-friend-list.html','添加宠物':'s3-add-pet.html','绑定':'s4-bind-device.html',
    '宠物列表':'s5-pet-list.html','我的宠物':'s5-pet-list.html','编辑':'s6-pet-detail.html'
  };
  function showTip(msg){
    var t=document.createElement('div');
    t.style.cssText='position:fixed;left:50%;bottom:30px;transform:translateX(-50%);background:rgba(31,35,41,.92);color:#fff;padding:10px 20px;border-radius:999px;font-size:13px;z-index:9999;transition:opacity .3s';
    t.textContent=msg;document.body.appendChild(t);
    setTimeout(function(){t.style.opacity='0';setTimeout(function(){t.remove()},300)},1600);
  }
  document.querySelectorAll('.menu-item,.cell,.meet-btn,.nav-icon,.ex-btn,.mini-btn,.link,.plus,.edit,.outline-btn,.date-bar .date,.shop-item,.switch-row,.nearby-row,.plan-card').forEach(function(el){
    el.addEventListener('click',function(e){
      e.stopPropagation();
      var txt=el.textContent||'';
      for(var k in NAV_MAP){
        if(txt.indexOf(k)>-1){location.href=NAV_MAP[k];return;}
      }
      showTip('原型演示：该入口暂未绑定跳转');
    });
  });
  document.querySelectorAll('.primary-btn,.danger-btn,.btn-main').forEach(function(el){
    el.addEventListener('click',function(e){
      e.stopPropagation();
      var txt=el.textContent||'';
      for(var k in NAV_MAP){
        if(txt.indexOf(k)>-1){location.href=NAV_MAP[k];return;}
      }
      showTip('原型演示：操作未绑定');
    });
  });
})();
</script>
"""

def build_mobile():
    for p in MOBILE_PAGES:
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p['title']} — 宠迹 UI 原型</title>
<style>{MOBILE_CSS}</style>
</head>
<body>
<div class="stage">
  <div class="meta">
    <span class="tag">{p['tag']}</span>
    <h1>{p['title']}</h1>
    <div class="prd-ref">{p['prd']}</div>
    <div class="nav"><a href="{p['prev']}">← 上一屏</a><a href="{p['next']}">下一屏 →</a></div>
  </div>
  <div class="phone">
    <div class="statusbar"><span>9:41</span><span>📶 🔋</span></div>
    <div class="content">
{p['body']}
    </div>
  </div>
</div>
{MOBILE_JS}
</body>
</html>"""
        with open(os.path.join(OUT_MOBILE, p['f']), 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ {p['f']}")

build_mobile()
