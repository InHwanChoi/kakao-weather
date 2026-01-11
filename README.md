# 카카오 날씨 알림 (Kakao Weather)

매일 아침 카카오톡으로 맞춤형 날씨 알림을 받아보세요.

## 🌟 주요 기능

- **시간별 예보**: 현재 시간부터 8시간 동안의 기온, 하늘 상태, 강수 확률
- **미세먼지 정보**: PM10/PM2.5 농도 및 등급 (좋음/보통/나쁨/매우나쁨)
- **스마트 코디 추천**: 기온과 성별에 맞는 의상 제안
- **계절 용품 알림**: 손난로, 목도리, 선크림 등 필요한 용품 안내
- **날씨 경고**: 우산 챙기기, 일교차 주의, 세차 금지 등

## 📱 메시지 예시

```
👔 오늘 코디: 히트텍 + 니트 + 롱패딩, 기모바지
🔥 손난로 챙기고 핫팩 붙여!
공기 좋아! 환기하기 좋은 날 🌬️

📍 서울 | 📅 01월 11일

🌡️ 최저 -8°C / 최고 -4°C
🌫️ 미세먼지 24㎍/㎥ 좋음😊 | 초미세 9㎍/㎥ 좋음😊

⏰ 시간별 예보
오전 11시 ☀️ -6°C
오후 12시 ☀️ -6°C
오후 1시 ☀️ -5°C
...
```

---

## 🚀 설치 및 설정

### 1단계: 프로젝트 클론

```bash
git clone https://github.com/InHwanChoi/kakao-weather.git
cd kakao-weather
```

### 2단계: 가상환경 생성 및 의존성 설치

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3단계: API 키 발급

#### 기상청 API (필수)
1. [data.go.kr](https://www.data.go.kr) 접속 및 회원가입
2. "기상청_단기예보 조회서비스" 검색 → 활용 신청
3. 마이페이지에서 API 키 확인

#### 에어코리아 API (필수)
1. [data.go.kr](https://www.data.go.kr) 접속
2. "한국환경공단_에어코리아_대기오염정보" 검색 → 활용 신청
3. 마이페이지에서 API 키 확인

#### 카카오 API (필수)
1. [developers.kakao.com](https://developers.kakao.com) 접속 및 로그인
2. 내 애플리케이션 → 애플리케이션 추가
3. 앱 키 → REST API 키 복사
4. 카카오 로그인 → 활성화 설정 ON
5. 동의항목 → talk_message 활성화
6. 플랫폼 → Web → 사이트 도메인에 `https://localhost.com` 추가
7. 카카오 로그인 → Redirect URI에 `https://localhost.com` 추가

### 4단계: 환경 변수 설정

`.env` 파일 생성:

```bash
# 기상청 API
KMA_SERVICE_KEY=발급받은_기상청_API_키

# 에어코리아 API
AIRKOREA_SERVICE_KEY=발급받은_에어코리아_API_키

# 카카오 API
KAKAO_REST_API_KEY=발급받은_REST_API_키
KAKAO_CLIENT_SECRET=발급받은_Client_Secret  # 선택사항
KAKAO_REDIRECT_URI=https://localhost.com

# 사용자 설정
GENDER=male  # 또는 female
```

### 5단계: 카카오 인증 (최초 1회)

```bash
python auth_helper.py
```

1. 출력되는 URL을 브라우저에서 열기
2. 카카오 로그인 및 동의
3. 리다이렉트된 URL에서 `code=` 뒤의 값 복사
4. 터미널에 붙여넣기

성공하면 `kakao_tokens.json` 파일이 생성됩니다.

### 6단계: 실행

```bash
python main.py
```

카카오톡에서 메시지를 확인하세요!

---

## ⏰ 자동화 (선택)

### macOS (launchd)

`~/Library/LaunchAgents/com.kakao.weather.plist` 생성:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kakao.weather</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/kakao-weather/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>/path/to/kakao-weather</string>
</dict>
</plist>
```

등록:
```bash
launchctl load ~/Library/LaunchAgents/com.kakao.weather.plist
```

### Linux (cron)

```bash
crontab -e
```

추가:
```
0 7 * * * cd /path/to/kakao-weather && /path/to/venv/bin/python main.py
```

### Windows (작업 스케줄러)

1. 작업 스케줄러 열기
2. 기본 작업 만들기
3. 트리거: 매일 오전 7시
4. 동작: 프로그램 시작
   - 프로그램: `C:\path\to\venv\Scripts\python.exe`
   - 인수: `main.py`
   - 시작 위치: `C:\path\to\kakao-weather`

---

## 📁 프로젝트 구조

```
kakao-weather/
├── main.py              # 메인 앱 (SmartWeatherAdvisor)
├── weather.py           # 기상청 API 서비스
├── air_quality.py       # 에어코리아 API 서비스
├── kakao_service.py     # 카카오톡 메시지 서비스
├── auth_helper.py       # 카카오 OAuth 인증 헬퍼
├── requirements.txt     # Python 의존성
├── .env                 # 환경 변수 (git 제외)
├── kakao_tokens.json    # 카카오 토큰 (git 제외)
├── Agents.md            # AI 에이전트 가이드
├── CLAUDE.md            # Claude 가이드
└── README.md            # 이 문서
```

---

## 🌡️ 기온별 코디 가이드

| 기온 | 카테고리 | 남성 | 여성 |
|------|----------|------|------|
| -5°C 이하 | 한파 | 히트텍+니트+롱패딩, 기모바지 | 히트텍+니트+롱패딩, 기모레깅스 |
| -4 ~ 4°C | 매우 추움 | 히트텍+맨투맨+패딩, 기모바지 | 터틀넥+패딩, 기모스커트+타이츠 |
| 5 ~ 9°C | 추움 | 니트+코트, 슬랙스 | 니트+롱코트, 슬랙스 |
| 10 ~ 16°C | 쌀쌀 | 셔츠+트렌치코트, 면바지 | 블라우스+트렌치코트, 와이드팬츠 |
| 17 ~ 19°C | 선선 | 가디건+셔츠, 슬랙스 | 가디건+원피스, 얇은 스타킹 |
| 20 ~ 22°C | 따뜻 | 긴팔 셔츠, 면바지 | 긴팔 블라우스, 면바지 |
| 23 ~ 27°C | 더움 | 반팔+얇은 셔츠, 면바지 | 반팔 블라우스, 린넨팬츠 |
| 28°C 이상 | 무더위 | 반팔, 반바지 | 민소매, 반바지 |

---

## 🎒 계절 용품 안내

| 기온 | 추천 용품 |
|------|----------|
| -5°C 이하 | 🔥 손난로, 핫팩 |
| -4 ~ 4°C | 🧣 목도리, 장갑 |
| 5 ~ 9°C | 🧤 장갑 |
| 28°C 이상 | 🧴 선크림, 물 |

---

## 🔧 트러블슈팅

### 토큰 만료 오류
```
Access token expired. Attempting refresh...
```
→ 정상입니다. 자동으로 갱신됩니다.

### Refresh token 만료
```
No refresh token available. Manual authentication required.
```
→ `kakao_tokens.json` 삭제 후 `python auth_helper.py` 다시 실행

### API 키 오류
```
KMA_SERVICE_KEY is missing.
```
→ `.env` 파일에 API 키가 올바르게 설정되었는지 확인

### 측정소 데이터 없음
```
No air quality data found for station
```
→ `air_quality.py`의 `STATION_MAP`에 해당 지역 측정소 추가

---

## 🚧 향후 계획

- [ ] 챗봇 모드 (위치 공유 기반)
- [ ] 다중 위치 지원 (집/회사)
- [ ] 캐릭터 이미지 코디 표시
- [ ] 시간대별 위치 자동 전환

---

## 📄 라이선스

MIT License
