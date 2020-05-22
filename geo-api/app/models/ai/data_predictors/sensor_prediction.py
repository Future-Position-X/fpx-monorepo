import numpy as np
import tensorflow as tf
import joblib

class SensorPrediction:
    @classmethod
    def make_prediction(self, sid, x_data, pred_len):
        model = tf.keras.models.load_model('app/assets/ml_models/sensor_' + str(sid) + '.h5')
        predictions = np.zeros(shape=(pred_len, 1), dtype=np.float32)
        y_scaler = joblib.load('app/assets/scalers/sensor_' + str(sid) + '.joblib')
        p_index = 0
        for i in range(len(x_data)-168-1):
            x_batch = np.zeros(shape=(1, 168, 24), dtype=np.float32)
            x_batch[0] = x_data[i:i+168]
            pred = y_scaler.inverse_transform(model.predict(x_batch).reshape(-1, 1))
            predictions[i] = pred[0]
            p_index = i
        for p in pred:
            if p_index < pred_len:
                predictions[p_index] = p      
            p_index += 1
        return predictions