from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencies import DbDep
from app.enums import UILanguages
from app.schemas.place import CoordinatesSchema, PlaceDetailsSchema, PlaceSearchSchema
from app.services.place import (
    get_place_by_coordinates,
    get_place_details,
    search_places,
)

router = APIRouter(prefix="/places", tags=["places"])


@router.get("/search")
async def search_places_endpoint(
    query: Annotated[str, Query(description="Search query for place names")],
    language: Annotated[str, Query()] = "en",
) -> list[PlaceSearchSchema]:
    """Search for places by name.

    Returns a list of places matching the search query with their names and place IDs.
    """
    try:
        ui_language = UILanguages[language]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language: {language}. "
                f"Supported: {[lang.name for lang in UILanguages]}"
            ),
        ) from None

    return await search_places(query, ui_language)


@router.get("/{place_id}")
async def get_place_endpoint(
    db: DbDep,
    place_id: str,
    language: Annotated[str, Query()] = "en",
) -> PlaceDetailsSchema:
    """Get detailed place information by place ID.

    Fetches place details from Google Maps and saves to database if not exists.
    """
    try:
        ui_language = UILanguages[language]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language: {language}. "
                f"Supported: {[lang.name for lang in UILanguages]}"
            ),
        ) from None

    try:
        return await get_place_details(db, place_id, ui_language)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/coordinates")
async def get_place_by_coordinates_endpoint(
    db: DbDep,
    coordinates: CoordinatesSchema,
    language: Annotated[str, Query()] = "en",
) -> PlaceDetailsSchema:
    """Get place information by coordinates.

    Fetches place details from Google Maps by coordinates and saves to database
    if found.
    """
    try:
        ui_language = UILanguages[language]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language: {language}. "
                f"Supported: {[lang.name for lang in UILanguages]}"
            ),
        ) from None

    try:
        return await get_place_by_coordinates(
            db,
            coordinates.latitude,
            coordinates.longitude,
            ui_language,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
