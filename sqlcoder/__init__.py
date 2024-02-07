from importlib.metadata import version

try:
    __version__ = version("sqlcoder")
except:
    pass