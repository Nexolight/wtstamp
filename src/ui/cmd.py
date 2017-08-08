import argparse
import logging
import os
from datetime import datetime
from src import settings
from src.stamper import Stamper
from src.visualizer import Visualizer
from models.models import Workday

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
		ap.add_argument("-L", "--display-saldo", dest="display_saldo", help="Displays the time saldo",action="store_true")
		ap.add_argument("-M", "--display-month", dest="display_month", help="Displays summary of month",action="store_true")
		ap.add_argument("-W", "--display-week", dest="display_week", help="Displays summary of week",action="store_true")
		ap.add_argument("-D", "--display-last", dest="display_last", help="Displays latest ended workday",action="store_true")
		ap.add_argument("-d", "--display-open", dest="display_open", help="Displays the currently open workday",action="store_true")
		ap.add_argument("-n", "--stamp-new", dest="stamp_new", help="Starts a new workday",action="store_true")
		ap.add_argument("-p", "--stamp-pause", dest="stamp_pause", help="Pauses the current workday",action="store_true")
		ap.add_argument("-r", "--stamp-resume", dest="stamp_resume", help="Resumes the current workday",action="store_true")
		ap.add_argument("-e", "--stamp-end", dest="stamp_end", help="Ends the workday",action="store_true")
		
		stamper = Stamper()
		visualizer = Visualizer()
		
		self.print_help()
		
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
		else:
			pass
		
	def print_help(self):
		'''
		Prints the header and some useful info
		'''
		
		#We want to know the last active workday
		lastwd = Workday.loadLast(os.path.join(settings.get("application_data"),"history"))
		
		curwd = None
		curbreak = None
		if(lastwd):
			curwd=datetime.fromtimestamp(lastwd.start).strftime(settings.get("time_format"))
			#print(lastwd.breaks)
			for breaks in lastwd.breaks:
				if(breaks.get("start") and not breaks.get("end")):
					curbreak=datetime.fromtimestamp(breaks.get("start")).strftime(settings.get("time_format"))
					break
		
		#box
		help="\n"
		help+="|----------------------------------------|\n"
		help+="|                                        |\n"
		help+="|  wtstamp - a flexible timestamp tool   |\n"
		help+="|                                        |\n"
		help+="|----------------------------------------|\n"
		help+="|                                        |\n"
		if(curwd):
			help+="| active workday >> "+curwd+"  |\n"
		if(curbreak):
			help+="| break since    >> "+curbreak+"  |\n"
		help+="\n"
		print(help)
		
		
		
		