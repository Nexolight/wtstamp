import argparse
import logging
import time
import shutil
import os
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
		cols, rows = shutil.get_terminal_size((100, 50))
		os.environ['COLUMNS'] = str(cols);
		
		ap = argparse.ArgumentParser()
		subParser = ap.add_subparsers(dest="subap", help='Advanced Options')
		editAp = subParser.add_parser("edit")
		gEditAp = editAp.add_mutually_exclusive_group(required=True)
		insertAp = subParser.add_parser("insert")
		gInsertAp = insertAp.add_mutually_exclusive_group(required=True)
		
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
		ap.add_argument("-X", "--display-proc", dest="display_proc", help="Shows how long the calculation took",action="store_true")
		gEditAp.add_argument("-s", "--set-start", dest="set_start", metavar=("<HH:MM>","dd.mm.yyyy"), nargs="+", help="Set the start time from the given day. When no day is given either the last open day (1st) or the last closed day (2nd) is choosen.")
		gEditAp.add_argument("-e", "--set-end", dest="set_end", metavar=("<dd.mm.yyyy:HH:MM>", "dd.mm.yyyy"), nargs="+", help="Set the end time for the given day. When no day is given, then the last closed day is choosen.")
		gEditAp.add_argument("-S", "--move-start", dest="move_start", metavar=("<<s/+>HH:MM>", "dd.mm.yyyy"), nargs="+", help="Moves the start time from the given day (+=forward, s=backward). When no day is given either the last open day (1st) or the last closed day (2nd) is choosen.")
		gEditAp.add_argument("-E", "--move-end", dest="move_end", metavar=("<<s/+>HH:MM>", "dd.mm.yyyy"), nargs="+", help="Moves the end time from the given day (+=forward, s=backward). When no day is given, then the last closed day is choosen.")
		gInsertAp.add_argument("-n", "--workday", dest="insert_workday", metavar=("<dd.mm.yyyy:HH:MM>", "<HH:MM>"), nargs=2, help="Inserts a new workday at the given day and time with the specified length as positive offset.")
		gInsertAp.add_argument("-b", "--break", dest="insert_break", metavar=("<dd.mm.yyyy>", "<dd.mm.yyyy:HH:MM>", "<HH:MM>"), nargs=3, help="Inserts a new break into the given workday, starting from the given day and time, with the specified positive offset for the break end")
		
		#gEditAp.add_argument("-b", "--insert-break", dest="insert_break", metavar=("<dd.mm.yyyy>", "<HH:MM>", "<+HH:MM>"), nargs=3, help="Insert a break into the given day, at the given time with the given offset.")

		
		now=time.time()*1000
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
		
		
		if args.subap == "edit":
			if args.set_start and len(args.set_start) >= 1:
				newTime = datetime.strptime(args.set_start[0], "%H:%M").timestamp() +2208992400 #epoch
				ts=None
				if(len(args.set_start) >= 2):
					ts = datetime.strptime(args.set_start[1], "%d.%m.%Y").timestamp()
				stamper.moveStart(newTime, ts=ts, visualizer=visualizer, noOffset=True)
			elif args.set_end and len(args.set_end) >= 1:
				newTime=0
				setDirect=False
				setFromDaystart=False
				if("." in args.set_end[0]):
					newTime = datetime.strptime(args.set_end[0], "%d.%m.%Y:%H:%M").timestamp()
					setDirect=True
				else:
					newTime = datetime.strptime(args.set_end[0], "%H:%M").timestamp() +2208992400 #epoch
					setFromDaystart=True
				ts=None
				if(len(args.set_end) >= 2):
					ts = datetime.strptime(args.set_end[1], "%d.%m.%Y").timestamp()
				stamper.moveEnd(newTime, ts=ts, visualizer=visualizer, setDirect=setDirect, setFromDaystart=setFromDaystart)
			elif args.move_start and len(args.move_start) >= 1:
				newOffsetStr = args.move_start[0][1:]
				newOffset = datetime.strptime(newOffsetStr, "%H:%M").timestamp() +2208992400 #epoch
				if(args.move_start[0][:1] == "s"):
					newOffset = newOffset * -1
				ts=None
				if(len(args.move_start) >= 2):
					ts=datetime.strptime(args.move_start[1], "%d.%m.%Y").timestamp()
				stamper.moveStart(newOffset, ts=ts, visualizer=visualizer)
			elif args.move_end and len(args.move_end) >= 1:
				newOffsetStr = args.move_end[0][1:]
				newOffset = datetime.strptime(newOffsetStr, "%H:%M").timestamp() +2208992400 #epoch
				if(args.move_end[0][:1] == "s"):
					newOffset = newOffset * -1
				ts=None
				if(len(args.move_end) >= 2):
					ts=datetime.strptime(args.move_end[1], "%d.%m.%Y").timestamp()
				stamper.moveEnd(newOffset, ts=ts, visualizer=visualizer)
			elif args.insert_break and len(args.insert_break) == 3:
				pass
		
		if args.subap == "insert":
			if args.insert_workday:
				insertAt = datetime.strptime(args.insert_workday[0], "%d.%m.%Y:%H:%M").timestamp()
				offset = Utils.convertHMToSeconds(args.insert_workday[1],separator=":")
				stamper.insert_workday(insertAt, offset, setDirect=False, visualizer=visualizer)
			elif args.insert_break:
				insertAt = datetime.strptime(args.insert_break[0], "%d.%m.%Y").timestamp()
				bStart = datetime.strptime(args.insert_break[1], "%d.%m.%Y:%H:%M").timestamp()
				offset = Utils.convertHMToSeconds(args.insert_break[2],separator=":")
				stamper.insert_break(insertAt, bStart, offset, setDirect=False, visualizer=visualizer)
		
		if(args.display_proc):
			self.l.info("Calculation took "+str((time.time()*1000)-now)+"ms")
			
			
	def print_head(self):
		help="\n"
		help+=Utils.pbdiv()
		help+=Utils.pbn()
		help+=Utils.pb("wtstamp - a flexible timestamp tool")
		help+=Utils.pbn()
		help+=Utils.pbdiv()
		print(help,end='')
		
		