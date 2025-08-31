import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import UILanguages
from app.geocoding import get_place
from app.geocoding import get_places as get_places_from_geocoding
from app.models.user import Place, PlaceName
from app.schemas.place import PlaceDetailsSchema, PlaceSearchSchema

logger = logging.getLogger(__name__)


async def search_places(
    query: str,
    language: UILanguages = UILanguages.en,
) -> list[PlaceSearchSchema]:
    """Search for places by name using geocoding service.

    Args:
        query: Search query for place names
        language: Language for the search results

    Returns:
        List[PlaceSearchSchema]: List of matching places with names and place IDs

    """
    places_data = get_places_from_geocoding(query, language)
    return [
        PlaceSearchSchema(name=name, place_id=place_id)
        for name, place_id in places_data
    ]


async def get_place_details(
    db: AsyncSession,
    place_id: str,
    language: UILanguages = UILanguages.en,
) -> PlaceDetailsSchema:
    """Get detailed place information by place ID.

    Fetches place details from geocoding service and saves to database if not exists.

    Args:
        db: Database session
        place_id: Google Maps place ID
        language: Language for place name

    Returns:
        PlaceDetailsSchema: Detailed place information

    Raises:
        ValueError: If place cannot be found or fetched

    """
    try:
        # Fetch place details from geocoding service
        latitude, longitude, place_name = get_place(place_id, language)

        # Check if place exists in database
        query = select(Place).where(Place.id == place_id)
        result = await db.scalars(query)
        place = result.one_or_none()

        # Create place and place name in database if not exists
        if not place:
            place = Place(id=place_id)
            place_name_db = PlaceName(
                place_id=place_id,
                language=language,
                name=place_name,
            )
            db.add(place)
            db.add(place_name_db)
            await db.commit()
            logger.info(f"Created new place in database: {place_id} - {place_name}")

        return PlaceDetailsSchema(
            place_id=place_id,
            latitude=latitude,
            longitude=longitude,
            name=place_name,
        )

    except Exception as e:
        logger.error(f"Error getting place details for ID '{place_id}': {e}")
        await db.rollback()
        raise ValueError(f"Could not fetch place details for ID: {place_id}") from e


async def get_place_by_coordinates(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    language: UILanguages = UILanguages.en,
) -> PlaceDetailsSchema:
    """Get place information by coordinates.

    Fetches place details from geocoding service and saves to database if found.

    Args:
        db: Database session
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        language: Language for place name

    Returns:
        PlaceDetailsSchema: Detailed place information

    Raises:
        ValueError: If place cannot be found at the coordinates

    """
    from app.geocoding import get_place_id

    try:
        # Get place_id from coordinates using geocoding service
        place_id = get_place_id(latitude, longitude)
        if not place_id:
            raise ValueError("No place found at the given coordinates")

        # Get detailed place information and save to database
        return await get_place_details(db, place_id, language)

    except Exception as e:
        logger.error(
            f"Error getting place by coordinates ({latitude}, {longitude}): {e}",
        )
        raise ValueError(
            f"Could not fetch place at coordinates ({latitude}, {longitude})",
        ) from e
