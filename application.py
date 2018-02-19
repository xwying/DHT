import socket
from client import Client
import random
from tqdm import tqdm
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
num_success=0
time_count=0
# Create link to server nodes
clients = []
for node in node_list:
	ip, port = node.split(':')
	clients.append(Client((ip, int(port))))

for i in range(num_operations):
	request_node = random.randint(0, num_node-1)
	key = str(random.randint(1,key_range))
	if random.random() > 0.4:
		message = ':'.join(['get', key]) + ";"
		failed = 'None'
	else:
		message = ':'.join(['put', key, put_value]) + ";"
		failed = 'False'

	print('{}:Sending message {} to node {}:'.format(i, message, request_node))
	start_time = timeit.default_timer()
	# response = send_request(message, node_list[request_node])
	response = clients[request_node].request(message.encode('utf-8')).decode('utf-8')
	end_time = timeit.default_timer()

	time_spend = end_time - start_time
	time_count += time_spend
	print(response)
	print('request {} takes {}'.format(i, time_spend))
	
	if response.split(':')[-1] is not failed:
		num_success += 1

	# time.sleep(2)
	
# time.sleep(15)
[client.close() for client in clients]
print('number of success operation: ',num_success)
print('average query time: ', time_count / num_operations)