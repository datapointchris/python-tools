from faker import Faker
from itertools import zip_longest

fake = Faker()


def str_to_binary_str(string: str) -> str:
    return ''.join([bin(ord(b))[2:] for b in string])


def binary_encode(bin_string: str) -> str:
    code = []
    previous = ''
    count = 1
    last_index = len(bin_string) - 1
    for i, char in enumerate(bin_string):
        if char == previous:
            count += 1
            if i == last_index:
                code.append(f'{count}{previous}')
        else:
            code.append(f'{count if count > 1 else ""}{previous}')
            count = 1
            previous = char
            if i == last_index:
                code.append(char)
    string_code = ''.join(code)
    return string_code


def binary_decode(encoded_string: str) -> str:
    bin_code = []
    count = 1
    for i, char in enumerate(encoded_string):
        num = int(char)
        if num > 1:
            count = num
        else:
            bin_code.append(char * count)
            count = 1
    bin_string = ''.join(bin_code)
    return bin_string


def test_encoding(original, decoded):
    errors = []
    for i, (o, d) in enumerate(zip_longest(original, decoded)):
        if o != d:
            errors.append((i, o, d))

    if errors:
        for error in errors:
            i, o, d = error
            print(f'Index: {i}, {o == d}: {o} != {d}')
        return False
    else:
        return True


def compression_ratio(original, encoded):
    orig = len(original)
    enc = len(encoded)
    return round(1 - enc / orig, 2)


def analyze_compression(string: str):
    print(string)
    print()
    binary = str_to_binary_str(string)
    print('Binary')
    print(binary)
    print()
    encoded = binary_encode(binary)
    print('Encoded')
    print(encoded)
    print()
    print('String Length: ', len(string))
    print('Binary Length: ', len(binary))
    print('Encoded Length: ', len(encoded))
    print('Binary to Encoded Compression: ', compression_ratio(binary, encoded))
