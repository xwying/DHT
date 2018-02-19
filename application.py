import socket
from client import Client
import random
import timeit
import time


num_operations = 5000
put_value = 'test'
key_range = 1000

def send_request(message, addr):
	ip, port = addr.split(':')
	with Client((ip, int(port))) as client:
		return client.request(message.encode('utf-8'))


with open('nodelist.txt', 'r') as f:
			content = f.readlines()
			node_list = [x.strip() for x in content]
num_node = len(node_list)

# Statistics
num_puts = 0
num_gets = 0
num_success_put = 0
num_success_get = 0
timeout_count = 0
time_count=0
# Create link to server nodes
clients = []
for node in node_list:
	ip, port = node.split(':')
	clients.append(Client((ip, int(port))))

# [client.request(b'timer:start') for client in clients]

for i in range(num_operations):
	request_node = random.randint(0, num_node-1)
	key = str(random.randint(1,key_range))
	if random.random() > 0.4:
		op = 'get'
		message = ':'.join([op, key]) + ";"
		failed = 'None'
		num_gets += 1
	else:
		op = 'put'
		message = ':'.join([op, key, put_value]) + ";"
		failed = 'False'
		num_puts += 1

	print('{}:Sending message {} to node {}:'.format(i, message, request_node))
	start_time = timeit.default_timer()
	# response = send_request(message, node_list[request_node])
	response = clients[request_node].request(message.encode('utf-8'))

	if response is None:
		continue
	else:
		response = response.decode('utf-8')
	end_time = timeit.default_timer()

	time_spend = end_time - start_time
	time_count += time_spend
	print(response)
	print('request {} takes {}'.format(i, time_spend))
	
	print(response.split(':')[-1])
	if response.split(':')[-1] != failed:
		if op == 'get':
			num_success_get += 1
		elif op == 'put':
			num_success_put += 1

	# time.sleep(2)
	
# time.sleep(15)

# [client.request(b'timer:stop') for client in clients]
[client.close() for client in clients]
print('{} out of {} puts sucesses.'.format(num_success_put, num_puts))
print('{} out of {} gets sucesses.'.format(num_success_get, num_gets))
# print('{} of queries got no response.'.format(timeout_count))
print('average query time: ', time_count / num_operations)