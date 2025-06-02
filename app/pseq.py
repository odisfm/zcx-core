from random import randint


class Pseq(object):

    def __init__(self, bundle: list, random=False):
        self._bundle = bundle
        self._random = random
        self._current_increment = 0
        self._max_increment = len(self._bundle)

    def get_next_command(self, increment=True):
        if self._random:
            command = self.get_random_command()
        else:
            command = self.get_sequential_command()

        if increment:
            self._current_increment += 1
            self._current_increment %= self._max_increment

        return command

    def get_random_command(self):
        return self._bundle[randint(0, self._max_increment - 1)]

    def get_sequential_command(self):
        return self._bundle[self._current_increment]
