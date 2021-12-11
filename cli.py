from RSA.crypto import encrypt, decrypt, encrypt_file, decrypt_file
from RSA.keys import PublicKey, PrivateKey, generate_keys, save_keys, load_keys
from Measure.timing import timed
from os import listdir, remove, urandom, makedirs
import os.path as path
from datetime import date
import time
import codecs
import shlex
import json

PVK: PrivateKey = None
PBK: PublicKey = None
KEYS_DIR = "Keys"
DATA_DIR = ".data"

TESTING_CONFIG = {
    "key_sizes": [1024, 2048, 3072, 4096],
    "num_of_runs": 100,
    "message_sizes": [1024, 1024 * 4, 1024 * 16, 1024 * 64]
}


def show_help(*args):
    if len(args) > 0:
        val_args = validate_inputs(args, [str])
        if all(val_args):
            command = val_args[0]
            if command in COMMANDS_HELP:
                print(COMMANDS_HELP[command])
            else:
                print(f"There is no command '{command}'. Please use 'help' to see available commands.")
    else:
        possible_commands = "\n".join(COMMANDS.keys())
        print("Type 'help <command name>' to get more information on a specific command.")
        print(f"The available commands are:\n{possible_commands}")


def generate_new_key(*args):
    if len(args) == 2:
        val_args = validate_inputs(args, [str, int])
        if all(val_args):
            key_name = val_args[0]
            key_size = val_args[1]
            n, e, d = generate_keys(key_size)
            save_keys(n, e, d, key_name)
            load_given_keys(key_name)
    else:
        print("Improper number of arguments!")
        print("keygen usage:")
        print(COMMANDS_HELP["keygen"])


def list_available_keys(*args):
    if len(args) < 1:
        if not path.exists('Keys'):
            makedirs('Keys')
        key_list = "\n".join(sorted([key for key in listdir('Keys') if ".pub" not in key]))
        print(key_list)
    else:
        print("Improper number of arguments!")
        print("keylist usage:")
        print(COMMANDS_HELP["keylist"])


def load_given_keys(*args):
    if len(args) == 1:
        val_args = validate_inputs(args, [str])
        if all(val_args):
            key_name = val_args[0]
            global PVK, PBK
            PVK, PBK = load_keys(key_name)
            if not all([PVK, PBK]):
                print(f"Failed to load key with name '{key_name}'!")
    else:
        print("Improper number of arguments!")
        print("load usage:")
        print(COMMANDS_HELP["load"])


def unload_current_keys(*args):
    if len(args) < 1:
        global PVK, PBK
        PVK, PBK = None, None
    else:
        print("Improper number of arguments!")
        print("unload usage:")
        print(COMMANDS_HELP["load"])


def delete_given_key(*args):
    if len(args) == 1:
        val_args = validate_inputs(args, [str])
        if all(val_args):
            key_name = val_args[0]
            if path.exists(path.join(KEYS_DIR, key_name)):
                remove(path.join(KEYS_DIR, key_name))
                remove(path.join(KEYS_DIR, key_name + ".pub"))
                global PVK, PBK
                if all([PVK, PBK]):
                    if key_name == PVK.name and key_name == PBK.name:
                        PVK, PBK = None, None
            else:
                print(f"No such key '{key_name}'")
    else:
        print("Improper number of arguments!")
        print("delkey usage:")
        print(COMMANDS_HELP["delkey"])


def encrypt_message_or_file(*args):
    if all([PBK, PVK]):
        is_file = False
        if 1 <= len(args) <= 2:
            if "--file" in args or "-f" in args:
                is_file = True
                args = [arg for arg in args if arg != "--file" and arg != "-f"]
            val_args = validate_inputs(args, [str])
            if is_file:
                filepath = val_args[0]
                if path.exists(filepath):
                    encrypt_file(filepath, PBK)
                else:
                    print(f"No such file '{filepath}' exists!")
            else:
                message = val_args[0]
                encrypted = encrypt(message.encode("utf-8"), PBK)
                print(encrypted)
        else:
            print("Improper number of arguments!")
            print("encrypt usage:")
            print(COMMANDS_HELP["encrypt"])
    else:
        print(
            "No key pair has been selected! Please select or generate a key pair before trying to encrypt or decrypt.")


def decrypt_message_or_file(*args):
    if all([PBK, PVK]):
        is_file = False
        if 1 <= len(args) <= 2:
            if "--file" in args or "-f" in args:
                is_file = True
                args = [arg for arg in args if arg != "--file" and arg != "-f"]
            val_args = validate_inputs(args, [str])
            if is_file:
                filepath = val_args[0]
                if path.exists(filepath):
                    decrypt_file(filepath, PVK)
                else:
                    print(f"No such file '{filepath}' exists!")
            else:
                message = codecs.decode(val_args[0], "unicode_escape")
                decrypted = decrypt(message.encode("latin-1"), PVK)
                print(codecs.decode(decrypted, "utf-8"))
        else:
            print("Improper number of arguments!")
            print("decrypt usage:")
            print(COMMANDS_HELP["decrypt"])
    else:
        print(
            "No key pair has been selected! Please select or generate a key pair before trying to encrypt or decrypt.")


def timed_data_gather(*args):
    confirm = input("WARNING! This could take several hours! Are you sure you want to continue? [y/yes] ").lower() in ["y", "yes"]
    if confirm:
        results = {}
        runs = TESTING_CONFIG["num_of_runs"]
        num_key_sizes = len(TESTING_CONFIG["key_sizes"])
        num_message_sizes = len(TESTING_CONFIG["message_sizes"])
        for i, key_size in enumerate(TESTING_CONFIG["key_sizes"]):
            key_gen_res = timed(generate_keys, (2048,), runs=runs, name=f"{key_size}")
            results.update(key_gen_res)

            pvk, pbk = load_keys(str(key_size))
            if not all([pvk, pbk]):
                generate_new_key((str(key_size), key_size))
                pvk, pbk = load_keys(str(key_size))

            for j, message_size in enumerate(TESTING_CONFIG["message_sizes"]):
                message = urandom(message_size)
                enc_message, enc_res = timed(encrypt, (message, pbk), runs=runs, name=f"{message_size}_{key_size}",
                                             ret_val=True)
                dec_message, dec_res = timed(decrypt, (enc_message, pvk), runs=runs, name=f"{message_size}_{key_size}",
                                             ret_val=True)
                if message != dec_message:
                    print("MESSAGES DO NOT MATCH")
                    return
                results.update(enc_res)
                results.update(dec_res)
                print((((i * num_message_sizes) + (j + 1)) / (num_key_sizes * num_message_sizes)) * 100, "%")
        if not path.exists(DATA_DIR):
            makedirs(DATA_DIR)
        with open(path.join(DATA_DIR,
                            f"{date.today().isoformat()}_{time.localtime().tm_hour}-{time.localtime().tm_min}-{time.localtime().tm_sec}.json"),
                  "w") as file:
            json.dump(results, file)


def exit_cli(*args):
    exit()


COMMANDS_HELP = {
    "help": "Displays a list of possible commands. When given another command as an argument it will tell more about "
            "that command. 'help keygen'",
    "keygen": "Takes a size and a name to generate a new key pair. 'keygen 2048 my-key'",
    "keylist": "Lists the available keys to select. 'keylist'",
    "load": "Takes a name and tries to select a generated key pair with that name. 'load my-key'",
    "unload": "Unloads the currently loaded key. Does nothing if there are no loaded keys. 'unload'",
    "delkey": "Tries to delete a key with the given name. 'delkey my-key'",
    "encrypt": "Encrypt a message or file. If the --file or -f flag is given, encrypt will expect the other argument "
               "to be a filepath. 'encrypt \"My message to encrypt\"' or 'encrypt -f path/to/file/name'",
    "decrypt": "Decrypt a message or file. If the --file or -f flag is given, decrypt will expect the other argument "
               "to be a filepath. 'decrypt \"My message to decrypt\"' or 'decrypt -f path/to/file/name'",
    "timed": "Runs a set of predetermined test to get the average times it takes for several key generations, "
             "encryptions, and decryptions to run",
    "exit": "exits the program"
}
COMMANDS = {
    "help": show_help,
    "keygen": generate_new_key,
    "keylist": list_available_keys,
    "load": load_given_keys,
    "unload": unload_current_keys,
    "delkey": delete_given_key,
    "encrypt": encrypt_message_or_file,
    "decrypt": decrypt_message_or_file,
    "timed": timed_data_gather,
    "exit": exit_cli
}


def validate_inputs(args, types):
    return [_validate_input(arg, types[i]) for i, arg in enumerate(args) if i < len(types)]


def _validate_input(value, val_type):
    try:
        new_val = val_type(value)
    except ValueError:
        return None
    return new_val


def main():
    print("Welcome to RSA Tool. Type 'help' to see a list of commands.")
    while 1:
        user_input = input(f"{PBK.name + '-' + str(PBK.bit_length) if PBK else str()}:> ")
        if user_input == "":
            continue
        try:
            user_split = shlex.split(user_input)
        except ValueError as err:
            print(err)
            continue
        command = user_split[0]
        if command in COMMANDS:
            COMMANDS[command](*user_split[1:])
        else:
            print(f"There is no command '{command}'. Please use 'help' to see available commands.")


if __name__ == '__main__':
    main()
