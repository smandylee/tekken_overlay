#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageGrab
import threading
import time
import json
import os
import sys
import win32gui
import win32con
import win32api
import win32process
from ctypes import *
from ctypes.wintypes import *

# character_data 패키지에서 콤보 로더 import
sys.path.append('.')
from character_data.combo_loader import combo_loader

class DirectXOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("철권8 DirectX 오버레이")
        self.root.geometry("400x300")
        
        # 오버레이 관련 변수들
        self.overlay_window = None
        self.game_hwnd = None
        self.current_character = None
        self.current_starter = None
        self.selected_combo = None
        
        # DirectX 오버레이 관련
        self.overlay_active = False
        self.overlay_thread = None
        
        # 콤보 로더 초기화
        self.combo_loader = combo_loader
        
        # UI 구성
        self.setup_ui()
        
    def setup_ui(self):
        """메인 UI 구성"""
        main_frame = tk.Frame(self.root, bg='#2C2C2C')
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="철권8 DirectX 오버레이", 
                              font=('Arial', 16, 'bold'), 
                              fg='#FFFFFF', bg='#2C2C2C')
        title_label.pack(pady=(10, 20))
        
        # 게임 감지 프레임
        game_frame = tk.Frame(main_frame, bg='#2C2C2C')
        game_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(game_frame, text="게임 감지:", 
                font=('Arial', 12), fg='#FFFFFF', bg='#2C2C2C').pack(side='left')
        
        self.game_status_label = tk.Label(game_frame, text="TEKKEN 8 감지 안됨", 
                                         font=('Arial', 10), fg='#FF0000', bg='#2C2C2C')
        self.game_status_label.pack(side='right', padx=10)
        
        # 오버레이 제어 프레임
        overlay_frame = tk.Frame(main_frame, bg='#2C2C2C')
        overlay_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(overlay_frame, text="오버레이:", 
                font=('Arial', 12), fg='#FFFFFF', bg='#2C2C2C').pack(side='left')
        
        self.overlay_btn = tk.Button(overlay_frame, text="오버레이 시작", 
                                    command=self.toggle_overlay,
                                    bg='#4A4A4A', fg='#FFFFFF')
        self.overlay_btn.pack(side='left', padx=10)
        
        # 캐릭터 선택 프레임
        char_frame = tk.Frame(main_frame, bg='#2C2C2C')
        char_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(char_frame, text="캐릭터:", 
                font=('Arial', 12), fg='#FFFFFF', bg='#2C2C2C').pack(side='left')
        
        # 캐릭터 선택 콤보박스
        self.char_var = tk.StringVar()
        available_characters = self.combo_loader.get_all_characters()
        char_combo = ttk.Combobox(char_frame, textvariable=self.char_var, 
                                  values=available_characters,
                                  state='readonly', width=15)
        char_combo.pack(side='left', padx=10)
        char_combo.bind('<<ComboboxSelected>>', self.on_character_selected)
        
        # 시동기 선택 프레임
        starter_frame = tk.Frame(main_frame, bg='#2C2C2C')
        starter_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(starter_frame, text="시동기:", 
                font=('Arial', 12), fg='#FFFFFF', bg='#2C2C2C').pack(side='left')
        
        # 시동기 선택 콤보박스
        self.starter_var = tk.StringVar()
        self.starter_combo = ttk.Combobox(starter_frame, textvariable=self.starter_var, 
                                     state='readonly', width=15)
        self.starter_combo.pack(side='left', padx=10)
        self.starter_combo.bind('<<ComboboxSelected>>', self.on_starter_selected)
        
        # 콤보 선택 프레임
        combo_frame = tk.Frame(main_frame, bg='#2C2C2C')
        combo_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(combo_frame, text="콤보:", 
                font=('Arial', 12), fg='#FFFFFF', bg='#2C2C2C').pack(side='left')
        
        # 콤보 선택 콤보박스
        self.combo_var = tk.StringVar()
        self.combo_combo = ttk.Combobox(combo_frame, textvariable=self.combo_var, 
                                   state='readonly', width=15)
        self.combo_combo.pack(side='left', padx=10)
        self.combo_combo.bind('<<ComboboxSelected>>', self.on_combo_selected)
        
        # 하단 버튼들
        button_frame = tk.Frame(main_frame, bg='#2C2C2C')
        button_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(button_frame, text="게임 감지", 
                 command=self.detect_game,
                 bg='#4A4A4A', fg='#FFFFFF').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="종료", 
                 command=self.quit_app,
                 bg='#FF0000', fg='#FFFFFF').pack(side='right', padx=5)
        
        # 게임 감지 시작
        self.detect_game()
        
    def detect_game(self):
        """TEKKEN 8 게임 창 감지"""
        try:
            # 방법 1: 창 제목으로 찾기
            possible_titles = [
                "TEKKEN™8  ",  # 정확한 제목 (끝에 공백 2개)
                "TEKKEN™8",
                "TEKKEN™ 8",
                "TEKKEN 8", 
                "TEKKEN8",
                "TEKKEN 8 - Steam",
                "TEKKEN™ 8 - Steam"
            ]
            
            self.game_hwnd = None
            for title in possible_titles:
                self.game_hwnd = win32gui.FindWindow(None, title)
                if self.game_hwnd:
                    print(f"게임 창 발견 (제목): '{title}'")
                    break
            
            # 방법 2: 프로세스 이름으로 찾기
            if not self.game_hwnd:
                import psutil
                
                def find_window_by_process():
                    def enum_windows_callback(hwnd, result):
                        if win32gui.IsWindowVisible(hwnd):
                            try:
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                process = psutil.Process(pid)
                                if "Polaris-Win64-Shipping.exe".lower() in process.name().lower():
                                    result.append(hwnd)
                            except:
                                pass
                        return True
                    
                    result = []
                    win32gui.EnumWindows(enum_windows_callback, result)
                    return result[0] if result else None
                
                self.game_hwnd = find_window_by_process()
                if self.game_hwnd:
                    print("게임 창 발견 (프로세스): Polaris-Win64-Shipping.exe")
            
            if self.game_hwnd:
                # 게임 창 정보 가져오기
                rect = win32gui.GetWindowRect(self.game_hwnd)
                process_id = win32process.GetWindowThreadProcessId(self.game_hwnd)[1]
                
                self.game_status_label.config(text=f"TEKKEN 8 감지됨 (PID: {process_id})", fg='#00FF00')
                print(f"게임 창 감지: {rect}, PID: {process_id}")
                
                return True
            else:
                self.game_status_label.config(text="TEKKEN 8 감지 안됨", fg='#FF0000')
                print("TEKKEN 8 게임 창을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            print(f"게임 감지 오류: {e}")
            self.game_status_label.config(text="게임 감지 오류", fg='#FF0000')
            return False
    
    def toggle_overlay(self):
        """오버레이 토글"""
        if not self.overlay_active:
            if not self.game_hwnd:
                messagebox.showerror("오류", "TEKKEN 8 게임을 먼저 실행해주세요.")
                return
            
            self.start_overlay()
        else:
            self.stop_overlay()
    
    def start_overlay(self):
        """DirectX 오버레이 시작"""
        try:
            self.overlay_active = True
            self.overlay_btn.config(text="오버레이 중지")
            
            # 오버레이 스레드 시작
            self.overlay_thread = threading.Thread(target=self.overlay_loop, daemon=True)
            self.overlay_thread.start()
            
            print("DirectX 오버레이 시작됨")
            
        except Exception as e:
            print(f"오버레이 시작 오류: {e}")
            messagebox.showerror("오류", f"오버레이 시작 실패: {e}")
    
    def stop_overlay(self):
        """DirectX 오버레이 중지"""
        try:
            self.overlay_active = False
            self.overlay_btn.config(text="오버레이 시작")
            
            if self.overlay_window:
                self.overlay_window.destroy()
                self.overlay_window = None
            
            print("DirectX 오버레이 중지됨")
            
        except Exception as e:
            print(f"오버레이 중지 오류: {e}")
    
    def overlay_loop(self):
        """오버레이 메인 루프"""
        while self.overlay_active:
            try:
                if self.game_hwnd and win32gui.IsWindow(self.game_hwnd):
                    # 게임 창 위치 가져오기
                    rect = win32gui.GetWindowRect(self.game_hwnd)
                    x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                    
                    # 오버레이 창 생성/업데이트
                    self.update_overlay_window(x, y, w, h)
                    
                    # 캐릭터 자동 감지
                    self.detect_character_from_game()
                    
                time.sleep(0.1)  # 100ms 간격
                
            except Exception as e:
                print(f"오버레이 루프 오류: {e}")
                time.sleep(1)
    
    def update_overlay_window(self, x, y, w, h):
        """오버레이 창 업데이트"""
        try:
            if not self.overlay_window:
                # 투명 오버레이 창 생성
                self.overlay_window = tk.Toplevel()
                self.overlay_window.title("철권8 콤보 오버레이")
                # 오버레이 크기를 좌측 프레임 데이터 영역에 맞게 조정
                overlay_width = min(400, w//3)  # 좌측 영역에 맞게 조정
                overlay_height = min(600, h//2)  # 세로로 더 크게
                overlay_x = x + 20  # 좌측에 배치
                overlay_y = y + 100  # 상단에서 약간 아래로
                self.overlay_window.geometry(f"{overlay_width}x{overlay_height}+{overlay_x}+{overlay_y}")
                self.overlay_window.attributes('-alpha', 0.9)  # 투명도 높임
                self.overlay_window.attributes('-topmost', True)  # 항상 위
                self.overlay_window.overrideredirect(True)  # 테두리 없음
                self.overlay_window.configure(bg='black')
                
                # 클릭 통과 설정
                self.overlay_window.attributes('-transparentcolor', 'black')
                
                # 항상 최상위 유지하는 타이머 설정
                self.overlay_window.after(100, self.keep_overlay_on_top)
                
                # 콤보 표시 프레임
                combo_frame = tk.Frame(self.overlay_window, bg='black')
                combo_frame.pack(expand=True, fill='both')
                
                if self.selected_combo:
                    self.display_combo_in_overlay(combo_frame)
                else:
                    # 기본 메시지도 제거 (깔끔하게)
                    pass
            
            else:
                # 창 위치 업데이트
                overlay_width = min(400, w//3)  # 좌측 영역에 맞게 조정
                overlay_height = min(600, h//2)  # 세로로 더 크게
                overlay_x = x + 20  # 좌측에 배치
                overlay_y = y + 100  # 상단에서 약간 아래로
                self.overlay_window.geometry(f"{overlay_width}x{overlay_height}+{overlay_x}+{overlay_y}")
                self.overlay_window.attributes('-topmost', True)  # 항상 최상위 유지
                
        except Exception as e:
            print(f"오버레이 창 업데이트 오류: {e}")
    
    def keep_overlay_on_top(self):
        """오버레이를 항상 최상위로 유지"""
        if self.overlay_window and self.overlay_active:
            try:
                # 게임 창이 활성화되어 있는지 확인
                if self.game_hwnd:
                    active_window = win32gui.GetForegroundWindow()
                    if active_window == self.game_hwnd:
                        # 게임 창이 활성화되면 오버레이를 최상위로
                        self.overlay_window.attributes('-topmost', True)
                        self.overlay_window.lift()
                        self.overlay_window.focus_force()
                
                # 100ms마다 반복
                self.overlay_window.after(100, self.keep_overlay_on_top)
            except:
                pass
    
    def display_combo_in_overlay(self, parent_frame):
        """오버레이에 콤보 표시"""
        try:
            # 기존 위젯 제거
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            # 이미지만 표시 (텍스트 제거)
            self.display_combo_image_in_overlay(parent_frame)
            
        except Exception as e:
            print(f"콤보 표시 오류: {e}")
    
    def display_combo_image_in_overlay(self, parent_frame):
        """오버레이에 콤보 이미지 표시"""
        try:
            combo_name = self.selected_combo['name']
            character_name = self.current_character
            starter_name = self.current_starter
            
            # 이미지 파일 찾기
            possible_filenames = [
                f"{character_name.lower()}_{starter_name.lower()}_{combo_name.lower().replace(' ', '')}.png",
                f"{character_name.lower()}_{combo_name.lower().replace(' ', '_')}.png",
                f"{character_name.lower()}_{starter_name.lower()}_{combo_name.lower().replace(' ', '_')}.png"
            ]
            
            image_path = None
            for filename in possible_filenames:
                temp_path = os.path.join("combo_images", filename)
                if os.path.exists(temp_path):
                    image_path = temp_path
                    break
            
            if image_path:
                # 이미지 로드 및 표시
                image = Image.open(image_path)
                # 좌측 프레임 데이터 영역에 맞게 조정
                image.thumbnail((350, 500), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                img_label = tk.Label(parent_frame, image=photo, bg='black')
                img_label.image = photo
                img_label.pack(expand=True, fill='both')
                
        except Exception as e:
            print(f"이미지 표시 오류: {e}")
    
    def detect_character_from_game(self):
        """게임에서 캐릭터 자동 감지"""
        try:
            if not self.game_hwnd:
                return
            
            # 게임 화면 캡처 (캐릭터 이름 영역)
            # 실제 구현에서는 OCR을 사용하여 캐릭터 이름을 읽어옴
            # 여기서는 간단한 예시만 구현
            
        except Exception as e:
            print(f"캐릭터 감지 오류: {e}")
    
    def on_character_selected(self, event):
        """캐릭터 선택 이벤트"""
        self.current_character = self.char_var.get()
        self.update_starter_list()
    
    def on_starter_selected(self, event):
        """시동기 선택 이벤트"""
        self.current_starter = self.starter_var.get()
        self.update_combo_list()
    
    def on_combo_selected(self, event):
        """콤보 선택 이벤트"""
        combo_name = self.combo_var.get()
        if combo_name:
            combos = self.combo_loader.get_starter_combos(self.current_character, self.current_starter)
            for combo in combos:
                if combo['name'] == combo_name:
                    self.selected_combo = combo
                    break
    
    def update_starter_list(self):
        """시동기 목록 업데이트"""
        if self.current_character:
            starters = self.combo_loader.get_character_starters(self.current_character)
            self.starter_var.set('')
            # ComboBox 위젯 직접 참조
            if hasattr(self, 'starter_combo'):
                self.starter_combo['values'] = starters
                print(f"시동기 목록 업데이트: {starters}")
    
    def update_combo_list(self):
        """콤보 목록 업데이트"""
        if self.current_character and self.current_starter:
            combos = self.combo_loader.get_starter_combos(self.current_character, self.current_starter)
            combo_names = [combo['name'] for combo in combos]
            self.combo_var.set('')
            # ComboBox 위젯 직접 참조
            if hasattr(self, 'combo_combo'):
                self.combo_combo['values'] = combo_names
                print(f"콤보 목록 업데이트: {combo_names}")
    
    def quit_app(self):
        """앱 종료"""
        self.stop_overlay()
        self.root.quit()
    
    def run(self):
        """프로그램 실행"""
        print("DirectX 철권8 콤보 오버레이가 시작되었습니다!")
        print(f"로드된 캐릭터: {', '.join(self.combo_loader.get_all_characters())}")
        self.root.mainloop()

if __name__ == "__main__":
    app = DirectXOverlay()
    app.run() 