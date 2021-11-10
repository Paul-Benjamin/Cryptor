############################################################################
#                     ____                  _                              #
#                    / ___|_ __ _   _ _ __ | |_ ___  _ __                  #
#                   | |   | '__| | | | '_ \| __/ _ \| '__|                 #
#                   | |___| |  | |_| | |_) | || (_) | |                    #
#                    \____|_|   \__, | .__/ \__\___/|_|     v1.0           #
#                               |___/|_|                                   #
#                                                                          #
#           Simple python script to encrypt files in linux. Supported      #
#   file format text, images, pdf. Note, This is Not written in view of    #
#   practical tool, instead testing python skill                           #
#                                                                          #
############################################################################
#                                                                          #
# Cryptor v1.0 - Uses AES algorithm, does not store key locally, password  #
# is the key used to encrypt/decrypt file.                                 #
#                                                                          #
############################################################################

#!/usr/bin/python3

import os
import pyfiglet
import argparse
import hashlib
import getpass
from Crypto import Cipher
from Crypto.Cipher import AES

parser = argparse.ArgumentParser()

parser.add_argument('-f', help='file name')
parser.add_argument('-m', help='mode encrypt or decrypt')
parser.add_argument('-r', help='for operation on directory (recursive)')
parser.add_argument('--v', help='banner GUI mode --v gui', nargs=1)

args = parser.parse_args()

CWD = os.getcwd()
newline = "\n"
linebreak1 = "_" * 44
linebreak2 = "-" * 44

def banner():
    print(linebreak1)
    print(pyfiglet.figlet_format("  Cryptor"))
    print("  ----Simple file encrypt/decrypt tool----")
    print(linebreak1)

class Cryptor:

	def __init__(self):
		pass

	def read_file(self, file):

		file_handle = open(file, 'rb')
		data = file_handle.read()
		file_handle.close()

		return data

	def recursive_encrypt(self, key, directory_name):


		for file in os.listdir(directory_name):

			file_in_dir = f'{directory_name}/{file}'
			data = self.read_file(file_in_dir)

			cipher = AES.new(key, AES.MODE_EAX)
			ciphertext, tag = cipher.encrypt_and_digest(data)

			file_handle = open(file_in_dir, 'wb')
			[file_handle.write(content) for content in (cipher.nonce, tag, ciphertext)]
			file_handle.close()

	def recursive_decrypt(self, key, directory_name):

			
		for file in os.listdir(directory_name):

			file_in_dir = f'{directory_name}/{file}'

			e_file_handle = open(file_in_dir, 'rb')
			nonce, tag, ciphertext = [e_file_handle.read(x) for x in (16,16,-1)]
			e_file_handle.close()

			cipher = AES.new(key, AES.MODE_EAX, nonce)
			decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

			with open(file_in_dir, 'w') as file_handle:
				file_handle.write(decrypted_data.decode())
		
	def encrypt_file(self, key, file_name):

		data = self.read_file(file_name)

		cipher = AES.new(key, AES.MODE_EAX)
		ciphertext, tag = cipher.encrypt_and_digest(data)

		file_handle = open(file_name, 'wb')
		[file_handle.write(content) for content in (cipher.nonce, tag, ciphertext)]
		file_handle.close()

	def decrypt_file(self, key, file_name):

		e_file_handle = open(file_name, 'rb')
		nonce, tag, ciphertext = [e_file_handle.read(x) for x in (16,16,-1)]
		e_file_handle.close()


		cipher = AES.new(key, AES.MODE_EAX, nonce)
		decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

		with open(file_name, 'w') as file_handle:
			file_handle.write(decrypted_data.decode())

msg_e = 'file encryption..done!'
msg_d = 'file decryption..done!'

cryptor = Cryptor()


if args.v != None:

	banner()

	encrypt_or_decrypt = input('encrypt or decrypt (e/d): ')

	directory = input('folder or file name: ')

	password = getpass.getpass('pick a password (length <= 16): ')

	password_hash = hashlib.sha256(bytes(password, 'utf-8')).hexdigest()[:16]


	key = bytes(password_hash, 'utf-8')

	if encrypt_or_decrypt == 'e':

		if '.' not in directory:
			cryptor.recursive_encrypt(key, directory)
			print(msg_e)

		if '.' in directory:

			cryptor.encrypt_file(key, directory)
			print(msg_e)

	if encrypt_or_decrypt == 'd':

		if '.' not in directory:
			cryptor.recursive_decrypt(key, directory)
			print(msg_d)

		if '.' in directory:

			cryptor.decrypt_file(key, directory)
			print(msg_d)

else:

	password = getpass.getpass('pick a password (length <= 16): ')

	password_hash = hashlib.sha256(bytes(password, 'utf-8')).hexdigest()[:16]


	key = bytes(password_hash, 'utf-8')

	if args.f and args.m == 'encrypt':
		cryptor.encrypt_file(key, args.f)
		print(msg_e)

	elif args.f and args.m == 'decrypt':
		cryptor.decrypt_file(key, args.f)
		print(msg_d)

	elif args.r and args.m == 'encrypt':
		cryptor.recursive_encrypt(key, args.r)
		print(msg_e)

	elif args.r and args.m == 'decrypt':
		cryptor.recursive_decrypt(key, args.r)
		print(msg_d)
