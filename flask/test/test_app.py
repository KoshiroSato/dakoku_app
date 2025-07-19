import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, STAMP_DATES


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    with app.test_client() as client:
        yield client


def test_get_root(client):
    '''
    ルートにGETを送信して、正常にアクセスできるかを確認
    '''
    response = client.get('/')
    assert response.status_code == 200
    assert '打刻アプリ'.encode('utf-8') in response.data


def test_post_start_stamp(client):
    '''
    出勤打刻のテスト
    '''
    response = client.post('/', json={'stamp_value': 'start'})
    assert response.status_code == 200
    assert STAMP_DATES['start'] is not None


def test_invalid_break_before_start(client):
    '''
    出勤前に休憩打刻を押した場合に記録されないことをテスト
    '''
    STAMP_DATES['start'] = None
    response = client.post('/', json={'stamp_value': 'break'})
    assert response.status_code == 200
    assert STAMP_DATES['break'] is None


def test_cancel_stamp(client):
    '''
    打刻の取り消しのテスト
    '''
    with client.session_transaction() as sess:
        sess['just_before_stamp'] = 'start'
        STAMP_DATES['start'] = '2025-07-17'
    
    response = client.post('/cancel')
    assert response.status_code == 200
    assert STAMP_DATES['start'] is None


def test_csv_download(client):
    '''
    CSVダウンロードのテスト
    '''
    response = client.get('/download_csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'