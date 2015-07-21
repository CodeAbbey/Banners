import cStringIO
import json
from PIL import Image, ImageDraw, ImageFont
import string
import StringIO
import urllib
import urllib2

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

class UserBadge(object):
    def __init__(self, x_size, y_size, rank = 'default'):
        self.rank = rank
        self.W = x_size
        self.H = y_size
        #store the colors
        self.rank_rgb_color_dict = { RankCodeAbbey.PEASANT: (136, 136, 136),
            RankCodeAbbey.ACOLYTE: (68, 255, 68),
            RankCodeAbbey.BELIEVER: (0, 221, 221),
            RankCodeAbbey.FOLLOWER: (68, 68, 255),
            RankCodeAbbey.PRIEST: (221, 0, 221),
            RankCodeAbbey.FANATIC: (255, 196, 0),
            RankCodeAbbey.DEACON: (255, 153, 17),
            RankCodeAbbey.BISHOP: (255, 68, 68),
            RankCodeAbbey.STARGAZER: (68, 68, 255),
            RankCodeAbbey.THE_DOCTOR: (255, 153, 17),
            RankCodeAbbey.FROST_ENCHANTER: (0, 204, 238),
            RankCodeAbbey.CARDINAL: (135, 0, 170),
            'default': (0, 0, 0)
            }

        if RankCodeAbbey.PEASANT <= rank <= RankCodeAbbey.CARDINAL:
            background_filename = 'static/rank' + str(rank) + '.png'
        else:
            background_filename = 'static/default.png'

        self.img = Image.open(background_filename)
        self.draw = ImageDraw.Draw(self.img)

        #leave this stub in for now to create arbitrary size images
        if rank == None:
            self.img = Image.new("RGB", (x_size, y_size), '#FFFFFF')
            self.draw = ImageDraw.Draw(self.img)
            #set this to default for use by the other derived fields
            self.rank = 'default'

        self.pad = 5
        #configure square user image
        self.tb_sz = 45
        self.tb_xo = self.W - self.tb_sz - self.pad
        self.tb_yo = self.pad

        #configure size of flag
        self.flg_W = 16
        self.flg_H = 11
        self.flag_spacing = 5

        #configure size available for user name
        self.nm_xo = self.pad
        self.nm_yo = self.pad
        self.un_allow_width = (self.W - self.nm_xo - \
                            self.flag_spacing - self.flg_W - self.pad \
                             - self.tb_sz - self.pad)
        self.usernm_baseline_offset = self.H * 0.35
        self.usernm_height = 35

    def AddUserName(self, name, rank = "default"):
        #parameters to adjust name location and appearance
        nm_fnt_sz = 14
        try:
            nm_fnt_color = self.rank_rgb_color_dict[self.rank]
        except KeyError as e:
            nm_fnt_color = (0,0,0)

        #we are using this font just to test since it looks different
        #than system font, so we can know when it is working
        unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSans-Bold.ttf", nm_fnt_sz)
        while True:
            #dynamically determine the offset for relative placement in image
            (pr_width, pr_height) = unicode_font.getsize(name)
            if(pr_width > self.un_allow_width) and nm_fnt_sz > 12:
                nm_fnt_sz -= 1
                unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSansCondensed-Bold.ttf", nm_fnt_sz)
            else:
                #check for case where we have to truncate
                
                while True:
                    if(pr_width > self.un_allow_width) and len(name) > 0:
                        (pr_width, pr_height) = unicode_font.getsize(name)
                        #truncate the string by one
                        name = name[:-1]
                    else:
                        break

                self.usernm_width = pr_width
                self.usernm_height = pr_height
                break

        #compute the y offset to keep constant baseline position
        # self.nm_yo = max([0, (self.usernm_baseline_offset - pr_height)])
        self.nm_yo = (self.pad + (self.usernm_baseline_offset - pr_height))/2
        self.draw.text((self.nm_xo, self.nm_yo), name, 
                        font = unicode_font, fill = nm_fnt_color)
    
    def AddCountryFlag(self, country):
        iso_country_codes = set(['BD', 'BE', 'BF', 'BG', 'BA', 'BB', 'WF', 
            'BM', 'BN', 'BO', 'BH', 'BI', 'BJ', 'BT', 'JM', 'BV', 'BW', 'WS',
            'BR', 'BS', 'JE', 'BY', 'BZ', 'RU', 'RW', 'RS', 'TL', 'RE', 'TM',
            'TJ', 'RO', 'TK', 'GW', 'GU', 'GT', 'GS', 'GR', 'GQ', 'GP', 'JP',
            'GY', 'GG', 'GF', 'GE', 'GD', 'GB', 'GA', 'GN', 'GM', 'GL', 'GI',
            'GH', 'OM', 'TN', 'JO', 'TA', 'HR', 'HT', 'HU', 'HK', 'HN', 'HM',
            'VE', 'PR', 'PW', 'PT', 'KN', 'PY', 'AI', 'PA', 'PF', 'PG', 'PE',
            'PK', 'PH', 'PN', 'PL', 'PM', 'ZM', 'EE', 'EG', 'ZA', 'EC', 'IT',
            'VN', 'SB', 'ET', 'SO', 'ZW', 'KY', 'ES', 'ER', 'ME', 'MD', 'MG',
            'MA', 'MC', 'UZ', 'MM', 'ML', 'MO', 'MN', 'MH', 'MK', 'MU', 'MT',
            'MW', 'MV', 'MQ', 'MP', 'MS', 'MR', 'IM', 'UG', 'MY', 'MX', 'IL',
            'FR', 'AW', 'SH', 'AX', 'SJ', 'FI', 'FJ', 'FK', 'FM', 'FO', 'NI',
            'NL', 'NO', 'NA', 'VU', 'NC', 'NE', 'NF', 'NG', 'NZ', 'NP', 'NR',
            'NU', 'CK', 'CI', 'CH', 'CO', 'CN', 'CM', 'CL', 'CC', 'CA', 'CG',
            'CF', 'CD', 'CZ', 'CY', 'CX', 'CR', 'CV', 'CU', 'SZ', 'SY', 'KG',
            'KE', 'SR', 'KI', 'KH', 'SV', 'KM', 'ST', 'SK', 'KR', 'SI', 'KP',
            'KW', 'SN', 'SM', 'SL', 'SC', 'KZ', 'SA', 'SG', 'SE', 'SD', 'DO',
            'DM', 'DJ', 'DK', 'VG', 'DE', 'YE', 'DZ', 'US', 'UY', 'YT', 'UM',
            'LB', 'LC', 'LA', 'TV', 'TW', 'TT', 'TR', 'LK', 'LI', 'LV', 'TO',
            'LT', 'LU', 'LR', 'LS', 'TH', 'TF', 'TG', 'TD', 'TC', 'LY', 'VA',
            'AC', 'VC', 'AE', 'AD', 'AG', 'AF', 'IQ', 'VI', 'IS', 'IR', 'AM',
            'AL', 'AO', 'AN', 'AQ', 'AS', 'AR', 'AU', 'AT', 'IO', 'IN', 'TZ',
            'AZ', 'IE', 'ID', 'UA', 'QA', 'MZ'])
        if country in iso_country_codes:
            self.flag_name = 'flags/' + country.lower() + '.gif'

    def AddNumSolved(self, num_solved = 0):
        #error case num solved is ?
        solved_xo = self.pad
        solved_yo = int(self.H * 0.38)
        text = 'solved: '
        unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSans.ttf", 10)
        (tmp, _) = unicode_font.getsize(text)
        self.draw.text((solved_xo, solved_yo), text, font = unicode_font, 
                        fill = (96,96,96))
        end_xo = solved_xo + tmp
        if num_solved > 0:
            if(num_solved > 9999):
                text = '>1e4'
            else:
                #hold field with to max of 4 chars
                text = str(num_solved)
            unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSans.ttf", 10)
            self.draw.text((end_xo, solved_yo), text, font = unicode_font,
                            fill = (0,0,0))

    def AddPosition(self, position):
        #error case num solved is ?
        solved_xo = self.pad + 65
        solved_yo = int(self.H * 0.38)     
        text = 'rank: '
        unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSans.ttf", 10)
        (tmp, _) = unicode_font.getsize(text)
        self.draw.text((solved_xo, solved_yo), text, font = unicode_font,
                        fill = (96,96,96))
        end_xo = solved_xo + tmp
        if position > 0:
            #switch to scientific notation if rank is large enough
            if position > 999999:
                if(position >= 1e100):
                    position = ">1e100"
                else:
                    position = "{:.2e}".format(position)
                #remove the positive exponent character
                position = string.replace(position, '+', '')
            else:
                position = str(position)

            #hold field with to max of 4 chars
            text = position[-10:]
        unicode_font = ImageFont.truetype("fonts/dejavu/DejaVuSans.ttf", 10)
        self.draw.text((end_xo, solved_yo), text, font = unicode_font, 
                        fill = (0,0,0))

    def RenderToBuffer(self):
        #render all of variable position boxes here at once
        self.flg_xo = int(self.nm_xo + self.usernm_width \
                                + self.flag_spacing)
        #Adjust this parameter to vary spacing of flag picture from baseline
        FLAG_FUDGE_F = 0.3
        self.flg_yo = max(
            [0,
            int(self.usernm_baseline_offset 
            - int(self.usernm_height * FLAG_FUDGE_F)- self.flg_H)])


        flag_file = Image.open(self.flag_name)
        (flag_x,flag_y) = flag_file.size
        self.img.paste(flag_file, 
            (self.flg_xo, self.flg_yo, self.flg_xo+flag_x , self.flg_yo+flag_y))

        #create buffer for output
        f = cStringIO.StringIO()
        self.img.save(f, "PNG")
        return f
