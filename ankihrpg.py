#AnkiRPG
#Anki 2 plugin for use with HabitRPG http://habitrpg.com
#Author: Edward Shapard <ed.shapard@gmail.com>
#Version 0.1
#License: GNU GPL v3 <www.gnu.org/licenses/gpl.html>

'''
Updated March 3, 2016 by Tim Wilson <twilsonco@gmail.com>
Now fetches info from database so that reviews can be done
on any device and you still get Habitica points for them
once you sync in Anki 2.
'''

from __future__ import division
import urllib2, urllib, os, sys, json, datetime, time
from anki.utils import ids2str
from anki.hooks import wrap, addHook
from aqt.reviewer import Reviewer
from anki.sched import Scheduler
from aqt import *
from anki.sync import Syncer
from aqt.main import AnkiQt

'''
	USER OPTIONS:
	You can change the variables below to customize the behavior of the add-on:
'''
# Default number required to increase Habitica habits (can be changed in setup function by user):
num_required = {
	'deck': 1,
	'timebox': 1,
	'score': 10,
	'matured': 5,
	'learned': 5
	}
'''
	END USER OPTIONS
'''


# Set to True to enable logging, False to disable
doLog = True
if doLog:
	logFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".habitrpg.log")

habit_names = {
	'deck': "'Anki Deck Complete' habit: ",
	'timebox': "'Anki Timebox Reached' habit: ",
	'score': "'Anki Correct Answer' habit: ",
	'matured': "'Anki Matured Cards' habit: ",
	'learned': "'Anki Learned Cards' habit: "
	}
custom_msg = {
	'deck': "Completed decks required to increment the 'Anki Deck Complete' habit:",
	'timebox': "Completed timeboxes required to increment the 'Anki Timebox Reached' habit:",
	'score': "Correct answers required to increment the 'Anki Correct Answer' habit:",
	'matured': "Cards made mature required to increment the 'Anki Matured Cards' habit:",
	'learned': "Cards learned required to increment the 'Anki Learned Cards' habit:"
	}

config = {}
config_old = {}
conffile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".habitrpg.conf")
conffile = conffile.decode(sys.getfilesystemencoding())
habitpost = {
	'deck': urllib2.Request('https://habitrpg.com/api/v2/user/tasks/Anki%20Deck%20Complete/up',''),
	'timebox':urllib2.Request('https://habitrpg.com/api/v2/user/tasks/Anki%20Timebox%20Reached/up',''),
	'score':urllib2.Request('https://habitrpg.com/api/v2/user/tasks/Anki%20Correct%20Answer/up',''),
	'matured':urllib2.Request('https://habitrpg.com/api/v2/user/tasks/Anki%20Matured%20Cards/up',''),
	'learned':urllib2.Request('https://habitrpg.com/api/v2/user/tasks/Anki%20Learned%20Cards/up','')
	}
Syncer.habit = {
	'deck': 0,
	'timebox': 0,
	'score': 0,
	'matured': 0,
	'learned': 0
	}
Syncer.last_sync = 0
Syncer.habit_configured = False

def internet_on():
	try:
		response=urllib2.urlopen('http://habitrpg.com',timeout=1)
		return True
	except urllib2.URLError as err: pass
	return False

#Return current local time as seconds from epoch
def newTime():
	return int((datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds())

#Read values from file if it exists
if os.path.exists(conffile): # Load config file
	config = json.load(open(conffile, 'r'))
	try:
		api_token = config['token']
		user_id = config['user']
		Syncer.habit_configured = True
	except:
		Syncer.habit_configured = False
	if Syncer.habit_configured:
		for i in Syncer.habit:
			try:
				Syncer.habit[i] = config[i]
			except:
				Syncer.habit[i] = 0
			try:
				num_required[i] = config[i + 'Required']
			except:
				junk = None
			config_old[i] = Syncer.habit[i]
			habitpost[i].add_header('x-api-user', user_id)
			habitpost[i].add_header('x-api-key', api_token)
		try:
			Syncer.last_sync = int(config['lastsync'])
		except:
			Syncer.last_sync = newTime()


#Setup menu to configure HRPG userid and api key
def setup():
	global config
	api_token = None
	user_id = None
	need_info = True
	if os.path.exists(conffile):
		need_info = False
		config = json.load(open(conffile, 'r'))
		try:
			api_token = config['token']
			user_id = config['user']
		except:
			need_info = True
		for i in Syncer.habit:
			try:
				Syncer.habit[i] = config[i]
			except:
				Syncer.habit[i] = 0				
			try:
				num_required[i] = config[i + 'Required']
			except:
				junk = None
	else:
		for i in Syncer.habit:
			config[i] = Syncer.habit[i]
	need_info = need_info or api_token is None or user_id is None
	if not need_info:
		if utils.askUser("Habitica user credentials already entered.\nEnter new Habitica user iD and API token?"):
			need_info = True
	if need_info:
		for i in [['user','user ID'],['token','API token']]:
			config[i[0]], ok = utils.getText("Enter your %s:\n(Go to Settings --> API to find your %s)" % (i[1],i[1]))
			config[i[0]] = str(config[i[0]])
			if not ok:
				utils.showWarning('HabitRPG setup cancelled. Run setup again to use HabitRPG add-on')
				Syncer.habit_configured = False
				return
	
	msg_str = "Customize HabitRPG add-on behavior?\n('No' to use default/current values)\n\nCurrent Values (0 means habit is disabled):"
	for i in custom_msg:
		msg_str += "\n\n" + custom_msg[i] + " %s" % num_required[i]
	if utils.askUser(msg_str):
		for i in num_required:
			while True:
				tmp, ok = utils.getText(
					prompt = custom_msg[i] + "\n(current: %d), (0 to disable this habit)" % num_required[i], 
					default = str(num_required[i]))
				if ok:
					try:
						num_required[i] = int(tmp)
						break
					except:
						utils.showWarning('Please enter a whole number')
				else:
					break
			if not ok: break
	
	for i in Syncer.habit:
		habitpost[i].add_header('x-api-user', user_id)
		habitpost[i].add_header('x-api-key', api_token)
		try:
			config[i + 'Required'] = num_required[i]
		except:
			junk = None
			
	if mw.col.conf['timeLim'] <= 0 and num_required['timebox'] > 0:
		utils.showInfo("If you want to get Habitica credit for completed timeboxes then you need to set the timebox value in Anki preferences.")
	
	Syncer.last_sync = newTime()
	config['lastsync'] = Syncer.last_sync
	json.dump( config, open( conffile, 'w' ) )
	Syncer.habit_configured = True
	utils.showInfo("The add-on has been setup.\n\nNow go to Anki settings and enable automatic sync on profile open/close, otherwise you risk losing Habitica credit for reviews!\n\nAlso, once the new habits have been created, change them to plus (+) only habits.")


#Add Setup to menubar
action = QAction("Setup Habitica Support", mw)
mw.connect(action, SIGNAL("triggered()"), setup)
mw.form.menuTools.addAction(action)

#Timebox Reached
def timebox_habit(self):
	elapsed = self.mw.col.timeboxReached()
	if elapsed:
		Syncer.habit['timebox'] += 1

def save_stats(x,y):
	global config
	for i in Syncer.habit:
		config[i] = Syncer.habit[i]
		try:
			config[i + 'Required'] = num_required[i]
		except:
			junk = None
	config['lastsync'] = Syncer.last_sync
	json.dump( config, open( conffile, 'w' ) )
	
# Prints the passed statement to the logFile specified at the begging of this file
def logIt(logStatement):
	if doLog:
		l = open(logFile,'a')
		l.write(logStatement + '\n')
		l.close()
	
# Return a formatted date string
def prettyTime(secFromEpoch):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(secFromEpoch))
	
#Update decks/timebox/score with data from db
def update_from_db(self):
	logIt("\nRun time: %s" % prettyTime(newTime()))
	logIt("Old time: %s (%s)" % (prettyTime(Syncer.last_sync), Syncer.last_sync))
	logIt("Before DB fetch stats: %s" % str(Syncer.habit))
	# get number of timebox done on desktop (already recorded)
	desktopTimeboxes = Syncer.habit['timebox'] - config_old['timebox']
	logIt("Desktop Syncer timebox value = %d" % desktopTimeboxes)
	# new score/timeBoxes from db since last_sync
	# only get number of correct answers
	dbScore = self.col.db.scalar("""select 
		count()
		from revlog where 
		ease is not 1 and
		id/1000 > ?""", 
		Syncer.last_sync)
	'''
	Getting total number of seconds, which will be divided by the timebox limit.
	This is the best you can do using the database, since timebox events aren't recorded
	in the database.
	'''
	dbTime = self.col.db.scalar("""select 
		sum(time)/1000 
		from revlog where 
		id/1000 > ?""", 
		Syncer.last_sync)
	# In case no reviews were found, dbTime will be None, so fix that
	if dbTime is None: dbTime = 0 
	logIt("db score and time: %d, %d" % (dbScore,dbTime))
	# Update recorded score/timebox values with info from db
	Syncer.habit['score'] += dbScore
	if self.col.conf['timeLim'] > 0:
		Syncer.habit['timebox'] += dbTime // self.col.conf['timeLim'] - desktopTimeboxes
	# Get cards made mature
	dbMatured = self.col.db.scalar("""
	select count() 
	from revlog 
	where ivl >= 21 and
	lastIvl < 21
	and id/1000 > ?
	""",Syncer.last_sync)
	Syncer.habit['matured'] += dbMatured
	logIt("Matured: %d" % dbMatured)
	# Get new learning cards
	learned = 0
	learned = self.col.db.scalar("""
		select
		sum(case when type = 0 then 1 else 0 end)
		from revlog where
		id/1000 > :oldTime
		""",
		oldTime = Syncer.last_sync)
	if learned is None: learned = 0
	Syncer.habit['learned'] += learned
	logIt("New learning cards: %d" % learned)
	'''
	new decks from db
	Here it takes a little bit of work. 
	For each deck we'll get the number of reviews due for each
	day since last_sync and the number of reviews performed for
	the same days.
	For a given day, if there are zero reviews due but more than 
	zero reviews completed, then it means the user finished all reviews
	for that day.
	'''
	dbDecks = 0
	finishedDecks = []
	# See how many previous days we need to check 
	numDays = int((newTime() - Syncer.last_sync)/86400)+2
	for d in self.col.decks.all():
		# get list of number of cards due for deck each day
		cardsDue = [(-nDays,self.col.db.scalar("""
			select 
			count()
			from cards where 
			queue in (2,3) and 
			did = :d and 
			due <= :oldDay""",
			d=d['id'],
			oldDay=self.col.sched.today-nDays)) for nDays in range(numDays)]
		# get list of number of cards reviewed for deck each day
		cardsDone = self.col.db.all("""
			select 
			(cast((id/1000.0 - :cut) / 86400.0 as int)) as day,
			sum(case when cid in %s then 1 else 0 end)
			from revlog where 
			id/1000 > :oldTime
			group by day order by day""" % ids2str([x[0] for x in self.col.db.all("""
				select
				id
				from cards where
				did = ?""", d['id'])]),
			cut = self.col.sched.dayCutoff,
			oldTime = Syncer.last_sync)
		'''
		The db.all() call above only returns data for days that have >= 1 completed review,
		so there is not in general a one-to-one corresponce between cardsDue and cardsDone
		(cardsDue[i] and cardsDone[i] might represent different days).
		So need to use the below ugly code to make sure that cardsDue[i] and cardsDone[j]
		are for the same day.
		'''	  
		if not cardsDue is None and not cardsDone is None:
			for due in cardsDue:
				if due[1] == 0:
					for done in cardsDone:
						if done[0] == due[0]:
							if done[1] > 0 and due[1] == 0:
								dbDecks += 1
								finishedDecks.append(d)
							break
	'''
	We've got the full list of completed decks, but there could be extras (i.e. if a user
	completes two children decks by completing the parent deck and the parent deck doesn't
	contain any cards, then it will count as 3 decks when it should count as 2.
	So check that a parent deck actually has cards of its own before giving credit for it.
	Check by getting combined cards of all child decks. If parent deck card count is not
	more than the combined child deck card count then the parent deck doesn't have any of
	its own cards and shouldn't be counted.
	'''
	for p in finishedDecks:
		children = self.col.decks.children(p['id'])
		cCardCount = 0
		for c in children:
			cCardCount += self.col.db.scalar("""
				select count() from cards where did = ?
				""", c[1])
		if cCardCount > 0:
			pCardCount = self.col.db.scalar("""
				select count() from cards where did = ?
				""", p['id'])
			if not pCardCount > cCardCount: dbDecks -= 1
			
	Syncer.habit['deck'] += dbDecks
	logIt("db decks: %d" % dbDecks)
	logIt("After DB fetch stats: %s" % str(Syncer.habit))
	# update last_sync using the most recent review time in the database
	Syncer.last_sync = self.col.db.scalar("select max(id/1000) from revlog")
	logIt("New time: %s (%s)" % (prettyTime(Syncer.last_sync), Syncer.last_sync))
	# just in case
	for i in Syncer.habit:
		if Syncer.habit[i] < 0: Syncer.habit[i] = 0
	
	

#Sync scores to HabitRPG
def habitrpg_sync():
	global config
	if Syncer.habit_configured:
		mw.progress.start(label="Habitica: Checking database")
		update_from_db(mw)
		config['lastsync'] = Syncer.last_sync
		save_stats(None,None)
		nHabits = 0
		for i in Syncer.habit:
			if num_required[i] > 0: nHabits += Syncer.habit[i] // num_required[i]
		if nHabits > 0:
			mw.progress.finish()
			tmpStr = "Habitica: Incrementing %d habit%s" % (nHabits, "" if nHabits == 1 else "s")
			for i in Syncer.habit:
				if num_required[i] > 0: tmpStr += "\n" + habit_names[i] + str(Syncer.habit[i] // num_required[i])
			mw.progress.start(max = nHabits, label = tmpStr)
			if internet_on:
				logIt("Before upload stats: %s" % str(Syncer.habit))
				for i in Syncer.habit:
					if num_required[i] > 0:
						logIt("Updating '%s'" % i)
						while Syncer.habit[i] >= num_required[i]:
							mw.progress.update()
							try:
								urllib2.urlopen(habitpost[i])
								Syncer.habit[i] -= num_required[i]
							except:
								logIt("Err: Failed to increment '%s'" % i)
								break
						config_old[i] = Syncer.habit[i]
					else:
						Syncer.habit[i] = 0
				logIt("After upload stats: %s" % str(Syncer.habit))
			else:
				logIt("No upload: no internet...")
		else:
			logIt("No upload: no progress...")
	
		save_stats(None,None)
		mw.progress.finish()

#Wrap Code
Reviewer.nextCard = wrap(Reviewer.nextCard, timebox_habit, "before")
addHook("profileLoaded", habitrpg_sync)
addHook("unloadProfile", habitrpg_sync)
AnkiQt.closeEvent = wrap(AnkiQt.closeEvent, save_stats, "before")
