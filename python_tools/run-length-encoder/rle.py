import itertools

class RunLengthEncoder:
    def __init__(self):
        pass

    def encode(self, data):
        encode = ''
        o = '|'
        sep = '-'
        for char, group in itertools.groupby(data):
            cnt = sum(1 for _ in group)
            if cnt == 1:
                encode = encode + char
            else:
                encode = encode + f'{o}{cnt}{sep}{char}'
        return encode

    def decode(self, data):
        decode = ''
        count = ''
        op = '|'
        sep = '-'
        enc = False
        num = False
        run = False
        print('char | enc | num')
        for i, char in enumerate(data):
            print(char, enc, num)
            
            if char == op and enc and not num:
                decode += char
                enc = False
            if char == op and not enc and not num:  # number is next
                num = True
                continue
            
            if char == sep and enc and not num:
                decode += char
                run = True
            if char == sep and not enc and num:  # encoded char is next
                enc = True
                num = False
                continue
            if char == sep and enc 
            
            if num:
                count += char
            if enc:
                decode += char * int(count or 1)
                count = ''
                enc = False
        return decode

    @staticmethod
    def compression_ratio(original, encoded):
        orig = len(original)
        enc = len(encoded)
        return round(1 - enc / orig, 2)