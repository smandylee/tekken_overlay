import json
import os
from typing import Dict, List, Optional

class ComboLoader:
    def __init__(self, data_dir: str = "character_data"):
        self.data_dir = data_dir
        self.character_data = {}
        self.load_all_characters()
    
    def load_all_characters(self):
        """모든 캐릭터의 콤보 데이터를 로드"""
        try:
            # character_data 폴더의 모든 JSON 파일 검색
            for filename in os.listdir(self.data_dir):
                if filename.endswith('_combos.json'):
                    character_name = filename.replace('_combos.json', '')
                    self.load_character_data(character_name)
        except Exception as e:
            print(f"캐릭터 데이터 로드 오류: {e}")
    
    def load_character_data(self, character_name: str) -> bool:
        """특정 캐릭터의 콤보 데이터 로드"""
        try:
            file_path = os.path.join(self.data_dir, f"{character_name}_combos.json")
            
            if not os.path.exists(file_path):
                print(f"캐릭터 데이터 파일이 없습니다: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 데이터 검증
            if 'character' not in data or 'starters' not in data:
                print(f"잘못된 데이터 형식: {file_path}")
                return False
            
            # 캐릭터 이름 확인
            if data['character'] != character_name:
                print(f"캐릭터 이름 불일치: {data['character']} != {character_name}")
                return False
            
            self.character_data[character_name] = data['starters']
            
            # 총 콤보 수 계산
            total_combos = sum(len(combos) for combos in data['starters'].values())
            print(f"캐릭터 데이터 로드 완료: {character_name} ({len(data['starters'])}개 시동기, {total_combos}개 콤보)")
            return True
            
        except Exception as e:
            print(f"캐릭터 데이터 로드 오류 ({character_name}): {e}")
            return False
    
    def get_all_characters(self) -> List[str]:
        """사용 가능한 모든 캐릭터 리스트 반환"""
        return list(self.character_data.keys())
    
    def get_character_starters(self, character_name: str) -> List[str]:
        """특정 캐릭터의 시동기 리스트 반환"""
        if character_name in self.character_data:
            return list(self.character_data[character_name].keys())
        return []
    
    def get_starter_combos(self, character_name: str, starter_name: str) -> List[Dict]:
        """특정 캐릭터의 특정 시동기 콤보 리스트 반환"""
        if character_name in self.character_data:
            if starter_name in self.character_data[character_name]:
                return self.character_data[character_name][starter_name]
        return []
    
    def get_all_character_combos(self, character_name: str) -> List[Dict]:
        """특정 캐릭터의 모든 콤보 리스트 반환 (평면화)"""
        all_combos = []
        if character_name in self.character_data:
            for starter, combos in self.character_data[character_name].items():
                all_combos.extend(combos)
        return all_combos
    
    def get_combo_by_name(self, character_name: str, combo_name: str) -> Optional[Dict]:
        """캐릭터와 콤보 이름으로 특정 콤보 찾기"""
        all_combos = self.get_all_character_combos(character_name)
        for combo in all_combos:
            if combo['name'] == combo_name:
                return combo
        return None
    
    def get_combos_by_difficulty(self, character_name: str, difficulty: str) -> List[Dict]:
        """난이도별 콤보 필터링 (전체 캐릭터)"""
        all_combos = self.get_all_character_combos(character_name)
        return [combo for combo in all_combos if combo.get('difficulty') == difficulty]
    
    def get_starter_combos_by_difficulty(self, character_name: str, starter_name: str, difficulty: str) -> List[Dict]:
        """특정 시동기의 난이도별 콤보 필터링"""
        combos = self.get_starter_combos(character_name, starter_name)
        return [combo for combo in combos if combo.get('difficulty') == difficulty]
    
    def add_starter_data(self, character_name: str, starter_name: str, combos: List[Dict]) -> bool:
        """새로운 시동기 데이터 추가"""
        try:
            if character_name not in self.character_data:
                self.character_data[character_name] = {}
            
            self.character_data[character_name][starter_name] = combos
            
            # 파일에 저장
            self.save_character_data(character_name)
            print(f"시동기 데이터 추가 완료: {character_name} - {starter_name}")
            return True
            
        except Exception as e:
            print(f"시동기 데이터 추가 오류 ({character_name} - {starter_name}): {e}")
            return False
    
    def add_combo_to_starter(self, character_name: str, starter_name: str, combo_data: Dict) -> bool:
        """특정 시동기에 콤보 추가"""
        try:
            if character_name not in self.character_data:
                self.character_data[character_name] = {}
            
            if starter_name not in self.character_data[character_name]:
                self.character_data[character_name][starter_name] = []
            
            self.character_data[character_name][starter_name].append(combo_data)
            
            # 파일에 저장
            self.save_character_data(character_name)
            print(f"콤보 추가 완료: {character_name} - {starter_name} - {combo_data['name']}")
            return True
            
        except Exception as e:
            print(f"콤보 추가 오류 ({character_name} - {starter_name}): {e}")
            return False
    
    def update_combo(self, character_name: str, starter_name: str, combo_name: str, new_combo_data: Dict) -> bool:
        """기존 콤보 업데이트"""
        try:
            combos = self.get_starter_combos(character_name, starter_name)
            
            # 기존 콤보 찾기 및 업데이트
            for i, combo in enumerate(combos):
                if combo['name'] == combo_name:
                    self.character_data[character_name][starter_name][i] = new_combo_data
                    
                    # 파일에 저장
                    self.save_character_data(character_name)
                    return True
            
            print(f"콤보를 찾을 수 없습니다: {character_name} - {starter_name} - {combo_name}")
            return False
            
        except Exception as e:
            print(f"콤보 업데이트 오류: {e}")
            return False
    
    def delete_combo(self, character_name: str, starter_name: str, combo_name: str) -> bool:
        """콤보 삭제"""
        try:
            combos = self.get_starter_combos(character_name, starter_name)
            
            # 기존 콤보 찾기 및 삭제
            for i, combo in enumerate(combos):
                if combo['name'] == combo_name:
                    del self.character_data[character_name][starter_name][i]
                    
                    # 파일에 저장
                    self.save_character_data(character_name)
                    return True
            
            print(f"콤보를 찾을 수 없습니다: {character_name} - {starter_name} - {combo_name}")
            return False
            
        except Exception as e:
            print(f"콤보 삭제 오류: {e}")
            return False
    
    def save_character_data(self, character_name: str) -> bool:
        """캐릭터 데이터를 파일에 저장"""
        try:
            data = {
                "character": character_name,
                "starters": self.character_data[character_name]
            }
            
            file_path = os.path.join(self.data_dir, f"{character_name}_combos.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"캐릭터 데이터 저장 오류 ({character_name}): {e}")
            return False

# 전역 인스턴스 생성
combo_loader = ComboLoader() 