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
from PIL import Image, ImageDraw, ImageFont
import cStringIO
from random import randint

app = flask.Flask(__name__)
app.config['DEBUG'] = False

class UserBadge(object):
	def __init__(self, x_size, y_size):
		self.width = x_size
		self.height = y_size
		self.img = Image.new("RGB", (x_size, y_size), '#FFFFFF')
		self.draw = ImageDraw.Draw(self.img)

		self.padding = 5
		#configure square user image
		self.tb_size = 50
		self.tb_x_offset = self.width - self.tb_size - self.padding
		self.tb_y_offset = self.padding

		#configure size of flag
		self.flag_width = 16
		self.flag_height = 11
		self.flag_spacing = 5

		#configure size available for user name
		self.name_x_offset = self.padding
		self.username_allowed_width = self.width - self.name_x_offset - self.flag_spacing - self.flag_width - self.padding - self.tb_size - self.padding
		print "allowed width:", self.username_allowed_width
		self.username_baseline_offset = self.height * 0.35
		self.username_height = 35


	def AddUserName(self, name, rank = "default"):
		#parameters to adjust name location and appearance
		name_font_size = 16
		name_font_color = (0,0,0)

		#we are using this font just to test since it looks different
		#than system font, so we can know when it is working
		unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSerifCondensed-BoldItalic.ttf", name_font_size)
		while True:
			#dynamically determine the offset to have a relative placement in image
			(predicted_width, predicted_height) = unicode_font.getsize(name)
			print "predicted width:", predicted_width
			if(predicted_width > self.username_allowed_width) and name_font_size > 0:
				name_font_size -= 2
				#clamp the output
				if(name_font_size < 0):
					name_font_size = 10
					name = "too long"
				unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSerifCondensed-BoldItalic.ttf", name_font_size)
				print name_font_size
			else:
				self.username_width = predicted_width
				self.username_height = predicted_height
				print "new font size of {} chosen".format(name_font_size)
				break

		#compute the y offset to keep constant baseline position
		self.name_y_offest = max([0, (self.username_baseline_offset - predicted_height)])
		
		self.draw.text((self.name_x_offset, self.name_y_offest), name, font = unicode_font, fill = name_font_color)
	
	def AddCountryFlag(self, country):
		iso_country_codes = set(['BD', 'BE', 'BF', 'BG', 'BA', 'BB', 'WF', 'BM', 'BN', 'BO',
		 'BH', 'BI', 'BJ', 'BT', 'JM', 'BV', 'BW', 'WS', 'BR', 'BS', 'JE', 'BY', 'BZ',
		 'RU', 'RW', 'RS', 'TL', 'RE', 'TM', 'TJ', 'RO', 'TK', 'GW', 'GU', 'GT', 'GS', 
		 'GR', 'GQ', 'GP', 'JP', 'GY', 'GG', 'GF', 'GE', 'GD', 'GB', 'GA', 'GN', 'GM', 
		 'GL', 'GI', 'GH', 'OM', 'TN', 'JO', 'TA', 'HR', 'HT', 'HU', 'HK', 'HN', 'HM', 
		 'VE', 'PR', 'PW', 'PT', 'KN', 'PY', 'AI', 'PA', 'PF', 'PG', 'PE', 'PK', 'PH', 
		 'PN', 'PL', 'PM', 'ZM', 'EE', 'EG', 'ZA', 'EC', 'IT', 'VN', 'SB', 'ET', 'SO', 
		 'ZW', 'KY', 'ES', 'ER', 'ME', 'MD', 'MG', 'MA', 'MC', 'UZ', 'MM', 'ML', 'MO', 
		 'MN', 'MH', 'MK', 'MU', 'MT', 'MW', 'MV', 'MQ', 'MP', 'MS', 'MR', 'IM', 'UG', 
		 'MY', 'MX', 'IL', 'FR', 'AW', 'SH', 'AX', 'SJ', 'FI', 'FJ', 'FK', 'FM', 'FO', 
		 'NI', 'NL', 'NO', 'NA', 'VU', 'NC', 'NE', 'NF', 'NG', 'NZ', 'NP', 'NR', 'NU', 
		 'CK', 'CI', 'CH', 'CO', 'CN', 'CM', 'CL', 'CC', 'CA', 'CG', 'CF', 'CD', 'CZ', 
		 'CY', 'CX', 'CR', 'CV', 'CU', 'SZ', 'SY', 'KG', 'KE', 'SR', 'KI', 'KH', 'SV', 
		 'KM', 'ST', 'SK', 'KR', 'SI', 'KP', 'KW', 'SN', 'SM', 'SL', 'SC', 'KZ', 'SA', 
		 'SG', 'SE', 'SD', 'DO', 'DM', 'DJ', 'DK', 'VG', 'DE', 'YE', 'DZ', 'US', 'UY', 
		 'YT', 'UM', 'LB', 'LC', 'LA', 'TV', 'TW', 'TT', 'TR', 'LK', 'LI', 'LV', 'TO', 
		 'LT', 'LU', 'LR', 'LS', 'TH', 'TF', 'TG', 'TD', 'TC', 'LY', 'VA', 'AC', 'VC', 
		 'AE', 'AD', 'AG', 'AF', 'IQ', 'VI', 'IS', 'IR', 'AM', 'AL', 'AO', 'AN', 'AQ', 
		 'AS', 'AR', 'AU', 'AT', 'IO', 'IN', 'TZ', 'AZ', 'IE', 'ID', 'UA', 'QA', 'MZ'])
		if country in iso_country_codes:
			self.flag_name = 'flags/' + country.lower() + '.gif'

	def AddUserImage(self, url = None):
		#if there is not any images, use a default
		if url == None:
			df_tb = Image.new("RGB", (self.tb_size,self.tb_size), "#FFFFFF")
			df_tb_draw = ImageDraw.Draw(df_tb)

			r,g,b = randint(0,255), randint(0,255), randint(0,255)
			dr = (randint(0,255) - r)/self.tb_size
			dg = (randint(0,255) - g)/self.tb_size
			db = (randint(0,255) - b)/self.tb_size
			for i in range(self.tb_size):
				r,g,b = r+dr, g+dg, b+db
				df_tb_draw.line((i,0,i,self.tb_size), fill=(int(r),int(g),int(b)))

			self.img.paste(df_tb, (self.tb_x_offset, self.tb_y_offset, self.tb_x_offset+self.tb_size, self.tb_y_offset+self.tb_size))
		else:
			#TODO load image and resize
			pass

	def AddNumSolved(self, num_solved = 0):
		#error case num solved is ?
		if num_solved < 0:
			pass

	def RenderToBuffer(self):
		#render all of variable position boxes here at once
		self.flag_x_offset = int(self.name_x_offset + self.username_width + self.flag_spacing)
		self.flag_y_offest = int(self.username_baseline_offset - int(self.username_height/2) - int(self.flag_height * 0.7))

		flag_file = Image.open(self.flag_name)
		(flag_x,flag_y) = flag_file.size
		self.img.paste(flag_file, (self.flag_x_offset, self.flag_y_offest, self.flag_x_offset+flag_x , self.flag_y_offest+flag_y))

		#create buffer for output
		f = cStringIO.StringIO()
		self.img.save(f, "PNG")
		return f

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
	try:
		api_response = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		print e.code
		return "User with given URL not found", 400
	except urllib2.URLError as e:
		#we could not reach the server, so try again in a little bit
		#TODO: choose a better error code to indicate try again
		# or set a retry after header
		return "try again", 500

	print api_response.getcode()

	if api_response.getcode() != 200:
		return "service down", 205

	if api_response.headers.getheader('content-type') == 'application/json':
		data = json.load(api_response)
		if 'error' in data.keys():
			return data['error'], 400

		#validate the API
		api_fields = [""]
		user_badge = UserBadge(200, 60)
		
		try:
			country = data['country']
		except KeyError as e:
			#we do not add a country
			pass
		else:
			user_badge.AddCountryFlag(country)
		try:
			badge_username = data['username']
		except KeyError as e:
			#do not add a user name to the badge
			pass
		else:
			user_badge.AddUserName(badge_username)

		try:
			solved = data['solved']
		except KeyError as e:
			user_badge.AddNumSolved(-1)

		#add a dummy user pic
		user_badge.AddUserImage(url = None)
		#at end prepare the file
		f = user_badge.RenderToBuffer()

		response = flask.make_response(f.getvalue())
		response.headers['Content-Type'] = 'image/png'
		return response

	else:
		return "hello world"


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

@app.errorhandler(404)
def page_not_found(e):
	return 'Sorry, nothing at this URL.', 404
