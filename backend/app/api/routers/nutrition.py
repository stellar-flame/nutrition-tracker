from typing import Annotated
from sqlmodel import Session
from app.ports.job_queue import JobQueue
from app.repositories import meal_repo, pending_meal_repo
from app.models.nutrition_schemas import (
    MealRead,
    MealCreateMinimal,
    MealApprovePayload,
    MealItemBase,
    MealStatus,
    NutritionSummary,
    PendingMealRead,
    PendingMealStatus,
)
from app.models.db_models import Meal, MealItem
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.database import get_session
from app.api.dependencies import get_current_user, get_queue, get_dynamo
import logging

router = APIRouter(prefix="/nutrition", tags=["nutrition"])
logger = logging.getLogger(__name__)


@router.get("/summary", response_model=NutritionSummary)
def get_nutrition_summary(
    date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")],
    db: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    meals = meal_repo.get_meals_by_date(db, date, user)
    mealreads = [MealRead.model_validate(meal) for meal in meals]
    meal_items = [item for meal in mealreads for item in meal.items]
    return NutritionSummary(
        date=date,
        caloriesKcal=sum(meal.caloriesKcal for meal in meal_items),
        proteinG=sum(meal.proteinG for meal in meal_items),
        carbsG=sum(meal.carbsG for meal in meal_items),
        fatG=sum(meal.fatG for meal in meal_items),
        fiberG=sum(meal.fiberG for meal in meal_items),
        sugarG=sum(meal.sugarG for meal in meal_items),
        sodiumMg=sum(meal.sodiumMg for meal in meal_items),
    )


@router.get("/meals", response_model=list[MealRead])
def get_meals(
    date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")],
    db: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    meals = meal_repo.get_meals_by_date(db, date, user)
    return [MealRead.model_validate(meal) for meal in meals]


@router.get("/pending-meals", response_model=list[PendingMealRead])
def get_pending_meals(
    date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")],
    dynamo=Depends(get_dynamo),
    user=Depends(get_current_user),
):
    items = pending_meal_repo.get_pending_meals_by_date(dynamo, user.id, date)
    return [PendingMealRead(**item) for item in items]


@router.post("/meals", response_model=PendingMealRead, status_code=201)
def create_meal_endpoint(
    payload: MealCreateMinimal,
    job: JobQueue = Depends(get_queue),
    dynamo=Depends(get_dynamo),
    user=Depends(get_current_user),
):
    pending = pending_meal_repo.create_pending_meal(
        dynamo,
        user_id=user.id,
        description=payload.description,
        date=str(payload.date),
        time=payload.time,
    )
    prompt = {"meal_description": payload.description, "meal_id": pending["meal_id"]}
    try:
        job.enqueue(prompt=prompt)
    except Exception as e:
        logger.error(f"Failed to enqueue job for meal_id {pending['meal_id']}: {e}")
        pending_meal_repo.delete_pending_meal(dynamo, pending["meal_id"])
        raise HTTPException(status_code=503, detail="Queue operation failed")
    return PendingMealRead(**pending)


@router.delete("/pending-meals/{meal_id}", status_code=204)
def dismiss_pending_meal(
    meal_id: str,
    dynamo=Depends(get_dynamo),
    user=Depends(get_current_user),
):
    pending = pending_meal_repo.get_pending_meal(dynamo, meal_id)
    if not pending:
        raise HTTPException(status_code=404, detail="Pending meal not found")
    if int(pending["user_id"]) != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    pending_meal_repo.delete_pending_meal(dynamo, meal_id)


@router.delete("/meals/{meal_id}", status_code=204)
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    meal = db.get(Meal, meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    if meal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    meal_repo.delete_meal(db, meal_id)


@router.post("/meals/{meal_id}/approve", response_model=MealRead, status_code=201)
def approve_meal(
    meal_id: str,
    payload: MealApprovePayload,
    db: Session = Depends(get_session),
    dynamo=Depends(get_dynamo),
    user=Depends(get_current_user),
):
    pending = pending_meal_repo.get_pending_meal(dynamo, meal_id)
    if not pending:
        raise HTTPException(status_code=404, detail="Pending meal not found")
    if int(pending["user_id"]) != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if pending["status"] != PendingMealStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=409, detail="Meal is not ready for approval")

    items_to_commit: list[MealItemBase] = (
        payload.items
        if payload.items is not None
        else [MealItemBase(**dict(i)) for i in pending["items"]]
    )

    meal = Meal(
        date=pending["date"],
        time=pending["time"],
        created_at=pending["created_at"],
        description=pending["description"],
        items=[],
        status=MealStatus.COMPLETE,
        user_id=user.id,
    )
    saved = meal_repo.create_meal(db, meal)
    meal_repo.attach_meal_items(db, saved.id, items_to_commit)
    pending_meal_repo.delete_pending_meal(dynamo, meal_id)

    db.refresh(saved)
    return MealRead.model_validate(saved)
