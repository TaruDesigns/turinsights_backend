from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/processes", response_model=None, status_code=201)
def getprocesses(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get processes from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of Jobs (Pydantic models)
    """
    if filter:
        try:
            return crud.tracked_process.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.tracked_process.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


@router.get("/queues", response_model=None, status_code=201)
def getqueues(
    filter: Optional[str] = Query(None),
    select: Optional[str] = Query(None),
    top: Optional[int] = Query(100),
    skip: Optional[int] = Query(0),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get processes from DB

    Args:
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).
        Standard OData Queries

    Returns:
        results: List of Jobs (Pydantic models)
    """
    if filter:
        try:
            return crud.tracked_queue.get_odata(db=db, filter=filter)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid OData Query")
    else:
        try:
            return crud.tracked_queue.get_multi(db=db, skip=skip, limit=top)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Error retrieving data")


# Add Post Endpoint. This will be used to add a new process to the database
# Endpoint will add a new process to the database
@router.post("/processes", response_model=schemas.TrackedProcess, status_code=201)
def addprocess(
    process: schemas.TrackedProcess, db: Session = Depends(deps.get_db)
) -> Any:
    """Add a new process to the database

    Args:
        process (schemas.ProcessCreate): Process to add to the database
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).

    Returns:
        results: List of Jobs (Pydantic models)
    """
    try:
        return crud.tracked_process.create(db=db, obj_in=process)
    except IntegrityError as e:
        raise HTTPException(status_code=503, detail="Error creating new record")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Error creating new record")


# Add Patch endpoint. It will be used to update a process in the database
# Endpoint will update a process in the database
@router.put(
    "/processes/{process_id}", response_model=schemas.TrackedProcess, status_code=201
)
def updateprocess(
    process_id: int, process: schemas.TrackedProcess, db: Session = Depends(deps.get_db)
) -> Any:
    """Update a process in the database

    Args:
        process (schemas.ProcessUpdate): Process to update in the database
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).

    Returns:
        results: List of Jobs (Pydantic models)
    """
    try:
        return crud.tracked_process.update(db=db, db_obj=process, obj_in=process)
    except IntegrityError as e:
        raise HTTPException(status_code=503, detail="Error updating record")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Error updating record")


# Add Patch endpoint to toggle process tracking. Set enable to true/false to enable/disable tracking
@router.patch(
    "/processes/{process_id}", response_model=schemas.TrackedProcess, status_code=201
)
def toggleprocess(
    process_id: int, enable: bool, db: Session = Depends(deps.get_db)
) -> Any:
    """Toggle process tracking

    Args:
        process (schemas.ProcessUpdate): Process to update in the database
        db (Session, optional): Database session. Defaults to Depends(deps.get_db).

    Returns:
        results: List of Jobs (Pydantic models)
    """
    try:
        return crud.tracked_process.toggle(db=db, process_id=process_id, enable=enable)
    except IntegrityError as e:
        raise HTTPException(status_code=503, detail="Error updating record")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Error updating record")
