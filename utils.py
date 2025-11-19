def format_bytes(bytes_num):
    """Форматирование байтов в человеко-читаемый вид"""
    if bytes_num == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} TB"


def format_speed(bytes_per_sec):
    """Форматирование скорости"""
    return format_bytes(bytes_per_sec) + "/s"