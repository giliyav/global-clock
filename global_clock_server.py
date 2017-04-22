import socket
import time
import signal
import sys
import select
from consts import ServerConnectionConsts
from consts import ClientInfo

class GlobalClockServer(object):
	"""Synchronized clock server"""
	def __init__(self, port = ServerConnectionConsts.TCP_PORT , max_connections = ServerConnectionConsts.NUM_CONNECTIONS):
		self.num_clients = 0
		self.master = None
		self.clientmap = {}
        # Output socket list
		self.outputs = []

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.setblocking(0)
		self.server.bind(('localhost', port))
		self.server.listen(max_connections)

        # Trap keyboard interrupts
		signal.signal(signal.SIGINT, self.sigHandler)
		self.lastbroadcasttime = -1
        
	def sigHandler(self, signum, frame):
        # Close the server
		print 'Shutting down server'
        # Close existing client sockets
		for o in self.outputs:
			o.close()
		self.server.close()
        
	def sync_time(self):
		inputs = [self.server]
		self.outputs = []

		running = 1

		while running:
			try:
				inputready,outputready,exceptready = select.select(inputs, self.outputs, [], 1)
			except select.error, e:
				break
			except socket.error, e:
				break

			for s in inputready:
				if s == self.server:
					# Handle the server socket
					client, address = self.server.accept()
					inputs.append(client)
					self.outputs.append(client)
					self.num_clients += 1
					timestamp = time.time()
					self.clientmap[client] = (address, None, timestamp)
 				else:
					try:
						# Update current time
						data = s.recv(ServerConnectionConsts.BUFFER_SIZE)
						if data:
							address = self.clientmap[client][ClientInfo.ADDRESS]
							data = float(data)
							timestamp = time.time()
							self.clientmap[client] = (address, data, timestamp)
						else:
							self.num_clients -= 1
							s.close()
							inputs.remove(s)
							self.outputs.remove(s)
                                
					except socket.error, e:
						inputs.remove(s)
						self.outputs.remove(s)
				
				# Brodcast new time
				if self.num_clients > 0 and time.time() > self.lastbroadcasttime + 1:
					master = self.get_master()
					if (master == None):
						print "No client with up to date time."
					else:
						master_time = self.clientmap[master][ClientInfo.TIME]
						for s in outputready:
							s.send(str(master_time))
						self.lastbroadcasttime = time.time()

		self.server.close()

	def get_master(self):
		''' Return the socket of the process that is the master clock'''
		currTime =  time.time()
		if self.master != None:
			# If 
			if self.master in self.outputs and \
			self.clientmap[self.master][ClientInfo.TIMESTAMP] + 60 >  currTime:
				return self.master
		self.master = None
		print "Choose new master!"
		for client in self.clientmap.keys():
			if self.clientmap[client][ClientInfo.TIMESTAMP] + 60 >  time.time()\
			and self.clientmap[client][ClientInfo.TIME] != None:
				self.master = client
		return self.master