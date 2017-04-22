#!/usr/bin/python
import time
import socket
import sys
import signal
from consts import ServerConnectionConsts


class GlobalClockClient(object):
	"""Synchronized clock client"""
	def __init__(self, host = ServerConnectionConsts.TCP_IP, port = ServerConnectionConsts.TCP_PORT):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ServerConnectionConsts.TCP_IP, ServerConnectionConsts.TCP_PORT))
  
        # Trap keyboard interrupts
		signal.signal(signal.SIGINT, self.sig_handler)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((host, port))
			print 'Connected to server.'
		except socket.error, e:
			print 'Could not connect to server.'
			sys.exit(1)
        
	def sig_handler(self, signum, frame):
		print "Closing connection..."
		self.s.close()


	
	def get_time(self):
		running = 1
		while running:
			try:
				msg = time.time()
				self.s.send(str(msg))
				masterTime = self.s.recv(ServerConnectionConsts.BUFFER_SIZE)
				if not masterTime:
					break
				print masterTime
				time.sleep(1)
			except KeyboardInterrupt:
				print "Interrupted."
				self.s.close()
				break
		self.s.close()
		