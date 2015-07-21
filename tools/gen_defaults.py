from PIL import Image, ImageDraw, ImageFont
import cStringIO
import StringIO
import urllib
import urllib2
import json
import sys
import string

from UserBadge import *


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

ranks_to_enum_dict = {'peasant': RankCodeAbbey.PEASANT, 
					  'acolyte': RankCodeAbbey.ACOLYTE,
					  'believer': RankCodeAbbey.BELIEVER,
					  'follower': RankCodeAbbey.FOLLOWER,
					  'priest': RankCodeAbbey.PRIEST,
					  'fanatic': RankCodeAbbey.FANATIC,
					  'deacon': RankCodeAbbey.DEACON,
					  'bishop': RankCodeAbbey.BISHOP,
					  'stargazer': RankCodeAbbey.STARGAZER,
					  'the_doctor': RankCodeAbbey.THE_DOCTOR,
					  'frost_enchanter': RankCodeAbbey.FROST_ENCHANTER,
					  'cardinal': RankCodeAbbey.CARDINAL
					 }


def main():
	if(len(sys.argv) != 5):
		print "usage {} <default file> <icon> <output filename> <rank>".format(sys.argv[0])
		sys.exit()
	else:
		rank = sys.argv[4].lower()
		if rank not in ranks_to_enum_dict.keys():
			print "must enter valid rank"
			sys.exit()

		rank_text = string.replace(rank, '_', ' ')
		#switch rank to enum entry
		rank = ranks_to_enum_dict[rank]

		font_size = 12
		unicode_font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)

		font_allowable_width = 56
		font_allowable_height = 14
	
		while True:
			pr_w, pr_h = unicode_font.getsize(rank_text)
			if pr_w > font_allowable_width:
				font_size -= 1
				print font_size
				unicode_font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
			else:
				break

		print "text size {} * {}".format(pr_w, pr_h)
		font_color = rank_rgb_color_dict[rank]

		img = Image.open(sys.argv[1])
		draw = ImageDraw.Draw(img)
		icon = Image.open(sys.argv[2])

		img_width, img_height = img.size
		if(img_width != 200) or (img_height != 60):
			print "default image size must be 200*60"
			sys.exit()
		#change the size to fit within the limits of 56 by 56
		icon_height, icon_width = icon.size
		print icon_height, icon_width
		if icon_height != icon_width:
			print "must choose a square image for icon image"
			sys.exit()
		target_size = 42
		if icon_width != target_size:
			#we must resize the image
			icon = icon.resize((target_size, target_size), Image.BICUBIC)
			print icon.size

		centering_allowance = (font_allowable_width - target_size)/2
		border_width = 2
		icon_xo = img_width - border_width - centering_allowance - target_size
		img.paste(icon, (icon_xo, 2, icon_xo+target_size, 2+target_size), icon)

		#compute text centering allowances
		text_xo = img_width - font_allowable_width + (font_allowable_width - pr_w)/2
		text_yo =  border_width + target_size + (font_allowable_height- pr_h)/2

		draw.text((text_xo, text_yo), rank_text, font = unicode_font, fill = font_color)

		img.save(sys.argv[3], "PNG")


if __name__ == '__main__':
	main()