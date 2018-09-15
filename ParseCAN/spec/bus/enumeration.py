from dataclasses import dataclass, field, InitVar

@dataclass
class Enumeration:
    name: str
    value: int
    max_value: InitVar[int] = field(repr=False, compare=False, hash=False, default=2 ** 64)
    
    def __post_init__(self, max_value):
        self.max_value = max_value
        self.value = self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.check()

    def check(self):
        if self.value < 0 or self.value > self.max_value:
            raise ValueError(f'value out of range: {self.value}')

    def __contains__(self, data):
        return self.value == data

# 1 _value vs value (init, property, setter)
# 2 __post_init__

# import dataclasses
# test = Enumeration('name', 1, 2)
# print('test:', dataclasses.astuple(test))
# print('value:', test.value)
# print(test._value)
# test.value = 4
# print('value:', test.value)
# print(test.value)
# print(test._value)


# class T:
#     def __init__(self, a, _a):
#         self.a = a
#         self._a = _a

# t = T(1, 2)
# print(t.a, t._a)
# t.a = 100
# t._a = 200
# print(t.a, t._a)

from typing import NewType

UserId = NewType('UserId', int)
some_id = UserId(524313)

def get_user_name(user_id: UserId) -> str:
    return user_id
