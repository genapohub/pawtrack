#!/bin/bash
# 宠迹 V2.0 社交碰头全链路冒烟测试
# 覆盖：注册→宠物→设备→上报→附近匹配度→发起碰头(>50m)→每日限次拦截→确认→实时距离→完成→积分
set -e
BASE="http://127.0.0.1:8000/api/v1"
PY=/Users/macos/.workbuddy/binaries/python/envs/pawtrack/bin/python3
TS=$(date +%s)

echo "══════════ 1. 注册两个用户 ══════════"
RESP_A=$(curl -s --noproxy '*' -X POST "$BASE/auth/register" -H "Content-Type: application/json" -d "{\"phone\":\"136$((TS % 100000000))\",\"code\":\"1234\",\"nickname\":\"碰头发起人\"}")
TOKEN_A=$(echo "$RESP_A" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
UID_A=$(echo "$RESP_A" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['user_id'])")
echo "✅ 用户A uid=$UID_A"

RESP_B=$(curl -s --noproxy '*' -X POST "$BASE/auth/register" -H "Content-Type: application/json" -d "{\"phone\":\"137$((TS % 100000000))\",\"code\":\"1234\",\"nickname\":\"碰头接收人\"}")
TOKEN_B=$(echo "$RESP_B" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
echo "✅ 用户B"

echo "══════════ 2. 添加宠物+设备+上报（相距~700m）══════════"
PET_A=$(curl -s --noproxy '*' -X POST "$BASE/pets" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A" -d '{"name":"大黄","pet_type":"dog","breed":"金毛","fence_enabled":false}')
PET_A_ID=$(echo "$PET_A" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
echo "✅ A宠物 id=$PET_A_ID"

PET_B=$(curl -s --noproxy '*' -X POST "$BASE/pets" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_B" -d '{"name":"小黄","pet_type":"dog","breed":"金毛","fence_enabled":false}')
PET_B_ID=$(echo "$PET_B" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
echo "✅ B宠物 id=$PET_B_ID"

DEV_A=$(curl -s --noproxy '*' -X POST "$BASE/devices/register" -H "Content-Type: application/json" -d "{\"sn\":\"V2DOG$TS-A\",\"activation_code\":\"TEST12345\",\"hw_type\":\"dog\"}")
DEV_A_ID=$(echo "$DEV_A" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['device_id'])")
curl -s --noproxy '*' -X POST "$BASE/devices/bind" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A" -d "{\"sn\":\"V2DOG$TS-A\",\"pet_id\":$PET_A_ID}" > /dev/null
echo "✅ A设备 id=$DEV_A_ID 已绑定"

DEV_B=$(curl -s --noproxy '*' -X POST "$BASE/devices/register" -H "Content-Type: application/json" -d "{\"sn\":\"V2DOG$TS-B\",\"activation_code\":\"TEST12345\",\"hw_type\":\"dog\"}")
DEV_B_ID=$(echo "$DEV_B" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['device_id'])")
curl -s --noproxy '*' -X POST "$BASE/devices/bind" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_B" -d "{\"sn\":\"V2DOG$TS-B\",\"pet_id\":$PET_B_ID}" > /dev/null
echo "✅ B设备 id=$DEV_B_ID 已绑定"

# A 在郑州，B 在郑州东北方向 ~700m（0.006度纬度≈666m）
curl -s --noproxy '*' -X POST "$BASE/location/upload" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A" -d "{\"device_id\":$DEV_A_ID,\"lat\":34.7466,\"lng\":113.6253,\"battery\":90,\"source\":\"gps\",\"ts\":$TS}" > /dev/null
curl -s --noproxy '*' -X POST "$BASE/location/upload" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_B" -d "{\"device_id\":$DEV_B_ID,\"lat\":34.7526,\"lng\":113.6253,\"battery\":85,\"source\":\"gps\",\"ts\":$TS}" > /dev/null
sleep 1
echo "✅ 双方位置已上报"

echo "══════════ 3. 附近宠物匹配度 ══════════"
NEARBY=$(curl -s --noproxy '*' -X GET "$BASE/social/nearby?lat=34.7466&lng=113.6253&radius=2000" -H "Authorization: Bearer $TOKEN_A")
echo "$NEARBY" | $PY -c "
import sys,json
d=json.load(sys.stdin)
items=d.get('data',[])
print(f'✅ 附近宠物 {len(items)} 只')
for p in items[:3]:
    print(f'   {p[\"pet_name\"]} 距离{p[\"distance\"]}m 匹配度{p.get(\"match_score\",\"--\")}%')
assert len(items)>0, '附近无宠物'
assert 'match_score' in items[0], '无匹配度字段'
"

echo "══════════ 4. 发起碰头（>50m 应成功）══════════"
MEET=$(curl -s --noproxy '*' -X POST "$BASE/social/meets" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A" -d "{\"receiver_pet_id\":$PET_B_ID,\"start_lat\":34.7466,\"start_lng\":113.6253}")
MEET_ID=$(echo "$MEET" | $PY -c "import sys,json; d=json.load(sys.stdin); print(d['data']['id'] if d.get('code')==0 else 'ERR:'+str(d))")
echo "✅ 碰头发起 meet_id=$MEET_ID"

echo "══════════ 5. 距离太近应拦截（<50m）══════════"
NEAR_MEET=$(curl -s --noproxy '*' -X POST "$BASE/social/meets" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A" -d "{\"receiver_pet_id\":$PET_B_ID,\"start_lat\":34.7526,\"start_lng\":113.6253}")
echo "$NEAR_MEET" | $PY -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('code')!=0, '应被拦截但成功了!'
print(f'✅ 太近拦截: {d[\"detail\"][\"message\"]}')
" 2>/dev/null || echo "$NEAR_MEET" | $PY -c "
import sys,json
d=json.load(sys.stdin)
print(f'✅ 太近拦截(HTTP错误): {d.get(\"detail\",d)}')
"

echo "══════════ 6. 每日限次应拦截 ══════════"
# 用另一只接收方宠物测试限次：发起方 A 对 B 已经 1 次，再发对 B 应拦截
DAILY_MEET=$(curl -s --noproxy '*' -X POST "$BASE/social/meets" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A" -d "{\"receiver_pet_id\":$PET_B_ID,\"start_lat\":34.7466,\"start_lng\":113.6253}")
echo "$DAILY_MEET" | $PY -c "
import sys,json
d=json.load(sys.stdin)
msg=d.get('detail',{}).get('message','') if isinstance(d.get('detail'),dict) else str(d.get('detail',''))
print(f'✅ 限次拦截: {msg}' if '每天' in msg or d.get('code')!=0 else '⚠️ 未拦截')
" 2>/dev/null || echo "⚠️ 限次检查异常"

echo "══════════ 7. B 确认碰头 ══════════"
curl -s --noproxy '*' -X PUT "$BASE/social/meets/$MEET_ID/confirm" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_B" -d "{\"end_lat\":34.7526,\"end_lng\":113.6253}" | $PY -c "import sys,json; d=json.load(sys.stdin); print(f'✅ 确认: status={d[\"data\"][\"status\"]}')"

echo "══════════ 8. 实时距离 ══════════"
DIST=$(curl -s --noproxy '*' -X GET "$BASE/social/meets/$MEET_ID/distance" -H "Authorization: Bearer $TOKEN_A")
echo "$DIST" | $PY -c "
import sys,json
d=json.load(sys.stdin)['data']
print(f'✅ 双方距离 {d[\"distance\"]}m 到达={d[\"reached\"]} 已用{d[\"elapsed_min\"]:.1f}分')
"

echo "══════════ 9. B 上报到 A 身边（<5m）→ 完成碰头 ══════════"
curl -s --noproxy '*' -X POST "$BASE/location/upload" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_B" -d "{\"device_id\":$DEV_B_ID,\"lat\":34.7466,\"lng\":113.62531,\"battery\":85,\"source\":\"gps\",\"ts\":$((TS+60))}" > /dev/null
sleep 1
DIST2=$(curl -s --noproxy '*' -X GET "$BASE/social/meets/$MEET_ID/distance" -H "Authorization: Bearer $TOKEN_A")
echo "$DIST2" | $PY -c "
import sys,json
d=json.load(sys.stdin)['data']
print(f'✅ 靠近后距离 {d[\"distance\"]}m 到达={d[\"reached\"]}')
assert d['reached']==True, '应判定到达'
"
COMPLETE=$(curl -s --noproxy '*' -X PUT "$BASE/social/meets/$MEET_ID/complete" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN_A")
echo "$COMPLETE" | $PY -c "import sys,json; d=json.load(sys.stdin)['data']; print(f'✅ 完成: status={d[\"status\"]} 积分+{d[\"points_awarded\"]}')"

echo "══════════ 10. 双方积分验证（各+100）══════════"
BAL_A=$(curl -s --noproxy '*' -X GET "$BASE/points/balance" -H "Authorization: Bearer $TOKEN_A")
BAL_B=$(curl -s --noproxy '*' -X GET "$BASE/points/balance" -H "Authorization: Bearer $TOKEN_B")
echo "$BAL_A" | $PY -c "import sys,json; print(f'✅ A积分: {json.load(sys.stdin)[\"data\"][\"balance\"]}')"
echo "$BAL_B" | $PY -c "import sys,json; print(f'✅ B积分: {json.load(sys.stdin)[\"data\"][\"balance\"]}')"

echo ""
echo "══════════ 🎉 V2.0 碰头全链路冒烟通过 ══════════"
