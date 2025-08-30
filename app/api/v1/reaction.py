import logging

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound

from app.api.dependencies import CurrentActiveUserDep, DbDep
from app.exceptions import InactiveUserError
from app.queries import create_or_update_reaction
from app.schemas.reaction import ReactionInSchema, ReactionOutSchema

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reactions", tags=["Reactions"])


@router.put("")
async def create_or_update_user_reaction(
    reaction_data: ReactionInSchema,
    db: DbDep,
    current_user: CurrentActiveUserDep,
) -> ReactionOutSchema:
    """Create a new reaction in the database."""
    # TODO: handle notifications
    # TODO: handle deleting older chats if reaction is negative and not new
    try:
        is_created, reaction = await create_or_update_reaction(
            current_user.id,
            reaction_data.to_user_id,
            reaction_data.reaction_type,
            db,
        )
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Match not found") from e
    except InactiveUserError as e:
        raise HTTPException(status_code=403, detail="Inactive user") from e

    return ReactionOutSchema.model_validate(reaction, from_attributes=True)
