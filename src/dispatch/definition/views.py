from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey

from .models import (
    DefinitionCreate,
    DefinitionPagination,
    DefinitionRead,
    DefinitionUpdate,
)
from .service import create, delete, get, get_by_text, update

router = APIRouter()


@router.get("", response_model=DefinitionPagination)
def get_definitions(*, common: dict = Depends(common_parameters)):
    """Get all definitions."""
    return search_filter_sort_paginate(model="Definition", **common)


@router.get("/{definition_id}", response_model=DefinitionRead)
def get_definition(*, db_session: Session = Depends(get_db), definition_id: PrimaryKey):
    """Update a definition."""
    definition = get(db_session=db_session, definition_id=definition_id)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The definition with this id does not exist."}],
        )
    return definition


@router.post("", response_model=DefinitionRead)
def create_definition(*, db_session: Session = Depends(get_db), definition_in: DefinitionCreate):
    """Create a new definition."""
    definition = get_by_text(db_session=db_session, text=definition_in.text)
    if definition:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A description with this text already exists."), loc="text"
                )
            ],
            model=DefinitionRead,
        )

    definition = create(db_session=db_session, definition_in=definition_in)
    return definition


@router.put("/{definition_id}", response_model=DefinitionRead)
def update_definition(
    *,
    db_session: Session = Depends(get_db),
    definition_id: PrimaryKey,
    definition_in: DefinitionUpdate,
):
    """Update a definition."""
    definition = get(db_session=db_session, definition_id=definition_id)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The definition with this id does not exist."}],
        )
    definition = update(db_session=db_session, definition=definition, definition_in=definition_in)
    return definition


@router.delete("/{definition_id}")
def delete_definition(*, db_session: Session = Depends(get_db), definition_id: PrimaryKey):
    """Delete a definition."""
    definition = get(db_session=db_session, definition_id=definition_id)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The definition with this id does not exist."}],
        )
    delete(db_session=db_session, definition_id=definition_id)
