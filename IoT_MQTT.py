import paho.mqtt.client as mqtt


class MySender:

	MQTT_BROKER_IP = "mqtt.ferdiland.be"
	DEVICE_NAME = "geigercounter_1"
	# MEASUREMENT_TYPE = ("cpm", "uSvh")
	MEASUREMENT_TYPE = "cpm"

	def __init__(self):
		self.topic = "event/measurement/{}".format(MySender.DEVICE_NAME)
		self.mqttc = mqtt.Client(MySender.DEVICE_NAME)
		self.mqttc.loop_start()

	def connect_with_broker(self):
		self.mqttc.connect(self.MQTT_BROKER_IP, 1883, 60)

	def disconnect(self):
		self.mqttc.disconnect()

	def send_out_measurement(self, data):
		measurement_topic = "{}/{}".format(self.topic, MySender.MEASUREMENT_TYPE)
		self.mqttc.publish(measurement_topic, data[MySender.MEASUREMENT_TYPE])


