import socket
import sys

class Client(object):
	def __init__(self, addr):
		# self.port = port
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.client_socket.connect(addr)
		self.client_socket.settimeout(0.2)
		# self.client_socket.setblocking(0)

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()
		return False

	def __enter__(self):
		return self

	def close(self):
		try:
			self.client_socket.send(b'close')
		except socket.error:
			print('client: CLOSURE WAS UNSUCCESSFUL')
			# logging.error('client: CLOSURE WAS UNSUCCESSFUL')
			sys.exit()
		else:
			self.client_socket.recv(1024)
			self.client_socket.close()

	def request(self, message):
		try:
			self.client_socket.send(message)
		except socket.error:
			print('client: SEND MESSAGE FAIL')
			# logging.error('client: SEND MESSAGE FAIL')
			sys.exit()

		try:
			self.answer = self.client_socket.recv(1024)
		except socket.error:
			print('client: READ MESSAGE FAIL')
			# self.answer = self.request(message)
			# logging.error('client: READ MESSAGE FAIL '+ str(self.PORT))
			pass
		except socket.timeout:
			# self.answer = self.request(message)
			pass
		else:
			return self.answer