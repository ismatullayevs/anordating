import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from dotenv import load_dotenv

load_dotenv()


def get_azure_client(language: str | None = None) -> MapsSearchClient:
    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")
    return MapsSearchClient(
        credential=AzureKeyCredential(subscription_key), accept_language=language
    )


def get_city_name(
    latitude: float, longitude: float, language: str | None = None
) -> str:
    client = get_azure_client(language)
    result = client.get_reverse_geocoding(coordinates=[longitude, latitude])
    try:
        return result["features"][0]["properties"]["address"]["locality"]
    except (KeyError, IndexError):
        raise ValueError("City name not found")


def get_location(city_name: str, language: str | None = None) -> tuple[float, float]:
    client = get_azure_client(language)
    result = client.get_geocoding(top=1, locality=city_name)
    try:
        longitude, latitude = result["features"][0]["properties"]["geocodePoints"][0][
            "geometry"
        ]["coordinates"]
        return (latitude, longitude)
    except (KeyError, IndexError):
        raise ValueError("City not found")
