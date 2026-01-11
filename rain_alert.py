#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from ultra_short_forecast import UltraShortForecastService
from kakao_service import KakaoTalkService

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALERT_STATE_FILE = "rain_alert_state.json"


def load_alert_state():
    if os.path.exists(ALERT_STATE_FILE):
        with open(ALERT_STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_alert_time": None, "last_alert_type": None}


def save_alert_state(state):
    with open(ALERT_STATE_FILE, "w") as f:
        json.dump(state, f)


def should_send_alert(rain_info, state):
    if not state.get("last_alert_time"):
        return True
    
    last_alert = datetime.fromisoformat(state["last_alert_time"])
    now = datetime.now()
    
    hours_since_last = (now - last_alert).total_seconds() / 3600
    if hours_since_last >= 3:
        return True
    
    if state.get("last_alert_type") != rain_info["type"]:
        return True
    
    return False


def format_rain_alert(rain_info):
    rain_type = rain_info["type"]
    minutes = rain_info["minutes_until"]
    
    if rain_type == "눈":
        emoji = "🌨️"
    elif rain_type in ("비/눈", "빗방울눈날림"):
        emoji = "🌨️"
    else:
        emoji = "🌧️"
    
    if minutes <= 10:
        time_text = "곧"
    elif minutes <= 30:
        time_text = f"{minutes}분 후"
    else:
        time_text = f"약 {minutes // 10 * 10}분 후"
    
    message = f"{emoji} {time_text} {rain_type} 올 예정! 우산 챙겨!"
    
    if rain_info.get("temp"):
        message += f"\n🌡️ 현재 기온: {rain_info['temp']}°C"
    
    return message


def check_and_alert(nx=60, ny=127):
    forecast_service = UltraShortForecastService()
    rain_info = forecast_service.check_upcoming_rain(nx, ny, within_minutes=60)
    
    if not rain_info:
        logger.info("No rain detected in the next hour.")
        return False
    
    state = load_alert_state()
    
    if not should_send_alert(rain_info, state):
        logger.info(f"Rain detected ({rain_info['type']}) but alert was sent recently. Skipping.")
        return False
    
    message = format_rain_alert(rain_info)
    logger.info(f"Sending rain alert: {message}")
    
    kakao_service = KakaoTalkService()
    success = kakao_service.send_me_message(message)
    
    if success:
        state["last_alert_time"] = datetime.now().isoformat()
        state["last_alert_type"] = rain_info["type"]
        save_alert_state(state)
        logger.info("Rain alert sent successfully.")
        return True
    else:
        logger.error("Failed to send rain alert.")
        return False


if __name__ == "__main__":
    check_and_alert()
