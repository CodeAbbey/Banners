import flask
import urllib2
import re
import time
from google.appengine.ext import db

import datetime
import StringIO
import random
import json

from random import randint

from UserBadge import UserBadge, RankCodeAbbey

app = flask.Flask(__name__)
app.config['DEBUG'] = False


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
		data = json.load(api_response, encoding = 'utf-8')
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
			solved = int(data['solved'])
		except KeyError as e:
			user_badge.AddNumSolved(-1)
		else
			user_badge.AddNumSolved(solved)

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

