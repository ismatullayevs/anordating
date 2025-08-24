
from fastapi import APIRouter

from app.api.dependencies import CurrentActiveUserDep, DbDep
from app.models.user import Reaction
from app.schemas.reaction import ReactionInSchema, ReactionOutSchema

router = APIRouter(prefix="/reactions", tags=["Reactions"])


@router.post("/", response_model=ReactionOutSchema)
async def create_new_reaction(
    reaction_data: ReactionInSchema,
    db: DbDep,
    current_user: CurrentActiveUserDep,
) -> Reaction:
    """Create a new reaction in the database."""
    # reaction = await create_reaction
