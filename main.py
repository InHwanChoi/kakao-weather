import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from weather import WeatherService
from air_quality import AirQualityService
from kakao_service import KakaoTalkService

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


OUTFIT_BY_TEMP = {
    "male": {
        "freezing": "히트텍 + 니트 + 롱패딩, 기모바지",
        "very_cold": "히트텍 + 맨투맨 + 패딩, 기모바지",
        "cold": "니트 + 코트, 슬랙스",
        "chilly": "셔츠 + 트렌치코트, 면바지",
        "cool": "가디건 + 셔츠, 슬랙스",
        "mild": "긴팔 셔츠, 면바지",
        "warm": "반팔 + 얇은 셔츠, 면바지",
        "hot": "반팔, 반바지",
    },
    "female": {
        "freezing": "히트텍 + 니트 + 롱패딩, 기모레깅스",
        "very_cold": "터틀넥 + 패딩, 기모스커트+타이츠",
        "cold": "니트 + 롱코트, 슬랙스",
        "chilly": "블라우스 + 트렌치코트, 와이드팬츠",
        "cool": "가디건 + 원피스, 얇은 스타킹",
        "mild": "긴팔 블라우스, 면바지",
        "warm": "반팔 블라우스, 린넨팬츠",
        "hot": "민소매, 반바지",
    },
}

SEASONAL_ITEMS = {
    "freezing": "🔥 손난로 챙기고 핫팩 붙여!",
    "very_cold": "🧣 목도리랑 장갑 필수!",
    "cold": "🧤 장갑 챙겨!",
    "hot": "🧴 선크림 바르고 물 많이 마셔!",
    "very_hot": "🧊 아이스팩 챙기고 그늘로 다녀!",
}


class SmartWeatherAdvisor:
    def __init__(self, forecast: dict, air_quality: dict | None = None, gender: str = "male"):
        self.forecast = forecast
        self.hourly = forecast.get("hourly", [])
        self.tomorrow = forecast.get("tomorrow", [])
        self.min_temp = forecast.get("min_temp")
        self.max_temp = forecast.get("max_temp")
        self.air_quality = air_quality
        self.gender = gender.lower() if gender else "male"
    
    def _get_temp_category(self, temp: int) -> str:
        if temp <= -5:
            return "freezing"
        elif temp <= 4:
            return "very_cold"
        elif temp <= 9:
            return "cold"
        elif temp <= 16:
            return "chilly"
        elif temp <= 19:
            return "cool"
        elif temp <= 22:
            return "mild"
        elif temp <= 27:
            return "warm"
        else:
            return "hot"
    
    def _find_rain_hours(self, hours: list) -> list:
        rain_hours = []
        for h in hours:
            pty = h.get("pty", "0")
            pop = h.get("pop", 0)
            if pty != "0" or pop >= 60:
                rain_hours.append(h)
        return rain_hours
    
    def _format_hour(self, hour: int) -> str:
        if hour < 12:
            return f"오전 {hour}시" if hour > 0 else "자정"
        elif hour == 12:
            return "낮 12시"
        else:
            return f"오후 {hour - 12}시"
    
    def _get_rain_advice(self) -> str | None:
        now_hour = datetime.now().hour
        future_hours = [h for h in self.hourly if h["hour"] > now_hour]
        rain_hours = self._find_rain_hours(future_hours)
        
        if not rain_hours:
            return None
        
        first_rain = rain_hours[0]
        rain_type = first_rain.get("pty_text", "비")
        if rain_type == "없음":
            rain_type = "비"
        
        return f"{self._format_hour(first_rain['hour'])}에 {rain_type} 온다니까 우산 챙겨! ☔"
    
    def _get_tomorrow_rain_advice(self) -> str | None:
        rain_hours = self._find_rain_hours(self.tomorrow[:12])
        if rain_hours:
            return "내일 비 온다니까 세차하지 마! 🚗"
        return None
    
    def _get_outfit_advice(self) -> str | None:
        temp = self.max_temp or self.min_temp
        if temp is None:
            return None
        
        category = self._get_temp_category(temp)
        outfit = OUTFIT_BY_TEMP.get(self.gender, OUTFIT_BY_TEMP["male"]).get(category, "")
        
        if outfit:
            return f"👔 오늘 코디: {outfit}"
        return None
    
    def _get_seasonal_item_advice(self) -> str | None:
        temp = self.min_temp or self.max_temp
        if temp is None:
            return None
        
        category = self._get_temp_category(temp)
        return SEASONAL_ITEMS.get(category)
    
    def _get_temp_warning(self) -> str | None:
        if self.min_temp and self.max_temp:
            diff = self.max_temp - self.min_temp
            if diff >= 10:
                return f"일교차 {diff}도니까 겉옷 챙겨! 🌡️"
        return None
    
    def _get_air_quality_advice(self) -> str | None:
        if not self.air_quality:
            return None
        
        pm10_grade = self.air_quality.get("pm10_grade", "")
        pm25_grade = self.air_quality.get("pm25_grade", "")
        
        if "매우나쁨" in (pm10_grade, pm25_grade):
            return "미세먼지 최악! 외출 자제하고 마스크 필수! 😷"
        elif "나쁨" in (pm10_grade, pm25_grade):
            return "미세먼지 나쁨, 마스크 챙겨! 😷"
        elif pm10_grade == "좋음" and pm25_grade == "좋음":
            return "공기 좋아! 환기하기 좋은 날 🌬️"
        
        return None
    
    def generate_advice(self) -> list[str]:
        advices = []
        
        rain = self._get_rain_advice()
        if rain:
            advices.append(rain)
        
        outfit = self._get_outfit_advice()
        if outfit:
            advices.append(outfit)
        
        seasonal = self._get_seasonal_item_advice()
        if seasonal:
            advices.append(seasonal)
        
        temp_warning = self._get_temp_warning()
        if temp_warning:
            advices.append(temp_warning)
        
        air_advice = self._get_air_quality_advice()
        if air_advice:
            advices.append(air_advice)
        
        tomorrow_rain = self._get_tomorrow_rain_advice()
        if tomorrow_rain:
            advices.append(tomorrow_rain)
        
        return advices


def format_hourly_forecast(hourly: list) -> str:
    now_hour = datetime.now().hour
    future_hours = [h for h in hourly if h["hour"] >= now_hour][:8]
    
    lines = []
    for h in future_hours:
        hour = h["hour"]
        temp = h.get("temp", "?")
        sky = h.get("sky_text", "")
        pop = h.get("pop", 0)
        
        period = "오전" if hour < 12 else "오후"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        
        weather_icon = "☀️" if sky == "맑음" else "⛅" if sky == "구름많음" else "☁️"
        rain_info = f" 💧{pop}%" if pop >= 30 else ""
        
        lines.append(f"{period} {display_hour}시 {weather_icon} {temp}°C{rain_info}")
    
    return "\n".join(lines)


def format_air_quality(air: dict | None) -> str:
    if not air:
        return ""
    
    pm10 = air.get("pm10", "-")
    pm25 = air.get("pm25", "-")
    pm10_grade = air.get("pm10_grade", "")
    pm25_grade = air.get("pm25_grade", "")
    pm10_emoji = air.get("pm10_emoji", "")
    pm25_emoji = air.get("pm25_emoji", "")
    
    return f"미세먼지 {pm10}㎍/㎥ {pm10_grade}{pm10_emoji} | 초미세 {pm25}㎍/㎥ {pm25_grade}{pm25_emoji}"


def main():
    gender = os.getenv("GENDER", "male")
    
    weather_service = WeatherService()
    forecast = weather_service.get_daily_forecast()
    
    if not forecast:
        logger.error("Failed to fetch weather data.")
        return

    air_service = AirQualityService()
    air_quality = air_service.get_air_quality("중구")

    advisor = SmartWeatherAdvisor(forecast, air_quality, gender)
    advices = advisor.generate_advice()
    
    date_str = forecast["date"]
    formatted_date = f"{date_str[4:6]}월 {date_str[6:8]}일"
    
    hourly_text = format_hourly_forecast(forecast["hourly"])
    
    temp_range = ""
    if forecast["min_temp"] and forecast["max_temp"]:
        temp_range = f"🌡️ 최저 {forecast['min_temp']}°C / 최고 {forecast['max_temp']}°C"
    
    air_text = format_air_quality(air_quality)
    
    advice_text = "\n".join(advices) if advices else "오늘 하루도 화이팅! 💪"
    
    message = f"""{advice_text}

📍 서울 | 📅 {formatted_date}

{temp_range}
🌫️ {air_text}

⏰ 시간별 예보
{hourly_text}"""

    kakao_service = KakaoTalkService()
    success = kakao_service.send_me_message(message)
    
    if success:
        logger.info("Weather update sent successfully.")
    else:
        logger.error("Failed to send weather update.")


if __name__ == "__main__":
    main()
