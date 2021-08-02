############################################################################
#                     ____                  _                              #
#                    / ___|_ __ _   _ _ __ | |_ ___  _ __                  #
#                   | |   | '__| | | | '_ \| __/ _ \| '__|                 #
#                   | |___| |  | |_| | |_) | || (_) | |                    #
#                    \____|_|   \__, | .__/ \__\___/|_|                    #
#                               |___/|_|                                   #
#                                                                          #
#           Simple python script to encrypt files in linux. Supported      #
#   file format text, images, pdf. Note, This is Not written in view of    #
#   practical tool, instead testing python skill                           #
#                                                                          #
############################################################################
#!/usr/bin/python3

import os
from os import stat
import subprocess
import pyfiglet
import platform
import getpass
import hashlib
from cryptography.fernet import Fernet
import argparse
import zipfile
from compressor import compress_file, decompress_file

user = getpass.getuser()
newline = "\n"
linebreak1 = "_" * 44
linebreak2 = "-" * 44

parser = argparse.ArgumentParser()

parser.add_argument('-d', help='location of file (full path)', nargs='?')
parser.add_argument('-r', help='recursive on directory', nargs='?')

args = parser.parse_args()


if args.d != None:
    file_location = args.d
    directory_name = file_location.split("/")[-1]
    file_name = args.d.split("/")[-1]
elif args.r != None:
    file_location = args.r
    directory_name = file_location.split("/")[-1]
else:
    print("insufficient arguments! type pycrypt.py -h to know more.")
    exit()



def banner():
    print(linebreak1)
    print(pyfiglet.figlet_format("  Cryptor"))
    print("  ----Simple file encrypt/decrypt tool----")
    print(linebreak1)


if platform.system() == "Linux":

    def password_hash(password):
        m = hashlib.sha256(bytes(password, 'utf-8'))
        return m.hexdigest()

    def selectFileToEncrypt():

        if args.d != None:

            # index_of_file = int(input("Enter file index: "))
            with open(file_location, "rb") as scope_file:
                data = scope_file.read()
            # print(data)

            password = getpass.getpass(prompt="pick a password:")

            # store password hash
            with open(f".{file_name}.auth", "w") as authFile:
                authFile.write(password_hash(password))

            # store key used for encryption and decryption
            with open(f".{file_name}.sign", "wb") as fileKey:
                fileKey.write(Fernet.generate_key())
                fileKey.write(b"\n")

            # read key to encrypt file
            with open(f".{file_name}.sign", "rb") as fileKey:
                key = fileKey.read()

            f = Fernet(key)

            # store encrypted data
            try:
                os.mkdir(f"/home/{user}/.cryptor")
            except FileExistsError:
                pass

            encrypted_data = f.encrypt(data)

            # overwrite content in file with encrypted data
            with open(file_location, "wb") as scope_file:
                scope_file.write(encrypted_data)

            crnt_dir = os.getcwd()

            # move key and hash file
            #os.chmod(f"/home/{user}/.cryptor", int("0444"))
            subprocess.call(['chmod', '-R', '700', f"/home/{user}/.cryptor"])
            os.rename(f"{crnt_dir}/.{file_name}.sign",
                        f"/home/{user}/.cryptor/.{file_name}.sign")
            os.rename(f"{crnt_dir}/.{file_name}.auth",
                        f"/home/{user}/.cryptor/.{file_name}.auth")
        
        elif args.r != None:

            password = getpass.getpass(prompt="pick a password:")

            # store password hash
            with open(f"/home/{user}/.cryptor/.{directory_name}.auth", "w") as authFile:
                authFile.write(password_hash(password))

            os.chdir(file_location)

            # index_of_file = int(input("Enter file index: "))
            for file in os.listdir(file_location):
                if not file.startswith("."):
                    with open(file, "rb") as scope_file:
                        data = scope_file.read()
                    # print(data)

                    # store key used for encryption and decryption
                    with open(f".{file}.sign", "wb") as fileKey:
                        fileKey.write(Fernet.generate_key())
                        fileKey.write(b"\n")

                    # read key to encrypt file
                    with open(f".{file}.sign", "rb") as fileKey:
                        key = fileKey.read()

                    f = Fernet(key)

                    # store encrypted data
                    try:
                        os.mkdir(f"/home/{user}/.cryptor")
                    except FileExistsError:
                        pass

                    encrypted_data = f.encrypt(data)

                    # overwrite content in file with encrypted data
                    with open(file, "wb") as scope_file:
                        scope_file.write(encrypted_data)

                    crnt_dir = os.getcwd()

                    # move key and hash file
                    os.rename(f"{crnt_dir}/.{file}.sign",
                                f"/home/{user}/.cryptor/.{file}.sign")
                

        # status
        print("file encryption, done..")

    def selectFileToDecrypt():

        # read password hash
        with open(f"/home/{user}/.cryptor/.{directory_name}.auth", "rb") as stored_hash:
            hash_value = stored_hash.read()

        tries = 0

        while tries < 3:
            password = getpass.getpass(prompt="enter password:")
            password = password_hash(password)
            # compare currently entered password hash with stored password hash
            if password != hash_value.decode('utf-8') and tries < 2:
                print("incorrect password. try again")
                tries += 1

            elif password != hash_value.decode('utf-8') and tries == 2:
                print("too many failed attempts. try after sometime.")
                exit()

            elif password == hash_value.decode('utf-8'):

                if args.d != None:

                    with open(file_location, "rb") as encrypted_file:
                        encrypted_data = encrypted_file.read()

                    # read stored key
                    with open(f"/home/{user}/.cryptor/.{file_name}.sign", "rb") as fileKey:
                        key = fileKey.read()

                    f = Fernet(key.strip())

                    # stored decrypted data
                    decrypted_data = f.decrypt(encrypted_data)

                    # overwrite encrypted data with decrypted data
                    with open(file_location, "wb") as encrypted_file:
                        encrypted_file.write(decrypted_data)

                    # remove key and hash file after decryption to clean up space
                    os.remove(f"/home/{user}/.cryptor/.{file_name}.sign")
                    os.remove(f"/home/{user}/.cryptor/.{file_name}.auth")
                
                elif args.r != None:

                    os.chdir(file_location)

                    for file in os.listdir(file_location):

                        with open(file, "rb") as encrypted_file:
                            encrypted_data = encrypted_file.read()
                
                    # read stored key
                        with open(f"/home/{user}/.cryptor/.{file}.sign", "rb") as fileKey:
                            key = fileKey.read()

                        f = Fernet(key.strip())

                        # stored decrypted data
                        decrypted_data = f.decrypt(encrypted_data)

                        # overwrite encrypted data with decrypted data
                        with open(file, "wb") as encrypted_file:
                            encrypted_file.write(decrypted_data)

                        # remove key and hash file after decryption to clean up space
                        os.remove(f"/home/{user}/.cryptor/.{file}.sign")

                # status
                print("file decryption, done..")
                break

    def startProgram():

        banner()

        print("""
options:
        e - encrypt file
        d - decrypt file
        ez - encrypt & zip file (gzip)
        dz - decrypt & unzip file (gzip)
        """)

        encrypt_or_decrypt = input("command:")

        if encrypt_or_decrypt == "e":
            try:
                selectFileToEncrypt()

            except FileNotFoundError:
                print(
                    "Oops error: failed encrypting file.\nCheck if directory name is correct or if file exits.")
                exit() 

        elif encrypt_or_decrypt == "d":
            
            try:
                selectFileToDecrypt()

            except FileNotFoundError:
                print(
                    "Oops error: failed decrypting file.\nCheck if directory name is correct or if file exits.")
                exit()

        elif encrypt_or_decrypt == "ez":
            try:
                selectFileToEncrypt()
                compress_file()

            except FileNotFoundError:
                print(
                    "Oops error: failed encrypting file.\nCheck if directory name is correct or if file exits.")
                exit()

        elif encrypt_or_decrypt == "dz":
            try:
                decompress_file()
                selectFileToDecrypt()

            except FileNotFoundError:
                print(
                    "Oops error: failed encrypting file.\nCheck if directory name is correct or if file exits.")
                exit()

        else:
            print("Invalid argument")
            exit()

    try:
        startProgram()

    except KeyboardInterrupt:
        print("\nexiting the program..")
        exit()


else:
    print("Sorry, Cryptor for Windows and Mac currently not available.")


