
class UClass:
    def set_all(self, obj):
        self.__dict__.update(obj.__dict__)