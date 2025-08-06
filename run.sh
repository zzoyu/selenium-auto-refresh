#!/bin/bash

# 가상 환경 폴더 이름
VENV_DIR="venv"

# 파이썬 가상 환경 생성 및 활성화
if [ ! -d "$VENV_DIR" ]; then
    echo "가상 환경을 생성합니다..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "오류: 가상 환경을 생성하지 못했습니다. python3가 설치되어 있는지 확인하세요."
        exit 1
    fi
fi

# 가상 환경 활성화
source $VENV_DIR/bin/activate

# 필요한 패키지 설치
echo "필요한 패키지를 설치합니다..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "오류: 패키지를 설치하지 못했습니다."
    deactivate
    exit 1
fi

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "오류: .env 파일이 없습니다. USERNAME과 PASSWORD를 포함한 .env 파일을 생성해주세요."
    deactivate
    exit 1
fi

# 메인 파이썬 스크립트 실행
echo "자동 새로고침 스크립트를 시작합니다..."
python main.py

# 가상 환경 비활성화
deactivate
echo "스크립트가 종료되었습니다."
