import flask
import urllib2
import re
import time
from google.appengine.ext import db

import urllib
import urllib2
import json
import datetime
import StringIO
import random
from PIL import Image, ImageDraw
import cStringIO
from random import randint

app = flask.Flask(__name__)
app.config['DEBUG'] = False

@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/banner/<username>')
def prepare_banner(username):
	#github max user name is 39, and site only has max of 15 
	MAX_USER_NAME_LEN = 40
	if len(username) > MAX_USER_NAME_LEN:
		return "bad request", 400
	#TODO: More vaidation of username here

	#make a request to code abbey site
	code_abbey_api = 'http://www.codeabbey.com/index/api_user/'


	target_user = code_abbey_api + username
	print target_user

	req = urllib2.Request(target_user)
	api_response = urllib2.urlopen(req)
	print api_response.getcode()
	if api_response.getcode() != 200:
		return "service down", 205
	if api_response.headers.getheader('content-type') == 'application/json':
		data = json.load(api_response)
		print "foo"
		return str(data)


	return "hello world"
	#return "User {}".format(username)


@app.route("/simple.png")
def randgradient():
	img = Image.new("RGB", (300,300), "#FFFFFF")
	draw = ImageDraw.Draw(img)
	flag = Image.open('flags/us.gif')

	r,g,b = randint(0,255), randint(0,255), randint(0,255)
	dr = (randint(0,255) - r)/300.
	dg = (randint(0,255) - g)/300.
	db = (randint(0,255) - b)/300.
	for i in range(300):
		r,g,b = r+dr, g+dg, b+db
		draw.line((i,0,i,300), fill=(int(r),int(g),int(b)))

	#paste in the country flag
	(flag_x,flag_y) = flag.size
	img.paste(flag, (20, 20, 20+flag_x , 20+flag_y))

	f = cStringIO.StringIO()
	img.save(f, "PNG")

	response = flask.make_response(f.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response

	# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	# from matplotlib.figure import Figure
	# from matplotlib.dates import DateFormatter

	# fig=Figure()
	# ax=fig.add_subplot(111)
	# x=[]
	# y=[]
	# now=datetime.datetime.now()
	# delta=datetime.timedelta(days=1)
	# for i in range(10):
	# 	x.append(now)
	# 	now+=delta
	# 	y.append(random.randint(0, 1000))
	# ax.plot_date(x, y, '-')
	# ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
	# fig.autofmt_xdate()
	# canvas=FigureCanvas(fig)
	# png_output = StringIO.StringIO()
	# canvas.prandint_png(png_output)
	# response=make_response(png_output.getvalue())
	# response.headers['Content-Type'] = 'image/png'
	# return response
	return "hello world"


@app.errorhandler(404)
def page_not_found(e):
	return 'Sorry, nothing at this URL.', 404
