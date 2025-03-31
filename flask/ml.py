import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from func import get_db_connection, get_record_length


def categorical_encoder(df):
    categorical_cols = ['month', 'day', 'weekday', 'season', 'weather_code']
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].values)
    return df


def seconds_to_minutes(seconds):
    minutes = (seconds % 3600) // 60
    return minutes


def get_train_dataset():
    with get_db_connection() as conn:
        train_df = pd.read_sql(
            'SELECT * FROM stamp JOIN info ON stamp.id = info.id;', 
            conn
            )
    train_df.drop(columns=['id', 'start', 'end', 'break', 'restart'], inplace=True)
    train_df.drop_duplicates(inplace=True)
    # 学習データなので目的変数が空の場合はその行を削除
    train_df.dropna(subset=['working_time'], inplace=True)
    train_df = categorical_encoder(train_df)
    train_df['working_time'] = train_df['working_time'].apply(seconds_to_minutes)
    train_df.to_csv('output/train.csv', index=False)
    y_train = train_df['working_time']
    X_train = train_df.drop('working_time', axis=1)
    # 欠損値補完
    transformer = ColumnTransformer(
        [
            ('num_imputer', SimpleImputer(strategy='mean'), ['max_precip_avg', 'min_precip_avg', 'max_temp_avg', 'min_temp_avg']), 
            ('cat_imputer', SimpleImputer(strategy='most_frequent'), ['month', 'day', 'weekday', 'season', 'weather_code'])
             ]
             )
    X_train = transformer.fit_transform(X_train)
    joblib.dump(transformer, 'output/transformer.pkl')
    return X_train, y_train


def get_test_data():
    with get_db_connection() as conn:
        query = '''
        SELECT 
            stamp.*,
            info.*
        FROM
            (SELECT * FROM stamp ORDER BY id DESC LIMIT 1) AS stamp
        JOIN
            (SELECT * FROM info ORDER BY id DESC LIMIT 1) AS info
        ON stamp.id = info.id;
        '''
        test_df = pd.read_sql(query, conn)
    test_df.drop(columns=['id', 'start', 'end', 'break', 'restart', 'working_time'], inplace=True)
    test_df = categorical_encoder(test_df)
    # 欠損値補完
    transformer = joblib.load('output/transformer.pkl')
    X_test = transformer.transform(test_df)
    return X_test


def model_fitting():
    db_length = get_record_length()
    if db_length >= 90:
        X_train, y_train = get_train_dataset()
        model = LinearRegression(n_jobs=-1)
        model.fit(X_train, y_train)
        joblib.dump(model, 'output/model.pkl')


def model_predict():
    X_test = get_test_data()
    model = joblib.load('output/model.pkl')
    pred = model.predict(X_test)
    pred = pred.astype(int)
    return int(pred)