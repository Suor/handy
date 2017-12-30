try:
    import cPickle as pickle
except ImportError:
    import pickle
from base64 import b64encode, b64decode
from handy.utils import get_module_attr


# Utilities to encode binary objects
def safe_encode(value):
    return b64encode(pickle.dumps(value, -1)).decode()

def safe_decode(value):
    return pickle.loads(b64decode(value))


# Utility functions to code/decode objects to/from JSON
def default_decode(cls_data_tuple):
    cls, data = cls_data_tuple
    cls = get_module_attr(cls)
    obj = cls.__new__(cls)
    obj.__dict__.update(data['__data__'])
    return obj

def encode_object(obj):
    if hasattr(obj, '__json__'):
        data = obj.__json__()
        if isinstance(data, tuple):
            decode, data = data
        else:
            decode = default_decode
            data = obj.__class__, data

        if callable(decode):
            decode = '%s.%s' % (decode.__module__, decode.__name__)

        return {
            '__decode__': decode,
            '__data__': data
        }
    else:
        return dict(__pickled__=safe_encode(obj))

def decode_object(d):
    if '__decode__' in d:
        return get_module_attr(d['__decode__'])(d['__data__'])
    elif '__pickled__' in d:
        return safe_decode(d['__pickled__'])
    else:
        return d
