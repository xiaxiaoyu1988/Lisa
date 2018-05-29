import functools
import threading


class DuplicateRouteException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ServerAdapter(object):
    quiet = False

    def __init__(self, host='127.0.0.1', port=8080, **options):
        self.options = options
        self.host = host
        self.port = int(port)

    def run(self, handler):  # pragma: no cover
        pass

    def __repr__(self):
        args = ', '.join(['%s=%s' % (k, repr(v))
                          for k, v in self.options.items()])
        return "%s(%s)" % (self.__class__.__name__, args)


class WSGIRefServer(ServerAdapter):
    def run(self, _app):  # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self):  # Prevent reverse DNS lookups please.
                return self.client_address[0]

            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls = self.options.get('server_class', WSGIServer)

        if ':' in self.host:  # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        srv = make_server(self.host, self.port, _app, server_cls, handler_cls)
        srv.serve_forever()


class Router(object):
    def __init__(self):
        self._routes = {}
    
    def match(self, environ):
        path = environ['PATH_INFO']
        if not path:
            path = '/'
        elif '?' in path:
            path = path.split('?')[0]

        key = environ['REQUEST_METHOD'] + path
        return self._routes.get(key)

    def add(self, route):
        key = route.method + route.path
        if self._routes.has_key(key):
            raise DuplicateRouteException(route)
        else:
            self._routes[key] = route.func

class Route(object):
    def __init__(self, method, path, func):
        self.method = method
        self.path   = path
        self.func   = func
    
    def __repr__(self):
        return 'Route object method:{0}, path:{1}, func:{2}'.format(self.method, self.path, self.func)
    __str__ = __repr__

class BaseResponse(dict):
    def __init__(self):
        super(BaseResponse, self).__init__()
        self.__setitem__('status_line', '200 OK')
        self.__setitem__('charset', 'UTF-8')
        self.__setitem__('Content-Type', 'application/json; charset=' +
                         self.__getitem__('charset'))
    
    def __setitem__(self,k,v):
        if isinstance(v, int):
            v = str(v)
        dict.__setitem__(self,k,v)
        dict.__setattr__(self,k,v)
    
    def __missing__(self,k):
        if k == 'headers':
            return self.items()
        else:
            self.__setitem__(k, None)
            return None
    
    __setattr__ = __setitem__
    __getattr__ = __missing__ 

class BaseRequest(object):
    def __init__(self, environ):
        pass

class Webserver(threading.Thread):
    def __init__(self):
        super(Webserver, self).__init__()

        self.server = WSGIRefServer()
        self.router = Router()
        self.routes = []
    
    def route(self, path = '', method = 'GET'):
        def decorator(func):
            route = Route(method, path, func)
            self.add_route(route)
            return func
        
        return decorator
    
    def add_route(self,route):
        self.routes.append(route)
        self.router.add(route)
    
    def _handle(self, environ):
        self.req = BaseRequest(environ)
        self.res = BaseResponse()
        func = self.router.match(environ)
        return func()
    
    def _cast(self, out):
        if not out:
            self.res['Content-Length'] = 0
        
        if isinstance(out, unicode):
            out = out.encode(self.res['charset'])
        
        if isinstance(out, bytes):
            self.res['Content-Length'] = len(out)
        
        return [out]
    
    def wsgi(self, environ, start_response):
        try:
            out = self._cast(self._handle(environ))
            # start_response('200 OK', [
                        #    ('Content-Length', '5'), ('Content-Type', 'text/html; charset=UTF-8')])
            start_response(self.res.status_line, self.res.headers)
            return out
        except Exception, e:
            print str(e)
    
    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def run(self):
        self.server.run(self)



def make_app_wrapper(name, cobj):
    @functools.wraps(getattr(Webserver, name))
    def wrapper(*a, **ka):
        return getattr(cobj, name)(*a, **ka)
    return wrapper