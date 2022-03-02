import paho.mqtt.client as mqtt


class MySender:

	MQTT_BROKER_IP = "mqtt.ferdiland.be"
	DEVICE_NAME = "geigercounter_1"
	# MEASUREMENT_TYPE = ("cpm", "uSvh")
	MEASUREMENT_TYPE = "cpm"

	def __init__(self):
		self.topic = "event/measurement/{}".format(MySender.DEVICE_NAME)
		self.mqttc = mqtt.Client(MySender.DEVICE_NAME)

	def send_out_measurement(self, data):
		measurement_topic = "{}/{}".format(self.topic, MySender.MEASUREMENT_TYPE)
		self.mqttc.publish(measurement_topic, data[MySender.MEASUREMENT_TYPE])


