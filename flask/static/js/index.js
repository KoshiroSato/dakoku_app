function disableCancelButton(button) {
  button.disabled = true;
  alert('直前の打刻は取り消しされました。');
}

function enableCancelButton() {
  const cancel_button = document.getElementById('cancel_btn');
  cancel_button.disabled = false;
  alert('打刻されました。');
}