#!/usr/bin/env python3

from subprocess import Popen, PIPE


class GitStorage:
    def store(self, value):
        process = Popen(
                ['git', 'hash-object', '-w', '--stdin'],
                stdout=PIPE, stdin=PIPE)
        result = process.communicate(value.encode('utf-8'))
        return result[0].strip().decode('utf-8')

    def load(self, key):
        process = Popen(['git', 'cat-file', '-p', key], stdout=PIPE)
        return process.communicate()[0].decode('utf-8')


class Memento:
    def __init__(self, key):
        self.key = key


class Originator:
    def __init__(self, state, key_value_storage):
        self.key_value_storage = key_value_storage
        self._state = state

    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self._state

    def create_memento(self):
        key = self.key_value_storage.store(
                type(self).__name__ + '|' + self._state)
        return Memento(key)

    def restore(self, memento):
        self._state = self.key_value_storage.load(memento.key).split('|')[1]


class Caretaker:
    def __init__(self, originator):
        self.originator = originator
        self.counter = 0
        self.mementos = []

    def do_some_action(self):
        self.originator.set_state('state# ' + str(self.counter))
        self.mementos.append(self.originator.create_memento())
        self.counter = self.counter + 1
        return self.originator.get_state()

    def undo(self):
        self.originator.restore(self.mementos.pop())
        return self.originator.get_state()


if __name__ == "__main__":
    key_value_storage = GitStorage()
    originator = Originator('init state', key_value_storage)
    caretaker = Caretaker(originator)

    print(caretaker.do_some_action())
    print(caretaker.do_some_action())
    print(caretaker.do_some_action())

    print(caretaker.undo())
    print(caretaker.undo())
    print(caretaker.undo())
