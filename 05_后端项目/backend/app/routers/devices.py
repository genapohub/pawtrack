"""
宠迹 PawTrack — 设备管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.database import get_db
from app.models import Device, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/devices", tags=["设备"])

# ── 请求/响应模型 ──────────────────────────────────────────

class DeviceRegisterRequest(BaseModel):
    sn: str = Field(..., min_length=8, max_length=32, description="设备序列号")
    activation_code: str = Field(..., min_length=8, max_length=32)
    hw_type: str = Field(..., pattern="^(cat|dog)$")
    fw_version: Optional[str] = "1.0.0"

class DeviceBindRequest(BaseModel):
    sn: str
    pet_id: int

class DeviceResponse(BaseModel):
    id: int
    sn: str
    hardware_type: str
    firmware_version: str
    battery_level: int
    status: str
    last_online_at: Optional[str]
    created_at: str

# ── 接口实现 ──────────────────────────────────────────────

@router.post("/register", response_model=dict)
async def register_device(body: DeviceRegisterRequest, db: AsyncSession = Depends(get_db)):
    """设备注册（获取 JWT Token，无需用户登录）"""
    # TODO: 验证 activation_code（MVP 阶段跳过）

    result = await db.execute(select(Device).where(Device.sn == body.sn))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(400, detail={"code": 20004, "message": "设备 SN 已被注册"})

    device = Device(
        sn=body.sn,
        hardware_type=body.hw_type,
        firmware_version=body.fw_version or "1.0.0",
        status="offline"
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)

    # 返回设备专用 JWT（用于 MQTT 连接）
    from app.auth import create_access_token, create_refresh_token
    access = create_access_token(device.id, "", "device", [])
    refresh, _ = create_refresh_token(device.id)

    return {"code": 0, "data": {
        "device_id": device.id,
        "sn": device.sn,
        "access_token": access,
        "refresh_token": refresh,
        "mqtt_url": "ssl://mqtt.pawtrack.app:8883",
        "token_type": "Bearer",
        "expires_in": 7200
    }}

@router.post("/bind", response_model=dict)
async def bind_device(body: DeviceBindRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """绑定设备到宠物"""
    result = await db.execute(select(Device).where(Device.sn == body.sn))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    # 验证宠物属于当前用户
    from app.models import Pet
    pet_result = await db.execute(select(Pet).where(Pet.id == body.pet_id, Pet.user_id == int(user["sub"])))
    pet = pet_result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})

    device.pet_id = body.pet_id
    device.user_id = int(user["sub"])
    await db.commit()
    await db.refresh(device)

    return {"code": 0, "message": "success", "data": {
        "device_id": device.id,
        "sn": device.sn,
        "pet_id": device.pet_id,
        "status": device.status
    }}

@router.get("/{device_id}", response_model=dict)
async def get_device(device_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取设备详情"""
    result = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == int(user["sub"])))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})
    return {"code": 0, "data": {
        "id": device.id,
        "sn": device.sn,
        "hardware_type": device.hardware_type,
        "firmware_version": device.firmware_version,
        "battery_level": device.battery_level,
        "status": device.status,
        "last_online_at": device.last_online_at.isoformat() if device.last_online_at else None,
        "created_at": device.created_at.isoformat() if device.created_at else ""
    }}

@router.get("", response_model=dict)
async def list_devices(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取我的设备列表"""
    result = await db.execute(select(Device).where(Device.user_id == int(user["sub"])))
    devices = result.scalars().all()
    return {"code": 0, "data": [{
        "id": d.id, "sn": d.sn, "hardware_type": d.hardware_type,
        "status": d.status, "battery_level": d.battery_level
    } for d in devices]}


# ── 设备交互接口（硬件相关，MVP 阶段先实现业务侧占位）──────────────

class DeviceUnbindRequest(BaseModel):
    sn: str


@router.post("/unbind", response_model=dict)
async def unbind_device(body: DeviceUnbindRequest, user: dict = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """解绑设备"""
    result = await db.execute(
        select(Device).where(Device.sn == body.sn, Device.user_id == int(user["sub"]))
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在或未绑定"})
    device.pet_id = None
    device.user_id = None
    await db.commit()
    return {"code": 0, "message": "设备已解绑"}


class DeviceConfigRequest(BaseModel):
    """下发配置到设备"""
    report_interval: int = Field(30, ge=5, le=3600, description="上报间隔(秒)")
    fence_enabled: Optional[bool] = None
    low_battery_threshold: Optional[int] = Field(None, ge=5, le=50)


@router.put("/{device_id}/config", response_model=dict)
async def set_device_config(device_id: int, body: DeviceConfigRequest,
                            user: dict = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
    """下发配置到设备（通过 MQTT 下发，MVP 阶段仅记录）"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == int(user["sub"]))
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    # MVP：配置写入 Redis，由 MQTT 网关下发；正式环境发布 MQTT 指令
    from app.main import redis_client
    config_key = f"device:config:{device_id}"
    config = body.model_dump()
    if redis_client:
        import json
        await redis_client.set(config_key, json.dumps(config, ensure_ascii=False))

    return {"code": 0, "message": "配置已下发（MVP 占位）", "data": config}


@router.post("/{device_id}/find", response_model=dict)
async def find_device(device_id: int, user: dict = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """寻找设备（触发设备响铃，通过 MQTT 下发）"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == int(user["sub"]))
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    # MVP：发布 MQTT find 指令（正式环境通过 paho-mqtt 发布）
    from app.main import redis_client
    if redis_client:
        await redis_client.publish(f"cmd:device:{device_id}", '{"cmd":"find","duration":10}')

    return {"code": 0, "message": "寻找指令已下发（设备将响铃 10 秒）"}


@router.get("/{device_id}/status", response_model=dict)
async def device_status(device_id: int, user: dict = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """获取设备实时状态（从 Redis 读取最近上报）"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == int(user["sub"]))
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    from app.main import redis_client
    status_data = {"device_id": device.id, "status": device.status,
                   "battery_level": device.battery_level,
                   "firmware_version": device.firmware_version}
    if redis_client:
        # 读取最近定位
        geo = await redis_client.geopos("location:geo:nearby", str(device.id))
        if geo and geo[0]:
            status_data["lat"] = geo[0][1]
            status_data["lng"] = geo[0][0]
        last_ts = await redis_client.get(f"device:lastts:{device.id}")
        if last_ts:
            status_data["last_report_ts"] = int(last_ts)

    return {"code": 0, "data": status_data}


class OTARequest(BaseModel):
    target_version: str = Field(..., description="目标固件版本")


@router.post("/{device_id}/ota", response_model=dict)
async def trigger_ota(device_id: int, body: OTARequest,
                      user: dict = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """触发固件升级（后台下发，MVP 阶段记录任务）"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == int(user["sub"]))
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    from app.main import redis_client
    task_id = f"ota_{device_id}_{int(datetime.now(timezone.utc).timestamp())}"
    if redis_client:
        import json
        await redis_client.set(f"ota:task:{task_id}", json.dumps({
            "device_id": device_id, "from_version": device.firmware_version,
            "target_version": body.target_version, "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }, ensure_ascii=False))
        # 通知设备开始 OTA
        await redis_client.publish(f"cmd:device:{device_id}",
                                    json.dumps({"cmd": "ota", "version": body.target_version}))

    return {"code": 0, "message": "OTA 升级任务已创建", "data": {"task_id": task_id}}


@router.get("/{device_id}/ota/progress", response_model=dict)
async def ota_progress(device_id: int, user: dict = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    """查询 OTA 升级进度"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == int(user["sub"]))
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    from app.main import redis_client
    # 查找该设备最近的 OTA 任务
    progress = {"device_id": device_id, "current_version": device.firmware_version,
                "status": "idle", "progress": 0}
    if redis_client:
        import json
        # 扫描 ota:task:* （MVP：取最新一个）
        keys = await redis_client.keys(f"ota:task:ota_{device_id}_*")
        if keys:
            raw = await redis_client.get(keys[-1])
            if raw:
                task = json.loads(raw)
                progress.update({
                    "task_id": keys[-1].split(":")[-1],
                    "target_version": task.get("target_version"),
                    "status": task.get("status", "pending"),
                    "progress": task.get("progress", 0),
                })

    return {"code": 0, "data": progress}
