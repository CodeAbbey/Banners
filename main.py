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

class RankCodeAbbey(object):
	PEASANT = 0
	ACOLYTE = 1
	BELIEVER = 2
	FOLLOWER = 3
	PRIEST = 4
	FANATIC = 5
	DEACON = 6
	BISHOP = 7
	STARGAZER = 8
	THE_DOCTOR = 9
	FROST_ENCHANTER = 10
	CARDINAL = 11

ranks_to_enum_dict = {'peasant': RankCodeAbbey.PEASANT, 
					  'acolyte': RankCodeAbbey.ACOLYTE,
					  'believer': RankCodeAbbey.BELIEVER,
					  'follower': RankCodeAbbey.FOLLOWER,
					  'priest': RankCodeAbbey.PRIEST,
					  'fanatic': RankCodeAbbey.FANATIC,
					  'deacon': RankCodeAbbey.DEACON,
					  'bishop': RankCodeAbbey.BISHOP,
					  'stargazer': RankCodeAbbey.STARGAZER,
					  'the doctor': RankCodeAbbey.THE_DOCTOR,
					  'frost enchanter': RankCodeAbbey.FROST_ENCHANTER,
					  'cardinal': RankCodeAbbey.CARDINAL
					 }

rank_rgb_color_dict = { RankCodeAbbey.PEASANT: (136, 136, 136),
						RankCodeAbbey.ACOLYTE: (68, 255, 68),
						RankCodeAbbey.BELIEVER: (0, 221, 221),
						RankCodeAbbey.FOLLOWER: (68, 68, 255),
						RankCodeAbbey.PRIEST: (221, 0, 221),
						RankCodeAbbey.FANATIC: (221, 221, 0),
						RankCodeAbbey.DEACON: (255, 153, 17),
						RankCodeAbbey.BISHOP: (255, 68, 68),
						RankCodeAbbey.STARGAZER: (68, 68, 255),
						RankCodeAbbey.THE_DOCTOR: (255, 153, 17),
						RankCodeAbbey.FROST_ENCHANTER: (0, 204, 238),
						RankCodeAbbey.CARDINAL: (135, 0, 170),
						'default': (0, 0, 0)
				  }

rank_default_image_dict = {
	RankCodeAbbey.PEASANT: 'static/peasant.png',
	RankCodeAbbey.ACOLYTE: 'static/acolyte.png',
	RankCodeAbbey.BELIEVER: 'static/believer.png',
	RankCodeAbbey.FOLLOWER: 'static/follower.png',
	RankCodeAbbey.PRIEST: 'static/priest.png',
	RankCodeAbbey.FANATIC: 'static/fanatic.png',
	RankCodeAbbey.DEACON: 	'static/deacon.png',
	RankCodeAbbey.BISHOP: 	'static/bishop.png',
	RankCodeAbbey.STARGAZER: 'static/stargazer.png',
	RankCodeAbbey.THE_DOCTOR: 'static/the_doctor.png',
	RankCodeAbbey.FROST_ENCHANTER: 'static/frost_enchanter.png',
	RankCodeAbbey.CARDINAL: 'static/cardinal.png',
	'default': 'static/default.png'
}	


class UserBadge(object):
	def __init__(self, x_size, y_size, rank = 'default'):
		self.rank = rank
		self.width = x_size
		self.height = y_size
		#use the rank to determine which default to use
		try:
			background_filename = rank_default_image_dict[rank]
		except KeyError as e:
			background_filename = rank_default_image_dict['default']
		finally:
			self.img = Image.open(background_filename)
			self.draw = ImageDraw.Draw(self.img)

		#leave this stub in for now	to create arbitrary size images
		if rank == None:
			self.img = Image.new("RGB", (x_size, y_size), '#FFFFFF')
			self.draw = ImageDraw.Draw(self.img)
			#set this to default for use by the other derived fields
			self.rank = 'default'


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
		self.username_baseline_offset = self.height * 0.35
		self.username_height = 35


	def AddUserName(self, name, rank = "default"):
		#parameters to adjust name location and appearance
		name_font_size = 16
		try:
			name_font_color = rank_rgb_color_dict[self.rank]
		except KeyError as e:
			name_font_color = (0,0,0)

		#we are using this font just to test since it looks different
		#than system font, so we can know when it is working
		unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSerifCondensed-BoldItalic.ttf", name_font_size)
		while True:
			#dynamically determine the offset to have a relative placement in image
			(predicted_width, predicted_height) = unicode_font.getsize(name)
			if(predicted_width > self.username_allowed_width) and name_font_size > 0:
				name_font_size -= 2
				#clamp the output
				if(name_font_size < 0):
					name_font_size = 10
					name = "too long"
				unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSerifCondensed-BoldItalic.ttf", name_font_size)
			else:
				self.username_width = predicted_width
				self.username_height = predicted_height
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
		#Adjust this parameter to vary the spacing of the flag picture from baseline
		FLAG_FUDGE_FACTOR = 0.3
		#self.draw.line((0, self.username_baseline_offset, self.width, self.username_baseline_offset), fill = (0,0,0))
		self.flag_y_offest = max([0, int(self.username_baseline_offset - int(self.username_height * FLAG_FUDGE_FACTOR)- self.flag_height)])


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

	if api_response.getcode() != 200:
		return "service down", 205

	if api_response.headers.getheader('content-type') == 'application/json':
		data = json.load(api_response)
		if 'error' in data.keys():
			return data['error'], 400

		#we nee the rank for the constructor to choose default image
		try:
			rank_str = data['rank'].lower()
		except KeyError as e:
			rank = None
		else:
			try:
				rank = ranks_to_enum_dict[rank_str]
			except KeyError as e:
				rank = None 

		user_badge = UserBadge(200, 60, rank)
		#dirty hack right now to test functioning
		#user_badge = UserBadge(200, 60, 'default')

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

@app.route('/robots.txt', methods=['GET'])
def deny_all():
	response = flask.make_response(open('static/robots.txt').read())
  	response.headers["Content-type"] = "text/plain"
  	return response

@app.errorhandler(404)
def page_not_found(e):
	return 'Sorry, nothing at this URL.', 404

