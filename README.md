# dakoku_app

http://dakokuapp.com/

勤怠管理アプリ。

退勤時間を機械学習モデルが予測する。

![dakoku_app_screen_shot.png](img/dakoku_app_screen_shot.png)

## Overview

![overview.png](img/overview.png)

## Database

### `stamp`テーブル

出退勤の時刻や休憩時間から実労働時間を計算して保存するテーブル

| カラム名           | データ型              | 説明                     |
| -------------- | ----------------- | ---------------------- |
| `id`           | INTEGER（主キー・自動採番） | 各レコードを一意に識別するID        |
| `start`        | TEXT              | 出勤時刻                        |
| `end`          | TEXT              | 退勤時刻                        |
| `break`        | TEXT              | 休憩開始（中断）時刻                     |
| `restart`      | TEXT              | 休憩終了（再開）時刻              |
| `working_time` | INTEGER           | 実労働時間（秒単位）              |

### `info`テーブル

`stamp`テーブルと1対1で対応して、打刻日ごとの天候や気温などの外部要因を保存するテーブル

| カラム名             | データ型         | 説明                                   |
| ---------------- | ------------ | ------------------------------------ |
| `id`             | INTEGER（主キー） | `stamp.id` と対応するためのキー     |
| `month`          | NUMERIC      | 月（1〜12）                              |
| `day`            | NUMERIC      | 日（1〜31）                              |
| `weekday`        | TEXT         | 曜日                                  |
| `season`         | TEXT         | 季節                                  |
| `weather_code`   | NUMERIC      | 天気コード                             |
| `max_precip_avg` | REAL         | 当日の最大降水確率                   |
| `min_precip_avg` | REAL         | 当日の最小降水確率                   |
| `max_temp_avg`   | REAL         | 当日の最高気温                     |
| `min_temp_avg`   | REAL         | 当日の最低気温                     |


## Usage

セッション管理用のシークレットキーを環境変数として`.env`で用意。

### `.env` 

```
export SECRET_KEY=YOUR_SECRET_KEY
```

アプリの起動。

```
$ docker-compose up -d --build
```

## Running Tests

testコンテナにexecして

```
$ docker-compose exec test bash
```
実行
```
# pytest test
```