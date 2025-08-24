from uuid import UUID

from app.models.user import Reaction


async def create_reaction(user_id: UUID, match_id: UUID) -> Reaction:
    """Create a reaction for a user on a match."""
