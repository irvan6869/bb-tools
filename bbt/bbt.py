#!/usr/bin/env python

# bbt.py v0.4b - BlackBerry BBThumbsXXXxXXX.key file parser
# Copyright (C) 2011, Sheran A. Gunasekera <sheran@zensay.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#

import sys
import struct
import datetime
import getopt
import os
from bbtmodules.DatFile import DatFile
from bbtmodules.BBThumbs import BBThumbs

def usage():
	print("Usage: bbt.py [options]")
	print("  -h, --help: This cruft")
	print("  -k, --key <bbthumbs key file>: Process post OS5 thumbs.key file (requires thumbs.dat file in same directory)")
	print("  -b, --bbthumbs <old bbthumbs file>: Process pre OS5 BBThumbs.dat file")
	print("  -x, --extract: Extracts the thumbnails into directory specified by -o")
	print("  -o, --output <output directory>: Directory to extract thumbs to (used only with -x)")
	print("  -l, --local: Express timestamps in local time as opposed to GMT")
	
def process(kf,outdir,extract,local):
	if(kf.startswith('-')):
		usage()
		sys.exit(2)
	if extract:
		if not os.path.exists(outdir):
			os.makedirs(outdir)
		else:
			print "Directory already exists"
			sys.exit(2)
	print "*** Processing "+os.path.split(kf)[1]+" on "+str(datetime.datetime.now())
	bbt_file = open(kf,'rb')
	magic = (struct.unpack(">4s",bbt_file.read(4)))[0].encode("hex").upper()
	if magic != "08062009":
		print kf+" is not a BlackBerry thumbs file!";
		sys.exit(2)
	bbt_file.seek(9,1)
	thumbs = {}

	try:
		while(True):
			tkey = (struct.unpack(">4s",bbt_file.read(4)))[0].encode("hex").upper()
			bbt_file.seek(4,1)
			tval = (struct.unpack(">I",bbt_file.read(4))[0])
			if tval != 0:
				thumbs[tkey] = tval 
	except:
		bbt_file.close()
		dfile = DatFile(kf[:-3]+"dat")
		ctr = 0;
		if dfile.is_valid:
			for key in thumbs.iterkeys():
				rec = dfile.record(thumbs[key], key)
				if rec != None:
					ctr += 1
					if extract:
						rec.save_to_disk(outdir)
					if local:
						timestamp = rec.local_timestamp()
					else:
						timestamp = rec.gmt_timestamp()
					print "+ "+rec.name()+" // "+timestamp+" // "+rec.sha1hash()
		dfile.close()
		print "*** "+os.path.split(kf)[1]+" has "+str(len(thumbs))+" records"
		print "*** Processed "+str(ctr)+" records"
		
def oldthumbs(bbthumbs,outdir,extract,local):
	if(bbthumbs.startswith('-')):
		usage()
		sys.exit(2)
	if extract:
		if not os.path.exists(outdir):
			os.makedirs(outdir)
		else:
			print "Directory already exists"
			sys.exit(2)
	print "*** Processing "+os.path.split(bbthumbs)[1]+" on "+str(datetime.datetime.now())
	bbth = BBThumbs(bbthumbs)
	if bbth.is_valid():
		recs = bbth.process()
		for rec in recs:
			if extract:
				bbth.record(rec).save_to_disk(outdir)
			if local:
				timestamp = bbth.record(rec).local_timestamp()
			else:
				timestamp = bbth.record(rec).gmt_timestamp()
			print "+ "+bbth.record(rec).name()+" // "+timestamp+" // "+bbth.record(rec).sha1hash()
	else:
		print bbthumbs+" is not a BlackBerry thumbs file!";
		sys.exit(2)
	bbth.close()
	print "*** "+os.path.split(bbthumbs)[1]+" has "+str(len(recs))+" records"

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hk:o:xb:l", ["help", "key=","output=","extract","bbthumbs=","local"])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	
	keyfile = None
	outdir = None
	extract = False
	bbthumbs = None
	local = False
	
	for o,a in opts:
		if o in ("-k","--key"):
			keyfile = a
		elif o in ("-h","--help"):
			usage()
			sys.exit()
		elif o in("-o","--output"):
			outdir = a
		elif o in("-x","--extract"):
			extract = True
		elif o in("-b","--bbthumbs"):
			bbthumbs = a
		elif o in("-l","--local"):
			local = True
		else:
			assert False, "unhandled option"
		
	if keyfile == None and bbthumbs == None:
		usage()
		sys.exit()
	
	if keyfile and bbthumbs:
		print "-k and -b are mutually exclusive.  Use one or the other."
		sys.exit(2)
	
	if extract:
		if outdir == None:
			print "-x requires an output directory"
			sys.exit(2)
		
	if keyfile:
		process(keyfile,outdir,extract,local)	
	elif bbthumbs:
		oldthumbs(bbthumbs,outdir,extract,local)
	else:
		sys.exit()


if __name__ == "__main__":
	main()
