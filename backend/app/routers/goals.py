from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalRead)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    return crud.create_goal(db, payload)


@router.get("", response_model=list[GoalRead])
def list_goals(db: Session = Depends(get_db)):
    return crud.list_goals(db)


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: str, db: Session = Depends(get_db)):
    uid = UUID(goal_id)
    g = crud.get_goal(db, uid)
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found")
    return g


@router.put("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: str, payload: GoalUpdate, db: Session = Depends(get_db)):
    uid = UUID(goal_id)
    g = crud.update_goal(db, uid, payload)
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found")
    return g


@router.delete("/{goal_id}")
def delete_goal(goal_id: str, db: Session = Depends(get_db)):
    uid = UUID(goal_id)
    ok = crud.delete_goal(db, uid)
    if not ok:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"deleted": True}
