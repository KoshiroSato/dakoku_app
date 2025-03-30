import pandas as pd
from sklearn.preprocessing import LabelEncoder
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
    train_df.drop(columns=['id', 'start', 'end', 'break', 'restart', 'id.1'], inplace=True)
    train_df.drop_duplicates(inplace=True)
    train_df.dropna(how='any', inplace=True)
    train_df = categorical_encoder(train_df)
    train_df['duration'] = train_df['duration'].apply(seconds_to_minutes)
    y_train = train_df['duration']
    X_train = train_df.drop('duration', axis=1).to_numpy()
    return X_train, y_train