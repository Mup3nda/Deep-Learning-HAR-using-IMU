
import pandas as pd
import numpy as np
from scipy import signal
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_WINDOW_SIZE = 128
DEFAULT_OVERLAP = 0.5
UCI_CUT_OFF_FREQ = 0.3
UCI_FILTER_ORDER = 3

def load_data_csv(filepath) -> pd.DataFrame:

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    try:
        df = pd.read_csv(filepath, delimiter=',')
        if len(df.columns) == 1:
            df = pd.read_csv(filepath, delimiter=';')
        logger.info("✅ Loaded csv file succesfully")
        return df
    except:
        df = pd.read_csv(filepath, delimiter=';')
    print(f"Loaded {filepath}")
    
def convert_units(df, acc_in_ms2=True, gyro_in_deg_s=False)-> pd.DataFrame:
    '''Creating a sliding window'''
    if acc_in_ms2:
        df[['acc_x', 'acc_y', 'acc_z']] = df[['acc_x', 'acc_y', 'acc_z']] / 9.81
        logger.info("Converted to g-force")
    
    if gyro_in_deg_s:
        df[['gyro_x', 'gyro_y', 'gyro_z']] = df[['gyro_x', 'gyro_y', 'gyro_z']] * (np.pi/180)
        logger.info("Print converted to deg/s")
    
    return df


def create_window(df, window_size=DEFAULT_WINDOW_SIZE, overlap=DEFAULT_OVERLAP, sampling_rate=50) -> np.ndarray:

    if len(df) < window_size:
        raise ValueError(f"Need at least {window_size} samples, only got {len(df)}")
    # Don't need time
    required_columns = ['timestamp','acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        ValueError(f"Mising required colums: {missing}. Found only {list(df.columns)}")
    
    acc = df[['acc_x', 'acc_y', 'acc_z']].to_numpy()
    gyro = df[['gyro_x', 'gyro_y', 'gyro_z']].to_numpy()

    b, a = signal.butter(UCI_FILTER_ORDER, UCI_CUT_OFF_FREQ, btype='high', fs=sampling_rate)
    body_acc = np.zeros_like(acc)
    for i in range(3):
        body_acc[:,i] = signal.filtfilt(b, a, acc[:,i])
    
    
    total_acc = acc

    all_features = np.hstack([body_acc, gyro, total_acc])

    step_size = int(window_size * (1 - overlap))
    windows = []
    for start in range(0, len(all_features) - window_size + 1, step_size):
        window = all_features[start: start + window_size]
        windows.append(window)
    
    windows = np.array(windows, dtype=np.float32)
    logger.info(f"Created a window with {len(windows)} size of shape {windows.shape}")
    return windows

def preprocess_for_prediction(csv_file, input_hz = 100, target_hz = 50) -> np.ndarray:

    df = load_data_csv(csv_file)
    df = convert_units(df, acc_in_ms2=True, gyro_in_deg_s=False)
    df_clean = df.dropna()

    if input_hz != target_hz:
        downsampling_factor = input_hz // target_hz
        df_clean = df_clean.iloc[::downsampling_factor].reset_index(drop=True)

    windows = create_window(df_clean)

    return windows, df_clean


def main():
    walking = '../data/sensor_data/Recorded/walking_down3_20260122_192131.csv'
    logger.info("Testing...")    

    data = load_data_csv(walking)
    data = convert_units(data)
    windows = create_window(data)


if __name__ == '__main__':
    main()





