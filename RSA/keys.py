import os.path
import random
from RSA.prime_tools import generate_primes

DEFAULT_E_VALUE = 65537


def _lcm(a, b):
    return abs(a * b) // _gcd(a, b)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _egcd(a, b):
    x, y, x1, y1 = 0, 1, 1, 0
    while b:
        q = a // b
        x, x1 = x1 - (q * x), x
        y, y1 = y1 - (q * y), y
        a, b = b, a % b
    return a, x1, y1


def _validate_p_and_q(p, q, key_size):
    if p == q:
        return False
    if (p * q).bit_length() != key_size:
        return False
    return True


def generate_keys(key_size=1024, random_e=False):
    prime_bit_length = key_size // 2
    offset = prime_bit_length // 16
    p_bit_length = prime_bit_length + offset
    q_bit_length = prime_bit_length - offset

    p = generate_primes(p_bit_length)
    q = generate_primes(q_bit_length)

    adjust_p = True
    while not _validate_p_and_q(p, q, key_size):
        if adjust_p:
            p = generate_primes(p_bit_length)
            adjust_p = False
        else:
            q = generate_primes(q_bit_length)
            adjust_p = True
    n = p * q
    lambda_n = _lcm(p - 1, q - 1)
    e = DEFAULT_E_VALUE
    if random_e:
        while _gcd((e := random.randint(1, lambda_n - 1)), lambda_n) != 1:
            continue
    _, d, _ = _egcd(e, lambda_n)
    if d < 0:
        d += lambda_n
    return n, e, d


def save_keys(n, e, d, name):
    if not os.path.exists("Keys"):
        os.mkdir("Keys")
    filepath = f"Keys/{name}"
    with open(filepath, "w") as file:
        file.write(str(n))
        file.write("\n")
        file.write(str(d))
    with open(f"{filepath}.pub", "w") as file:
        file.write(str(n))
        file.write("\n")
        file.write(str(e))


def load_keys(name):
    filepath = f"Keys/{name}"
    pvk_data = []
    pbk_data = []
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                pvk_data.append(int(line))
    except FileNotFoundError:
        pvk = None
    else:
        pvk = PrivateKey(name, int(pvk_data[0]), int(pvk_data[1]))
    try:
        with open(f"{filepath}.pub", "r") as file:
            lines = file.readlines()
            for line in lines:
                pbk_data.append(int(line))
    except FileNotFoundError:
        pbk = None
    else:
        pbk = PublicKey(name, int(pbk_data[0]), int(pbk_data[1]))
    return pvk, pbk


class Key:

    def __init__(self, name, n):
        self.n = n
        self.name = name

    @property
    def bit_length(self):
        return self.n.bit_length()

    @property
    def byte_length(self):
        return -(-self.n.bit_length() // 8)


class PrivateKey(Key):

    def __init__(self, name, n, d):
        super().__init__(name, n)
        self.d = d

    def decrypt(self, cryptogram):
        return pow(cryptogram, self.d, self.n)


class PublicKey(Key):

    def __init__(self, name, n, e):
        super().__init__(name, n)
        self.e = e

    def encrypt(self, message):
        return pow(message, self.e, self.n)
