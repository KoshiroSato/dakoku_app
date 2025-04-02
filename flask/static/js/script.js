// サーバーにデータを送る関数
async function sendStamp(stamp_value) {
  try {
    const response = await fetch('/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({ stamp_value: stamp_value })
    });

    if (response.ok) {
      console.log(`${stamp_value} 打刻成功`);
      enableCancelButton();
      
      // stamp_valueが 'start' でない場合、アラートを出す
      if (stamp_value !== 'start') {
        alert('打刻されました。');
      }
    } else {
      console.error('送信失敗:', response.statusText);
      alert('打刻に失敗しました');
    }
  } catch (error) {
    console.error('通信エラー:', error);
    alert('サーバーと通信できません');
  }
}

// 取り消し送信
async function sendCancel() {
  try {
    const response = await fetch('/cancel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cancel_value: 'cancel' })
    });

    if (response.ok) {
      console.log('打刻取り消し成功');
      disableCancelButton();
      alert('直前の打刻は取り消しされました。');
    } else {
      console.error('送信失敗:', response.statusText);
      alert('取り消しに失敗しました');
    }
  } catch (error) {
    console.error('通信エラー:', error);
    alert('サーバーと通信できません');
  }
}

// 出勤打刻時実行
document.addEventListener('DOMContentLoaded', function () {
  var alertButton = document.getElementById('start_btn');

  alertButton.addEventListener('click', function () {
      alert('本日の業務を開始します。'); 
      window.location.href = '/predict'; // フラッシュメッセージをセットするエンドポイントへリダイレクト
  });

  if (messages.length > 0) {
      var messageBox = document.getElementById('flash-message');
      messageBox.textContent = messages.join('\n');
      messageBox.style.display = 'block'; // メッセージを表示

      // 5秒後にフェードアウト
      setTimeout(function () {
          messageBox.style.opacity = '0';
          setTimeout(function () {
              messageBox.style.display = 'none';
          }, 500);
      }, 5000);
  }
});

// ボタンの有効・無効制御
function enableCancelButton() {
  const cancel_button = document.getElementById('cancel_btn');
  cancel_button.disabled = false;
}

function disableCancelButton() {
  const cancel_button = document.getElementById('cancel_btn');
  cancel_button.disabled = true;
}

function downloadCSV() {
  window.location.href = '/download_csv'
}

// ボタンにイベントを設定
document.getElementById('start_btn').addEventListener('click', () => sendStamp('start'));
document.getElementById('end_btn').addEventListener('click', () => sendStamp('end'));
document.getElementById('break_btn').addEventListener('click', () => sendStamp('break'));
document.getElementById('restart_btn').addEventListener('click', () => sendStamp('restart'));
document.getElementById('cancel_btn').addEventListener('click', sendCancel);