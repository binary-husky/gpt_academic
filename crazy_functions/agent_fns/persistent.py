from toolbox import Singleton
@Singleton
class GradioMultiuserManagerForPersistentClasses():
    def __init__(self):
        self.mapping = {}

    def already_alive(self, key):
        return (key in self.mapping) and (self.mapping[key].is_alive())

    def set(self, key, x):
        self.mapping[key] = x
        return self.mapping[key]

    def get(self, key):
        return self.mapping[key]
