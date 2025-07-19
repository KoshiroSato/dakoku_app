import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from module import DatabaseManager, StampManager
from utils import format_leave_time, seconds_to_minutes


def categorical_encoder(df, mode='train'):
    categorical_cols = ['month', 'day', 'weekday', 'season', 'weather_code']
    encoders = {}
    if mode == 'train':
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].values)
            encoders[col] = le
        joblib.dump(encoders, 'output/label_encoders.pkl')
    elif mode == 'test':
        encoders = joblib.load('output/label_encoders.pkl')
        for col in categorical_cols:
            df[col] = encoders[col].transform(df[col].values)
    return df


class CreateDataset:
    '''
    機械学習用の訓練、テストデータセット作成
    '''
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_train_dataset(self):
        with self.db_manager.get_connection() as conn:
            train_df = pd.read_sql(
                'SELECT * FROM stamp JOIN info ON stamp.id = info.id;', 
                conn
                )
        train_df.drop(columns=['id', 'start', 'end', 'break', 'restart'], inplace=True)
        train_df.drop_duplicates(inplace=True)
        # 学習データなので目的変数が空の場合はその行を削除
        train_df.dropna(subset=['working_time'], inplace=True)
        train_df = categorical_encoder(train_df, mode='train')
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

    def get_test_data(self):
        with self.db_manager.get_connection() as conn:
            query = '''
            SELECT * FROM stamp
            JOIN info ON stamp.id = info.id
            WHERE stamp.id = (SELECT MAX(id) FROM
            stamp);
            '''
            test_df = pd.read_sql(query, conn)
        test_df.drop(columns=['id', 'start', 'end', 'break', 'restart', 'working_time'], inplace=True)
        test_df = categorical_encoder(test_df, mode='test')
        # 欠損値補完
        transformer = joblib.load('output/transformer.pkl')
        X_test = transformer.transform(test_df)
        return X_test


class MLModel:
    def __init__(self, stamp_manager: StampManager, dataset: CreateDataset):
        self.stamp_manager = stamp_manager
        self.dataset = dataset
    
    def fitting(self):
        db_length = self.stamp_manager.get_record_length()
        if db_length >= 90:
            X_train, y_train = self.dataset.get_train_dataset()
            model = RandomForestRegressor(random_state=42)
            model.fit(X_train, y_train)
            joblib.dump(model, 'output/model.pkl')

    def predict(self):
        X_test = self.dataset.get_test_data()
        model = joblib.load('output/model.pkl')
        pred = model.predict(X_test)
        pred = pred.astype(int)
        pred = format_leave_time(int(pred))
        return pred