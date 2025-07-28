# 🎮 Tekken 8 Combo Overlay

철권 8 게임 중 콤보 루트를 실시간으로 오버레이해주는 프로그램입니다.

## ✨ 주요 기능

- **자동 캐릭터 인식**: 화면에서 선택된 캐릭터를 자동으로 감지
- **REFramework 스타일 UI**: 게임 오버레이에 최적화된 디자인
- **이미지 기반 콤보 표시**: 사용자가 만든 콤보 이미지 표시
- **3단계 콤보 선택**: 캐릭터 → 시동기 → 콤보
- **실시간 오버레이**: 항상 위에 표시되는 투명 오버레이

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
python3 -m pip install -r requirements.txt
```

### 2. 실행
```bash
python3 starter_based_overlay.py
```

## 📦 exe 파일 생성

### 자동 빌드 (권장)
```bash
python3 build_exe.py
```

### 수동 빌드
```bash
pyinstaller tekken_overlay.spec
```

## 📁 폴더 구조

```
TEKKEN OVERLAY/
├── starter_based_overlay.py    # 메인 프로그램
├── character_data/             # 캐릭터별 콤보 데이터
│   ├── jin_combos.json
│   ├── kazuya_combos.json
│   └── ...
├── combo_images/              # 콤보 이미지들
│   ├── jin_easy_1.png
│   ├── kazuya_medium_1.png
│   └── ...
├── build_exe.py              # exe 빌드 스크립트
├── requirements.txt           # 필요한 패키지 목록
└── README.md                 # 이 파일
```

## 🖼️ 콤보 이미지 설정

### 이미지 파일 명명 규칙
- 형식: `캐릭터명_콤보명.png`
- 예시: `jin_easy_1.png`, `kazuya_medium_1.png`

### 지원하는 이미지 형식
- PNG, JPG, JPEG, GIF 등

### 이미지 크기 권장사항
- 최대 600x400 픽셀
- 자동으로 크기 조정됨

## 🎯 사용 방법

1. **프로그램 실행**
2. **자동 캐릭터 인식 활성화** (선택사항)
3. **게임에서 캐릭터 선택**
4. **콤보 선택** → 오버레이 창에서 콤보 확인
5. **게임 플레이 중 참조**

## 🔧 설정

### 자동 캐릭터 인식 영역
- 기본: 화면 좌상단 (50, 50, 300, 150)
- 게임 내 캐릭터 이름 표시 위치

### 오버레이 설정
- 투명도: 95%
- 항상 위에 표시
- 클릭 통과 가능

## 📋 지원 캐릭터

철권 8의 모든 캐릭터를 지원합니다:
- Jin, Kazuya, Jun, Paul, Law, King
- Hwoarang, Steve, Lee, Anna, Nina, Eddy
- Yoshimitsu, Kuma, Panda, Devil Jin, Lars
- Leo, Reina, Raven, Leroy, Lili, Xiaoyu
- Marshall Law, Victor, Bryan, Shaheen, Dragunov
- Azucena, Asuka, Alisa, Zafina, Jack-8
- Claudio, Feng, Lidia, Heihachi, Clive, Fahkumram

## 🛠️ 개발 환경

- Python 3.9+
- macOS (현재 개발 환경)
- Windows 호환 가능

## 📝 라이선스

개인 사용 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 언제든 환영합니다! 