#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
OUT = Path("/Users/macos/Downloads/WorkBuddy/pawtrack/03_设计文档/ardot-frames-20261115")
OUT.mkdir(parents=True, exist_ok=True)
CSS = Path("/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/pawtrack_tokens.css").read_text()

IC_BACK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M15 5L8 12l7 7"/></svg>'
IC_HOME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1z"/></svg>'
IC_SOC = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="8" cy="10" r="2.2"/><circle cx="16" cy="10" r="2.2"/><path d="M4.5 17c.7-2 2.2-3 3.5-3s2.8 1 3.5 3M12.5 17c.7-2 2.2-3 3.5-3s2.8 1 3.5 3"/></svg>'
IC_ALM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 4a7 7 0 0 1 7 7v3.2l1.2 2.3H3.8L5 14.2V11a7 7 0 0 1 7-7z"/><path d="M10 19a2 2 0 0 0 4 0"/></svg>'
IC_ME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="9" r="3"/><path d="M5.5 19c1.2-3 3.4-4.5 6.5-4.5s5.3 1.5 6.5 4.5"/></svg>'

def wrap(title, body, w, h):
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>'
            + title + '</title><style>' + CSS +
            '\nhtml,body,.app{width:%dpx;height:%dpx}</style></head><body>%s</body></html>' % (w, h, body))

def write(name, title, body, w=375, h=812):
    (OUT / name).write_text(wrap(title, body, w, h), encoding="utf-8")
    print("wrote", name)

def sb(t="09:41"):
    return '<div class="sb"><span>%s</span><span>示意机 100%%</span></div>' % t

def nav(title, back=True):
    b = '<div class="back"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M15 5L8 12l7 7"/></svg></div>' if back else ""
    return '<div class="nav">%s%s</div>' % (b, title)

def mock(text="本地 Mock 预览 · 非真实硬件 / 微信 / 短信 / 地图 / 支付"):
    return '<div class="mock">%s</div>' % text

def tabs(active):
    items = [("home","首页",IC_HOME),("social","社交",IC_SOC),("alarms","报警",IC_ALM),("me","我的",IC_ME)]
    parts = []
    for k,lab,ic in items:
        parts.append('<div class="tab %s">%s<span>%s</span></div>' % ("on" if k==active else "", ic, lab))
    return '<div class="tabbar">' + "".join(parts) + '</div>'

def phone(title, inner, active=None, back=True, extra_mock=None):
    has_tab = active is not None
    body_cls = "body hasmock"
    if not has_tab:
        body_cls += " nontab"
    mk = mock() if extra_mock is None else mock(extra_mock)
    tab = tabs(active) if has_tab else ""
    return ('<div class="phone">' + sb() + nav(title, back) + mk +
            '<div class="%s"><div class="pad">%s</div></div>%s</div>' % (body_cls, inner, tab))

def fmap(cap="示意位置，非实地地图服务 · 示意坐标 31.230, 121.473"):
    return '<div class="map"><div class="grid"></div><div class="fence"></div><div class="pin"></div><div class="cap">%s</div></div>' % cap

write("cover.html", "封面", """
<div class="cover">
  <div class="chip">正式设计稿 · 待设计评审 · 非可编码依据</div>
  <h1>宠迹 · 本地 Mock 可演示主路径</h1>
  <p>登录（Mock 预览）到添加宠物、绑定设备、位置与轨迹、围栏告警，以及我的与设置底线、管理端登录与设备告警看数。全程为本地示意，不是真实硬件、微信、短信、支付或地图服务已接入。会员购买、积分兑换、邀请、社交碰头不是本轮必做。Tab 为首页 / 社交 / 报警 / 我的，围栏并入报警设置。Token：Pawtrack Tokens（钢蓝 #2B4F8A）。Logo 精稿未放入。</p>
</div>
""", 1200, 320)

def login(state):
    phone_v = "138 0000 0000" if state != "empty" else ""
    code_v = "123456" if state not in ("empty","cred") else ""
    err = ""
    btn = "进入本地预览"
    dis = ""
    if state == "loading":
        btn = "登录中..."; dis = "disabled"
    if state == "empty":
        err = '<div class="banner warn">请先输入手机号后再进入预览</div>'; dis = "disabled"
    if state == "cred":
        err = '<div class="banner err">预览凭证不正确，请核对后重试。本页仍是本地示意，未调用真实短信。</div>'
    if state == "service":
        err = '<div class="banner err">无法连接服务，请确认后端已启动。当前未接入生产登录。</div>'
    inner = """
    <div style="display:flex;flex-direction:column;align-items:center;padding:18px 0 8px">
      <div class="mark">迹</div>
      <div style="font-size:22px;font-weight:600;margin-top:10px">宠迹</div>
      <div class="muted" style="margin-top:4px">宠物定位与围栏告警 · 本地预览</div>
    </div>
    <div class="card" style="margin-top:8px">
      <div class="field"><label>手机号</label><input class="input" placeholder="请输入手机号" value="%s"></div>
      <div class="field"><label>验证码</label>
        <div class="row">
          <input class="input" placeholder="请输入验证码" value="%s">
          <button class="btn btn-ghost" disabled style="width:108px;flex-shrink:0;font-size:12px">短信未接入</button>
        </div>
      </div>
      %s
      <button class="btn btn-block" %s>%s</button>
      <div class="tiny" style="margin-top:10px;text-align:center">默认以本地 Mock 进入，不调用真实微信、短信或 Apple 登录。</div>
      <div style="height:1px;background:var(--border);margin:16px 0"></div>
      <button class="btn btn-ghost btn-block" disabled>微信登录未接入</button>
    </div>
    """ % (phone_v, code_v, err, dis, btn)
    write("login-%s.html" % state, "登录-"+state, phone("登录", inner, active=None, back=False,
        extra_mock="本地 Mock 预览 · 不接真实微信 / 短信 · 非验收"))

for s in ("default","loading","empty","cred","service"):
    login(s)

pet_cards = """
<div class="card" style="margin-top:12px">
  <div class="between">
    <div class="row"><div class="av">橘</div><div><div style="font-weight:600">橘子</div><div class="tiny">英短 · 猫 · 已绑定定位器</div></div></div>
    <div><span class="tag cat">宅家</span> <span class="tag ok">在线 72%</span></div>
  </div>
  <div class="muted" style="margin-top:8px">最后位置（示意）：小区中心点附近 · 来源 Wi-Fi · 2 分钟前</div>
</div>
<div class="card" style="margin-top:8px">
  <div class="between">
    <div class="row"><div class="av" style="background:#EEE6DA;color:#6A4A28">豆</div><div><div style="font-weight:600">豆豆</div><div class="tiny">柯基 · 狗 · 已绑定定位器</div></div></div>
    <div><span class="tag dog">户外</span> <span class="tag ok">在线 88%</span></div>
  </div>
  <div class="muted" style="margin-top:8px">最后位置（示意）：滨江步道 · 来源 GPS · 刚刚。预览不模拟真实刷新间隔。</div>
</div>
"""

write("home-default.html","首页-默认", phone("首页",
    fmap() + pet_cards + '<button class="btn btn-block" style="margin-top:14px">添加宠物</button>' +
    '<div class="tiny" style="margin-top:8px;text-align:center">地图钉与列表均可进入宠物详情。社交页本轮不做必交付，底栏仅保留入口。</div>',
    active="home", back=False))

write("home-empty.html","首页-无宠物", phone("首页",
    fmap("还没有位置记录，请先添加宠物并绑定设备（当前为本地预览数据）") +
    '<div class="empty">还没有宠物，先添加一只。<br>添加后可绑定定位器，查看示意位置与围栏。</div>' +
    '<button class="btn btn-block">添加宠物</button>',
    active="home", back=False))

write("home-loading.html","首页-定位中", phone("首页",
    '<div class="map"><div class="grid"></div><div class="cap">定位中... 当前为本地预览，不模拟真实刷新间隔</div></div>' +
    '<div class="card" style="margin-top:12px"><div class="skel"></div><div class="skel" style="width:70%"></div><div class="skel" style="width:40%"></div></div>' +
    '<div class="card" style="margin-top:8px"><div class="skel"></div><div class="skel" style="width:60%"></div></div>',
    active="home", back=False))

write("home-map-unconfigured.html","首页-地图未配置", phone("首页",
    '<div class="map" style="background:#E3E6EE"><div class="grid"></div><div class="cap">地图服务未配置，仅显示示意坐标 31.230, 121.473 · 非实地地图服务</div></div>' +
    '<div class="banner warn">地图 Key 未接入。页面不会白屏，位置以示意坐标和文案展示。</div>' + pet_cards,
    active="home", back=False))

write("pet-list.html","宠物列表", phone("宠物",
    pet_cards + '<button class="btn btn-ghost btn-block" style="margin-top:14px">添加宠物</button>',
    active="home"))

write("pet-list-empty.html","宠物列表-空", phone("宠物",
    '<div class="empty">还没有宠物，先添加一只。<br>须选择猫或狗，这会影响默认围栏。</div><button class="btn btn-block">添加宠物</button>',
    active="home"))

write("pet-list-loading.html","宠物列表-加载中", phone("宠物",
    '<div class="card"><div class="skel"></div><div class="skel" style="width:50%"></div></div>'
    '<div class="card" style="margin-top:8px"><div class="skel"></div><div class="skel" style="width:60%"></div></div>',
    active="home"))

write("pet-list-fail.html","宠物列表-失败", phone("宠物",
    '<div class="banner err">列表加载失败，请检查本地服务后重试。当前不是实地数据中断。</div>'
    '<button class="btn btn-ghost btn-block">重新加载</button>',
    active="home"))

write("pet-add.html","添加宠物", phone("添加宠物", """
<div class="muted" style="margin-bottom:10px">必须选择猫或狗。猫默认围栏 100 米且离家报警开启；狗默认 300 米、报警默认关闭。</div>
<div class="field"><label>类型（必选）</label>
  <div class="row">
    <button class="btn" style="flex:1">猫</button>
    <button class="btn btn-ghost" style="flex:1">狗</button>
  </div>
</div>
<div class="field"><label>名称（必填）</label><input class="input" placeholder="给它起个名字" value="橘子"></div>
<div class="field"><label>品种</label><input class="input" placeholder="选填，按现有字段" value="英短"></div>
<div class="banner info">保存后将按猫咪规则预置围栏：半径 100 米，离家报警开启且不可关闭。数据为本地示意。</div>
<button class="btn btn-block">保存并继续绑定设备</button>
"""))

write("pet-add-fail.html","添加宠物-保存失败", phone("添加宠物", """
<div class="field"><label>类型（必选）</label>
  <div class="row"><button class="btn" style="flex:1">猫</button><button class="btn btn-ghost" style="flex:1">狗</button></div>
</div>
<div class="field"><label>名称（必填）</label><input class="input" value="橘子"></div>
<div class="field"><label>品种</label><input class="input" value="英短"></div>
<div class="banner err">保存失败，已保留刚填写的内容。请确认本地服务后重试。未写入真实档案。</div>
<button class="btn btn-block">重新保存</button>
"""))

write("pet-detail.html","宠物详情", phone("橘子",
    fmap("示意位置，非实地地图服务 · 来源 Wi-Fi · 电量 72% · 在线") + """
    <div class="card" style="margin-top:12px">
      <div class="between"><div style="font-weight:600">定位器 PT-MOCK-10086</div><span class="tag ok">已绑定</span></div>
      <div class="muted" style="margin-top:6px">示例 SN，非真机配对。固件升级仅保留示意入口。</div>
    </div>
    <div class="card" style="margin-top:8px">
      <div class="list-item between"><span>查看历史轨迹</span><span class="tiny">免费档可看 7 天</span></div>
      <div class="list-item between"><span>报警设置（含围栏）</span><span class="tiny">猫 · 100 米 · 开启且不可关</span></div>
      <div class="list-item between"><span>设备管理</span><span class="tiny">解绑需确认</span></div>
    </div>
    """, active="home"))

write("pet-detail-no-device.html","宠物详情-未绑定", phone("橘子",
    '<div class="map"><div class="grid"></div><div class="cap">还没有位置记录，请先绑定设备并等待上报（当前为本地预览数据）</div></div>'
    '<div class="empty">还没有定位器，请绑定设备。<br>绑定走示例 SN 信息结构，不是真机配对。</div>'
    '<button class="btn btn-block">绑定定位器</button>',
    active="home"))

write("device-bind.html","绑定设备", phone("绑定定位器", """
<div class="muted">绑定方式：输入 SN 或模拟扫码。真实相机权限失败时可改用手输。必须写明非真机配对。</div>
<div class="field" style="margin-top:12px"><label>设备 SN / 激活码</label><input class="input" value="PT-MOCK-10086" placeholder="输入 SN"></div>
<div class="tiny">示例 SN 仅用于走通「绑定成功」信息结构，不是真实激活码体系，也未对接厂商。</div>
<div class="row" style="margin-top:12px">
  <button class="btn btn-ghost" style="flex:1" disabled>模拟扫码（相机未接入）</button>
  <button class="btn" style="flex:1">绑定</button>
</div>
"""))

write("device-bind-loading.html","绑定设备-绑定中", phone("绑定定位器", """
<div class="field"><label>设备 SN / 激活码</label><input class="input" value="PT-MOCK-10086"></div>
<div class="banner info">绑定中，请稍候。当前为本地示意状态机：绑定中。不会连接真实设备。</div>
<button class="btn btn-block" disabled>绑定中...</button>
"""))

write("device-bind-sn-invalid.html","绑定设备-SN无效", phone("绑定定位器", """
<div class="field"><label>设备 SN / 激活码</label><input class="input" value="PT-XXXX-00000"></div>
<div class="banner err">未找到该设备或激活码不正确。即使在 Mock 下也走这条信息结构，不会假装已经连上真硬件。</div>
<button class="btn btn-block">重新绑定</button>
"""))

write("device-bind-already-bound.html","绑定设备-已被绑定", phone("绑定定位器", """
<div class="field"><label>设备 SN / 激活码</label><input class="input" value="PT-MOCK-20001"></div>
<div class="banner err">该设备已绑定其他宠物。一台设备同时只属于一只宠物。</div>
<button class="btn btn-block">更换 SN 后重试</button>
"""))

write("device-manage.html","设备管理", phone("设备管理", """
<div class="card">
  <div class="between"><div style="font-weight:600">PT-MOCK-10086</div><span class="tag ok">已绑定 · 在线</span></div>
  <div class="muted" style="margin-top:6px">绑定宠物：橘子（猫）· 电量 72% · 来源 Wi-Fi（均为 Mock 值）</div>
  <div class="tiny" style="margin-top:6px">示例设备，非真机配对。状态机：未绑定 / 绑定中 / 已绑定 / 解绑中。</div>
</div>
<div class="card" style="margin-top:8px">
  <div class="list-item between"><span>固件升级</span><span class="tiny">当前为示意，无真机不可执行</span></div>
  <div class="list-item between"><span>查看位置</span><span class="tiny">示意坐标</span></div>
</div>
<button class="btn btn-danger btn-block" style="margin-top:16px">解绑设备</button>
""", active="me"))

write("device-unbind-confirm.html","设备管理-解绑确认", phone("设备管理", """
<div class="card">
  <div style="font-weight:600;margin-bottom:8px">确认解绑这台定位器？</div>
  <div class="muted">解绑后，橘子将不再收到示意位置与围栏告警。这是本地预览中的确认，不会对真实硬件下发指令。</div>
  <div class="row" style="margin-top:16px">
    <button class="btn btn-ghost" style="flex:1">取消</button>
    <button class="btn btn-danger" style="flex:1">确认解绑</button>
  </div>
</div>
""", active="me"))

write("device-unbind-fail.html","设备管理-解绑失败", phone("设备管理", """
<div class="card">
  <div class="between"><div style="font-weight:600">PT-MOCK-10086</div><span class="tag ok">已绑定 · 在线</span></div>
  <div class="muted" style="margin-top:6px">绑定宠物：橘子（猫）</div>
</div>
<div class="banner err">解绑未完成，设备仍留在列表中。请稍后重试。失败不会清除列表项，也不是真机已断开。</div>
<button class="btn btn-danger btn-block">再次尝试解绑</button>
""", active="me"))

write("history.html","历史轨迹", phone("历史轨迹",
    fmap("示意轨迹，非实地地图服务 · 免费档可查看 7 天") + """
    <div class="card" style="margin-top:12px">
      <div class="between"><span style="font-weight:600">今天 07:12-09:40</span><span class="tag">示意</span></div>
      <div class="muted" style="margin-top:6px">小区门口到中心绿地（示意折线，不是真实上报）。</div>
    </div>
    <div class="banner warn" style="margin-top:8px">7 天以外的轨迹需升级会员。升级入口可打开，但未接入支付，不能真实开通，也不会扣款。</div>
    <button class="btn btn-ghost btn-block" disabled>查看开通方式（未接入支付）</button>
    """))

write("history-empty.html","历史轨迹-空", phone("历史轨迹",
    '<div class="empty">所选时间没有轨迹。<br>当前为本地预览数据，不是设备尚未上报到生产。</div>'))

write("history-loading.html","历史轨迹-加载中", phone("历史轨迹",
    '<div class="map"><div class="grid"></div><div class="cap">轨迹加载中...</div></div>'
    '<div class="card" style="margin-top:12px"><div class="skel"></div><div class="skel" style="width:70%"></div></div>'))

write("alarm-settings-dog.html","报警设置-狗可关闭", phone("报警设置", """
<div class="muted">报警设置绑定豆豆（狗）。与全局通知设置分开。狗可关闭离家报警，默认半径 300 米。</div>
<div class="card" style="margin-top:12px">
  <div class="between"><div><div style="font-weight:600">离家报警</div><div class="tiny">离开围栏时记录一条告警（示意，非真推送）</div></div><div class="switch"><i></i></div></div>
</div>
<div class="card" style="margin-top:8px">
  <div class="between"><div style="font-weight:600">围栏半径</div><div style="font-weight:600;color:var(--accent)">300 米</div></div>
  <div style="height:4px;background:var(--accent-subtle);border-radius:2px;margin:14px 0;position:relative">
    <div style="width:60%;height:4px;background:var(--accent);border-radius:2px"></div>
    <div style="position:absolute;left:60%;top:-5px;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:var(--accent)"></div>
  </div>
  <div class="tiny">半径不能小于 20 米。圆心可在示意地图上点选，不是实地地图服务。</div>
</div>
<div class="card" style="margin-top:8px">
  <div class="between"><div><div style="font-weight:600">进入围栏提醒</div><div class="tiny">可选项</div></div><div class="switch"><i></i></div></div>
</div>
<button class="btn btn-block" style="margin-top:16px">保存设置</button>
"""))

write("alarm-settings-cat-locked.html","报警设置-猫不可关", phone("报警设置", """
<div class="muted">报警设置绑定橘子（猫）。猫咪离家报警默认开启且不可关闭，只能改圆心和半径（默认 100 米）。</div>
<div class="card" style="margin-top:12px">
  <div class="between"><div><div style="font-weight:600">离家报警</div><div class="tiny">锁定开启</div></div><div class="switch locked"><i></i></div></div>
</div>
<div class="banner warn">猫咪离家报警默认开启，不能关闭。点击开关不会关闭，只会看到本说明。</div>
<div class="card">
  <div class="between"><div style="font-weight:600">围栏半径</div><div style="font-weight:600;color:var(--accent)">100 米</div></div>
  <div style="height:4px;background:var(--accent-subtle);border-radius:2px;margin:14px 0;position:relative">
    <div style="width:32%;height:4px;background:var(--accent);border-radius:2px"></div>
    <div style="position:absolute;left:32%;top:-5px;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:var(--accent)"></div>
  </div>
</div>
<button class="btn btn-block" style="margin-top:16px">保存半径与圆心</button>
"""))

write("alarm-settings-fence-small.html","报警设置-围栏过小", phone("报警设置", """
<div class="card">
  <div class="between"><div style="font-weight:600">围栏半径</div><div style="font-weight:600;color:var(--danger)">12 米</div></div>
  <div style="height:4px;background:var(--danger-subtle);border-radius:2px;margin:14px 0;position:relative">
    <div style="width:8%;height:4px;background:var(--danger);border-radius:2px"></div>
    <div style="position:absolute;left:8%;top:-5px;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:var(--danger)"></div>
  </div>
</div>
<div class="banner err">围栏范围不能小于 20 米。未保存，仍保留原半径。请调大后再保存。</div>
<button class="btn btn-block" disabled>保存设置</button>
"""))

write("alarm-settings-no-device.html","报警设置-未绑定设备", phone("报警设置",
    '<div class="empty">请先绑定定位器再设置围栏。<br>没有设备时不能保存圆心或半径。</div>'
    '<button class="btn btn-block">去绑定定位器</button>'))

write("alarm-settings-saving.html","报警设置-保存中", phone("报警设置", """
<div class="card"><div class="between"><div style="font-weight:600">离家报警</div><div class="switch on"><i></i></div></div></div>
<div class="banner info">设置保存中... 保存失败时会保留原值。</div>
<button class="btn btn-block" disabled>保存中...</button>
"""))

write("alarms.html","报警列表", phone("报警", """
<div class="row" style="margin-bottom:10px">
  <span class="tag">全部</span><span class="tag err">未处理</span><span class="tag off">已处理</span>
</div>
<div class="card">
  <div class="list-item">
    <div class="av" style="background:var(--danger-subtle);color:var(--danger)">离</div>
    <div style="flex:1"><div class="between"><div style="font-weight:600">橘子 离开围栏</div><span class="tag err">未处理</span></div>
    <div class="tiny">今天 14:02 · 示意地址：小区西门附近 · 非实地定位</div></div>
  </div>
  <div class="list-item">
    <div class="av" style="background:var(--warning-subtle);color:var(--warning)">电</div>
    <div style="flex:1"><div class="between"><div style="font-weight:600">豆豆 低电量</div><span class="tag">已处理</span></div>
    <div class="tiny">昨天 21:18 · 电量 16%（Mock）· 优先级低于离线与拆卸</div></div>
  </div>
</div>
<div class="tiny" style="margin-top:10px">不验收真实短信、模板消息或紧急联系人外呼。处理与标记误报后状态会变化（示意）。</div>
""", active="alarms", back=False))

write("alarms-empty.html","报警列表-空", phone("报警",
    '<div class="empty">暂时没有报警记录。<br>围栏触发在本预览里为示意数据，不是真实离家事件。</div>',
    active="alarms", back=False))

write("alarms-loading.html","报警列表-加载中", phone("报警",
    '<div class="card"><div class="skel"></div><div class="skel" style="width:60%"></div></div>'
    '<div class="card" style="margin-top:8px"><div class="skel"></div><div class="skel" style="width:50%"></div></div>',
    active="alarms", back=False))

write("alarms-fail.html","报警列表-失败", phone("报警",
    '<div class="banner err">告警列表拉取失败，请重试。这是接口失败态，不是「暂时没有报警记录」。</div>'
    '<button class="btn btn-ghost btn-block">重新加载</button>',
    active="alarms", back=False))

write("alarm-notify.html","报警通知详情", phone("报警通知", """
<div class="card">
  <div class="between"><div style="font-weight:600">橘子 离开围栏</div><span class="tag err">未处理</span></div>
  <div class="muted" style="margin-top:8px">时间：今天 14:02<br>示意地址：小区西门附近（非实地定位）<br>规则：离家报警 · 半径 100 米</div>
</div>
<div class="banner info">本页只展示 App 内通知。不验收真推送、短信或电话。报警风暴静音算法本轮只保留规则说明。</div>
<div class="row" style="margin-top:12px">
  <button class="btn btn-ghost" style="flex:1">标记误报</button>
  <button class="btn" style="flex:1">标记已处理</button>
</div>
""", active="alarms"))

write("profile.html","我的", phone("我的", """
<div class="card">
  <div class="row">
    <div class="av">预</div>
    <div><div style="font-weight:600">预览用户</div><div class="tiny">138****0000 · 免费版（Mock 字段）</div></div>
  </div>
</div>
<div class="card" style="margin-top:8px">
  <div class="list-item between"><span>设备管理</span><span class="tiny">主路径</span></div>
  <div class="list-item between"><span>会员</span><span class="tiny">入口保留 · 非本轮必做 · 非真实扣款</span></div>
  <div class="list-item between"><span>积分</span><span class="tiny">后续 · 入口不删</span></div>
  <div class="list-item between"><span>邀请</span><span class="tiny">后续</span></div>
  <div class="list-item between"><span>通知</span><span class="tiny">与报警设置分离</span></div>
  <div class="list-item between"><span>设置</span><span class="tiny">隐私与退出</span></div>
</div>
<div class="tiny" style="margin-top:10px">个人中心不做运营化大改。会员 / 积分 / 邀请 / 社交不是本轮必交付。</div>
""", active="me", back=False))

write("profile-fail.html","我的-加载失败", phone("我的",
    '<div class="banner err">资料加载失败，请重试。未登录时会回到登录页。</div>'
    '<button class="btn btn-ghost btn-block">重新加载</button>',
    active="me", back=False))

write("settings.html","设置", phone("设置", """
<div class="card">
  <div class="list-item">
    <div style="flex:1"><div style="font-weight:600">位置可见性</div><div class="tiny">仅好友 / 全部可见 / 不可见。本轮只展示规则文案，不接真实附近曝光或地图分享。</div></div>
  </div>
  <div class="list-item between"><div><div style="font-weight:600">可见范围</div><div class="tiny">500 米 / 1 千米 / 3 千米（展示用）</div></div><span class="tag">1 千米</span></div>
  <div class="list-item between"><div><div style="font-weight:600">匿名只显示类型</div><div class="tiny">不展示昵称</div></div><div class="switch"><i></i></div></div>
</div>
<div class="card" style="margin-top:8px">
  <div class="list-item between"><span>隐私政策与用户协议</span><span class="tiny">文案入口</span></div>
</div>
<button class="btn btn-ghost btn-block" style="margin-top:16px">退出登录（需确认）</button>
""", active="me"))

def admin_side(active):
    items = [
        ("dash","数据概览","off"),
        ("dev","设备","on" if active=="dev" else ""),
        ("alm","报警","on" if active=="alm" else ""),
        ("usr","用户 / 宠物","off"),
        ("soc","社交审核","off"),
        ("pts","积分规则","off"),
        ("pkg","套餐 / 订单 / 收入","off"),
        ("sys","系统设置","off"),
    ]
    links = "".join('<a class="%s" href="#">%s</a>' % (cls, lab) for key,lab,cls in items)
    return ('''<aside class="aside"><div class="brand"><div class="mark" style="width:32px;height:32px;font-size:15px">迹</div>
      <div><div class="brand-name">宠迹管理端</div><div class="brand-sub">本地 Mock · 非验收</div></div></div>
      <nav>%s</nav>
      <div class="foot">预览管理员<br>社交审核、退款、固件推送本轮不做必交付。<br>不得把 Mock 订单写成真实营收。</div>
    </aside>''' % links)

def admin_shell(title, active, inner):
    return ('<div class="admin">' + admin_side(active) +
            '<div class="main"><div class="top"><h1>' + title + '</h1>'
            '<div class="muted">本地 Mock 可预览 · 非真实硬件与第三方 · 待设计评审</div></div>'
            '<div class="content">' + inner + '</div></div></div>')

def admin_login(state):
    err = ""
    btn = "登录"; dis = ""
    if state == "loading":
        btn = "登录中..."; dis = "disabled"
    if state == "fail":
        err = '<div class="banner err">账号或密码错误。本页是本地预览，不是生产登录。</div>'
    body = """
    <div class="login-wrap">
      <div class="login-l">
        <div class="chip" style="display:inline-block;background:rgba(255,255,255,.16);padding:4px 10px;border-radius:999px;font-size:12px">本地 Mock · 非验收</div>
        <h1>宠迹管理端</h1>
        <p>本轮只要求看懂设备与告警信息结构。SN、在线、电量、告警地址均为 Mock。关闭 Mock 且后端未启动时，应提示无法连接服务，而不是写死预览口令。</p>
        <p>不把 Mock 订单「已支付」写成真实营收。社交审核、退款审批、固件批量推送不是本轮必交付。</p>
      </div>
      <div class="login-r"><div class="box">
        <h2>管理员登录</h2>
        <p class="muted" style="margin-bottom:16px">必须能看出这是本地预览。非 Mock 时不写死预览口令。</p>
        <div class="field"><label>账号</label><input class="input" value="admin.preview"></div>
        <div class="field"><label>密码</label><input class="input" type="password" value="........"></div>
        %s
        <button class="btn btn-block" %s>%s</button>
      </div></div>
    </div>
    """ % (err, dis, btn)
    write("admin-login-%s.html" % state, "管理端登录-"+state, body, 1440, 900)

for s in ("default","loading","fail"):
    admin_login(s)

write("admin-devices.html","管理端-设备列表", admin_shell("设备", "dev", """
<div class="muted" style="margin-bottom:12px">列表中的 SN、在线、电量均为 Mock，用词与小程序一致（在线 / 离线 / 低电）。</div>
<table class="table">
  <tr><th>SN</th><th>绑定宠物</th><th>状态</th><th>电量</th><th>最后上报（示意）</th></tr>
  <tr><td>PT-MOCK-10086</td><td>橘子 · 猫</td><td><span class="tag ok">在线</span></td><td>72%</td><td>今天 14:02</td></tr>
  <tr><td>PT-MOCK-20011</td><td>豆豆 · 狗</td><td><span class="tag ok">在线</span></td><td>88%</td><td>今天 14:01</td></tr>
  <tr><td>PT-MOCK-30002</td><td>未绑定</td><td><span class="tag off">离线</span></td><td>—</td><td>昨天 18:20（超过 30 分钟无上报）</td></tr>
</table>
"""), 1440, 900)

write("admin-devices-empty.html","管理端-设备空", admin_shell("设备", "dev",
    '<div class="card empty">暂无数据。这是空列表，不是加载失败。</div>'), 1440, 900)

write("admin-devices-fail.html","管理端-设备失败", admin_shell("设备", "dev",
    '<div class="banner err">设备列表拉取失败，请重试。当前为本地服务失败态，不是硬件掉线统计。</div><button class="btn btn-ghost">重新加载</button>'), 1440, 900)

write("admin-device-detail.html","管理端-设备详情", admin_shell("设备详情 PT-MOCK-10086", "dev", """
<div class="card">
  <div class="between"><div style="font-weight:600;font-size:16px">PT-MOCK-10086</div><span class="tag ok">在线 · 已绑定</span></div>
  <div class="muted" style="margin-top:10px">宠物：橘子（猫） · 电量 72% · 来源 Wi-Fi<br>最后位置（示意）：31.230, 121.473 · 非实地地图服务<br>围栏：100 米 · 离家报警开启（猫规则，不可关闭）</div>
  <div class="tiny" style="margin-top:8px">固件升级在无真机时仅示意，不可执行真实 OTA。</div>
</div>
"""), 1440, 900)

write("admin-alarms.html","管理端-报警列表", admin_shell("报警", "alm", """
<div class="muted" style="margin-bottom:12px">状态用词与小程序一致：离开围栏、进入围栏、低电量、设备离线、设备拆卸。地址为示意。</div>
<table class="table">
  <tr><th>时间</th><th>宠物 / 设备</th><th>类型</th><th>状态</th><th>示意地址</th></tr>
  <tr><td>今天 14:02</td><td>橘子 / PT-MOCK-10086</td><td>离开围栏</td><td><span class="tag err">未处理</span></td><td>小区西门附近</td></tr>
  <tr><td>昨天 21:18</td><td>豆豆 / PT-MOCK-20011</td><td>低电量</td><td><span class="tag">已处理</span></td><td>—</td></tr>
</table>
"""), 1440, 900)

write("admin-alarms-empty.html","管理端-报警空", admin_shell("报警", "alm",
    '<div class="card empty">暂无数据。</div>'), 1440, 900)

write("admin-alarms-fail.html","管理端-报警失败", admin_shell("报警", "alm",
    '<div class="banner err">报警列表拉取失败，请重试。本态不可用空列表代替。</div><button class="btn btn-ghost">重新加载</button>'), 1440, 900)

print("ALL", len(list(OUT.glob('*.html'))))
for p in sorted(OUT.glob('*.html')):
    print(p.name)
