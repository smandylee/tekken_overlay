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
import pytesseract
from PIL import Image, ImageEnhance

# character_data 패키지에서 콤보 로더 import
sys.path.append('.')
from character_data.combo_loader import combo_loader

class StarterBasedOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("철권8 시동기별 콤보 오버레이")
        self.root.geometry("600x700")
        
        # 오버레이 관련 변수들
        self.menu_overlay = None
        self.combo_overlay = None
        self.current_character = None
        self.current_starter = None
        self.selected_combo = None
        
        # 자동 인식 관련 변수들
        self.auto_detection_active = False
        self.detection_thread = None
        self.detection_interval = 2.0  # 2초마다 감지
        
        # REFramework 스타일 설정
        self.bg_color = "#2C2C2C"
        self.text_color = "#FFFFFF"
        self.accent_color = "#4A4A4A"
        self.check_color = "#00FF00"
        
        # 콤보 로더 초기화
        self.combo_loader = combo_loader
        
        # UI 구성
        self.setup_ui()
        
    def setup_ui(self):
        """메인 UI 구성"""
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="철권8 시동기별 콤보 오버레이", 
                              font=('Arial', 16, 'bold'), 
                              fg=self.text_color, bg=self.bg_color)
        title_label.pack(pady=(10, 20))
        
        # 자동 인식 프레임
        auto_frame = tk.Frame(main_frame, bg=self.bg_color)
        auto_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(auto_frame, text="자동 캐릭터 인식:", 
                font=('Arial', 12), fg=self.text_color, bg=self.bg_color).pack(side='left')
        
        # 자동 인식 토글 버튼
        self.auto_detection_var = tk.BooleanVar()
        self.auto_detection_btn = tk.Button(auto_frame, text="자동 인식 시작", 
                                           command=self.toggle_auto_detection,
                                           bg='#4A4A4A', fg=self.text_color)
        self.auto_detection_btn.pack(side='left', padx=10)
        
        # 현재 감지된 캐릭터 표시
        self.detected_char_label = tk.Label(auto_frame, text="감지된 캐릭터: 없음", 
                                           font=('Arial', 10), fg='#FF0000', bg=self.bg_color)
        self.detected_char_label.pack(side='right', padx=10)
        
        # 캐릭터 선택 프레임
        char_frame = tk.Frame(main_frame, bg=self.bg_color)
        char_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(char_frame, text="수동 캐릭터 선택:", 
                font=('Arial', 12), fg=self.text_color, bg=self.bg_color).pack(side='left')
        
        # 캐릭터 선택 콤보박스
        self.char_var = tk.StringVar()
        available_characters = self.combo_loader.get_all_characters()
        char_combo = ttk.Combobox(char_frame, textvariable=self.char_var, 
                                  values=available_characters,
                                  state='readonly', width=15)
        char_combo.pack(side='left', padx=10)
        char_combo.bind('<<ComboboxSelected>>', self.on_character_selected)
        
        # 시동기 선택 프레임
        starter_frame = tk.Frame(main_frame, bg=self.bg_color)
        starter_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(starter_frame, text="시동기 선택:", 
                font=('Arial', 12), fg=self.text_color, bg=self.bg_color).pack(side='left')
        
        # 시동기 선택 콤보박스
        self.starter_var = tk.StringVar()
        self.starter_combo = ttk.Combobox(starter_frame, textvariable=self.starter_var,
                                         state='readonly', width=15)
        self.starter_combo.pack(side='left', padx=10)
        self.starter_combo.bind('<<ComboboxSelected>>', self.on_starter_selected)
        
        # 콤보 리스트 프레임
        combo_frame = tk.Frame(main_frame, bg=self.bg_color)
        combo_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(combo_frame, text="콤보 리스트:", 
                font=('Arial', 12), fg=self.text_color, bg=self.bg_color).pack(anchor='w')
        
        # 콤보 리스트박스
        self.combo_listbox = tk.Listbox(combo_frame, bg=self.accent_color, fg=self.text_color, 
                                       font=('Arial', 10), height=8)
        self.combo_listbox.pack(fill='both', expand=True, pady=5)
        self.combo_listbox.bind('<<ListboxSelect>>', self.on_combo_selected)
        
        # 난이도 필터 프레임
        filter_frame = tk.Frame(main_frame, bg=self.bg_color)
        filter_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(filter_frame, text="난이도 필터:", 
                font=('Arial', 10), fg=self.text_color, bg=self.bg_color).pack(side='left')
        
        self.difficulty_var = tk.StringVar(value="all")
        difficulty_combo = ttk.Combobox(filter_frame, textvariable=self.difficulty_var,
                                       values=["all", "easy", "medium", "hard"],
                                       state='readonly', width=10)
        difficulty_combo.pack(side='left', padx=10)
        difficulty_combo.bind('<<ComboboxSelected>>', self.on_difficulty_filter)
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        # 컨트롤 버튼들
        tk.Button(button_frame, text="REFramework 스타일 메뉴", 
                 command=self.create_reframework_style_menu,
                 bg='#4A4A4A', fg=self.text_color).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="콤보 오버레이", 
                 command=self.create_combo_overlay,
                 bg='#4A4A4A', fg=self.text_color).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="종료", 
                 command=self.quit_app,
                 bg='#8B0000', fg=self.text_color).pack(side='right', padx=5)
        
        # 상태 표시
        self.status_label = tk.Label(main_frame, text="상태: 대기중", 
                                    font=('Arial', 10), 
                                    fg='#00FF00', bg=self.bg_color)
        self.status_label.pack(pady=10)
    
    def toggle_auto_detection(self):
        """자동 인식 토글"""
        if not self.auto_detection_active:
            self.start_auto_detection()
        else:
            self.stop_auto_detection()
    
    def start_auto_detection(self):
        """자동 인식 시작"""
        self.auto_detection_active = True
        self.auto_detection_btn.config(text="자동 인식 중지", bg='#8B0000')
        self.status_label.config(text="상태: 자동 인식 시작됨", fg='#00FF00')
        
        # 별도 스레드에서 감지 시작
        self.detection_thread = threading.Thread(target=self.character_detection_loop, daemon=True)
        self.detection_thread.start()
        
        messagebox.showinfo("자동 인식", "자동 캐릭터 인식이 시작되었습니다!\n인게임에서 왼쪽 위에 표시되는 캐릭터 이름을 인식합니다.")
    
    def stop_auto_detection(self):
        """자동 인식 중지"""
        self.auto_detection_active = False
        self.auto_detection_btn.config(text="자동 인식 시작", bg='#4A4A4A')
        self.status_label.config(text="상태: 자동 인식 중지됨", fg='#FF0000')
        self.detected_char_label.config(text="감지된 캐릭터: 없음", fg='#FF0000')
    
    def character_detection_loop(self):
        """캐릭터 감지 루프"""
        while self.auto_detection_active:
            try:
                detected_char = self.detect_character_from_screen()
                if detected_char and detected_char != self.current_character:
                    # UI 업데이트는 메인 스레드에서 실행
                    self.root.after(0, self.update_detected_character, detected_char)
                
                time.sleep(self.detection_interval)
            except Exception as e:
                print(f"감지 오류: {e}")
                time.sleep(self.detection_interval)
    
    def detect_character_from_screen(self):
        """화면에서 캐릭터 감지"""
        try:
            # 전체 화면 캡처
            screen = ImageGrab.grab()
            screen_width, screen_height = screen.size
            
            # 인게임에서 왼쪽 위에 뜨는 캐릭터 이름 영역 캡처
            # 왼쪽 위 모서리 부분 (캐릭터 이름이 표시되는 위치)
            char_name_area = screen.crop((50, 50, 300, 150))  # 왼쪽 위 영역
            
            # 이미지 전처리
            char_name_area = char_name_area.convert('L')  # 그레이스케일
            enhancer = ImageEnhance.Contrast(char_name_area)
            char_name_area = enhancer.enhance(2.0)  # 대비 증가
            
            # OCR로 텍스트 추출
            text = pytesseract.image_to_string(char_name_area, lang='eng')
            text = text.strip().lower()
            
            print(f"감지된 텍스트: {text}")  # 디버깅용
            
            # 캐릭터 이름 매칭
            detected_char = self.match_character_name(text)
            
            return detected_char
            
        except Exception as e:
            print(f"화면 감지 오류: {e}")
            return None
    
    def match_character_name(self, text):
        """텍스트에서 캐릭터 이름 매칭"""
        # 철권8 캐릭터 이름 매핑 (인게임 표시명 기준)
        character_mappings = {
            'jin': 'Jin',
            'kazuya': 'Kazuya',
            'jun': 'Jun',
            'paul': 'Paul',
            'law': 'Law',
            'king': 'King',
            'hwoarang': 'Hwoarang',
            'steve': 'Steve',
            'lee': 'Lee',
            'anna': 'Anna',
            'nina': 'Nina',
            'eddy': 'Eddy',
            'yoshimitsu': 'Yoshimitsu',
            'kuma': 'Kuma',
            'panda': 'Panda',
            'devil jin': 'Devil Jin',
            'lars': 'Lars',
            'leo': 'Leo',
            'reina': 'Reina',
            'raven': 'Raven',
            'leroy': 'Leroy',
            'lili': 'Lili',
            'xiaoyu': 'Xiaoyu',
            'victor': 'Victor',
            'bryan': 'Bryan',
            'shaheen': 'Shaheen',
            'dragunov': 'Dragunov',
            'azucena': 'Azucena',
            'asuka': 'Asuka',
            'alisa': 'Alisa',
            'zafina': 'Zafina',
            'jack-8': 'Jack-8',
            'claudio': 'Claudio',
            'feng': 'Feng',
            'lidia': 'Lidia',
            'heihachi': 'Heihachi',
            'clive': 'Clive',
            'fahkumram': 'Fahkumram',
            # 인게임에서 표시되는 다른 이름들도 추가
            'devil': 'Devil Jin',
            'marshall': 'Marshall Law',
            'jack': 'Jack-8'
        }
        
        for key, value in character_mappings.items():
            if key in text:
                return value
        
        return None
    
    def update_detected_character(self, character_name):
        """감지된 캐릭터로 UI 업데이트"""
        if character_name in self.combo_loader.get_all_characters():
            self.current_character = character_name
            self.char_var.set(character_name)
            self.detected_char_label.config(text=f"감지된 캐릭터: {character_name}", fg='#00FF00')
            
            # 시동기 리스트 업데이트
            starters = self.combo_loader.get_character_starters(character_name)
            self.starter_combo['values'] = starters
            self.starter_var.set('')
            self.combo_listbox.delete(0, tk.END)
            
            self.status_label.config(text=f"상태: {character_name} 자동 감지됨", fg='#00FF00')
            
            # 자동으로 첫 번째 시동기 선택
            if starters:
                self.current_starter = starters[0]
                self.starter_var.set(starters[0])
                self.update_combo_list(character_name, starters[0])
                
                # 첫 번째 콤보 자동 선택
                combos = self.combo_loader.get_starter_combos(character_name, starters[0])
                if combos:
                    self.selected_combo = combos[0]
                    if self.menu_overlay:
                        self.create_reframework_style_menu()
        else:
            self.detected_char_label.config(text=f"감지된 캐릭터: {character_name} (지원되지 않음)", fg='#FF0000')
    
    def on_character_selected(self, event):
        """캐릭터 선택 시 시동기 리스트 업데이트"""
        character = self.char_var.get()
        if character:
            self.current_character = character
            self.current_starter = None
            self.selected_combo = None
            
            # 시동기 리스트 업데이트
            starters = self.combo_loader.get_character_starters(character)
            self.starter_combo['values'] = starters
            self.starter_var.set('')  # 시동기 선택 초기화
            
            # 콤보 리스트 초기화
            self.combo_listbox.delete(0, tk.END)
            
            self.status_label.config(text=f"상태: {character} 선택됨", fg='#00FF00')
    
    def on_starter_selected(self, event):
        """시동기 선택 시 콤보 리스트 업데이트"""
        starter = self.starter_var.get()
        if starter and self.current_character:
            self.current_starter = starter
            self.update_combo_list(self.current_character, starter)
            self.status_label.config(text=f"상태: {self.current_character} - {starter} 선택됨", fg='#00FF00')
    
    def on_difficulty_filter(self, event):
        """난이도 필터 적용"""
        if self.current_character and self.current_starter:
            self.update_combo_list(self.current_character, self.current_starter)
    
    def update_combo_list(self, character, starter):
        """콤보 리스트 업데이트"""
        self.combo_listbox.delete(0, tk.END)
        
        # 난이도 필터 적용
        difficulty = self.difficulty_var.get()
        if difficulty == "all":
            combos = self.combo_loader.get_starter_combos(character, starter)
        else:
            combos = self.combo_loader.get_starter_combos_by_difficulty(character, starter, difficulty)
        
        for combo in combos:
            combo_text = f"{combo['name']} - {combo['damage']} 데미지 ({combo.get('difficulty', 'unknown')})"
            self.combo_listbox.insert(tk.END, combo_text)
    
    def create_reframework_style_menu(self):
        """REFramework 스타일 메뉴 오버레이 생성"""
        if self.menu_overlay:
            self.menu_overlay.destroy()
        
        # 메뉴 오버레이 창 생성 - 가로로 길고 세로로 짧게
        self.menu_overlay = tk.Toplevel()
        self.menu_overlay.title("철권8 콤보 메뉴")
        self.menu_overlay.geometry("800x80+50+50")  # 가로 800, 세로 80
        
        # 오버레이 설정
        self.menu_overlay.attributes('-topmost', True)
        self.menu_overlay.attributes('-alpha', 0.95)
        
        # REFramework 스타일 배경
        menu_frame = tk.Frame(self.menu_overlay, bg=self.bg_color)
        menu_frame.pack(fill='both', expand=True)
        
        # 제목 표시줄 (REFramework 스타일) - 세로로 짧게
        title_bar = tk.Frame(menu_frame, bg=self.accent_color, height=25)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        
        # 제목과 닫기 버튼
        title_label = tk.Label(title_bar, text="철권8 콤보 메뉴 [v1.0]", 
                              font=('Arial', 9, 'bold'), 
                              fg=self.text_color, bg=self.accent_color)
        title_label.pack(side='left', padx=10, pady=2)
        
        close_btn = tk.Button(title_bar, text="×", 
                             command=self.menu_overlay.destroy,
                             bg=self.accent_color, fg=self.text_color,
                             font=('Arial', 10, 'bold'), bd=0)
        close_btn.pack(side='right', padx=10, pady=2)
        
        # 메뉴 내용 - 가로로 배치
        content_frame = tk.Frame(menu_frame, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 왼쪽: 설정 옵션들
        settings_frame = tk.Frame(content_frame, bg=self.bg_color)
        settings_frame.pack(side='left', fill='y', padx=(0, 20))
        
        # 체크박스 스타일 옵션들 - 세로로 배치
        self.transparency_var = tk.BooleanVar(value=True)
        self.input_passthrough_var = tk.BooleanVar(value=False)
        
        # Transparency 체크박스
        trans_frame = tk.Frame(settings_frame, bg=self.bg_color)
        trans_frame.pack(fill='x', pady=1)
        self.create_checkbox(trans_frame, "Transparency", self.transparency_var)
        
        # Input Passthrough 체크박스
        input_frame = tk.Frame(settings_frame, bg=self.bg_color)
        input_frame.pack(fill='x', pady=1)
        self.create_checkbox(input_frame, "Input Passthrough", self.input_passthrough_var)
        
        # 구분선 (세로)
        separator1 = tk.Frame(content_frame, bg=self.accent_color, width=1)
        separator1.pack(side='left', fill='y', padx=10)
        
        # 중앙: 캐릭터 정보
        char_frame = tk.Frame(content_frame, bg=self.bg_color)
        char_frame.pack(side='left', fill='y', padx=10)
        
        if self.current_character:
            # 현재 캐릭터 정보
            tk.Label(char_frame, text=f"캐릭터: {self.current_character}", 
                    font=('Arial', 10, 'bold'), fg='#00FF00', bg=self.bg_color).pack(pady=2)
            
            # 시동기 목록 - 가로로 배치
            starters = self.combo_loader.get_character_starters(self.current_character)
            starter_frame = tk.Frame(char_frame, bg=self.bg_color)
            starter_frame.pack(fill='x', pady=5)
            
            for i, starter in enumerate(starters):
                self.create_starter_menu_button(starter_frame, starter)
                if i < len(starters) - 1:  # 마지막이 아니면 구분선
                    tk.Label(starter_frame, text="|", fg=self.accent_color, bg=self.bg_color).pack(side='left', padx=5)
        else:
            # 캐릭터 선택 안내
            tk.Label(char_frame, text="캐릭터를 먼저 선택해주세요", 
                    font=('Arial', 9), fg='#FF0000', bg=self.bg_color).pack(pady=5)
        
        # 구분선 (세로)
        separator2 = tk.Frame(content_frame, bg=self.accent_color, width=1)
        separator2.pack(side='left', fill='y', padx=10)
        
        # 오른쪽: 선택된 콤보 정보 (이름과 데미지만)
        combo_info_frame = tk.Frame(content_frame, bg=self.bg_color)
        combo_info_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        if self.selected_combo:
            # 콤보 이름과 데미지만 표시
            combo_name = self.selected_combo['name']
            combo_damage = self.selected_combo['damage']
            
            tk.Label(combo_info_frame, text=f"선택: {combo_name}", 
                    font=('Arial', 9, 'bold'), fg=self.text_color, bg=self.bg_color).pack(anchor='w')
            
            tk.Label(combo_info_frame, text=f"데미지: {combo_damage}", 
                    font=('Arial', 8), fg='#FF0000', bg=self.bg_color).pack(anchor='w')
        else:
            tk.Label(combo_info_frame, text="콤보를 선택해주세요", 
                    font=('Arial', 9), fg=self.text_color, bg=self.bg_color).pack(anchor='w')
        
        messagebox.showinfo("REFramework 스타일 메뉴", "REFramework 스타일 메뉴바가 생성되었습니다!")
    
    def create_checkbox(self, parent, text, variable):
        """REFramework 스타일 체크박스 생성"""
        # 체크박스 프레임
        checkbox_frame = tk.Frame(parent, bg=self.bg_color)
        checkbox_frame.pack(fill='x', padx=5, pady=2)
        
        # 체크박스 버튼
        def toggle_checkbox():
            variable.set(not variable.get())
            self.update_checkbox_display(checkbox_btn, variable.get())
        
        checkbox_btn = tk.Button(checkbox_frame, text="", 
                                command=toggle_checkbox,
                                bg=self.accent_color, fg=self.check_color,
                                font=('Arial', 8), width=3, height=1, bd=0)
        checkbox_btn.pack(side='left', padx=(0, 5))
        
        # 텍스트 라벨
        tk.Label(checkbox_frame, text=text, 
                font=('Arial', 9), fg=self.text_color, bg=self.bg_color).pack(side='left')
        
        # 초기 상태 설정
        self.update_checkbox_display(checkbox_btn, variable.get())
    
    def update_checkbox_display(self, button, is_checked):
        """체크박스 표시 업데이트"""
        if is_checked:
            button.config(text="✓", fg=self.check_color)
        else:
            button.config(text="", fg=self.accent_color)
    
    def create_starter_menu_button(self, parent, starter):
        """시동기 메뉴 버튼 생성 (가로 배치용)"""
        # 메뉴 버튼
        starter_btn = tk.Button(parent, text=starter, 
                               command=lambda: self.select_starter_from_menu(starter),
                               bg=self.accent_color, fg=self.text_color,
                               font=('Arial', 9), bd=0, padx=8, pady=2)
        starter_btn.pack(side='left', padx=2)
        
        # 마우스 오버 효과
        def on_enter(e):
            starter_btn.config(bg='#666666')
        
        def on_leave(e):
            starter_btn.config(bg=self.accent_color)
        
        starter_btn.bind('<Enter>', on_enter)
        starter_btn.bind('<Leave>', on_leave)
    
    def select_starter_from_menu(self, starter):
        """메뉴에서 시동기 선택"""
        self.current_starter = starter
        self.starter_var.set(starter)
        self.update_combo_list(self.current_character, starter)
        self.status_label.config(text=f"상태: {self.current_character} - {starter} 선택됨", fg='#00FF00')
        
        # 시동기 선택 시 첫 번째 콤보 자동 선택
        combos = self.combo_loader.get_starter_combos(self.current_character, starter)
        if combos:
            self.selected_combo = combos[0]
            # 메뉴바 업데이트
            if self.menu_overlay:
                self.create_reframework_style_menu()
    
    def on_combo_selected(self, event):
        """콤보 선택 시"""
        selection = self.combo_listbox.curselection()
        if selection and self.current_character and self.current_starter:
            combo_index = selection[0]
            
            # 난이도 필터 적용된 콤보 리스트에서 선택
            difficulty = self.difficulty_var.get()
            if difficulty == "all":
                combos = self.combo_loader.get_starter_combos(self.current_character, self.current_starter)
            else:
                combos = self.combo_loader.get_starter_combos_by_difficulty(self.current_character, self.current_starter, difficulty)
            
            if combo_index < len(combos):
                self.selected_combo = combos[combo_index]
                combo_name = self.selected_combo['name']
                self.status_label.config(text=f"상태: {combo_name} 선택됨", fg='#00FF00')
                
                # 콤보 선택 시 자동으로 오버레이 생성
                self.create_combo_overlay()
                
                # 메뉴바 업데이트
                if self.menu_overlay:
                    self.create_reframework_style_menu()
    
    def create_combo_overlay(self):
        """콤보 루트 오버레이 생성 (이미지 기반)"""
        if not self.selected_combo:
            return
        
        if self.combo_overlay:
            self.combo_overlay.destroy()
        
        # 콤보 오버레이 창 생성
        self.combo_overlay = tk.Toplevel()
        self.combo_overlay.title("콤보 루트")
        self.combo_overlay.geometry("800x600+100+100")
        
        # 오버레이 설정
        self.combo_overlay.attributes('-topmost', True)
        self.combo_overlay.attributes('-alpha', 0.95)
        
        # REFramework 스타일 배경
        combo_frame = tk.Frame(self.combo_overlay, bg=self.bg_color)
        combo_frame.pack(fill='both', expand=True)
        
        # 제목 표시줄
        title_bar = tk.Frame(combo_frame, bg=self.accent_color, height=30)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        
        # 제목과 닫기 버튼
        title_label = tk.Label(title_bar, text="철권8 콤보 루트", 
                              font=('Arial', 12, 'bold'), 
                              fg=self.text_color, bg=self.accent_color)
        title_label.pack(side='left', padx=10, pady=5)
        
        close_btn = tk.Button(title_bar, text="×", 
                             command=self.combo_overlay.destroy,
                             bg=self.accent_color, fg=self.text_color,
                             font=('Arial', 12, 'bold'), bd=0)
        close_btn.pack(side='right', padx=10, pady=5)
        
        # 콤보 내용
        content_frame = tk.Frame(combo_frame, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 콤보 이름
        combo_name = self.selected_combo['name']
        tk.Label(content_frame, text=f"콤보: {combo_name}", 
                font=('Arial', 14, 'bold'), 
                fg=self.text_color, bg=self.bg_color).pack(pady=10)
        
        # 콤보 이미지 표시
        self.display_combo_image(content_frame)
        
        # 데미지 정보
        damage = self.selected_combo['damage']
        tk.Label(content_frame, text=f"데미지: {damage}", 
                font=('Arial', 12), 
                fg='#FF0000', bg=self.bg_color).pack(pady=5)
        
        # 난이도 정보
        difficulty = self.selected_combo.get('difficulty', 'unknown')
        tk.Label(content_frame, text=f"난이도: {difficulty}", 
                font=('Arial', 10), 
                fg=self.text_color, bg=self.bg_color).pack(pady=5)
    
    def display_combo_image(self, parent_frame):
        """콤보 이미지 표시"""
        combo_name = self.selected_combo['name']
        character_name = self.current_character
        starter_name = self.current_starter
        
        # combo_images 폴더 확인
        combo_images_dir = "combo_images"
        if not os.path.exists(combo_images_dir):
            os.makedirs(combo_images_dir)
            messagebox.showinfo("이미지 폴더 생성", f"'{combo_images_dir}' 폴더가 생성되었습니다.\n콤보 이미지들을 이 폴더에 넣어주세요.")
            return
        
        # 이미지 파일명 생성 (여러 형식 시도)
        possible_filenames = [
            # 형식 1: 캐릭터명_시동기_콤보명.png (예: alisa_3RP_easy1.png)
            f"{character_name.lower()}_{starter_name.lower()}_{combo_name.lower().replace(' ', '')}.png",
            # 형식 2: 캐릭터명_콤보명.png (예: alisa_easy_1.png)
            f"{character_name.lower()}_{combo_name.lower().replace(' ', '_')}.png",
            # 형식 3: 캐릭터명_시동기_콤보명.png (예: alisa_3RP_easy_1.png)
            f"{character_name.lower()}_{starter_name.lower()}_{combo_name.lower().replace(' ', '_')}.png"
        ]
        
        image_path = None
        for filename in possible_filenames:
            temp_path = os.path.join(combo_images_dir, filename)
            if os.path.exists(temp_path):
                image_path = temp_path
                print(f"이미지 파일 찾음: {filename}")
                break
        
        # 이미지 프레임
        image_frame = tk.Frame(parent_frame, bg=self.bg_color)
        image_frame.pack(pady=20)
        
        if image_path:
            try:
                # 이미지 로드 및 표시
                image = Image.open(image_path)
                # 이미지 크기 조정 (최대 600x400)
                image.thumbnail((600, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # 이미지 라벨
                img_label = tk.Label(image_frame, image=photo, bg=self.bg_color)
                img_label.image = photo  # 참조 유지
                img_label.pack()
                
            except Exception as e:
                print(f"이미지 로드 오류: {e}")
                self.show_combo_text_fallback(image_frame)
        else:
            # 이미지가 없으면 텍스트로 표시
            print(f"이미지 파일을 찾을 수 없습니다. 시도한 파일명들: {possible_filenames}")
            self.show_combo_text_fallback(image_frame)
    
    def show_combo_text_fallback(self, parent_frame):
        """이미지가 없을 때 텍스트로 콤보 표시"""
        combo_sequence = self.selected_combo['combo']
        combo_display = " → ".join(combo_sequence)
        
        tk.Label(parent_frame, text=combo_display,
                font=('Arial', 16, 'bold'),
                fg='#00FF00', bg=self.bg_color).pack(pady=20)
        
        tk.Label(parent_frame, text="(이미지 파일을 추가하면 이미지로 표시됩니다)",
                font=('Arial', 10),
                fg=self.text_color, bg=self.bg_color).pack()
    
    def quit_app(self):
        """앱 종료"""
        if self.menu_overlay:
            self.menu_overlay.destroy()
        if self.combo_overlay:
            self.combo_overlay.destroy()
        self.root.quit()
    
    def run(self):
        """프로그램 실행"""
        print("시동기별 철권8 콤보 오버레이가 시작되었습니다!")
        print(f"로드된 캐릭터: {', '.join(self.combo_loader.get_all_characters())}")
        self.root.mainloop()

if __name__ == "__main__":
    app = StarterBasedOverlay()
    app.run() 