function alert_func() {
  alert('打刻されました。');
}

document.getElementById('start_btn').addEventListener('click', alert_func);
document.getElementById('end_btn').addEventListener('click', alert_func);
document.getElementById('break_btn').addEventListener('click', alert_func);
document.getElementById('restart_btn').addEventListener('click', alert_func);