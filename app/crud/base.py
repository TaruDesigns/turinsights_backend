from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import DateTime, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def parse_datetime(value):
    # Helper for jsonable encoder
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int | None = 0, limit: int | None = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def create_async(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def remove_all_but_id(self, db: Session, *, id: int):
        # Helper function to remove all rows except the one with the specified id
        # Useful for tables that need to keep only one row (like uipath token)
        stmt = delete(self.model).where(self.model.access_token != id)
        db.execute(stmt)
        db.commit()

    def upsert(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType | None:
        """Helper function to "Upsert" -> If item is not created, create it
        If it already exists, just update it"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        try:
            db.merge(db_obj)
            db.commit()
            return db_obj
        except IntegrityError as e:
            db.rollback()
            logger.error(e)

    def parse_and_replace_datetimes(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in json_data.items():
            # Get the column property from the SQLAlchemy model. We instantiate a model
            column = getattr(self.model().__class__.__table__.c, key, None)

            if column is not None and isinstance(column.type, DateTime) and isinstance(value, str):
                # Convert the string to datetime
                json_data[key] = parse_datetime(value)

        return json_data

    async def upsert_async(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType | None:
        """Helper function to "Upsert" -> If item is not created, create it
        If it already exists, just update it"""
        obj_in_data = jsonable_encoder(obj_in)
        # Parse the strings into datetime objects so the following conversion doesn't just ignore them
        json_data = self.parse_and_replace_datetimes(obj_in_data)
        db_obj = self.model(**json_data)  # type: ignore
        try:
            await db.merge(db_obj)
            await db.commit()
            return db_obj
        except IntegrityError as e:
            await db.rollback()  # Let the context manager do the rollback
            logger.error(e)

    def create_safe(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType | None:
        """Helper function to "Create and ignore duplicate errors"""
        try:
            db_obj = self.create(db=db, obj_in=obj_in)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            logger.warning(e)
            return None

    async def create_safe_async(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType | None:
        """Helper function to "Create and ignore duplicate errors"""
        try:
            db_obj = await self.create_async(db=db, obj_in=obj_in)
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            logger.warning(e)
            return None
            return None
