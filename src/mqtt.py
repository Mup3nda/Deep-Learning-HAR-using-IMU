import paho.mqtt.client as mqtt
import time
import logging
from config import BROKER_ADDR, TOPIC, MQTT_USER, MQTT_PASS
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LABEL_INDEX = {
    "WALKING": 0,
    "WALKING_UPSTAIRS": 1,
    "WALKING_DOWNSTAIRS": 2,
    "SITTING": 3,
    "STANDING": 4,
    "LAYING": 5
}

class MQTTPublisher:
    def __init__(self, broker, topic, user, password, client_id="Gateway_Device"):
        #self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(user, password)
        self.broker = broker
        self.topic = topic

    def connect(self):
        try:
            self.client.connect(self.broker)
            self.client.loop_start()
            logger.info("Publisher connected to broker")
        except Exception as e:
            logger.error(f"Failed to connect publisher: {e}")
            raise

    def publish(self, message):
        try:
            info = self.client.publish(self.topic, message, qos=1)
            info.wait_for_publish()
            logger.info(f"Published: {message}")
        except Exception as e:
            logger.error(f"Failed to publish: {e}")
            raise

    def publish_sensor_data(self, tag, timestamp, acc_z, acc_y, acc_x, gyro_z, gyro_y, gyro_x):
        """Formats and publishes sensor data message."""
        message = f"{tag};{timestamp};{acc_z};{acc_y};{acc_x};{gyro_z};{gyro_y};{gyro_x}"
        self.publish(message)

    def publish_prediction(self, tag, timestamp, file_path, predicted_activity, predicted_label, corrected_label, confidence, model_version, num_windows, is_correct):
        """Formats and publishes prediction data message."""
        message = f"{tag};{timestamp};{file_path};{predicted_activity};{predicted_label};{corrected_label};{confidence};{model_version};{num_windows}:{is_correct}"
        self.publish(message)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Publisher disconnected")

class MQTTSubscriber:
    def __init__(self, broker, topic, user, password, on_message_callback, client_id="Local_Server"):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client.username_pw_set(user, password)
        self.client.on_message = on_message_callback
        self.broker = broker
        self.topic = topic

    def connect(self):
        try:
            self.client.connect(self.broker)
            logger.info("Subscriber connected to broker")
        except Exception as e:
            logger.error(f"Failed to connect subscriber: {e}")
            raise

    def subscribe(self):
        try:
            self.client.subscribe(self.topic, qos=1)
            logger.info(f"Subscribed to topic: {self.topic}")
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")
            raise

    def loop_start(self):
        self.client.loop_start()
        logger.info("Subscriber loop started")

    def loop_stop(self):
        self.client.loop_stop()
        logger.info("Subscriber loop stopped")

    def disconnect(self):
        self.client.disconnect()
        logger.info("Subscriber disconnected")


def example_publisher():
    """Example of using MQTTPublisher to send periodic test data."""
    publisher = MQTTPublisher(BROKER_ADDR, TOPIC, MQTT_USER, MQTT_PASS)
    publisher.connect()
    try:
        count = 1
        while True:
            test_data = f"IMU Burst Pakke nr {count}"
            publisher.publish(test_data)
            count += 1
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Publisher interrupted by user")
    finally:
        publisher.disconnect()

def example_subscriber():
    """Example of using MQTTSubscriber to listen for messages."""
    def on_message(client, userdata, message):
        payload = message.payload.decode("utf-8")
        logger.info(f"Received: '{payload}' on topic '{message.topic}' (QoS: {message.qos})")

    subscriber = MQTTSubscriber(BROKER_ADDR, TOPIC, MQTT_USER, MQTT_PASS, on_message)
    subscriber.connect()
    subscriber.subscribe()
    subscriber.loop_start()
    try:
        while True:
            time.sleep(1)  # Keep alive
    except KeyboardInterrupt:
        logger.info("Subscriber interrupted by user")
    finally:
        subscriber.loop_stop()
        subscriber.disconnect()

def raw_sensor_to_mqtt(sensor_data):
    """Example of formatting and publishing sensor data."""
    publisher = MQTTPublisher(BROKER_ADDR, TOPIC, MQTT_USER, MQTT_PASS)
    publisher.connect()
    try:
        # Test
        tag = "RawData"
        timestamp = 1867708643575376601
        acc_z = 0.0420989990234375
        acc_y = 0.0620880126953125
        acc_x = 0.990997314453125
        gyro_z = 0.03930852189660072
        gyro_y = -0.021207816898822784
        gyro_x = 0.69420 #05567098408937454
        
        # tag = 'RawData'
        # timestamp = sensor_data['timestamp']
        # acc_x = sensor_data['acc_x']
        # acc_y = sensor_data['acc_y']
        # acc_z = sensor_data['acc_z']
        # gyro_x = sensor_data['gyro_x']
        # gyro_y = sensor_data['gyro_y']
        # gyro_z = sensor_data['gyro_z']
        
        publisher.publish_sensor_data(tag, timestamp, acc_z, acc_y, acc_x, gyro_z, gyro_y, gyro_x)
        logger.info("✅ Raw sensor data has been sent!")
    finally:
        publisher.disconnect()

def prediction_to_mqtt(timestamp, file_path, pred_activity, confidence, model_version, num_windows):
    """Example of formatting and publishing prediction data."""
    publisher = MQTTPublisher(BROKER_ADDR, TOPIC, MQTT_USER, MQTT_PASS)
    publisher.connect()
    
    
    try:
        # Sample prediction data
        #tag = "Prediction"
        # timestamp = "2026-01-14T15:13:59.585793"
        # file_path = "./sensor_data/walking2_data.csv"
        # predicted_activity = "Aura farming"
        # predicted_label = 2
        #corrected_label = None
        # confidence = "0f0dad42"
        # model_version = "lstm_model_v002"
        #num_windows = 53
        #is_correct = None
        
        # Sample prediction data
        tag = "Prediction"
        pred_label = LABEL_INDEX[pred_activity]
        corrected_label = None
        is_correct = None
        
        publisher.publish_prediction(tag, timestamp, file_path, pred_activity, pred_label, corrected_label, confidence, model_version, num_windows, is_correct)
        logger.info("✅ Model prediction has been sent!")
    finally:
        publisher.disconnect()

if __name__ == "__main__":
    # Uncomment the one you want to test.
    pass
    # example_publisher()
    # example_subscriber()
    # raw_sensor_to_mqtt()
    # prediction_to_mqtt()