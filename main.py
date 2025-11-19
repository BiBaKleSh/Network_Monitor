#!/usr/bin/env python3
import sys
import argparse
from ui_display import display_warning
from gui_interface import start_gui


def check_root():
    """Проверка прав root"""
    import os
    return os.geteuid() == 0


def main():
    parser = argparse.ArgumentParser(description='Мониторинг сети Ubuntu')
    parser.add_argument('--gui', action='store_true', help='Запуск в графическом режиме')
    parser.add_argument('--cli', action='store_true', help='Запуск в терминале')

    args = parser.parse_args()

    # Проверка прав
    if not check_root():
        display_warning()

    # Выбор режима
    if args.gui or not args.cli:
        print("Запуск графического интерфейса...")
        start_gui()
    else:
        # Запуск консольной версии
        from ui_display import display_dashboard
        from data_processor import NetworkData
        from network_collector import get_connections, get_network_usage
        import time

        network_data = NetworkData()

        try:
            while True:
                connections = get_connections()
                traffic_stats = get_network_usage()

                network_data.update_connections(connections)
                network_data.update_traffic(traffic_stats)

                display_dashboard(network_data)
                print(f"\nОбновление через 3 секунды... (Ctrl+C для выхода)")
                time.sleep(3)

        except KeyboardInterrupt:
            print("\nМониторинг остановлен")


if __name__ == "__main__":
    main()