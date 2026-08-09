#!/bin/bash
# 邀请链路冒烟测试
set -e
PY=/Users/macos/.workbuddy/binaries/python/envs/pawtrack/bin/python3
B=http://127.0.0.1:8000/api/v1

RESP_A=$(curl -s --noproxy '*' -X POST $B/auth/register -H "Content-Type: application/json" -d '{"phone":"13711110001","code":"1234","nickname":"邀请人A"}')
CODE_A=$(echo "$RESP_A" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['invite_code'])")
TOKEN_A=$(echo "$RESP_A" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
echo "1. A注册成功 邀请码=$CODE_A"

RESP_B=$(curl -s --noproxy '*' -X POST $B/auth/register -H "Content-Type: application/json" -d "{\"phone\":\"13711110002\",\"code\":\"1234\",\"nickname\":\"被邀请人B\",\"invite_code\":\"$CODE_A\"}")
TOKEN_B=$(echo "$RESP_B" | $PY -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
echo "2. B用邀请码注册成功"

echo "3. A积分余额: $(curl -s --noproxy '*' -X GET $B/points/balance -H "Authorization: Bearer $TOKEN_A")"
echo "4. A邀请记录: $(curl -s --noproxy '*' -X GET $B/invites -H "Authorization: Bearer $TOKEN_A" | head -c 220)"
echo "5. B积分余额: $(curl -s --noproxy '*' -X GET $B/points/balance -H "Authorization: Bearer $TOKEN_B")"

# 兑换测试（用B的50积分，兑换需300 → 应报不足；先签到再兑换）
echo "6. B签到: $(curl -s --noproxy '*' -X POST $B/points/signin -H "Authorization: Bearer $TOKEN_B")"
echo "7. B兑换300分商品(积分不足预期): $(curl -s --noproxy '*' -X POST "$B/points/redeem?item_id=4" -H "Authorization: Bearer $TOKEN_B" | head -c 150)"
