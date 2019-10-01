import paho.mqtt.client as mqtt

class MeasurementSender(mqtt):

	MQTT_BROKER_IP = "192.168.0.195"
	DEVICE_TYPE = "geigercounter"
	DEVICE_NAME = "gc_1"
	MEASUREMENT_TYPE = ("cpm", "uSvh")

	def __init__(self):
		self.topic = "/measurement/{}/{}".format(self.DEVICE_TYPE, self.DEVICE_NAME)
		self.mqttc = mqtt.Client(self.DEVICE_NAME)
		self.mqttc.loop_sart()

	def connect_with_broker(self):
		self.mqttc.connect(self.MQTT_BROKER_IP, 1883, 60)

	def disconnect(self):
		self.mqttc.disconnect()

	def send_out_measurement(self, data):
		for data_type in self.MEASUREMENT_TYPE:
			print(data_type)
			measurement_topic = "{}/{}".format(self.topic, data_type)
			print("xxx", measurement_topic)
			self.mqttc.publish(measurement_topic, data[data_type])


