import requests
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, service_key=None):
        self.service_key = service_key or os.getenv("KMA_SERVICE_KEY")
        self.base_url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        self.base_times = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]

    def _get_base_time(self):
        """기상청 API 발표 시간: 02, 05, 08, 11, 14, 17, 20, 23시 (발표 후 ~10분 후 데이터 가용)"""
        now = datetime.now()
        current_hour = now.hour * 100 + now.minute
        
        for bt in reversed(self.base_times):
            if current_hour >= int(bt) + 10:
                return now.strftime("%Y%m%d"), bt
        
        yesterday = now - timedelta(days=1)
        return yesterday.strftime("%Y%m%d"), "2300"

    def get_daily_forecast(self, nx=60, ny=127):
        if not self.service_key:
            logger.error("KMA_SERVICE_KEY is missing.")
            return None

        base_date, base_time = self._get_base_time()
        today = datetime.now().strftime("%Y%m%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        
        params = {
            "serviceKey": self.service_key,
            "pageNo": "1",
            "numOfRows": "1000",
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": str(nx),
            "ny": str(ny)
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("response", {}).get("header", {}).get("resultCode") != "00":
                logger.error(f"API Error: {data.get('response', {}).get('header', {}).get('resultMsg')}")
                return None

            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not items:
                logger.error("No weather items found in response.")
                return None

            hourly_data = {}
            for item in items:
                fcst_date = item["fcstDate"]
                fcst_time = item["fcstTime"]
                category = item["category"]
                value = item["fcstValue"]
                
                key = f"{fcst_date}_{fcst_time}"
                if key not in hourly_data:
                    hourly_data[key] = {
                        "date": fcst_date,
                        "time": fcst_time,
                        "hour": int(fcst_time[:2])
                    }
                
                if category == "TMP":
                    hourly_data[key]["temp"] = int(value)
                elif category == "SKY":
                    hourly_data[key]["sky"] = value
                    hourly_data[key]["sky_text"] = self._parse_sky(value)
                elif category == "PTY":
                    hourly_data[key]["pty"] = value
                    hourly_data[key]["pty_text"] = self._parse_pty(value)
                elif category == "POP":
                    hourly_data[key]["pop"] = int(value)
                elif category == "REH":
                    hourly_data[key]["reh"] = int(value)
                elif category == "TMN":
                    hourly_data[key]["min_temp"] = int(float(value))
                elif category == "TMX":
                    hourly_data[key]["max_temp"] = int(float(value))
            
            today_forecast = []
            tomorrow_forecast = []
            
            for key in sorted(hourly_data.keys()):
                entry = hourly_data[key]
                if entry["date"] == today:
                    today_forecast.append(entry)
                elif entry["date"] == tomorrow:
                    tomorrow_forecast.append(entry)
            
            temps = [h.get("temp") for h in today_forecast if h.get("temp") is not None]
            min_temp = min(temps) if temps else None
            max_temp = max(temps) if temps else None
            
            for h in today_forecast:
                if h.get("min_temp"):
                    min_temp = h["min_temp"]
                if h.get("max_temp"):
                    max_temp = h["max_temp"]
            
            return {
                "date": today,
                "min_temp": min_temp,
                "max_temp": max_temp,
                "hourly": today_forecast,
                "tomorrow": tomorrow_forecast
            }

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None

    def get_weather(self, nx=60, ny=127):
        forecast = self.get_daily_forecast(nx, ny)
        if not forecast or not forecast["hourly"]:
            return None
        
        now_hour = datetime.now().hour
        for h in forecast["hourly"]:
            if h["hour"] >= now_hour:
                return {
                    "date": h["date"],
                    "time": h["time"],
                    "temp": str(h.get("temp", "N/A")),
                    "sky": h.get("sky_text", "알 수 없음"),
                    "pty": h.get("pty_text", "없음"),
                    "pop": str(h.get("pop", "N/A")),
                    "reh": str(h.get("reh", "N/A")),
                }
        
        return None

    def _parse_sky(self, value):
        mapping = {"1": "맑음", "3": "구름많음", "4": "흐림"}
        return mapping.get(value, "알 수 없음")

    def _parse_pty(self, value):
        mapping = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
        return mapping.get(value, "알 수 없음")

if __name__ == "__main__":
    service = WeatherService()
    forecast = service.get_daily_forecast()
    if forecast:
        print(f"=== {forecast['date']} 날씨 예보 ===")
        print(f"최저: {forecast['min_temp']}°C / 최고: {forecast['max_temp']}°C\n")
        print("시간별 예보:")
        for h in forecast["hourly"]:
            print(f"  {h['hour']:02d}시: {h.get('temp', '?')}°C, {h.get('sky_text', '?')}, 강수확률 {h.get('pop', '?')}%")
