import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import socket
import threading
import subprocess
import os
import platform
import psutil
import time
from datetime import datetime
from urllib.parse import urlparse

class MinecraftResourcepackTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Resourcepack Tester")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Переменные
        self.is_testing = False
        self.log_data = []
        self.desktop_path = os.path.expanduser("~\\Desktop")
        
        # Тестовые URL ресурспаков (популярные источники)
        self.test_urls = [
            {"name": "Основной", "url": "Скрыто"},
            {"name": "Резервный", "url": "Скрыто"},
            {"name": "Внутренний", "url": "Скрыто"},
        ]
        
        self.setup_ui()
        self.add_log("=== TESTER ЗАПУЩЕН ===", "info")
        self.add_log(f"Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self.add_log(f"ОС: {platform.system()} {platform.release()}", "info")
        self.add_log(f"Рабочий стол: {self.desktop_path}", "info")
    
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Тестер Ресурспака Minecraft", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Запустить Тестирование", 
                                       command=self.start_testing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Остановить", 
                                      command=self.stop_testing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="💾 Сохранить Лог", 
                  command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🗑️ Очистить", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Панель с URL
        url_frame = ttk.LabelFrame(main_frame, text="Пользовательские URL для теста", padding="10")
        url_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(url_frame, text="Добавить", command=self.add_custom_url).pack(side=tk.LEFT, padx=5)
        
        # Логи
        log_label = ttk.Label(main_frame, text="📋 Логи тестирования:", font=("Arial", 10, "bold"))
        log_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=25, width=100, 
                                                   font=("Courier", 9), bg="#1e1e1e", 
                                                   fg="#00ff00", insertbackground="#00ff00")
        self.log_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Конфигурируем теги для цветов
        self.log_text.tag_config("error", foreground="#ff4444")
        self.log_text.tag_config("success", foreground="#44ff44")
        self.log_text.tag_config("warning", foreground="#ffff44")
        self.log_text.tag_config("info", foreground="#44ddff")
        
        # Настройка весов для масштабирования
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def add_log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        self.log_data.append(log_message)
        self.log_text.insert(tk.END, log_message + "\n", level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def add_custom_url(self):
        url = self.url_entry.get().strip()
        if url:
            if url not in [u["url"] for u in self.test_urls]:
                self.test_urls.append({"name": "Пользовательский URL", "url": url})
                self.add_log(f"✅ Добавлен URL: {url}", "success")
                self.url_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Внимание", "Этот URL уже в списке!")
        else:
            messagebox.showerror("Ошибка", "Введите URL!")
    
    def start_testing(self):
        self.is_testing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        test_thread = threading.Thread(target=self.run_tests, daemon=True)
        test_thread.start()
    
    def stop_testing(self):
        self.is_testing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.add_log("⏸️ Тестирование остановлено пользователем", "warning")
    
    def run_tests(self):
        try:
            self.add_log("\n" + "="*50, "info")
            self.add_log("НАЧАЛО ТЕСТИРОВАНИЯ", "info")
            self.add_log("="*50, "info")
            
            # 1. Проверка интернета
            self.test_internet_connection()
            if not self.is_testing:
                return
            
            # 2. Проверка DNS
            self.test_dns()
            if not self.is_testing:
                return
            
            # 3. Проверка скорости интернета
            self.test_connection_speed()
            if not self.is_testing:
                return
            
            # 4. Проверка сетевых интерфейсов
            self.test_network_interfaces()
            if not self.is_testing:
                return
            
            # 5. Проверка портов
            self.test_ports()
            if not self.is_testing:
                return
            
            # 6. Загрузка ресурспаков
            self.test_downloads()
            if not self.is_testing:
                return
            
            # 7. Проверка системных ресурсов
            self.test_system_resources()
            
            self.add_log("\n" + "="*50, "info")
            self.add_log("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО", "success")
            self.add_log("="*50, "info")
            
            messagebox.showinfo("Успех", "Тестирование завершено!\nСохраните лог и передайте его поддержке.")
            
        except Exception as e:
            self.add_log(f"❌ Ошибка: {str(e)}", "error")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def test_internet_connection(self):
        self.add_log("\n📡 ТЕСТ 1: Проверка подключения к интернету", "info")
        
        test_servers = [
            ("8.8.8.8", "Google DNS"),
            ("1.1.1.1", "Cloudflare DNS"),
            ("208.67.222.222", "OpenDNS"),
        ]
        
        for ip, name in test_servers:
            try:
                socket.create_connection((ip, 53), timeout=3)
                self.add_log(f"  ✅ {name} ({ip}): подключение успешно", "success")
                return True
            except Exception as e:
                self.add_log(f"  ❌ {name} ({ip}): {str(e)}", "error")
        
        self.add_log("  ⚠️ Интернет не доступен!", "error")
        return False
    
    def test_dns(self):
        self.add_log("\n🔍 ТЕСТ 2: Проверка DNS", "info")
        
        domains = [
            "google.com",
            "github.com",
            "curseforge.com",
        ]
        
        for domain in domains:
            try:
                ip = socket.gethostbyname(domain)
                self.add_log(f"  ✅ {domain} -> {ip}", "success")
            except socket.gaierror as e:
                self.add_log(f"  ❌ {domain}: ошибка DNS ({e})", "error")
            except Exception as e:
                self.add_log(f"  ❌ {domain}: {str(e)}", "error")
    
    def test_connection_speed(self):
        self.add_log("\n⚡ ТЕСТ 3: Проверка скорости подключения", "info")
        
        try:
            url = "https://www.google.com"
            start_time = time.time()
            response = requests.get(url, timeout=5)
            elapsed_time = (time.time() - start_time) * 1000
            
            self.add_log(f"  ✅ Время ответа от Google: {elapsed_time:.2f}ms", "success")
            
            if elapsed_time > 1000:
                self.add_log(f"  ⚠️ Медленное подключение (>1000ms)", "warning")
        except requests.exceptions.Timeout:
            self.add_log("  ❌ Тайм-аут подключения", "error")
        except Exception as e:
            self.add_log(f"  ❌ Ошибка: {str(e)}", "error")
    
    def test_network_interfaces(self):
        self.add_log("\n🖧 ТЕСТ 4: Проверка сетевых интерфейсов", "info")
        
        try:
            net_interfaces = psutil.net_if_addrs()
            
            for interface, addresses in net_interfaces.items():
                for addr in addresses:
                    if addr.family.name == "AF_INET":
                        self.add_log(f"  ✅ {interface}: {addr.address}", "success")
                    elif addr.family.name == "AF_INET6":
                        self.add_log(f"  ℹ️ {interface}: {addr.address} (IPv6)", "info")
        except Exception as e:
            self.add_log(f"  ❌ Ошибка: {str(e)}", "error")
    
    def test_ports(self):
        self.add_log("\n🔌 ТЕСТ 5: Проверка портов", "info")
        
        ports_to_check = [80, 443, 8080, 25565]  # 25565 - Minecraft порт
        
        for port in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(("google.com", port))
                sock.close()
                
                if result == 0:
                    self.add_log(f"  ✅ Порт {port}: открыт", "success")
                else:
                    self.add_log(f"  ⚠️ Порт {port}: закрыт/недоступен", "warning")
            except Exception as e:
                self.add_log(f"  ❌ Порт {port}: {str(e)}", "error")
    
    def test_downloads(self):
        self.add_log("\n📥 ТЕСТ 6: Тестирование загрузки", "info")
        
        for test in self.test_urls:
            if not self.is_testing:
                break
            
            url = test["url"]
            name = test["name"]
            
            try:
                self.add_log(f"\n  Проверка: {name}", "info")
                # self.add_log(f"  URL: {url}", "info")
                
                start_time = time.time()
                response = requests.head(url, timeout=10, allow_redirects=True)
                elapsed_time = time.time() - start_time
                
                status_code = response.status_code
                content_length = response.headers.get("Content-Length", "Неизвестно")
                
                if 200 <= status_code < 300:
                    self.add_log(f"  ✅ Статус: {status_code}", "success")
                    self.add_log(f"  ⏱️ Время: {elapsed_time:.2f}s", "success")
                    self.add_log(f"  📦 Размер: {content_length} байт", "success")
                else:
                    self.add_log(f"  ⚠️ Статус: {status_code}", "warning")
                
            except requests.exceptions.Timeout:
                self.add_log(f"  ❌ Тайм-аут (>10 сек)", "error")
            except requests.exceptions.ConnectionError:
                self.add_log(f"  ❌ Ошибка подключения", "error")
            except Exception as e:
                self.add_log(f"  ❌ Ошибка: {str(e)}", "error")
    
    def test_system_resources(self):
        self.add_log("\n💻 ТЕСТ 7: Проверка системных ресурсов", "info")
        
        try:
            # Процессор
            cpu_percent = psutil.cpu_percent(interval=2)
            self.add_log(f"  CPU: {cpu_percent}%", "info" if cpu_percent < 80 else "warning")
            
            # Память
            memory = psutil.virtual_memory()
            self.add_log(f"  RAM: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)", 
                        "info" if memory.percent < 80 else "warning")
            
            # Диск
            disk = psutil.disk_usage("/")
            self.add_log(f"  Диск: {disk.percent}% используется", 
                        "info" if disk.percent < 80 else "warning")
            
            # Количество ядер
            cores = psutil.cpu_count()
            self.add_log(f"  Ядра процессора: {cores}", "info")
            
        except Exception as e:
            self.add_log(f"  ❌ Ошибка: {str(e)}", "error")
    
    def save_log(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"minecraft_test_{timestamp}.log"
        log_path = os.path.join(self.desktop_path, log_filename)
        
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log_data))
            
            self.add_log(f"💾 Лог сохранён: {log_path}", "success")
            messagebox.showinfo("Успех", f"Лог сохранён на рабочем столе:\n{log_filename}")
            
            # Открыть папку
            os.startfile(self.desktop_path)
        except Exception as e:
            self.add_log(f"❌ Ошибка при сохранении: {str(e)}", "error")
            messagebox.showerror("Ошибка", f"Не удалось сохранить лог: {str(e)}")
    
    def clear_log(self):
        if messagebox.askyesno("Очистить", "Вы уверены?"):
            self.log_text.delete(1.0, tk.END)
            self.log_data.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftResourcepackTester(root)
    root.mainloop()