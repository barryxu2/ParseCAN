from dataclasses import dataclass
from typing import Sequence, Union

from ... import data, spec, plural
from . import Message


@dataclass
class Bus:
    '''
    A (CAN) bus specification.
    Describes the set of messages that flow through a CAN bus.
    Can unpack CAN Messages that were sent based on this spec.bus.
    '''

    name: str
    baudrate: int
    extended: bool = False
    messages: plural.Unique[Message]

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, messages):
        if isinstance(messages, plural.Unique):
            self._messages = messages.copy()
            # TODO: Make checks happen here too
            return

        self._messages = plural.Unique('name', 'id')

        if isinstance(messages, list):
            self._messages.extend(messages)
            return

        for msgnm in messages or ():
            if isinstance(messages[msgnm], dict):
                try:
                    self.messages.add(Message(name=msgnm, **messages[msgnm]))
                except Exception as e:
                    e.args = (
                        'in message {}: {}'.format(
                            msgnm,
                            e
                        ),
                    )

                    raise
            else:
                self.messages.add(messages[msgnm])

    def unpack(self, frame, **kwargs):
        '''
        unpacks a data.Frame instance based on this spec.can.
        '''
        assert isinstance(frame, data.Frame)

        ret = {}
        for msg in self.messages:
            potential = msg.unpack(frame, **kwargs)

            if potential:
                ret[msg.name] = potential

        return ret

    def __str__(self):
        return self.name


class BusFiltered(Bus):
    def __init__(self, bus: Bus, interests: Sequence[Union[int, str]]):
        self.bus = bus
        self.interests = interests

    @property
    def interests(self):
        return self._interests

    @interests.setter
    def interests(self, interests):
        for interest in interests:
            try:
                if isinstance(interest, int):
                    self.bus.messages.id[interest]
                elif isinstance(interest, str):
                    self.bus.messages.name[interest]
                else:
                    raise ValueError('in bus {}: in interest {}: must be of type int or str'.format(
                        self.bus, interest))
            except KeyError:
                raise ValueError('in bus {}: in interest {}: does not exist in the bus'.format(
                    self.bus, interest))

        self._interests = interests

    def interested(self, msg):
        assert isinstance(msg, spec.message)
        return msg.name in self.interests or msg.id in self.interests

    @property
    def messages(self):
        return filter(self.interested, self.bus.messages)

    def __getattr__(self, attr):
        return getattr(self.bus, attr)