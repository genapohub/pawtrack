"""
宠迹 PawTrack — 宠物管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.database import get_db
from app.models import Pet, PetType, PetGender, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/pets", tags=["宠物"])

# ── 请求/响应模型 ──────────────────────────────────────────

class PetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    pet_type: PetType
    breed: Optional[str] = Field(None, max_length=50)
    gender: PetGender = PetGender.unknown
    birthday: Optional[str] = None  # "2024-03-15"
    weight: Optional[float] = Field(None, ge=0, le=100)
    avatar: Optional[str] = None
    fence_enabled: bool = True
    fence_radius: int = Field(100, ge=20, le=5000)

class PetUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    breed: Optional[str] = None
    gender: Optional[PetGender] = None
    birthday: Optional[str] = None
    weight: Optional[float] = Field(None, ge=0, le=100)
    avatar: Optional[str] = None
    fence_enabled: Optional[bool] = None
    fence_radius: Optional[int] = Field(None, ge=20, le=5000)

class PetFenceRequest(BaseModel):
    fence_enabled: bool
    fence_center_lat: Optional[float] = None
    fence_center_lng: Optional[float] = None
    fence_radius: Optional[int] = Field(None, ge=20, le=5000)

class PetResponse(BaseModel):
    id: int
    name: str
    type: str
    breed: Optional[str]
    gender: str
    birthday: Optional[str]
    weight: Optional[float]
    avatar: Optional[str]
    fence_enabled: bool
    fence_radius: int
    status: str
    created_at: str

# ── 工具函数 ──────────────────────────────────────────────

def _pet_to_dict(pet: Pet) -> dict:
    return {
        "id": pet.id,
        "name": pet.name,
        "type": pet.type.value,
        "breed": pet.breed,
        "gender": pet.gender.value,
        "birthday": pet.birthday.isoformat() if pet.birthday else None,
        "weight": float(pet.weight) if pet.weight else None,
        "avatar": pet.avatar,
        "fence_enabled": pet.fence_enabled,
        "fence_radius": pet.fence_radius,
        "status": pet.status,
        "created_at": pet.created_at.isoformat() if pet.created_at else ""
    }

# ── 接口实现 ──────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_pets(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取宠物列表"""
    result = await db.execute(
        select(Pet).where(Pet.user_id == user["sub"], Pet.status == "active")
    )
    pets = result.scalars().all()
    return {"code": 0, "data": [_pet_to_dict(p) for p in pets]}

@router.post("", response_model=dict)
async def create_pet(body: PetCreateRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """添加宠物"""
    # 免费用户最多 3 只宠物
    count = await db.execute(
        select(func.count()).where(Pet.user_id == user["sub"], Pet.status == "active")
    )
    if count.scalar() >= 3 and user.get("member_level") == "free":
        raise HTTPException(400, detail={"code": 20006, "message": "免费版最多添加3只宠物，请升级会员"})

    from decimal import Decimal
    fence_center_lat = None
    fence_center_lng = None
    if body.fence_center_lat and body.fence_center_lng:
        fence_center_lat = Decimal(str(body.fence_center_lat))
        fence_center_lng = Decimal(str(body.fence_center_lng))
    elif body.fence_enabled:
        # 默认围栏：猫咪100m，狗狗300m
        default_radius = 100 if body.pet_type == PetType.cat else 300
        body.fence_radius = default_radius

    pet = Pet(
        user_id=int(user["sub"]),
        name=body.name,
        type=body.pet_type,
        breed=body.breed,
        gender=body.gender,
        birthday=datetime.fromisoformat(body.birthday) if body.birthday else None,
        weight=body.weight,
        avatar=body.avatar,
        fence_enabled=body.fence_enabled,
        fence_center_lat=fence_center_lat,
        fence_center_lng=fence_center_lng,
        fence_radius=body.fence_radius
    )
    db.add(pet)
    await db.commit()
    await db.refresh(pet)
    return {"code": 0, "data": _pet_to_dict(pet)}

@router.get("/{pet_id}", response_model=dict)
async def get_pet(pet_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取宠物详情"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})
    return {"code": 0, "data": _pet_to_dict(pet)}

@router.put("/{pet_id}", response_model=dict)
async def update_pet(pet_id: int, body: PetUpdateRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新宠物信息"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})

    if body.name is not None: pet.name = body.name
    if body.breed is not None: pet.breed = body.breed
    if body.gender is not None: pet.gender = body.gender
    if body.birthday is not None: pet.birthday = datetime.fromisoformat(body.birthday)
    if body.weight is not None: pet.weight = body.weight
    if body.avatar is not None: pet.avatar = body.avatar
    if body.fence_enabled is not None: pet.fence_enabled = body.fence_enabled
    if body.fence_radius is not None: pet.fence_radius = body.fence_radius

    await db.commit()
    await db.refresh(pet)
    return {"code": 0, "data": _pet_to_dict(pet)}

@router.get("/{pet_id}/fence", response_model=dict)
async def get_fence(pet_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取围栏设置"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})

    # 围栏中心点
    lat = float(pet.fence_center_lat) if pet.fence_center_lat else None
    lng = float(pet.fence_center_lng) if pet.fence_center_lng else None

    return {
        "code": 0,
        "data": {
            "pet_id": pet.id,
            "fence_enabled": pet.fence_enabled,
            "fence_radius": pet.fence_radius,
            "fence_center_lat": lat,
            "fence_center_lng": lng,
        }
    }

@router.put("/{pet_id}/fence", response_model=dict)
async def update_fence(pet_id: int, body: PetFenceRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """设置围栏"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})

    pet.fence_enabled = body.fence_enabled
    if body.fence_radius is not None:
        pet.fence_radius = body.fence_radius
    if body.fence_center_lat and body.fence_center_lng:
        from decimal import Decimal
        pet.fence_center_lat = Decimal(str(body.fence_center_lat))
        pet.fence_center_lng = Decimal(str(body.fence_center_lng))

    await db.commit()
    return {"code": 0, "message": "success", "data": _pet_to_dict(pet)}

@router.delete("/{pet_id}", response_model=dict)
async def delete_pet(pet_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """删除宠物（软删除）"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})
    pet.status = "deleted"
    await db.commit()
    return {"code": 0, "message": "success"}
