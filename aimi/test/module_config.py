import sys; sys.path.append('.')

# imports
from aimi.generic.Config import Config, Module

# define test module
class TestModule(Module):
    def printmyConfig(self) -> None:
        print("my config: ", self.c)

# fake config 
config = Config()
config._config["modules"] = {
    "TestModule": {
        "module_specific_atribute": "value"
    }
}

# test
testModule = TestModule(config)
testModule.printmyConfig()