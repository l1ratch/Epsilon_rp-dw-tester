import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import hashlib
from datetime import datetime
from pathlib import Path
import queue

class NEPSTester:
    def __init__(self, root):
        self.root = root
        self.root.title("NEPS Тестер")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # СКРЫТЫЕ сервера
        self.servers = [
            {"name": "Основной", "url": "#"},
            {"name": "Резервный", "url": "#"},
            {"name": "Внутренний", "url": "#"}
        ]
        self.expected_sha1 = "#"
        
        self.log_content = []
        self.desktop = Path.home() / "Desktop"
        
        self.create_minimal_ui()
    
    def create_minimal_ui(self):
        # Заголовок
        title_label = ttk.Label(self.root, text="🎮 NEPS ТЕСТЕР", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=30)
        
        # Информация о ПО
        info_frame = ttk.LabelFrame(self.root, text="Информация", padding=15)
        info_frame.pack(fill=tk.X, padx=30, pady=10)
        
        ttk.Label(info_frame, 
                 text="⚠️  ЗАПУСКАЙТЕ ТОЛЬКО ПО РЕКОМЕНДАЦИИ АДМИНА\n🔒 НЕ ПЕРЕДАВАЙТЕ ПРОГРАММУ НИКОМУ", 
                 font=('Arial', 10), foreground='red', justify=tk.CENTER).pack()
        
        ttk.Label(info_frame, 
                 text="Программа проверяет доступность ресурсов сервера.\nРезультат сохраняется автоматически на рабочий стол.", 
                 font=('Arial', 9), justify=tk.CENTER).pack(pady=(10,0))
        
        # Кнопка теста
        self.test_btn = ttk.Button(self.root, text="🚀 ЗАПУСТИТЬ ТЕСТ", 
                                  command=self.run_test, style="Accent.TButton")
        self.test_btn.pack(pady=30)
        
        # Статус
        self.status_label = ttk.Label(self.root, text="Готов к тестированию", 
                                     font=('Arial', 11))
        self.status_label.pack()
    
    def test_resourcepack_server(self, server):
        """Подробный тест одного сервера РП"""
        name = server["name"]
        url = server["url"]
        log_lines = []
        
        try:
            # HEAD запрос
            log_lines.append(f"🔍 [{name}] HEAD запрос...")
            resp = requests.head(url, timeout=15, allow_redirects=True)
            log_lines.append(f"   ✅ Статус: {resp.status_code}")
            
            if resp.status_code != 200:
                return False, log_lines
            
            # Размер
            size_str = resp.headers.get('content-length', '0')
            size = int(size_str) if size_str.isdigit() else 0
            size_mb = size / (1024*1024)
            log_lines.append(f"   📏 Размер: {size_mb:.1f} МБ ({size:,} байт)")
            
            if size_mb > 100:
                log_lines.append("   ⚠️  Размер >100МБ - Minecraft может блокировать!")
            
            # Полное скачивание
            log_lines.append("   📥 Скачивание для проверки...")
            resp = requests.get(url, timeout=120, stream=True)
            resp.raise_for_status()
            
            sha1_hash = hashlib.sha1()
            total_downloaded = 0
            chunk_count = 0
            
            for chunk in resp.iter_content(8192):
                if chunk:
                    sha1_hash.update(chunk)
                    total_downloaded += len(chunk)
                    chunk_count += 1
            
            calculated_sha1 = sha1_hash.hexdigest()
            log_lines.append(f"   📊 Скачано: {total_downloaded/(1024*1024):.1f} МБ")
            log_lines.append(f"   📦 Чанков: {chunk_count}")
            log_lines.append(f"   ⏱️  Время: {resp.elapsed.total_seconds():.1f}с")
            log_lines.append(f"   🔐 SHA1: {calculated_sha1}")
            
            # Проверка
            if calculated_sha1 == self.expected_sha1:
                log_lines.append("   ✅ SHA1 СОВПАДАЕТ - СЕРВЕР РАБОТАЕТ!")
                return True, log_lines
            else:
                log_lines.append("   ❌ SHA1 НЕ СОВПАДАЕТ!")
                return False, log_lines
                
        except requests.exceptions.Timeout:
            log_lines.append("   ❌ TIMEOUT - сервер не отвечает")
        except requests.exceptions.ConnectionError as e:
            log_lines.append(f"   ❌ ОШИБКА СОЕДИНЕНИЯ: {str(e)[:50]}")
        except Exception as e:
            log_lines.append(f"   ❌ ОШИБКА: {str(e)[:70]}")
        
        return False, log_lines
    
    def save_log_auto(self):
        """Автосохранение подробного лога"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.desktop / f"NEPS_Диагностика_{timestamp}.txt"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("🎮 NEPS ДИАГНОСТИКА РЕСУРСПАКОВ\n")
                f.write("="*60 + "\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Версия: v5.0\n\n")
                f.write("\n".join(self.log_content))
                f.write("\n\n" + "="*60)
            
            return str(log_file)
        except:
            return None
    
    def run_test(self):
        def worker():
            self.test_btn.config(state='disabled')
            self.status_label.config(text="Выполняется тест...")
            
            self.log_content = []
            self.log_content.append("🚀 ЗАПУСК ДИАГНОСТИКИ РЕСУРСПАКОВ")
            self.log_content.append("="*60)
            
            # Тест 3 серверов
            working_servers = 0
            for i, server in enumerate(self.servers, 1):
                success, details = self.test_resourcepack_server(server)
                self.log_content.extend(details)
                self.log_content.append("")  # Пустая строка
                if success:
                    working_servers += 1
            
            # ИТОГО
            self.log_content.append("="*60)
            self.log_content.append(f"📊 ИТОГО: {working_servers} из 3 серверов работают")
            
            log_file = self.save_log_auto()
            
            # Финальный статус
            if working_servers > 0:
                self.status_label.config(text="✅ ВСЁ ХОРОШО - передайте лог администратору")
                messagebox.showinfo("✅ УСПЕХ", 
                    f"Тест завершён успешно!\n\nЛог автоматически сохранён:\n{log_file}\n\nПередайте файл администратору.")
            else:
                self.status_label.config(text="❌ ПРОБЛЕМА - передайте лог администратору")
                messagebox.showwarning("❌ ПРОБЛЕМА", 
                    f"Обнаружены проблемы!\n\nЛог сохранён:\n{log_file}\n\nПередайте администратору для анализа.")
            
            self.test_btn.config(state='normal')
        
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = NEPSTester(root)
    root.mainloop()
