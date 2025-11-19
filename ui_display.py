import os
import pandas as pd


def clear_screen():
    os.system('clear')


def format_bytes(bytes_num):
    """Форматирование байтов в человеко-читаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} TB"


def format_speed(bytes_per_sec):
    """Форматирование скорости"""
    return format_bytes(bytes_per_sec) + "/s"


def display_dashboard(network_data):
    clear_screen()
    print("=== СЕТЕВОЙ МОНИТОР (Ubuntu Linux) ===")
    print("Для выхода нажмите Ctrl+C\n")

    # Трафик по приложениям
    app_traffic = network_data.get_app_traffic()
    if app_traffic:
        df_apps = pd.DataFrame.from_dict(app_traffic, orient='index')
        df_apps.columns = ['Отправлено', 'Получено', 'Скорость отправки', 'Скорость приема', 'Пользователь']

        # Форматируем данные
        df_display = df_apps.copy()
        df_display['Отправлено'] = df_display['Отправлено'].apply(format_bytes)
        df_display['Получено'] = df_display['Получено'].apply(format_bytes)
        df_display['Скорость отправки'] = df_display['Скорость отправки'].apply(format_speed)
        df_display['Скорость приема'] = df_display['Скорость приема'].apply(format_speed)

        print("ТРАФИК ПО ПРИЛОЖЕНИЯМ:")
        print(df_display.sort_values('Скорость отправки', ascending=False).head(15))
    else:
        print("Нет данных о трафике приложений")

    # Удаленные подключения
    remote_conns = network_data.get_remote_connections()
    if remote_conns:
        print(f"\nАКТИВНЫЕ ПОДКЛЮЧЕНИЯ ({len(remote_conns)} уникальных адресов):")
        for ip, apps in list(remote_conns.items())[:10]:
            print(f"\n{ip}:")
            for app in apps[:3]:  # Показываем до 3 приложений на IP
                print(f"  └─ {app['name']} (PID:{app['pid']}, User:{app['user']})")
                print(f"     Port {app['local_port']} → {app['protocol']}")
    else:
        print("\nНет активных подключений")

    # Подключения по приложениям
    app_conns = network_data.get_connections_by_app()
    if app_conns:
        print(f"\nПОДКЛЮЧЕНИЯ ПО ПРИЛОЖЕНИЯМ:")
        for app_name, connections in list(app_conns.items())[:5]:
            print(f"\n{app_name}:")
            for conn in connections[:2]:  # Показываем до 2 подключений на приложение
                print(f"  └─ {conn['remote_host']}:{conn['remote_port']} ({conn['protocol']})")


def display_warning():
    print("⚠️  Для полного доступа к информации о всех процессах")
    print("   рекомендуется запустить программу с правами root:")
    print("   sudo python3 main.py")