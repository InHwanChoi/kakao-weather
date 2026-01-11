# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python application that fetches weather forecasts from the Korea Meteorological Administration (KMA) API and sends daily weather notifications to the user via KakaoTalk.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application (sends weather notification)
python main.py

# Initial Kakao authentication (run once to get tokens)
python auth_helper.py

# Test weather API separately
python weather.py

# Test KakaoTalk service separately
python kakao_service.py
```

## Architecture

**main.py** - Entry point that orchestrates weather fetching and KakaoTalk messaging.

**weather.py** - `WeatherService` class that calls the KMA VilageFcst (동네예보) API. Uses grid coordinates (nx, ny) for location - default is Seoul (60, 127). Parses forecast categories: TMP (temp), SKY (sky condition), PTY (precipitation type), POP (precipitation probability), REH (humidity).

**kakao_service.py** - `KakaoTalkService` class that sends messages via Kakao Talk Memo API. Handles OAuth token refresh automatically when access token expires. Tokens are stored in `kakao_tokens.json`.

**auth_helper.py** - One-time helper to exchange Kakao OAuth authorization code for access/refresh tokens.

## Environment Variables

Required in `.env` file (see `.env.example`):
- `KMA_SERVICE_KEY` - API key from data.go.kr for weather API
- `KAKAO_REST_API_KEY` - Kakao REST API key from developers.kakao.com
- `KAKAO_CLIENT_SECRET` - Kakao client secret (optional but recommended)
- `KAKAO_REDIRECT_URI` - OAuth redirect URI (default: https://localhost.com)

## Token Management

Kakao OAuth tokens are stored in `kakao_tokens.json` (not committed to repo). First-time setup requires:
1. Get authorization code from Kakao OAuth URL
2. Run `python auth_helper.py` and paste the code
3. Tokens will be saved and auto-refreshed on subsequent runs
