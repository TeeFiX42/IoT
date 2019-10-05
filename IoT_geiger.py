from PiPocketGeiger import RadiationWatch
import time
import datetime
# from IoT_MQTT import MeasurementSender
import time

import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import threading
from subprocess import call


class ParseResult:
    BUTTON_STICK_TIME = 2
    SHUTDOWN_DELAY = 2

    def __init__(self):
        self.display_result = "on"
        self.send_mqtt = False
        self.instant_message = False
        self.wifi = True
        # self.mqttc = MeasurementSender
        self.show_information = OnScreen()
        self.show_information.wifi_on = True
        self.display_last_change = datetime.datetime.now()
        self.wifi_last_change = datetime.datetime.now()
        self.shutdown_button_last_change = None


    def reveal_result(self, data):
        if data == "radiation":
                self.show_information.first_text(text="CPM= {}".format(radiationWatch.status()["cpm"]))
                self.show_information.hit = True
        if data == "movement":
                self.show_information.wifi_on = True
                self.show_information.third_text(text="Movement detected!")
        '''
        if self.send_mqtt:
            # put here code to send result via MQTT
            self.mqttc.connect_with_broker()
            self.mqttc.send_out_measurement(radiationWatch.status())
        else:
            # put here code to disconnect from MQTT if you are connected.
            self.mqttc.disconnect()
            # perhaps we can disable wifi to save battery?
            pass
        '''

    def on_radiation(self):
        self.reveal_result(data="radiation")

    def on_noise(self):
        self.reveal_result(data="movement")

    def on_wifi(self):
        print("wifi knopje ingedrukt")
        time_diff = (datetime.datetime.now() - self.wifi_last_change).total_seconds()
        if time_diff >= self.BUTTON_STICK_TIME:
            self.toggle_wifi()

    def toggle_wifi(self):
        if self.wifi:
            print("disabling wifi")
            # call("sudo ifconfig wlan0 down", shell=True)
            self.wifi = False
        else:
            print("enabling wifi")
            # call("sudo ifconfig wlan0 up", shell=True)
            self.wifi = True
        self.show_information.wifi_on = self.wifi
        self.wifi_last_change = datetime.datetime.now()

    def on_display(self):
        print("display knopje ingedrukt")
        print("current state: ", self.show_information.display_state)
        # prevent multiple callbacks generating mutliple on/off/on triggers:

        time_diff = (datetime.datetime.now() - self.display_last_change).total_seconds()
        if time_diff >= self.BUTTON_STICK_TIME:
            if self.show_information.display_state == "on":
                self.show_information.display_state = "off"
                self.display_last_change = datetime.datetime.now()
            else:
                self.show_information.display_state = "on"
                self.display_last_change = datetime.datetime.now()
            self.reveal_result(data="dummy")

    def on_shutdown(self):
        print("shutdown knopje ingedrukt")
        # shutdown button must be pressed long time (to avoid mis-intended clicks.)
        if self.shutdown_button_last_change is None:
            self.shutdown_button_last_change = datetime.datetime.now()
        elif (datetime.datetime.now() - self.shutdown_button_last_change).total_seconds() > 3:
            self.shutdown_button_last_change = None
        else:
            time_diff = (datetime.datetime.now() - self.shutdown_button_last_change).total_seconds()
            if time_diff >= self.SHUTDOWN_DELAY:
                self.shutdown()

    def shutdown(self):
        self.show_information.third_text(text="Bye Bye ...")
        time.sleep(3)
        self.show_information.display_state = "off"
        call("sudo shutdown -h now", shell=True)


class OnScreen:
    def __init__(self):
        self.display = OLED()
        # boolean to indicate if a measurement is active.
        self.measurement_running = False
        # boolean to indicate if we WiFi is on
        self.wifi_on = False
        # boolean to indicate if we are connected with wifi
        self.wifi_connected = False
        # boolean to indicate if we are connected to MQTT broker
        self.mqtt_connected = False
        # value to turn on or off the display
        self.display_state = "on"
        self.text1 = "Initiating"
        self.text2 = ""
        self.text3 = ""
        self.text3_time = datetime.datetime.now()
        self.text3_timeout = 3
        self.hit = False
        # position info for 2nd line
        self.line2_pos = 0
        self.line2_max_pos = 125
        x = threading.Thread(target=self.draw_on_screen)
        x.start()


    def print_line1(self):
        line1 = "{}".format(self.text1)
        return line1

    def print_line2(self):
        to_show = "_"
        if self.hit:
            to_show = "#"
            self.hit = False
        if self.line2_pos > self.line2_max_pos:
            self.line2_pos = 0
        else:
            self.line2_pos += 5
        return to_show

    def print_line3(self):
        line2 = "{}".format(self.text3)
        return line2

    def first_text(self, text):
        self.text1 = text
        return

    def second_text(self, text):
        self.text2 = text

    def third_text(self, text):
        self.text3 = text
        self.text3_time = datetime.datetime.now()

    def print_wifi_status(self):
        if self.wifi_connected:
            return "WC"
        elif self.wifi_on:
            return "W"
        else:
            return ""

    def print_mqtt_status(self):
        if self.mqtt_connected:
            return "MC"
        else:
            return ""

    def black_screen(self):
        self.display.all_oled_out()

    def draw_on_screen(self):
        '''
        This function needs to run continuously. it will update the displayed information.
        Just thread this one.
        :return:
        '''
        while True:
            # line 3 contains temporary status messages, they should appear after a timeout value.
            if (self.text3_time + datetime.timedelta(seconds=self.text3_timeout)) < datetime.datetime.now():
                self.text3 = ""

            self.display.text_oled(text1=self.print_line1(),
                                   text2=self.print_line2(),
                                   pos2=self.line2_pos,
                                   text3=self.print_line3(),
                                   wifi=self.print_wifi_status(),
                                   mqtt=self.print_mqtt_status(),
                                   display_state=self.display_state
                                   )
            # time.sleep(0.5)


class OLED:
    def __init__(self):
        # Raspberry Pi pin configuration:
        RST = 21  # on the PiOLED this pin isnt used

        # 128x32 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        print(self.width)
        print(self.height)
        self.image = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        self.verticaltop = padding
        self.verticalbottom = self.height - padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.left = 0

        # Load default font.
        # self.font = ImageFont.load_default()
        self.font = ImageFont.truetype("OpenSans-Bold.ttf", 12)
        self.font2 = ImageFont.truetype("OpenSans-Bold.ttf", 9)
        # define vertical position of each line.
        self.vline1 = self.verticaltop - 2
        self.vline2 = self.verticaltop + 10
        self.vline3 = self.verticaltop + 18

    def text_oled(self, text1="", text2="", pos2= 0, text3="", wifi="", mqtt="", display_state="on"):
        # empty the upper and lower part of the display
        self.draw.rectangle((0, 0, self.width -1, self.vline2 + 3), outline=0, fill=0)
        self.draw.rectangle((0, self.vline3 + 4, self.width - 1, self.height), outline=0, fill=0)
        # empty the next position on line 2.
        self.draw.rectangle((pos2, self.vline2 + 4, pos2 + 10, self.height), outline=0, fill=0)

        # Here we position the different fields to display
        self.draw.text((self.left, self.vline1), text1, font=self.font, fill=255)
        self.draw.text((pos2, self.vline2), text2, font=self.font2, fill=255)
        self.draw.text((self.left, self.vline3), text3, font=self.font, fill=255)
        self.draw.text((self.left + 115, self.vline1), wifi, font=self.font, fill=255)
        self.draw.text((self.left + 115, self.vline3), mqtt, font=self.font, fill=255)
        if display_state == "off":
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # show the fields on the screen.
        self.disp.image(self.image)
        self.disp.display()


class ButtonHandler(OnScreen):
    SHUTDOWN = "shutdown"
    MQTT = "mqtt"
    WIFI = "wifi"

    def __init__(self):
        super().__init__(self)
        self.gpio_pin = None
        self.action = None

    def trigger(self):
        if self.action == self.WIFI:
            self.action_wifi()
        elif self.action == self.MQTT:
            self.action_mqtt()
        elif self.action == self.SHUTDOWN:
            self.action_shutdown()


    def action_wifi(self):
        pass

    def action_mqtt(self):
        pass

    def action_shutdown(self):
        pass


if __name__ == "__main__":

    start = datetime.datetime.now()
    # sender = MeasurementSender()
    reporter = ParseResult()
    reporter.send_mqtt = True
    reporter.display_result = True
    reporter.instant_message = True

    with RadiationWatch(radiation_pin=24, noise_pin=23, shutdown_pin=26, wifi_pin=19, display_pin=13) as radiationWatch:
        reporter.show_information.first_text(text="CPM= waiting")
        radiationWatch.register_radiation_callback(reporter.on_radiation)
        radiationWatch.register_noise_callback(reporter.on_noise)
        radiationWatch.register_display_callback(reporter.on_display)
        radiationWatch.register_wifi_callback(reporter.on_wifi)
        radiationWatch.register_shutdown_callback(reporter.on_shutdown)
        while True:
            print("xxx")
            time.sleep(1)
            time_delta = (datetime.datetime.now() - start).total_seconds()
            '''
            if time_delta > 600:
                sender.connect_with_broker()
                sender.send_out_measurement(radiationWatch.status())
                # reset the stats for the next period.
                start = datetime.datetime.now()
                radiationWatch.radiation_count = 0
                radiationWatch.noise_count = 0
                radiationWatch.count = 0
                radiationWatch.duration = 0
            '''
