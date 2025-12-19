import json
from langchain.tools import tool
from models import DataGovScraper, load_model, predict_image, model_path, device, classes, load_model_wheat, \
    predict_image_wheat, wheat_model_path, class_names
import os
import pandas as pd
import openmeteo_requests
import requests
import requests_cache
from retry_requests import retry
from io import StringIO
scraper = DataGovScraper()

# Fixed image paths
FIXED_IMAGE_PATH = "uploaded_image.jpg"
FIXED_WHEAT_IMAGE_PATH = "uploaded_image.jpg"


@tool("get_market_price")
def getMarketPrice(crop: str = "tomato", location: str = "",state:str = "") -> str:
    """Get current market price from Data.gov.in government database.

    Args:
        crop: Name of the crop (tomato, wheat, rice, maize, cotton, etc.)
        location: location (optional - will find best available match) (district)
        state: state (tamil-nadu,punnjab)

    Returns:
        Current government market price with location and market details
    """
    return scraper.get_market_price(crop, location,state)


@tool("get_crop_locations")
def getCropLocations(crop: str = "tomato") -> str:
    """Find which states have data for a specific crop"""

    try:
        params = {
            'api-key': scraper.api_key,
            'format': 'json',
            'limit': '200'
        }

        response = scraper.session.get(scraper.api_url, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])

            # Find states with this crop
            states_with_crop = set()
            for record in records:
                commodity = str(record.get('commodity', '')).lower()
                state = record.get('state', '')

                if crop.lower() in commodity:
                    states_with_crop.add(state)

            if states_with_crop:
                states_list = ', '.join(sorted(states_with_crop))
                return f"📍 {crop.title()} price data available in: {states_list}"
            else:
                return f"❌ No {crop} data found in current dataset"

        return f"❌ Error fetching location data"

    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool("disease_Detect")
def disease_Detect() -> str:
    """Detect plant diseases from the uploaded image.
    User must upload an image first. The image is automatically saved to a fixed location.

    Returns:
        Disease diagnosis and treatment recommendations
    """
    print("disease tool called")
    try:
        if not os.path.exists(FIXED_IMAGE_PATH):
            return "❌ No image found. Please upload a plant image first."

        model = load_model(model_path, num_classes=len(classes), device=device)
        prediction = predict_image(model, FIXED_IMAGE_PATH, device=device)
        return prediction
    except Exception as e:
        return f"❌ Error analyzing image: {str(e)}"


@tool("Wheat_disease_detection")
def Wheat_disease_detection() -> str:
    """Detect wheat-specific diseases from the uploaded image.
    User must upload an image first. The image is automatically saved to a fixed location.

    Returns:
        Wheat disease diagnosis and recommendations
    """
    print("Wheat disease tool called")
    try:
        if not os.path.exists(FIXED_IMAGE_PATH):
            return "❌ No image found. Please upload a wheat plant image first."

        model = load_model_wheat(wheat_model_path, num_classes=len(class_names), device=device)
        label = predict_image_wheat(FIXED_IMAGE_PATH, model, class_names, device)
        return label
    except Exception as e:
        return f"❌ Error analyzing wheat image: {str(e)}"


@tool(description="Fetch all available schemes with description and link")
def Find_scheme():
    json_file_path = "scheme.json"
    file = pd.read_json(json_file_path)
    des = file["description"]
    link = file["link"]
    output_json = []
    for i in range(len(file)):
        output_json.append({"description": des[i], "link": link[i]})
    return output_json


@tool(description="Get the full details of a scheme using its link")
def Scheme_detials(correct_link: str):
    json_file_path = "scheme.json"
    file = pd.read_json(json_file_path)
    link = file["link"]
    for i in range(len(file)):
        if link[i] == correct_link:
            break
    output = {
        "title": file["title"][i],
        "ministry": file["ministry"][i],
        "description": file["description"][i],
        "details": file["details"][i],
        "eligibility": file["eligibility"][i],
        "application_process": file["application_process"][i],
        "documents_required": file["documents_required"][i]
    }
    return output


def get_lat_lon(city_name: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "country": "IN"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"Could not find coordinates for city: {city_name}")

    location = data["results"][0]
    return location["latitude"], location["longitude"]


@tool(
    description="Get 7-day daily weather forecast for an Indian city. Returns structured data suitable for LLM reasoning."
)
def Weather_tool(location: str) -> dict:
    """
    Args:
        location: Indian city name (e.g., Delhi, Chandigarh)
    Returns:
        Structured daily weather forecast with metadata
    """
    try:
        latitude, longitude = get_lat_lon(location)

        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "rain_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "weather_code"
            ],
            "forecast_days": 7,
            "timezone": "auto"
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()

        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(days=1),
            inclusive="left"
        )

        forecast = []
        for i, date in enumerate(dates):
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "temp_max_c": float(daily.Variables(0).ValuesAsNumpy()[i]),
                "temp_min_c": float(daily.Variables(1).ValuesAsNumpy()[i]),
                "precip_mm": float(daily.Variables(2).ValuesAsNumpy()[i]),
                "rain_mm": float(daily.Variables(3).ValuesAsNumpy()[i]),
                "precip_prob_pct": float(daily.Variables(4).ValuesAsNumpy()[i]),
                "wind_speed_max_mps": float(daily.Variables(5).ValuesAsNumpy()[i]),
                "weather_code": int(daily.Variables(6).ValuesAsNumpy()[i])
            })

        return {
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "forecast_type": "daily",
            "units": {
                "temperature": "°C",
                "precipitation": "mm",
                "wind_speed": "m/s",
                "probability": "%"
            },
            "columns": {
                "date": "Forecast date (YYYY-MM-DD)",
                "temp_max_c": "Maximum air temperature at 2m height",
                "temp_min_c": "Minimum air temperature at 2m height",
                "precip_mm": "Total precipitation for the day",
                "rain_mm": "Rainfall amount",
                "precip_prob_pct": "Maximum probability of precipitation",
                "wind_speed_max_mps": "Maximum wind speed at 10m",
                "weather_code": "WMO weather condition code"
            },
            "data": forecast
        }

    except Exception as e:
        return {"error": str(e)}


tools = [getCropLocations, getMarketPrice, disease_Detect, Wheat_disease_detection, Scheme_detials, Find_scheme, Weather_tool]