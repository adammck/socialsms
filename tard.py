#!/usr/bin/env python
# vim: noet

from smsapp import *
import kannel, time


# prepopulate a bunch of people during dev
DEV_PEOPLE = {
	"16467444705": "ADAM",
	"16072066710": "MARK",
	"13364130840": "EVAN",
	"12064849177": "MERRICK",
	"16462039624": "KATIE",
	"16464105122": "CHRIS",
	"16462266361": "ERICA" }

# same with groups
DEV_GROUPS = {
	"CHICKS": ["16462039624", "16462266361"],
	"DUDES":  ["16467444705", "16072066710", "13364130840", "12064849177", "16464105122"],
	"DEVS":   ["16467444705", "16072066710", "13364130840", "12064849177"],
	"ADULTS": ["16464105122", "16462266361"]
}


class SocialSMS(SmsApplication):
	people = DEV_PEOPLE
	groups = DEV_GROUPS
	kw = SmsKeywords()


	def __identify(self, caller, task=None):

		# if the caller is not yet identified, then
		# send a message asking them to do so, and
		# stop further processing
		if not self.people.has_key(caller):
			err = "You must identify yourself"
			if task: err += " before %s" % (task)
			raise CallerError(err)
		
		return self.people[caller]
	
	
	# everything that we pass around (identities and
	# group names, for now) must be short and upper,
	# to keep things simple for texters
	def __slug(self, str):
		return str[:10].upper()
	
	
	# slugize a string, and check that it's a
	# valid (already existing) group name
	def __group(self, str):
		grp = self.__slug(str)
		if not self.groups.has_key(grp):
			err = "There is no %s group" % (grp)
			raise CallerError(err)
		return grp
	
	
	# HELP
	@kw("help")
	def help(self, caller):
		self.send(caller, [
			"join <GROUP>",
			"leave <GROUP>",
			"identify <NAME>",
			"list [my] groups",
			"list members of <GROUP>",
			"<GROUP> <MESSAGE>"])
	
	
	# LIST GROUPS
	@kw("list (my )?groups")
	def list_groups(self, caller, my_groups=None):
		group_names = []
		
		# collate groups to list into a
		# flat list of slugized names
		for g in self.groups.keys():
			member = caller in self.groups[g]
			
			# include this group if we are listing ALL
			# groups, OR we are already a member of it
			# (also add a star to denote groups
			# which the caller is a member of)
			if member or not my_groups:
				if not my_groups and member: g += "*"
				group_names.append(g)
		
		# if there is nothing to return, then abort
		if not len(group_names):
			if my_groups: raise CallerError("You are not a member of any groups")
			else:         raise CallerError("No groups have been created yet")
			
		# return a list of [your|all] groups
		capt = my_groups and "Your groups" or "Groups"
		msg = "%s: %s" % (capt, ", ".join(group_names))
		self.send(caller, msg)
	
	
	# LIST MEMBERS OF <GROUP>
	@kw("list members of (letters)")
	def list_members_of_group(self, caller, grp):
		ident = self.__identify(caller, "making queries")
		grp = self.__group(grp)

		# collate the names of the members of this group
		# with a very ugly list comprehension, and send
		member_names = [self.__identify(p) for p in self.groups[grp]]
		msg = "Members of %s: %s" % (grp, ", ".join(member_names))
		self.send(caller, msg)
		
	
	# JOIN <GROUP>
	@kw("join (letters)")
	def join(self, caller, grp):
		ident = self.__identify(caller, "joining groups")
		grp = self.__slug(grp)
		
		# create the group if it
		# doesn't already exist
		if not self.groups.has_key(grp):
			self.groups[grp] = []
		
		# is the caller already in this group?
		if caller in self.groups[grp]:
			err = "You are already a member of the %s group" % (grp)
			raise CallerError(err)
			
		else:
			# join the group and notify
			self.groups[grp].append(caller)
			msg = "You have joined the %s group" % grp
			self.send(caller, msg)
	
	
	# LEAVE <GROUP>
	@kw("leave (letters)")
	def leave(self, caller, grp):
		grp = self.__group(grp)
		
		# callers can only send messages to groups which they are members of
		if not caller in self.groups[grp]:
			err = "You are not a member of the %s group" % (grp)
			raise CallerError(err)
		
		self.groups[grp].remove(caller)
		msg = "You have left the %s group" % grp
		self.send(caller, msg)
	
	
	# IDENTIFY <NAME>
	@kw("identify (letters)", "my name is (letters)", "i am (letters)")
	def identify(self, caller, name):
		name = self.__slug(name)
		self.people[caller] = name
		reply = 'Your name is now "%s"' % name
		self.send(caller, reply)


	# <GROUP> <MESSAGE>
	@kw("(letters) (.+)")
	def to_group(self, caller, grp, rest):
		ident = self.__identify(caller, "posting")
		grp = self.__group(grp)
		
		# check that the caller is a member of
		# the group to which we are broadcasting
		if not caller in self.groups[grp]:
			err = "You are not a member of the %s group" % (grp)
			raise CallerError(err)
		
		# keep a log of broadcasts
		self.log("Sending to group: %s" % grp)
		
		# iterate every member of the group we are broadcasting
		# to, and queue up the same message to each of them
		msg = "[%s] %s: %s" % (grp, ident, rest)
		for dest in self.groups[grp]:
			if dest != caller:
				self.send(dest, msg, buffer=True)
		
		# notify the caller that his/her message was sent
		people = len(self.groups[grp]) - 1
		msg = "Your message was sent to the %s group (%d people)" % (grp, people)
		self.send(caller, msg, buffer=True)
		
		# now REALLY send those sms in one
		# block, to help pygnokii keep up
		self.sender.flush()


	# ALL OTHER INCOMMING MESSAGES
	def incoming_sms(self, caller, msg):
		self.help(caller)




# start the application in a new thread
SocialSMS(
	backend=kannel,
	sender_args=["kuser", "kpass"]
).run()

	
try:
	# block until ctrl+c
	while True: time.sleep(1)
	
except KeyboardInterrupt:
	print "Shutting Down..."

