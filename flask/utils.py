from datetime import datetime, timedelta


def format_leave_time(minutes):
    now = datetime.now()
    leave_time = now + timedelta(minutes=minutes)
    return f'{leave_time.hour}時間{leave_time.minute}分'


def seconds_to_minutes(seconds):
    minutes = (seconds % 3600) // 60
    return minutes