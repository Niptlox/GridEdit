class UClass:
    set_all_exceptions = set()

    def set_all(self, obj):
        d = obj.copy() if isinstance(obj, dict) else obj.__dict__.copy()
        for e in self.set_all_exceptions:
            if e in d:
                d.pop(e)
        self.__dict__.update(d)
