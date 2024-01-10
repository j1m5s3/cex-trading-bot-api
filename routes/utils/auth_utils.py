from functools import wraps
from copy import deepcopy


def document_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)

    decorated._apidoc = deepcopy(getattr(f, "_apidoc", {}))
    decorated._apidoc.setdefault('manual_doc', {})
    decorated._apidoc['manual_doc']['security'] = [{"Bearer Auth": []}]

    return decorated