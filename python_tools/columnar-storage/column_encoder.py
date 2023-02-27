import re


class ColumnEncoder:
    def _create_key_and_storage_map(self):
        self.key_map = {i: name for i, name in enumerate(set(self.column))}
        self.storage_map = {name: i for i, name in self.key_map.items()}
        self.unique_items = len(self.key_map)

    def encode(self, column: list):
        """Format: '#{num}-{key}'"""
        self.column = column
        self._create_key_and_storage_map()
        encoded = []
        prev = None
        num = 1
        length = len(self.column)
        for i, key in enumerate(self.column, start=1):
            value = self.storage_map.get(key)
            if i == 1:
                prev = value
            elif i == length:
                if value == prev:
                    num += 1
                encoded.append(f'#{num}-{prev}')
                encoded.append(f'#1-{value}')
            elif value == prev:
                num += 1
                prev = value
            else:
                encoded.append(f'#{num}-{prev}')
                num = 1
                prev = value
        return ''.join(encoded)

    def decode(self, encoded: str) -> list:
        decoded = []
        p = re.compile(r'\d+-\d+')
        for s in p.findall(encoded):
            num, key = s.split('-')
            key = self.key_map.get(int(key))
            decoded.extend([key] * int(num))
        return decoded

    def storage_reduction(self, encoded: str, precision: int = 4):
        """Higher is better"""
        len_column = len(''.join(str(o) for o in self.column))
        len_encoded = len(encoded)
        reduction = round(1 - (len_encoded / len_column), precision)
        return reduction
