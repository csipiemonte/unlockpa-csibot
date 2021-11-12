from .run import Run
from .botmanager import Botmanager
from .insert import Insert
from .monitor import Monitor
from .remove import Remove


classes = Run, Botmanager, Insert, Monitor, Remove
__all__ = ['classes']
