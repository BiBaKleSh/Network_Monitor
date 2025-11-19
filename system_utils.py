import subprocess
import re

def get_dns_name(ip):
    """Получение DNS имени для IP-адреса"""
    try:
        if ip and ip not in ['0.0.0.0', '127.0.0.1', '::', '::1']:
            result = subprocess.run(['nslookup', ip],
                                  capture_output=True, text=True, timeout=2)
            if 'name =' in result.stdout:
                match = re.search(r'name = (.+)\.', result.stdout)
                if match:
                    return match.group(1)
    except:
        pass
    return ip

def get_protocol_name(port):
    """Получение имени протокола по порту"""
    common_ports = {
        80: 'HTTP', 443: 'HTTPS', 22: 'SSH', 53: 'DNS',
        25: 'SMTP', 110: 'POP3', 143: 'IMAP', 993: 'IMAPS',
        995: 'POP3S', 21: 'FTP', 23: 'TELNET', 587: 'SMTP',
        3306: 'MySQL', 5432: 'PostgreSQL', 27017: 'MongoDB'
    }
    return common_ports.get(port, f'port {port}')