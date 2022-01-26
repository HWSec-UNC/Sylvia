"""More general utility functions."""

def to_binary(i: int, digits: int = 128) -> str:
    num: str = bin(i)[2:]
    padding_len: int = digits - len(num)
    return  ("0" * padding_len) + num 