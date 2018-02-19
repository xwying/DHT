from hashlib import md5
from struct import unpack_from

class Hash_Table(object):
	def __init__(self, table_size):
		#Initialize the hashmap
		self.table_size = table_size
		self.hashmap = [None for i in range(table_size)]

	def put(self, key, value):
		index = self.__get_index(key)
		if self.hashmap[index] is not None:
			return False
		else:
			self.hashmap[index] = value
			return True

	def get(self, key):
		index = self.__get_index(key)
		if self.hashmap[index] is not None:
			return self.hashmap[index]
		else:
			return None

	def __get_index(self, hash_key):
		return self.generate_hash(hash_key) % self.table_size

	def generate_hash(self, key_str):
		md5_hash = md5(str(key_str).encode('utf-8')).digest()
		hash_key = unpack_from(">I", md5_hash)[0]
		return hash_key

# hashtable = Hash_Table(256)
# hashtable.put('Xiaowen', '123')
# hashtable.put('Xin', '456')
# print(hashtable.get('Xiaowen'))
# print(hashtable.get('Xin'))