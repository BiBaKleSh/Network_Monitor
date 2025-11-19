import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from data_processor import NetworkData
from network_collector import get_connections, get_network_usage
from utils import format_bytes, format_speed


class NetworkMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг сети Ubuntu")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')

        self.network_data = NetworkData()
        self.is_running = False
        self.update_thread = None

        self.setup_gui()
        self.start_monitoring()

    def setup_gui(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка с общей информацией
        self.dashboard_frame = ttk.Frame(notebook)
        notebook.add(self.dashboard_frame, text="Обзор")

        # Вкладка с приложениями
        self.apps_frame = ttk.Frame(notebook)
        notebook.add(self.apps_frame, text="Приложения")

        # Вкладка с подключениями
        self.connections_frame = ttk.Frame(notebook)
        notebook.add(self.connections_frame, text="Подключения")

        self.setup_dashboard_tab()
        self.setup_apps_tab()
        self.setup_connections_tab()

        # Панель управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = ttk.Label(control_frame, text="Статус: Запущен")
        self.status_label.pack(side=tk.LEFT)

        ttk.Button(control_frame, text="Обновить", command=self.manual_update).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Остановить", command=self.stop_monitoring).pack(side=tk.RIGHT, padx=5)

    def setup_dashboard_tab(self):
        # Статистика системы
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Системная статистика")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.system_stats_text = scrolledtext.ScrolledText(stats_frame, height=8, width=80)
        self.system_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Активные подключения
        conn_frame = ttk.LabelFrame(self.dashboard_frame, text="Активные подключения")
        conn_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.connections_text = scrolledtext.ScrolledText(conn_frame, height=12, width=80)
        self.connections_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_apps_tab(self):
        # Таблица приложений
        columns = ('name', 'sent', 'recv', 'sent_rate', 'recv_rate', 'user')
        self.apps_tree = ttk.Treeview(self.apps_frame, columns=columns, show='headings', height=20)

        # Заголовки колонок
        self.apps_tree.heading('name', text='Приложение')
        self.apps_tree.heading('sent', text='Отправлено')
        self.apps_tree.heading('recv', text='Получено')
        self.apps_tree.heading('sent_rate', text='Скорость отправки')
        self.apps_tree.heading('recv_rate', text='Скорость приема')
        self.apps_tree.heading('user', text='Пользователь')

        # Настройка ширины колонок
        self.apps_tree.column('name', width=150)
        self.apps_tree.column('sent', width=100)
        self.apps_tree.column('recv', width=100)
        self.apps_tree.column('sent_rate', width=120)
        self.apps_tree.column('recv_rate', width=120)
        self.apps_tree.column('user', width=100)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.apps_frame, orient=tk.VERTICAL, command=self.apps_tree.yview)
        self.apps_tree.configure(yscroll=scrollbar.set)

        self.apps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def setup_connections_tab(self):
        # Таблица подключений
        columns = ('app', 'local', 'remote', 'protocol', 'status', 'user')
        self.conn_tree = ttk.Treeview(self.connections_frame, columns=columns, show='headings', height=20)

        # Заголовки колонок
        self.conn_tree.heading('app', text='Приложение')
        self.conn_tree.heading('local', text='Локальный адрес')
        self.conn_tree.heading('remote', text='Удаленный адрес')
        self.conn_tree.heading('protocol', text='Протокол')
        self.conn_tree.heading('status', text='Статус')
        self.conn_tree.heading('user', text='Пользователь')

        # Настройка ширины колонок
        self.conn_tree.column('app', width=120)
        self.conn_tree.column('local', width=150)
        self.conn_tree.column('remote', width=200)
        self.conn_tree.column('protocol', width=80)
        self.conn_tree.column('status', width=80)
        self.conn_tree.column('user', width=100)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.connections_frame, orient=tk.VERTICAL, command=self.conn_tree.yview)
        self.conn_tree.configure(yscroll=scrollbar.set)

        self.conn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def start_monitoring(self):
        self.is_running = True
        self.update_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.update_thread.start()

    def stop_monitoring(self):
        self.is_running = False
        self.status_label.config(text="Статус: Остановлен")

    def manual_update(self):
        if not self.is_running:
            self.start_monitoring()

    def monitoring_loop(self):
        while self.is_running:
            try:
                # Сбор данных
                connections = get_connections()
                traffic_stats = get_network_usage()

                # Обработка данных
                self.network_data.update_connections(connections)
                self.network_data.update_traffic(traffic_stats)

                # Обновление GUI в основном потоке
                self.root.after(0, self.update_display)

                time.sleep(2)

            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Ошибка: {e}"))
                time.sleep(5)

    def update_display(self):
        if not self.is_running:
            return

        self.update_dashboard()
        self.update_apps_table()
        self.update_connections_table()
        self.status_label.config(text="Статус: Обновлено")

    def update_dashboard(self):
        # Очистка текстовых полей
        self.system_stats_text.delete(1.0, tk.END)
        self.connections_text.delete(1.0, tk.END)

        # Системная статистика
        app_traffic = self.network_data.get_app_traffic()
        total_sent = sum(data['sent'] for data in app_traffic.values())
        total_recv = sum(data['recv'] for data in app_traffic.values())
        total_sent_rate = sum(data['sent_rate'] for data in app_traffic.values())
        total_recv_rate = sum(data['recv_rate'] for data in app_traffic.values())

        stats_text = f"""Общая статистика трафика:
• Всего отправлено: {format_bytes(total_sent)}
• Всего получено: {format_bytes(total_recv)}
• Скорость отправки: {format_speed(total_sent_rate)}
• Скорость приема: {format_speed(total_recv_rate)}
• Отслеживается приложений: {len(app_traffic)}
• Активных подключений: {len(self.network_data.connections)}

Топ приложений по трафику:
"""

        # Топ 5 приложений по отправке данных
        sorted_apps = sorted(app_traffic.items(), key=lambda x: x[1]['sent_rate'], reverse=True)[:5]
        for app_name, data in sorted_apps:
            stats_text += f"• {app_name}: {format_speed(data['sent_rate'])} отправка\n"

        self.system_stats_text.insert(1.0, stats_text)

        # Активные подключения
        remote_conns = self.network_data.get_remote_connections()
        conn_text = f"Уникальных удаленных адресов: {len(remote_conns)}\n\n"

        for ip, apps in list(remote_conns.items())[:10]:
            conn_text += f"{ip}:\n"
            for app in apps[:2]:
                conn_text += f"  └─ {app['name']} (PID:{app['pid']}, User:{app['user']})\n"
            conn_text += "\n"

        self.connections_text.insert(1.0, conn_text)

    def update_apps_table(self):
        # Очистка таблицы
        for item in self.apps_tree.get_children():
            self.apps_tree.delete(item)

        # Заполнение данными
        app_traffic = self.network_data.get_app_traffic()
        sorted_apps = sorted(app_traffic.items(), key=lambda x: x[1]['sent_rate'], reverse=True)

        for app_name, data in sorted_apps[:50]:  # Показываем топ 50
            self.apps_tree.insert('', tk.END, values=(
                app_name,
                format_bytes(data['sent']),
                format_bytes(data['recv']),
                format_speed(data['sent_rate']),
                format_speed(data['recv_rate']),
                data['user']
            ))

    def update_connections_table(self):
        # Очистка таблицы
        for item in self.conn_tree.get_children():
            self.conn_tree.delete(item)

        # Заполнение данными
        connections = self.network_data.connections
        sorted_conns = sorted(connections, key=lambda x: x['name'])

        for conn in sorted_conns[:100]:  # Показываем до 100 подключений
            local_addr = f"{conn['local_ip']}:{conn['local_port']}"
            remote_addr = f"{conn['remote_ip']}:{conn['remote_port']}"

            self.conn_tree.insert('', tk.END, values=(
                conn['name'],
                local_addr,
                remote_addr,
                conn.get('protocol', 'N/A'),
                conn['status'],
                conn['user']
            ))


def start_gui():
    root = tk.Tk()
    app = NetworkMonitorGUI(root)

    def on_closing():
        app.stop_monitoring()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()