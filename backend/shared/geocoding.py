import os

import googlemaps
from dotenv import load_dotenv
from googlemaps.geocoding import geocode, reverse_geocode

from shared.enums import UILanguages

load_dotenv()


def get_maps_client() -> googlemaps.Client:
    return googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))


def get_place_id(latitude: float, longitude: float) -> str | None:
    client = get_maps_client()
    result = reverse_geocode(
        client,
        (latitude, longitude),
        result_type=["locality", "administrative_area_level_2"],
    )
    try:
        return result[0]["place_id"]
    except (IndexError, KeyError):
        return None


def get_places(
    city_name: str, language: UILanguages = UILanguages.en, max_results: int = 5
) -> list[tuple[str, str]]:
    client = get_maps_client()
    result = geocode(client, city_name, language=language.name)
    cities = []
    for res in result:
        if "locality" in res["types"] or "administrative_area_level_2" in res["types"]:
            cities.append(
                (
                    res["formatted_address"],
                    res["place_id"],
                )
            )

    return cities[:max_results]


def get_place(
    place_id: str, language: UILanguages = UILanguages.en
) -> tuple[float, float, str]:
    client = get_maps_client()
    result = geocode(client, place_id=place_id, language=language.name)
    try:
        return (
            result[0]["geometry"]["location"]["lat"],
            result[0]["geometry"]["location"]["lng"],
            result[0]["address_components"][0]["long_name"],
        )
    except (IndexError, KeyError):
        raise ValueError("Location not found")
