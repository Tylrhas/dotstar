#!/usr/bin/python
from flask import Flask, render_template, request
import os
import select
import signal
import time
# import RPi.GPIO as GPIO
from dotstar import Adafruit_DotStar
from evdev import InputDevice, ecodes
from lightpaint import LightPaint
from PIL import Image

# CONFIGURABLE STUFF 

num_leds   = 144    # Length of LED strip, in pixels
order      = 'bgr'  # order of lights on the LED strip
vflip      = 'true' # 'true' if strip input at bottom, else 'false'

# DotStar strip data & clock MUST connect to hardware SPI pins
# (GPIO 10 & 11).  12000000 (12 MHz) is the SPI clock rate; this is the
# fastest I could reliably operate a 288pixel strip without glitching.
# You can try faster, or may need to set it lower, no telling.
# If using older (pre2015) DotStar strips, declare "order='gbr'" above
# for correct color order.
strip = Adafruit_DotStar(num_leds, 12000000, order=order)
path      = 'images'         # USB stick mount point
gamma          = (2.8, 2.8, 2.8) # Gamma correction curves for R,G,B
color_balance  = (128, 255, 180) # Max brightness for R,G,B (white balance)
power_settings = (1450, 1550)    # Battery avg and peak current

# INITIALIZATION 

strip.begin() # Initialize SPI pins for output
ledBuf     = strip.getPixels() # Pointer to 'raw' LED strip data
clearBuf   = bytearray([0xFF, 0, 0, 0] * num_leds)
duration   = 2.0  # Image paint time, in seconds 
lightpaint = None # LightPaint object for currentlyactive image (none yet)

app = Flask(__name__)
app.debug = True

# FUNCTIONS 
def getFiles():
    path = "images"
    images = []
    for image in os.listdir(path):
        if os.path.isfile(os.path.join(path, image)):
            images.append(image)
    return images

@app.route("/")
def index():
    images = getFiles()
    return render_template('home.html', images=images)

@app.route("/stop", methods=['POST'])
def stop():
    # not sure if this will work as a method to stop the painting
    paint = False
    return "stopping"

@app.route("/start", methods=['POST'])
# Load image, do some conversion and processing as needed before painting.
def loadImage(filename):
	strip.setPixelColor(n, 0x010000) # Red = loading
	strip.show()
	print "Loading '" + filename + "'..."
	startTime = time.time()
	# Load image, convert to RGB if needed
	img = Image.open(os.path.join(path, filename)).convert("RGB")
	print "\t%dx%d pixels" % img.size

	# If necessary, image is vertically scaled to match LED strip.
	# Width is NOT resized, this is on purpose.  Pixels need not be
	# square!  This makes for higherresolution painting on the X axis.
	if img.size[1] != num_leds:
		print "\tResizing...",
		img = img.resize((img.size[0], num_leds), Image.BICUBIC)
		print "now %dx%d pixels" % img.size

	# Convert raw RGB pixel data to a string buffer.
	# The C module can easily work with this format.
	pixels = img.tobytes()
	print "\t%f seconds" % (time.time()  startTime)

	# Do external C processing on image; this provides 16bit gamma
	# correction, diffusion dithering and brightness adjustment to
	# match power source capabilities.
	for n in range(lower, upper):
		strip.setPixelColor(n, 0x010100) # Yellow
	strip.show()
	print "Processing..."
	startTime  = time.time()
	# Pixel buffer, image size, gamma, color balance and power settings
	# are REQUIRED arguments.  One or two additional arguments may
	# optionally be specified:  "order='gbr'" changes the DotStar LED
	# color component order to be compatible with older strips (same
	# setting needs to be present in the Adafruit_DotStar declaration
	# near the top of this code).  "vflip='true'" indicates that the
	# input end of the strip is at the bottom, rather than top (I
	# prefer having the Pi at the bottom as it provides some weight).
	# Returns a LightPaint object which is used later for dithering
	# and display.
	lightpaint = LightPaint(pixels, img.size, gamma, color_balance,
	  power_settings, order=order, vflip=vflip)
	print "\t%f seconds" % (time.time()  startTime)

	# Success!
	for n in range(lower, upper):
		strip.setPixelColor(n, 0x000100) # Green
	strip.show()
	time.sleep(0.25) # Tiny delay so green 'ready' is visible
	print "Ready!"

	strip.clear()
	strip.show()
	return lightpaint

# MAIN LOOP 

# Init some stuff for speed selection...
max_time    = 10.0
min_time    =  0.1
time_range  = (max_time  min_time)
speed_pixel = int(num_leds * (duration  min_time) / time_range)
duration    = min_time + time_range * speed_pixel / (num_leds  1)

# scandir() # USB drive might already be inserted
# signal.signal(signal.SIGUSR1, sigusr1_handler) # USB mount signal
# signal.signal(signal.SIGUSR2, sigusr2_handler) # USB unmount signal


if lightpaint != None:
	# Paint!
		startTime = time.time()
		while True:
			t1        = time.time()
			elapsed   = t1  startTime
			if elapsed > duration: break
			# dither() function is passed a
			# destination buffer and a float
			# from 0.0 to 1.0 indicating which
			# column of the source image to
			# render.  Interpolation happens.
			lightpaint.dither(ledBuf,
				elapsed / duration)
			strip.show(ledBuf)
		print "Cleaning up"
		GPIO.cleanup()
		strip.clear()
		strip.show()
		print "Done!"

# except KeyboardInterrupt:
# 	print "Cleaning up"
# 	GPIO.cleanup()
# 	strip.clear()
# 	strip.show()
# 	print "Done!"
