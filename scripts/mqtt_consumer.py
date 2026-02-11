import paho.mqtt.client as mqtt
import psycopg2
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from config import BROKER_ADDR, TOPIC, MQTT_USER, MQTT_PASS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# def on_message(client, userdata, message):
#     payload = message.payload.decode("utf-8")
#     logger.info(f"Received: '{payload}' on topic '{message.topic}'")

#     parts = payload.split(';')
    
#     if len(parts) == 9 and parts[0] == "RawData":
#         # Sensor data: tag;timestamp;acc_z;acc_y;acc_x;gyro_z;gyro_y;gyro_x
#         try:
#             tag, timestamp, acc_z, acc_y, acc_x, gyro_z, gyro_y, gyro_x = parts
#             conn = psycopg2.connect(
#                 host="localhost",  # since running in WSL
#                 port=5432,
#                 user="app",
#                 password="app",
#                 database="appdb"
#             )
#             with conn.cursor() as cur:
#                 cur.execute(
#                     "INSERT INTO sensor_data (timestamp, acc_z, acc_y, acc_x, gyro_z, gyro_y, gyro_x) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                     (int(timestamp), float(acc_z), float(acc_y), float(acc_x), float(gyro_z), float(gyro_y), float(gyro_x))
#                 )
#                 conn.commit()
#             logger.info("Inserted sensor data")
#         except Exception as e:
#             logger.error(f"Failed to insert sensor data: {e}")
#         finally:
#             if 'conn' in locals():
#                 conn.close()
    
#     elif len(parts) == 10 and parts[0] == "Prediction":
#         # Prediction data: Tag;timestamp;file_path;predicted_activity;predicted_label;corrected_label;confidence;model_version;num_windows:is_correct
#         try:
#             tag, timestamp, file_path, predicted_activity, predicted_label, corrected_label, confidence, model_version, last_part = parts
#             num_windows, is_correct = last_part.split(':')
#             corrected_label = None if corrected_label == 'None' else int(corrected_label)
#             conn = psycopg2.connect(
#                 host="localhost",  # since running in WSL
#                 port=5433,
#                 user="app",
#                 password="app",
#                 database="appdb2"
#             )
#             with conn.cursor() as cur:
#                 cur.execute(
#                     "INSERT INTO predictions (timestamp, file_path, predicted_activity, predicted_label, corrected_label, confidence, model_version, num_windows, is_correct) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
#                     (timestamp, file_path, predicted_activity, int(predicted_label), corrected_label, confidence, model_version, int(num_windows), is_correct)
#                 )
#                 conn.commit()
#             logger.info("Inserted prediction data")
#         except Exception as e:
#             logger.error(f"Failed to insert prediction data: {e}")
#         finally:
#             if 'conn' in locals():
#                 conn.close()
#     else:
#         logger.warning(f"Unknown message format: {payload}")
def on_connect(client, userdata, flags, reason_code, properties):
    logger.info(f"Connected to broker with reason_code={reason_code}")
    client.subscribe(TOPIC, qos=1)
    logger.info(f"Subscribe requested to topic: {TOPIC}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    logger.info(f"Subscribed: mid={mid}, reason_codes={reason_code_list}")


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    logger.info(f"Received: '{payload}' on topic '{message.topic}'")

    msg_type, sep, rest = payload.partition(";")
    if sep == "":
        logger.warning(f"Unknown message format (no ';'): {payload}")
        return

    if msg_type == "RawData":
        # Expected:
        # RawData;timestamp;acc_z;acc_y;acc_x;gyro_z;gyro_y;gyro_x
        fields = rest.split(";")
        if len(fields) != 7:
            logger.warning(f"Bad RawData format (expected 7 fields after tag, got {len(fields)}): {payload}")
            return

        try:
            timestamp, acc_z, acc_y, acc_x, gyro_z, gyro_y, gyro_x = fields

            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="app",
                password="app",
                database="appdb"
            )
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sensor_data
                    (timestamp, acc_z, acc_y, acc_x, gyro_z, gyro_y, gyro_x)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (int(timestamp), float(acc_z), float(acc_y), float(acc_x),
                     float(gyro_z), float(gyro_y), float(gyro_x))
                )
                conn.commit()
            logger.info("Inserted sensor data")

        except Exception as e:
            logger.error(f"Failed to insert sensor data: {e}")

        finally:
            if 'conn' in locals():
                conn.close()

    elif msg_type == "Prediction":
        # Expected:
        # Prediction;timestamp;file_path;predicted_activity;predicted_label;corrected_label;confidence;model_version;num_windows:is_correct
        fields = rest.split(";")
        if len(fields) != 8:
            logger.warning(f"Bad Prediction format (expected 8 fields after tag, got {len(fields)}): {payload}")
            return

        try:
            timestamp, file_path, predicted_activity, predicted_label, corrected_label, confidence, model_version, last_part = fields

            if ":" not in last_part:
                logger.warning(f"Bad Prediction tail (expected num_windows:is_correct): {payload}")
                return

            num_windows, is_correct = last_part.split(":", 1)

            corrected_label = None if corrected_label == "None" else int(corrected_label)

            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                user="app",
                password="app",
                database="appdb2"
            )
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO predictions
                    (timestamp, file_path, predicted_activity, predicted_label,
                     corrected_label, confidence, model_version, num_windows, is_correct)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (timestamp, file_path, predicted_activity, int(predicted_label),
                     corrected_label, confidence, model_version, int(num_windows), is_correct)
                )
                conn.commit()
            logger.info("Inserted prediction data")

        except Exception as e:
            logger.error(f"Failed to insert prediction data: {e}")

        finally:
            if 'conn' in locals():
                conn.close()

    else:
        logger.warning(f"Unknown message type '{msg_type}': {payload}")



# def main():
#     #subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="MQTT_Consumer")
#     subscriber = mqtt.Client(client_id="MQTT_Consumer")
#     subscriber.username_pw_set(MQTT_USER, MQTT_PASS)
#     subscriber.on_message = on_message
#     subscriber.connect(BROKER_ADDR)
#     subscriber.subscribe(TOPIC, qos=1)
#     logger.info("MQTT Consumer started")
#     subscriber.loop_forever()
def main():
    subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="MQTT_Consumer")
    subscriber.username_pw_set(MQTT_USER, MQTT_PASS)

    subscriber.on_connect = on_connect        # <-- add
    subscriber.on_subscribe = on_subscribe    # <-- add
    subscriber.on_message = on_message

    logger.info(f"Connecting to broker={BROKER_ADDR}, topic={TOPIC}")
    subscriber.connect(BROKER_ADDR)
    logger.info("MQTT Consumer started")
    subscriber.loop_forever()


if __name__ == "__main__":
    main()