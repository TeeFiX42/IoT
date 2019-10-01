from PiPocketGeiger import RadiationWatch
import time


def onRadiation():
	print("Ray appeared!")


def onNoise():
	print("Vibration! Stop moving!")


if __name__ == "__main__":
	with RadiationWatch(24, 23) as radiationWatch:
		radiationWatch.register_radiation_callback(onRadiation)
		radiationWatch.register_noise_callback(onNoise)
		while 1:
			time.sleep(1)
