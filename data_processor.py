import pandas as pd
from collections import defaultdict
from system_utils import get_dns_name


class NetworkData:
    def __init__(self):
        self.connections = []
        self.traffic_stats = defaultdict(lambda: {'sent': 0, 'recv': 0, 'name': 'Unknown', 'user': 'Unknown'})
        self.prev_traffic = defaultdict(lambda: {'sent': 0, 'recv': 0})
        self.current_rates = defaultdict(lambda: {'sent_rate': 0, 'recv_rate': 0})

    def update_connections(self, new_connections):
        # Добавляем DNS имена к соединениям
        for conn in new_connections:
            conn['remote_host'] = get_dns_name(conn['remote_ip'])
        self.connections = new_connections

    def update_traffic(self, new_stats):
        import time
        current_time = time.time()

        for pid, data in new_stats.items():
            # Расчет скорости передачи
            if pid in self.prev_traffic:
                time_diff = 1  # предполагаем 1 секунду между обновлениями
                sent_diff = data['sent'] - self.prev_traffic[pid]['sent']
                recv_diff = data['recv'] - self.prev_traffic[pid]['recv']

                self.current_rates[pid] = {
                    'sent_rate': sent_diff / time_diff,
                    'recv_rate': recv_diff / time_diff
                }

            self.prev_traffic[pid] = {'sent': data['sent'], 'recv': data['recv']}
            self.traffic_stats[pid].update(data)

    def get_app_traffic(self):
        """Суммарный трафик по приложениям"""
        app_traffic = defaultdict(lambda: {'sent': 0, 'recv': 0, 'sent_rate': 0, 'recv_rate': 0, 'user': ''})
        for pid, data in self.traffic_stats.items():
            app_traffic[data['name']]['sent'] += data['sent']
            app_traffic[data['name']]['recv'] += data['recv']
            app_traffic[data['name']]['sent_rate'] += self.current_rates[pid]['sent_rate']
            app_traffic[data['name']]['recv_rate'] += self.current_rates[pid]['recv_rate']
            app_traffic[data['name']]['user'] = data['user']
        return app_traffic

    def get_remote_connections(self):
        """Группировка подключений по удаленным IP"""
        remote_ips = defaultdict(list)
        for conn in self.connections:
            key = f"{conn['remote_ip']} ({conn['remote_host']})"
            remote_ips[key].append({
                'pid': conn['pid'],
                'name': conn['name'],
                'local_port': conn['local_port'],
                'protocol': conn['protocol'],
                'user': conn['user']
            })
        return remote_ips

    def get_connections_by_app(self):
        """Группировка подключений по приложениям"""
        app_conns = defaultdict(list)
        for conn in self.connections:
            app_conns[conn['name']].append({
                'pid': conn['pid'],
                'remote_ip': conn['remote_ip'],
                'remote_host': conn['remote_host'],
                'remote_port': conn['remote_port'],
                'protocol': conn['protocol'],
                'user': conn['user']
            })
        return app_conns