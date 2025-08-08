# 자동 로그인 스크립트

파이썬 셀레니움 기반 자동화 스크립트입니다.

otp 인증 포함해 특정 페이지 접근 후 특정 버튼을 주기적으로 누르는 게 끝

보안이 필요한 데이터는 env로 관리.

## 요구 사항

- Python 3
- Chrome
- Google Authenticator

## 사용법

1. 환경 변수 설정

- `.env.sample` -> `.env` 이름 변경
- 필요한 환경 변수 입력
- 여기서 `OTP_SECRET`는 우선 공란으로 둡니다.

2. `OTP_SECRET` 설정

- 이미 Secret Key를 가지고 있는 경우
  - 해당 Secret Key를 `.env` 파일의 `OTP_SECRET`에 입력합니다.
- Secret Key를 모르는 경우
  - Google Authenticator 앱에서 "내보내기"로 QR을 생성
  - QR 내 텍스트 추출 시 다음과 같은 형식이 됩니다. `otpauth-migration://offline?data={ ... }`
  - 이 텍스트를 `.env` 파일의 `OTP_SECRET`에 입력하면, Secret Key를 자동으로 추출합니다.

3. 스크립트 실행

```bash
# 자동으로 venv를 생성하고 requirements.txt에 있는 패키지 설치하여 실행하므로 별도의 사전 설치 과정이 필요 없습니다.
./run.sh
```
