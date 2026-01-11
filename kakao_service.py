import requests
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KakaoTalkService:
    def __init__(self):
        self.token_file = "kakao_tokens.json"
        self.rest_api_key = os.getenv("KAKAO_REST_API_KEY")
        self.client_secret = os.getenv("KAKAO_CLIENT_SECRET")
        self.tokens = self._load_tokens()

    def _load_tokens(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                return json.load(f)
        return None

    def _save_tokens(self, tokens):
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)
        self.tokens = tokens

    def refresh_token(self):
        if not self.tokens or "refresh_token" not in self.tokens:
            logger.error("No refresh token available. Manual authentication required.")
            return False

        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": self.tokens["refresh_token"],
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            new_tokens = response.json()
            
            updated_tokens = self.tokens.copy()
            updated_tokens.update(new_tokens)
            self._save_tokens(updated_tokens)
            logger.info("Kakao tokens refreshed successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh Kakao token: {e}")
            return False

    def send_me_message(self, text, web_url="https://www.weather.go.kr"):
        if not self.tokens:
            logger.error("Tokens not found. Please authenticate first.")
            return False

        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {self.tokens['access_token']}"
        }
        
        template_object = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": web_url,
                "mobile_web_url": web_url
            },
            "button_title": "날씨 상세보기"
        }
        
        data = {
            "template_object": json.dumps(template_object)
        }

        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 401:
            logger.info("Access token expired. Attempting refresh...")
            if self.refresh_token():
                headers["Authorization"] = f"Bearer {self.tokens['access_token']}"
                response = requests.post(url, headers=headers, data=data)
            else:
                return False

        if response.status_code == 200:
            logger.info("Message sent successfully.")
            return True
        else:
            logger.error(f"Failed to send message: {response.text}")
            return False

if __name__ == "__main__":
    service = KakaoTalkService()
    if service.tokens:
        service.send_me_message("테스트 메시지입니다.")
    else:
        print("토큰 파일(kakao_tokens.json)이 없습니다.")
