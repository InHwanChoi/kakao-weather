import requests
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UltraShortForecastService:
    """초단기예보 서비스 - 6시간 이내 예보, 매시간 30분 발표"""
    
    PTY_MAP = {
        "0": None,
        "1": "비",
        "2": "비/눈",
        "3": "눈",
        "5": "빗방울",
        "6": "빗방울눈날림",
        "7": "눈날림",
    }

    def __init__(self, service_key=None):
        self.service_key = service_key or os.getenv("KMA_SERVICE_KEY")
        self.base_url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"

    def _get_base_time(self):
        now = datetime.now()
        minute = now.minute
        
        if minute < 45:
            base = now - timedelta(hours=1)
        else:
            base = now
        
        return base.strftime("%Y%m%d"), f"{base.hour:02d}30"

    def get_forecast(self, nx=60, ny=127):
        if not self.service_key:
            logger.error("KMA_SERVICE_KEY is missing.")
            return None

        base_date, base_time = self._get_base_time()
        
        params = {
            "serviceKey": self.service_key,
            "pageNo": "1",
            "numOfRows": "60",
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
                logger.error("No forecast items found.")
                return None

            hourly = {}
            for item in items:
                fcst_time = item["fcstTime"]
                fcst_date = item["fcstDate"]
                category = item["category"]
                value = item["fcstValue"]
                
                key = f"{fcst_date}_{fcst_time}"
                if key not in hourly:
                    hourly[key] = {
                        "date": fcst_date,
                        "time": fcst_time,
                        "hour": int(fcst_time[:2]),
                        "minute": int(fcst_time[2:])
                    }
                
                if category == "PTY":
                    hourly[key]["pty"] = value
                    hourly[key]["pty_text"] = self.PTY_MAP.get(value)
                elif category == "RN1":
                    hourly[key]["rn1"] = value
                elif category == "T1H":
                    hourly[key]["temp"] = value
                elif category == "SKY":
                    hourly[key]["sky"] = value

            return list(hourly.values())

        except Exception as e:
            logger.error(f"Error fetching ultra short forecast: {e}")
            return None

    def check_upcoming_rain(self, nx=60, ny=127, within_minutes=60):
        forecast = self.get_forecast(nx, ny)
        if not forecast:
            return None
        
        now = datetime.now()
        
        for entry in forecast:
            fcst_datetime = datetime.strptime(
                f"{entry['date']}{entry['time']}", "%Y%m%d%H%M"
            )
            
            diff = (fcst_datetime - now).total_seconds() / 60
            
            if 0 < diff <= within_minutes:
                pty_text = entry.get("pty_text")
                if pty_text:
                    return {
                        "type": pty_text,
                        "time": fcst_datetime,
                        "minutes_until": int(diff),
                        "temp": entry.get("temp"),
                        "rn1": entry.get("rn1")
                    }
        
        return None


if __name__ == "__main__":
    service = UltraShortForecastService()
    
    print("=== 초단기예보 테스트 ===\n")
    
    forecast = service.get_forecast()
    if forecast:
        print("향후 6시간 예보:")
        for f in forecast[:6]:
            pty = f.get("pty_text") or "없음"
            print(f"  {f['hour']:02d}:{f['minute']:02d} - 기온: {f.get('temp', '?')}°C, 강수: {pty}")
    
    print("\n=== 1시간 내 강수 체크 ===")
    rain = service.check_upcoming_rain()
    if rain:
        print(f"⚠️ {rain['minutes_until']}분 후 {rain['type']} 예상!")
    else:
        print("✅ 1시간 내 강수 없음")
