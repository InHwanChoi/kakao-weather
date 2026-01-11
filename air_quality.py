import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AirQualityService:
    GRADE_MAP = {
        "1": ("좋음", "😊"),
        "2": ("보통", "🙂"),
        "3": ("나쁨", "😷"),
        "4": ("매우나쁨", "🚨"),
    }
    
    STATION_MAP = {
        "서울": "중구",
        "청담": "강남구",
        "강남": "강남구",
        "구의": "광진구",
        "광진": "광진구",
        "송파": "송파구",
        "잠실": "송파구",
    }

    def __init__(self, service_key=None):
        self.service_key = service_key or os.getenv("AIRKOREA_SERVICE_KEY")
        self.base_url = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"

    def get_air_quality(self, station_name="중구"):
        if not self.service_key:
            logger.error("AIRKOREA_SERVICE_KEY is missing.")
            return None

        params = {
            "serviceKey": self.service_key,
            "returnType": "json",
            "numOfRows": "1",
            "pageNo": "1",
            "stationName": station_name,
            "dataTerm": "DAILY",
            "ver": "1.0"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            items = data.get("response", {}).get("body", {}).get("items", [])
            if not items:
                logger.error(f"No air quality data found for station: {station_name}")
                return None

            item = items[0]
            
            pm10_value = item.get("pm10Value", "-")
            pm25_value = item.get("pm25Value", "-")
            pm10_grade = item.get("pm10Grade", "0")
            pm25_grade = item.get("pm25Grade", "0")
            
            pm10_info = self.GRADE_MAP.get(pm10_grade, ("측정중", "⏳"))
            pm25_info = self.GRADE_MAP.get(pm25_grade, ("측정중", "⏳"))

            return {
                "station": station_name,
                "pm10": pm10_value,
                "pm10_grade": pm10_info[0],
                "pm10_emoji": pm10_info[1],
                "pm25": pm25_value,
                "pm25_grade": pm25_info[0],
                "pm25_emoji": pm25_info[1],
                "data_time": item.get("dataTime", ""),
            }

        except Exception as e:
            logger.error(f"Error fetching air quality data: {e}")
            return None

    def get_air_quality_by_location(self, location="서울"):
        station = self.STATION_MAP.get(location, location)
        return self.get_air_quality(station)

    def get_advice(self, air_data: dict) -> str | None:
        if not air_data:
            return None
        
        pm10_grade = air_data.get("pm10_grade", "")
        pm25_grade = air_data.get("pm25_grade", "")
        
        if "매우나쁨" in (pm10_grade, pm25_grade):
            return "미세먼지 최악! 외출 자제하고 마스크 필수! 😷"
        elif "나쁨" in (pm10_grade, pm25_grade):
            return "미세먼지 나쁨, 마스크 챙겨! 😷"
        elif pm10_grade == "좋음" and pm25_grade == "좋음":
            return "공기 좋아! 환기하기 좋은 날 🌬️"
        
        return None


if __name__ == "__main__":
    service = AirQualityService()
    air = service.get_air_quality("중구")
    if air:
        print(f"측정소: {air['station']}")
        print(f"측정시간: {air['data_time']}")
        print(f"미세먼지(PM10): {air['pm10']}㎍/㎥ - {air['pm10_grade']} {air['pm10_emoji']}")
        print(f"초미세먼지(PM2.5): {air['pm25']}㎍/㎥ - {air['pm25_grade']} {air['pm25_emoji']}")
        
        advice = service.get_advice(air)
        if advice:
            print(f"\n💬 {advice}")
