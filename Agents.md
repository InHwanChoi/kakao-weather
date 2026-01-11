# Agents.md

This file provides guidance to AI agents when working with code in this repository.

## Session Start Instructions

**CRITICAL**: All git operations, documentation writing, and UI changes MUST be delegated to the appropriate agent. Do NOT do these directly.

- Git (init, commit, push, PR) → delegate to `general`
- README, guides, docs → delegate to `document-writer`
- .tsx, .css, styling → delegate to `frontend-ui-ux-engineer`

## Project Overview

A Python application that fetches weather forecasts and air quality data, then sends personalized daily notifications via KakaoTalk with smart clothing recommendations based on temperature and gender.

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

# Test air quality API separately
python air_quality.py

# Test KakaoTalk service separately
python kakao_service.py
```

## Architecture

**main.py** - Entry point that orchestrates all services. Contains `SmartWeatherAdvisor` class that generates personalized advice including outfit recommendations, seasonal items, and weather warnings.

**weather.py** - `WeatherService` class that calls the KMA VilageFcst (동네예보) API. Returns hourly forecasts for today and tomorrow with temperature, sky condition, precipitation info.

**air_quality.py** - `AirQualityService` class that calls the AirKorea API. Returns PM10/PM2.5 levels with grade (좋음/보통/나쁨/매우나쁨).

**kakao_service.py** - `KakaoTalkService` class that sends messages via Kakao Talk Memo API. Handles OAuth token refresh automatically.

**auth_helper.py** - One-time helper to exchange Kakao OAuth authorization code for access/refresh tokens.

## Features

- **Hourly Forecast**: Shows next 8 hours with temperature, sky condition, rain probability
- **Air Quality**: PM10/PM2.5 levels with emoji indicators
- **Smart Outfit Advice**: Gender-specific clothing recommendations by temperature
- **Seasonal Items**: Suggests hand warmers, scarves, sunscreen based on weather
- **Weather Alerts**: Umbrella reminders, temperature difference warnings, car wash advice

## Environment Variables

Required in `.env` file:
- `KMA_SERVICE_KEY` - API key from data.go.kr for weather API
- `AIRKOREA_SERVICE_KEY` - API key from data.go.kr for air quality API
- `KAKAO_REST_API_KEY` - Kakao REST API key from developers.kakao.com
- `KAKAO_CLIENT_SECRET` - Kakao client secret (optional but recommended)
- `KAKAO_REDIRECT_URI` - OAuth redirect URI (default: https://localhost.com)
- `GENDER` - User gender for outfit recommendations (`male` or `female`)

## Temperature-based Outfit Logic

| Temperature | Category | Male Outfit | Female Outfit |
|-------------|----------|-------------|---------------|
| ≤ -5°C | freezing | 히트텍+니트+롱패딩, 기모바지 | 히트텍+니트+롱패딩, 기모레깅스 |
| -4 ~ 4°C | very_cold | 히트텍+맨투맨+패딩, 기모바지 | 터틀넥+패딩, 기모스커트+타이츠 |
| 5 ~ 9°C | cold | 니트+코트, 슬랙스 | 니트+롱코트, 슬랙스 |
| 10 ~ 16°C | chilly | 셔츠+트렌치코트, 면바지 | 블라우스+트렌치코트, 와이드팬츠 |
| 17 ~ 19°C | cool | 가디건+셔츠, 슬랙스 | 가디건+원피스, 얇은 스타킹 |
| 20 ~ 22°C | mild | 긴팔 셔츠, 면바지 | 긴팔 블라우스, 면바지 |
| 23 ~ 27°C | warm | 반팔+얇은 셔츠, 면바지 | 반팔 블라우스, 린넨팬츠 |
| ≥ 28°C | hot | 반팔, 반바지 | 민소매, 반바지 |

## Seasonal Items

- **freezing**: 손난로, 핫팩
- **very_cold**: 목도리, 장갑
- **cold**: 장갑
- **hot**: 선크림, 물

## Token Management

Kakao OAuth tokens are stored in `kakao_tokens.json` (not committed to repo). First-time setup:
1. Get authorization code from Kakao OAuth URL
2. Run `python auth_helper.py` and paste the code
3. Tokens will be saved and auto-refreshed on subsequent runs

## Agent Delegation Rules

### Mandatory Delegation (Sisyphus must NOT do directly)

| Task Type | Delegate To | Trigger |
|-----------|-------------|---------|
| Git operations (init, commit, push, PR) | `general` | 3+ git commands needed |
| Frontend UI/Styling | `frontend-ui-ux-engineer` | .tsx, .css, style changes |
| Documentation | `document-writer` | README, guides, docs |
| External library research | `librarian` | Unfamiliar packages |
| Codebase exploration | `explore` | 2+ modules involved |

### Delegation Prompt Structure (Required)

When delegating, include ALL 7 sections:

```
1. TASK: Atomic, specific goal
2. EXPECTED OUTCOME: Concrete deliverables
3. REQUIRED SKILLS: Which skill to invoke
4. REQUIRED TOOLS: Explicit tool whitelist
5. MUST DO: Exhaustive requirements
6. MUST NOT DO: Forbidden actions
7. CONTEXT: File paths, patterns, constraints
```

### After Delegation

Always verify results:
- Does it work as expected?
- Follows existing codebase patterns?
- Agent followed MUST DO / MUST NOT DO?

## Future Enhancements

- [ ] Chatbot mode with location sharing
- [ ] Multiple location support (home/office)
- [ ] Character images for outfit visualization
- [ ] Time-based location switching (morning: home, afternoon: office)
- [ ] Ultra-short-term precipitation alerts (radar-based)
