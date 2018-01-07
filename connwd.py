#!/usr/bin/env python3

import sys
import time
import subprocess
import logging


class ConnectionApi:
	def up(self):
		subprocess.Popen(["pon", "dsl-provider"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def down(self):
		subprocess.Popen(["poff", "dsl-provider"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def check(self):
		url = "ya.ru"
		out, err = subprocess.Popen(["ping", url, "-c", "1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		return err.decode("utf-8") not in ["ping: unknown host %s\n" % url, 'ping: %s: Временный сбой в разрешении имен\n' % url]

	@property
	def name(self) -> str:
		return "pppoe"


class ConnWD:
	def __init__(self, connapi):
		logging.basicConfig(format="%(levelname)-8s [%(asctime)s]  %(message)s", level=logging.DEBUG)
		self._running = False
		self._connapi = connapi

	def up(self):
		self._running = True

		self._connapi.up()
		time.sleep(1)
		if self._connapi.check():
			logging.info("Connection upped")
		else:
			logging.error("Failed to up connection")
			
		self._running = False

	def down(self):
		self._running = True

		self._connapi.down()
		time.sleep(1)
		if self._connapi.check():
			logging.info("Failed to down connection")
		else:
			logging.error("Connection downed")

		self._running = False

	def check(self):
		self._running = True

		if self._connapi.check():
			print("true")
		else:
			print("false")

		self._running = False

	def watch(self, tries_reup_level=2):
		self._running = True

		tries = 0
		while self._running:
			try:
				if not self._connapi.check():
					if tries > tries_reup_level:
						self._connapi.down()
						logging.info("Downing...")
						time.sleep(1)
					self._connapi.up()
					tries += 1
					logging.info("Upping... (try %s)" % tries)
				elif tries > 0:
					logging.info("Upped!")
					tries = 0
				time.sleep(1)
			except KeyboardInterrupt:
				logging.info("Stopping watching...")
				self._running = False

		self._running = False


def print_help():
	print(
"""connwd
{argv0} ACTION [ADDPARAM]

ACTION:
	up    -- up connection
	down  -- down connection
	check -- check connection
	watch -- watch the connection
		TRL -- count of tries before re-upping connection
""".format(argv0=sys.argv[0]))
		

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print_help()
		sys.exit(1)

	act = sys.argv[1]

	connwd = ConnWD(ConnectionApi())
	
	actions = {
		"up": lambda: connwd.up(),
		"down": lambda: connwd.down(),
		"check": lambda: connwd.check(),
		"watch": None
	}

	if act not in actions:
		print_help()
		print("Unknown ACTION %s" % act)
		sys.exit(1)

	if act == "watch":
		if len(sys.argv) == 3:
			connwd.watch(int(sys.argv[2]))
		else:
			connwd.watch()
	else:
		actions[act]()
