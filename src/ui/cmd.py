import argparse
import logging
from src.stamper import Stamper
from src.visualizer import Visualizer
from src.utils import Utils

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
		ap.add_argument("-I", "--display-info", dest="display_info", help="Displays info about the current workday",action="store_true")
		ap.add_argument("-S", "--display-saldo", dest="display_saldo", help="Displays the time saldo",action="store_true")
		ap.add_argument("-M", "--display-month", dest="display_month", help="Displays summary of month",action="store_true")
		ap.add_argument("-W", "--display-week", dest="display_week", help="Displays summary of week",action="store_true")
		ap.add_argument("-D", "--display-last", dest="display_last", help="Displays latest ended workday",action="store_true")
		ap.add_argument("-d", "--display-open", dest="display_open", help="Displays the currently open workday",action="store_true")
		ap.add_argument("-n", "--stamp-new", dest="stamp_new", help="Starts a new workday",action="store_true")
		ap.add_argument("-p", "--stamp-pause", dest="stamp_pause", help="Pauses the current workday",action="store_true")
		ap.add_argument("-r", "--stamp-resume", dest="stamp_resume", help="Resumes the current workday",action="store_true")
		ap.add_argument("-e", "--stamp-end", dest="stamp_end", help="Ends the workday",action="store_true")
		ap.add_argument("-X", "--test", dest="test", help="Dev option",action="store_true")
		
		stamper = Stamper()
		visualizer = Visualizer()
		
		self.print_head()
		
		args = ap.parse_args()
		if args.display_saldo:
			visualizer.saldo()
		elif args.display_month:
			visualizer.month()
		elif args.display_week:
			visualizer.week()
		elif args.display_last:
			visualizer.last()
		elif args.display_open:
			visualizer.open()
		elif args.stamp_new:
			stamper.new()
		elif args.stamp_pause:
			stamper.pause();
		elif args.stamp_resume:
			stamper.resume()
		elif args.stamp_end:
			stamper.end()
		elif args.test:
			Utils.getRequiredWork()
		
		if args.display_info:
			visualizer.day()
			
			
	def print_head(self):
		help="\n"
		help+=Utils.pbdiv()
		help+=Utils.pbn()
		help+=Utils.pb("wtstamp - a flexible timestamp tool")
		help+=Utils.pbn()
		help+=Utils.pbdiv()
		print(help,end='')
		
		