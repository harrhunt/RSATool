import pytest
import RSA.prime_tools as prime_tools

PRIMES = [
    2,
    7,
    31,
    pow(2, 127) - 1,
    pow(2, 521) - 1,
    pow(2, 2203) - 1,
    pow(2, 11213) - 1
]

NON_PRIMES = [
    4,
    12,
    8192,
    41041,
    75361,
    9746347772161,
]

MIX_PRIMES = [
    (2, True),
    (7, True),
    (31, True),
    (pow(2, 127) - 1, True),
    (pow(2, 521) - 1, True),
    (4, False),
    (12, False),
    (8192, False),
    (41041, False),
    (75361, False),
    (9746347772161, False)
]


@pytest.mark.slow
@pytest.mark.parametrize("prime", PRIMES)
def test_is_prime(prime):
    assert prime_tools.is_prime(prime)


@pytest.mark.parametrize("not_prime", NON_PRIMES)
def test_not_is_prime(not_prime):
    assert not prime_tools.is_prime(not_prime)


@pytest.mark.parametrize("number, value", MIX_PRIMES)
def test_miller_rabin(number, value):
    for i in range(4, 8):
        assert prime_tools.miller_rabin(number, i) == value


@pytest.mark.slow
@pytest.mark.parametrize("key_size", [7, 16, 36, 64, 1024, 2048, 3072])
def test_generate_primes(key_size):
    assert prime_tools.generate_primes(key_size).bit_length() == key_size
