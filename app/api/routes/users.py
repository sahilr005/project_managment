from __future__ import annotations
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.api.deps import db
from app.db.models.user import User
from app.schemas.users import UserCreate,UserOut,UserUpdate

router = APIRouter(prefix="/v1/users",tags=["users"])

@router.post("",response_model=UserOut)
async def create_user(payload:UserCreate, session: AsyncSession=Depends(db)):
    exists = (await session.execute(select(User).where(User.email== payload.email))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409,detail="Email Already Exist")
    u = User(email=payload.email,full_name= payload.full_name)
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u

@router.get("",response_model=list[UserOut])
async def list_users(
    session: AsyncSession= Depends(db),
    limit: int = Query(50,ge=1,le=200),
    offset: int = Query(0,ge=0)
):
    q = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.get("/{user_id}",response_model=UserOut)
async def get_user(user_id:UUID,session: AsyncSession=Depends(db)):
    rows = await session.get(User,user_id)
    if not rows:
        raise HTTPException(status_code=404,detail="User not found")
    return row

@router.patch("/{user_id}",response_model=UserOut)
async def update_user(user_id:UUID,payload:UserUpdate ,session: AsyncSession= Depends(db)):
    rows = await session.get(User,user_id)
    if not rows:
        raise HTTPException(status_code=404,detail="User Not Found")
    if payload.full_name is not None:
        rows.full_name = payload.full_name
    if payload.is_active is not None:
        rows.is_active = payload.is_active
    await session.commit()
    await session.refresh(rows)
    return rows

@router.delete("/{user_id}",status_code=204)
async def delete_user(user_id:UUID, session: AsyncSession= Depends(db)):
    rows = await session.get(User,user_id)
    if not rows:
        raise HTTPException( status_code=404, detail="User not found")
    await session.delete(rows)
    await session.commit()
    return None
