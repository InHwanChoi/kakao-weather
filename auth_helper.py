import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_initial_tokens(auth_code):
    url = "https://kauth.kakao.com/oauth/token"
    client_id = os.getenv("KAKAO_REST_API_KEY")
    client_secret = os.getenv("KAKAO_CLIENT_SECRET")
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI", "https://localhost.com")

    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": auth_code,
    }
    if client_secret:
        data["client_secret"] = client_secret

    response = requests.post(url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        with open("kakao_tokens.json", "w") as f:
            json.dump(tokens, f)
        print("Tokens saved to kakao_tokens.json")
        return tokens
    else:
        print(f"Failed to get tokens: {response.text}")
        return None

if __name__ == "__main__":
    code = input("Enter the authorization code: ")
    get_initial_tokens(code)
