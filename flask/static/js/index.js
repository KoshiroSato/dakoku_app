function disableMe(button) {
  button.disabled = true;
}

function reactivateCancelButton() {
  const cancel_button = document.getElementById('buttonA');
  if (cancel_button.disabled) {
    cancel_button.disabled = false;
  }
}

function alertFunc() {
  alert('打刻されました。');
}

function cancelAlertFunc() {
  alert('直前の打刻は取り消しされました。');
}

document.getElementById('start_btn').addEventListener('click', alertFunc);
document.getElementById('end_btn').addEventListener('click', alertFunc);
document.getElementById('break_btn').addEventListener('click', alertFunc);
document.getElementById('restart_btn').addEventListener('click', alertFunc);
document.getElementById('cancel_btn').addEventListener('click', cancelAlertFunc)
