import argparse
import logging
import time
from datetime import datetime
import sys
from src.stamper import Stamper
from src.visualizer import Visualizer
from src.utils import Utils
from src.settings import SettingsHelper

'''
Entry point
'''
class CMD():
	#---------------------------------------------------------------------------
	# Argparse stuff only
	#---------------------------------------------------------------------------
	def __init__(self):
		self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
		ap = argparse.ArgumentParser()
		ap.add_argument("-n", "--stamp-new", dest="stamp_new", help="Starts a new workday",action="store_true")
		ap.add_argument("-p", "--stamp-pause", dest="stamp_pause", help="Pauses the current workday",action="store_true")
		ap.add_argument("-r", "--stamp-resume", dest="stamp_resume", help="Resumes the current workday",action="store_true")
		ap.add_argument("-e", "--stamp-end", dest="stamp_end", help="Ends the workday",action="store_true")
		ap.add_argument("-S", "--display-saldo", dest="display_saldo", help="Displays the time saldo",action="store_true")
		ap.add_argument("-L", "--display-last", dest="display_last", help="Displays latest ended workday",action="store_true")
		ap.add_argument("-D", "--display-day", dest="display_info", default=None, const=time.time(), nargs="?", metavar="dd.mm.yyyy", help="Displays info about a workday")
		ap.add_argument("-W", "--display-week", dest="display_week", default=None, const=time.time(), nargs="?", metavar="dd.mm.yyyy", help="Displays summary of week")
		ap.add_argument("-M", "--display-month", dest="display_month", default=None, const=time.time(), nargs="?", metavar="mm.yyyy", help="Displays summary of month")
		ap.add_argument("-Y", "--display-year", dest="display_year", default=None, const=time.time(), nargs="?", metavar="yyyy", help="Displays summary of the year")
		
		SettingsHelper.rangesToArray()
		stamper = Stamper()
		visualizer = Visualizer()
		self.print_head()
		args = ap.parse_args()
		
		if args.display_saldo:
			visualizer.saldo()
		elif args.display_month:
			if(isinstance(args.display_month, str)):
				args.display_month=datetime.strptime(args.display_month, "%m.%Y").timestamp()
			visualizer.month(args.display_month)
		elif args.display_week:
			if(isinstance(args.display_week, str)):
				args.display_week=datetime.strptime(args.display_week, "%d.%m.%Y").timestamp()
			visualizer.week(args.display_week)
		elif args.display_year:
			if(isinstance(args.display_year, str)):
				args.display_year=datetime.strptime(args.display_year, "%Y").timestamp()
			visualizer.year(args.display_year)
		elif args.display_last:
			visualizer.last()
		elif args.stamp_new:
			stamper.new()
		elif args.stamp_pause:
			stamper.pause();
		elif args.stamp_resume:
			stamper.resume()
		elif args.stamp_end:
			stamper.end()
		
		if args.display_info:
			if(isinstance(args.display_info, str)):
				ts=datetime.strptime(args.display_info, "%d.%m.%Y").timestamp()
				visualizer.day(ts)
			else:
				visualizer.ongoing()
			
			
	def print_head(self):
		help="\n"
		help+=Utils.pbdiv()
		help+=Utils.pbn()
		help+=Utils.pb("wtstamp - a flexible timestamp tool")
		help+=Utils.pbn()
		help+=Utils.pbdiv()
		print(help,end='')
		
		