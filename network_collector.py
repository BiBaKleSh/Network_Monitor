import psutil
import socket
from collections import defaultdict
import os
from system_utils import get_dns_name, get_protocol_name


def get_connections():
    """Возвращает активные сетевые соединения с привязкой к процессам"""
    connections = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        connections.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'user': proc.info['username'],
                            'local_ip': conn.laddr.ip,
                            'local_port': conn.laddr.port,
                            'remote_ip': conn.raddr.ip,
                            'remote_port': conn.raddr.port,
                            'status': conn.status,
                            'protocol': get_protocol_name(conn.raddr.port)
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        print(f"Ошибка при получении соединений: {e}")

    return connections


def get_network_usage():
    """Сбор статистики использования сети по процессам через /proc"""
    stats = defaultdict(lambda: {'sent': 0, 'recv': 0, 'name': 'Unknown', 'user': 'Unknown'})

    try:
        # Получаем сетевую статистику из /proc
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            pid = proc.info['pid']
            try:
                # Читаем статистику сети из /proc/pid/net/dev
                net_stats_path = f"/proc/{pid}/net/dev"
                if os.path.exists(net_stats_path):
                    with open(net_stats_path, 'r') as f:
                        lines = f.readlines()

                    total_recv = 0
                    total_sent = 0

                    for line in lines[2:]:  # Пропускаем заголовки
                        parts = line.split()
                        if len(parts) >= 10:
                            interface = parts[0].strip(':')
                            # Пропускаем loopback интерфейсы
                            if not interface.startswith('lo'):
                                total_recv += int(parts[1])  # receive bytes
                                total_sent += int(parts[9])  # transmit bytes

                stats[pid] = {
                    'name': proc.info['name'],
                    'user': proc.info['username'],
                    'recv': total_recv,
                    'sent': total_sent
                }

            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue

    except Exception as e:
        print(f"Ошибка при получении статистики сети: {e}")

    return stats


def get_system_network_stats():
    """Общая сетевая статистика системы"""
    return psutil.net_io_counters(pernic=True)