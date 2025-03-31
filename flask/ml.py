import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from func import get_db_connection


def categorical_encoder(df):
    categorical_cols = ['weekday', 'season', 'weather_code']
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
    train_df.dropna(how='any', inplace=True)
    train_df = categorical_encoder(train_df)
    train_df['working_time'] = train_df['working_time'].apply(seconds_to_minutes)
    train_df.to_csv('output/train.csv', index=False)
    y_train = train_df['working_time']
    X_train = train_df.drop('working_time', axis=1).to_numpy()
    return X_train, y_train


def get_test_dataset():
    return X_test


def model_fitting():
    X_train, y_train = get_train_dataset()
    model = LinearRegression(n_jobs=-1)
    model.fit(X_train, y_train)
    joblib.dump(model, 'output/model.pkl')
    return model


def model_predict():
    X_test = get_test_dataset()
    model = joblib.load('output/model.pkl')
    pred = model.predict(X_test)
    return pred