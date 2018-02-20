import socket
import threading
from hash_table import Hash_Table
import queue as Queue
import time
from hashlib import md5
from struct import unpack_from
import sys
from client import Client
import timeit

class Server(object):
	def __init__(self, port):
		# Defining available operations with dictionary for easily adding features
		self.operations = {'get': self.__get,
						   'put': self.__put,
						   'close': self.__quit,
						   'timer': self.__timer}
		self.server_port = port
		self.server_ip = socket.gethostbyname(socket.gethostname())
		self.server_address = ':'.join([self.server_ip, str(self.server_port)])
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(1)
		# self.port = port
		self.thread_list = []
		self.mutex = threading.Lock()
		self.message_queues = {}
		self.shutdown = False


		self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		self.socket.bind((self.server_ip, self.server_port))
		self.socket.listen(10)

		with open('nodelist.txt', 'r') as f:
			content = f.readlines()
			self.node_list = [x.strip() for x in content]

		self.num_nodes = len(self.node_list)
		self.table_size = 1024
		self.hash_table = Hash_Table(self.table_size)
		self.node_links = {}


		self.operation_count=0
		self.start_time = None
		self.start_flag = 0
		self.end_time = None
		self.end_flag = 0


	def __del__(self):
		"""Destructor"""
		self.socket.close()

	def run(self): # Main Loop
		print('Starting Server at {}'.format(self.server_address))
		print('Waiting for connection...')
		while True:
			try:
				print('number of connection = ', len(self.message_queues.keys()))
				conn, addr = self.socket.accept()
			except socket.timeout:
				print('socket time out')
				pass
			else:
				self.message_queues[conn] = Queue.Queue()
				now_thread = threading.Thread(target=self.tcplink, args=(conn, addr))
				self.thread_list.append(now_thread)
				
				# print(len(self.thread_list))
				now_thread.start()
				
				# self.thread_list[-1].daemon=True
				# self.thread_list[-1].start()

	def tcplink(self, conn, addr):
		if self.start_flag == 0:
			self.start_flag = 1
			self.start_time = timeit.default_timer()

		while True:
			try:
				print('number of connection = ', len(self.message_queues.keys()))
				data = conn.recv(1024).decode('utf-8')
				# time.sleep(0.1)
				if not data:
					break
				else:
					for msg in data.strip(';').split(';'):
						print(msg)
						operate = self.operations.get(msg.split(':')[0], self.__badrequest)
						operate(msg, conn)
			except socket.error:
				print('Data Receive Failed')
				break

			else:
				try:
					# self.mutex.acquire()
					pending_msg = self.message_queues[conn].get_nowait()
					# self.mutex.release()
				except Queue.Empty:	
					continue
				else:
					# self.mutex.acquire()
					# print('sending message in queue')
					print(pending_msg)
					if pending_msg is None:
						continue
					conn.send(pending_msg)
					# print('message in queue sended')
					# self.mutex.release()
					# self.mutex.release()
					if pending_msg == b'CLOSE CONNECTION':
						# time.sleep(5)
						del self.message_queues[conn]
						conn.close()
						print('Close connection from %s:%s...' % addr)
						# print('number of connection = ', len(self.message_queues.keys()))
						if len(self.message_queues.keys()) <= 2:
							self.end_time = timeit.default_timer()
							print('Average Throughput = ', self.operation_count/ (self.end_time - self.start_time))
						return

		# print('thread end')
		# 
		# # time.sleep(3)
		# del self.message_queues[conn]
		# # # time.sleep(3)
		# conn.close()
		# # # [self.node_links[addr].close() for addr in self.node_links.keys()]
		# return

	def send_request(self, message, addr):
		ip, port = addr.split(':')
		if addr not in self.node_links:
			self.node_links[addr] = Client((ip, int(port)))

		return self.node_links[addr].request(message.encode('utf-8'))
		# with Client((ip, int(port))) as client:
		# 	return client.request(message.encode('utf-8'))

	def __get(self, data, conn):
		# data_format = get:key
		_, key = data.split(':')
		target_node = self.__findNode(key) # check which node has the key
		print('{} is located on node {}'.format(key, target_node))

		# If the key is stored in this node
		if self.server_address == self.node_list[target_node]:
			self.mutex.acquire()
			# print('mutex locked')
			value = self.hash_table.get(key)
			self.mutex.release()
			# print('mutex released')

			if value is not None:
				print('get operation success.')

			else:
				print('get operation failed')

			response = '{}:{}:{}'.format('get', key, str(value)).encode('utf-8')
		# If the key is in another node, send request to the target node.
		else:
			response = self.send_request(data + ';', self.node_list[target_node])
			# print(response)
		print()
		self.operation_count += 1
		self.message_queues[conn].put(response)

	def __put(self, data, conn):
		# data_format = put:key:value
		_, key, value = data.split(':')

		target_node = self.__findNode(key) # check which node shoud store the key
		print('{} is located on node {}'.format(key, target_node))

		# If the key shoud be stored in this node
		if self.server_address == self.node_list[target_node]: 
			self.mutex.acquire()

			sucesses = self.hash_table.put(key, value)
			self.mutex.release()

			if sucesses:
				print('put operation success.')
			else:
				print('put operation failed')

			response = '{}:{}:{}:{}'.format('put', key, value, sucesses).encode('utf-8')
		# If the key is in another node, send request to the target node.
		else:
			response = self.send_request(data + ';', self.node_list[target_node])
		print()
		self.operation_count += 1
		self.message_queues[conn].put(response)

	def __badrequest(self, data, conn):
		self.message_queues[conn].put(b'This operation is not supported.')

	def __quit(self, data, sock):
		print('we are in __quit')
		# time.sleep(5)
		self.message_queues[sock].put(b'CLOSE CONNECTION')

	def __timer(self, data, sock):
		# data format = timer:start / timer:stop
		_, op = data.split(":")
		if op == 'start' and self.start_time == None:
			self.start_time = timeit.default_timer()
			self.message_queues[sock].put(b'Start Timmer')
		elif op == 'stop':
			self.end_time_flag += 1
			print('end_time_flag=',self.end_time_flag)
			if self.end_flag == 3:
				self.end_time = timeit.default_timer()
				self.message_queues[sock].put(b'Stop Timmer')
				self.end_time_flag = 0
				print('Average Throughput = ', self.operation_count/ (self.end_time - self.start_time) )


	def __findNode(self, key_str):
	# Find the node that stores the key
		target_node = self.__generate_hash(key_str) % self.num_nodes
		return target_node

	def __generate_hash(self, key_str):
		md5_hash = md5(str(key_str).encode('utf-8')).digest()
		hash_key = unpack_from(">I", md5_hash)[0]
		return hash_key

def main():
	_port = sys.argv[1]
	my_node = Server(port=int(_port))
	my_node.run()

if __name__ == "__main__":
    main()
