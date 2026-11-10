"""Public entrypoints load independently, including the two separate checkers."""
from importlib import import_module
__version__='0.2.0'
__all__=['compare','verify','prior_atlas','verify_atlas']
_modules={'compare':'.engine','verify':'.verify','prior_atlas':'.atlas','verify_atlas':'.atlas_verify'}
def __getattr__(name):
    if name not in _modules:raise AttributeError(name)
    result=getattr(import_module(_modules[name],__name__),name)
    globals()[name]=result
    return result
