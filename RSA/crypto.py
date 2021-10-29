import os

from RSA.keys import PublicKey, PrivateKey, load_keys


def bytes_to_int(data):
    return int.from_bytes(data, "big", signed=False)


def int_to_bytes(data: int, size):
    return data.to_bytes(size, "big", signed=False)


def pad(block, size):
    padding_length = size - len(block)
    if padding_length < 11:
        raise OverflowError
    random_bytes = b""
    random_length = padding_length - 3
    new_random_bytes = os.urandom(random_length).replace(b"\x00", b"\x3c")
    random_bytes += new_random_bytes
    return b"".join([b"\x00\x03", random_bytes, b"\x00", block])


def encrypt(string, pub_key: PublicKey):
    string_length = len(string)
    key_size = pub_key.byte_length
    blocksize = pub_key.byte_length - 11
    div_mod_res = divmod(string_length, blocksize)
    result = []
    print(div_mod_res[0]+1)
    for block in range(div_mod_res[0] if div_mod_res[1] == 0 else div_mod_res[0] + 1):
        result.append(int_to_bytes(pub_key.encrypt(bytes_to_int(pad(string[block * blocksize:(block + 1) * blocksize], key_size))), key_size))
    return b"".join(result)


def decrypt(string, priv_key: PrivateKey):
    string_length = len(string)
    key_size = priv_key.byte_length
    blocksize = priv_key.byte_length - 11
    div_mod_res = divmod(string_length, key_size)
    result = []
    for block in range(div_mod_res[0] if div_mod_res[1] == 0 else div_mod_res[0] + 1):
        padded_message = int_to_bytes(priv_key.decrypt(bytes_to_int(string[block * key_size:(block + 1) * key_size])), key_size)
        first_mark = padded_message.find(b"\x00\x03")
        second_mark = padded_message.find(b"\x00", 3)
        if first_mark == -1:
            raise Exception
        result.append(padded_message[second_mark + 1:])
    return b"".join(result)


def encrypt_file(filepath, pub_key: PublicKey):
    path, filename = os.path.split(filepath)
    filename += ".ENC"
    with open(filepath, "rb") as file:
        data = file.read()
    encrypted = encrypt(data, pub_key)
    with open(os.path.join(path, filename), "wb") as file:
        file.write(encrypted)


def decrypt_file(filepath, priv_key: PrivateKey):
    path, filename = os.path.split(filepath)
    with open(os.path.join(path, filename + ".ENC"), "rb") as file:
        data = file.read()
    decrypted = decrypt(data, priv_key)
    with open(os.path.join(path, filename + ".DEC"), "wb") as file:
        file.write(decrypted)


if __name__ == '__main__':
    pvk, pbk = load_keys("1024")
    encrypt_file("C:/Users/RockP/Downloads/Exercise1_BufferOverflow_Task2.mp4", pbk)
    decrypt_file("C:/Users/RockP/Downloads/Exercise1_BufferOverflow_Task2.mp4", pvk)
    # encrypted = encrypt(
    #     "This is a really long test message to test all the functions that I want to test This is a really long test "
    #     "message to test all the functions that I want to test This is a really long test message to test all the "
    #     "functions that I want to test This is a really long test message to test all the functions that I want to "
    #     "test This is a really long test message to test all the functions that I want to test This is a really long "
    #     "test message to test all the functions that I want to test This is a really long test message to test all "
    #     "the functions that I want to test This is a really long test message to test all the functions that I want "
    #     "to test This is a really long test message to test all the functions that I want to test This is a really "
    #     "long test message to test all the functions that I want to test This is a really long test message to test "
    #     "all the functions that I want to test This is a really long test message to test all the functions that I "
    #     "want to test This is a really long test message to test all the functions that I want to test This is a "
    #     "really long test message to test all the functions that I want to test This is a really long test message to "
    #     "test all the functions that I want to test This is a really long test message to test all the functions that "
    #     "I want to test This is a really long test message to test all the functions that I want to test This is a "
    #     "really long test message to test all the functions that I want to test This is a really long test "
    #     "message to test all the functions that I want to test This is a really long test message to test all the "
    #     "functions that I want to test This is a really long test message to test all the functions that I want to "
    #     "test This is a really long test message to test all the functions that I want to test This is a really long "
    #     "test message to test all the functions that I want to test This is a really long test message to test all "
    #     "the functions that I want to test This is a really long test message to test all the functions that I want "
    #     "to test This is a really long test message to test all the functions that I want to test This is a really "
    #     "long test message to test all the functions that I want to test This is a really long test message to test "
    #     "all the functions that I want to test This is a really long test message to test all the functions that I "
    #     "want to test This is a really long test message to test all the functions that I want to test This is a "
    #     "really long test message to test all the functions that I want to test This is a really long test message to "
    #     "test all the functions that I want to test This is a really long test message to test all the functions that "
    #     "I want to test This is a really long test message to test all the functions that I want to test".encode(
    #         "utf-8"),
    #     pbk)
    # print(encrypted)
    # decrypted = decrypt(encrypted, pvk)
    # print(decrypted)
