#!/usr/bin/env python3

import sys
import subprocess
import time


class ConnD:
	def __init__(self):
		self._running = False
	
	def check(self, url="ya.ru"):
		out, err = subprocess.Popen(["ping", url, "-c", "1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		return err.decode("utf-8") != "ping: unknown host %s\n" % url

	def up(self):
		subprocess.Popen(["pon", "dsl-provider"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def down(self):
		subprocess.Popen(["poff", "dsl-provider"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def try_up(self):
		tries = 0
		while not self.check():
			if tries > 2:
				self.down()
				print("Downing...")
				time.sleep(1)
			self.up()
			tries += 1
			print("Upping... (try %s)" % tries)

			time.sleep(1)

		print("Connected")

	def run(self, target: str):
		self._running = True
		if target == "up":
			self.up()
			time.sleep(1)
			if self.check():
				print("Connection upped")
			else:
				print("Failed to up connection")
		elif target == "down":
			self.down()
			time.sleep(1)
			if self.check():
				print("Failed to down connection")
			else:
				print("Connection downed")
		elif target == "check":
			if self.check():
				print("true")
			else:
				print("false")
		elif target == "watch":
			tries = 1
			while self._running:
				try:
					if not self.check():
						if tries > 2:
							self.down()
							print("Downing...")
							time.sleep(1)
						self.up()
						tries += 1
						print("Upping... (try %s)" % tries)
					elif tries > 0:
						print("Upped!")
						tries = 0
					time.sleep(1)
				except KeyboardInterrupt:
					print("Stopping watching...")
					self._running = False
		else:
			print("Unknown target %s" % target)
		self._running = False


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Expected 1 argument")
		sys.exit(1)
	elif sys.argv[1] not in ["up", "down", "check", "watch"]:
		print("Unknown command %s" % sys.argv[1])
		sys.exit(1)

	ConnD().run(target=sys.argv[1])
