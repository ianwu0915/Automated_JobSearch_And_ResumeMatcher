from importlib import import_module

class LazyModule:
    def __init__(self, name: str) -> None:
        self.name = name
        self.module = None
    
    def __getattr__(self, attr: str):
        # Lazy import the module if it hasn't been imported yet
        if self.module is None:
            self.module = import_module(self.name)
        return getattr(self.module, attr)
    
            