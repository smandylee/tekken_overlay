#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

def check_dependencies():
    """필요한 패키지들이 설치되어 있는지 확인"""
    required_packages = [
        'PIL',
        'pytesseract', 
        'cv2',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 설치됨")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 설치 필요")
    
    if missing_packages:
        print(f"\n설치가 필요한 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print("python3 -m pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """필요한 디렉토리들 생성"""
    directories = ['combo_images', 'dist', 'build']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 {directory} 폴더 생성됨")

def build_exe():
    """exe 파일 빌드"""
    print("\n🔨 exe 파일 빌드 시작...")
    
    # PyInstaller 명령어 실행
    cmd = [
        'pyinstaller',
        '--onefile',           # 단일 exe 파일
        '--windowed',          # GUI 앱 (콘솔 창 숨김)
        '--name=Tekken8_Combo_Overlay',
        '--add-data=character_data:character_data',
        '--add-data=combo_images:combo_images',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageTk',
        '--hidden-import=PIL.ImageGrab',
        '--hidden-import=PIL.ImageEnhance',
        '--hidden-import=pytesseract',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        'starter_based_overlay.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ exe 빌드 성공!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        print(f"에러 출력: {e.stderr}")
        return False

def cleanup():
    """임시 파일들 정리"""
    print("\n🧹 임시 파일 정리 중...")
    
    # build 폴더 삭제
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("📁 build 폴더 삭제됨")
    
    # .spec 파일 삭제 (자동 생성된 것)
    spec_file = 'starter_based_overlay.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"🗑️ {spec_file} 삭제됨")

def main():
    print("🎮 Tekken 8 Combo Overlay - exe 빌더")
    print("=" * 50)
    
    # 1. 의존성 확인
    if not check_dependencies():
        return
    
    # 2. 디렉토리 생성
    create_directories()
    
    # 3. exe 빌드
    if build_exe():
        print("\n🎉 빌드 완료!")
        print("📁 dist/Tekken8_Combo_Overlay.exe 파일이 생성되었습니다.")
        print("\n💡 사용 방법:")
        print("1. dist 폴더의 exe 파일을 실행")
        print("2. combo_images 폴더에 콤보 이미지들 추가")
        print("3. 게임 실행 후 오버레이 사용")
    else:
        print("\n❌ 빌드 실패!")
    
    # 4. 정리
    cleanup()

if __name__ == "__main__":
    main() 