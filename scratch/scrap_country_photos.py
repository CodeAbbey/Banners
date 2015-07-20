import argparse
import csv
import gzip
import logging
import os
import re
import requests
from StringIO import StringIO
import sys
import time
import urllib
import urllib2

try:
	import http.client as http_client
except ImportError:
	# Python 2
	import httplib as http_client
http_client.HTTPConnection.debuglevel = 0
# logging.basicConfig() 
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

from bs4 import BeautifulSoup


#set up the scraper session
base_url = 'http://www.codeabbey.com/img/flags/'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1250.0 Iron/22.0.2150.0 Safari/537.4'

header = {'User-Agent': user_agent}
header['Host'] = 'passion-hd.com'
header['Accept']="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
header['Accept-Language'] = 'en,en-GB;q=0.5'
header['Accept-Encoding'] = 'gzip,deflate'
header['Connection'] = 'keep-alive'
header['Cache-Control'] = 'max-age=0'


session = requests.Session()
session.headers.update(header)

#read the ISO 3166-1 csv file to extract the codes we will try
def main():
	parser = argparse.ArgumentParser(prog = "Flag Scrapper", description = "downloads all flags possible from Code Abbey to make a zip file")
	parser.add_argument("filename")

	args = parser.parse_args()
	if args.filename:
		try:
			statinfo = os.stat(args.filename)
		except OSError:
			print "{} does not exist".format(args.filename)
			sys.exit()


	with open(args.filename, 'rb') as csvfile:
		#first line of file is the field names
		reader = csv.DictReader(csvfile)
		if('ISO 3166-1 2 Letter Code' in reader.fieldnames):
			#make set of all valid codes, since the same code may
			#belong to technically different geographical regions
			codes_array = [row['ISO 3166-1 2 Letter Code'] for row in reader]
			codes = set(codes_array)
			del codes_array
			#relative path, puts results in same folder
			flag_dir = './flags/'
			if not os.path.exists(flag_dir):
				os.mkdir(flag_dir)
			else:
				print flag_dir
			for unique in codes:
				if not unique:
					#skip empty lines
					continue

				flag_name = unique.lower() + '.gif'
				flag_url = base_url + flag_name
				print flag_url
				r = requests.get(flag_url, cookies = {}, stream = True)
				print "status code", r.status_code
				if not r.ok:
					print "error in fetching resource"
					continue
				file_size = int(r.headers['content-length'])
				#put the file into the flag_dir
				flag_name = os.path.join(flag_dir, flag_name)
				print "Flag name", flag_name

				with open(flag_name, "wb") as fh:
					count = 1
					chunk_size = 1048576
					start_time = time.time()
					try:
						for block in r.iter_content(chunk_size):
							total_time = time.time() - start_time
							percent = count*chunk_size/float(file_size) * 100.0
							percent = min([percent, 100])
							fraction = int(percent/5)
							fraction = min([fraction, 20])

							download_speed = 1.0 / total_time

							sys.stdout.write('\r')
							sys.stdout.write("[%-20s] %d%%  %3.2f MB/s       " % ('='* fraction , percent, download_speed))
							sys.stdout.flush()
							if not block:
								break
							fh.write(block)
							count += 1
							start_time = time.time()
					except Exception as e:
						print e
					finally:    
						#close up the stream
						r.close()
						print

		else:
			print "error: could not find 'ISO 3166-1 2 Letter Code' as field name"
			sys.exit()

if __name__ == '__main__':
	main()