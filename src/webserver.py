import functools
import threading
import os

class DuplicateRouteException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ServerAdapter(object):
    quiet = False

    def __init__(self, host='127.0.0.1', port=0, **options):
        self.options = options
        self.host = host
        self.port = int(port)
        self.srv = None

    def run(self, handler):  # pragma: no cover
        pass

    def __repr__(self):
        args = ', '.join(['%s=%s' % (k, repr(v))
                          for k, v in self.options.items()])
        return "%s(%s)" % (self.__class__.__name__, args)


class WSGIRefServer(ServerAdapter):
    def run(self, _app, app):  # pragma: no cover
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

        self.srv = make_server(self.host, self.port, _app, server_cls, handler_cls)
        self.port = self.srv.server_address[1]

        app.bindings.SetProperty("FRONT_BASE_PATH", 'file://' + os.getcwd() + '/client')
        app.bindings.SetProperty("BACKEND_BASE_PATH", 'http://127.0.0.1:' + str(self.port))
        app.bind_python_to_js(app.bindings)

        self.srv.serve_forever()
    
        


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
        self.__setitem__('Access-Control-Allow-Origin', '*')
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

class HTTPError(BaseResponse):
    def __init__(self, error_code, error_line, location = None):
        super(HTTPError, self).__init__()
        self.__setitem__('status_line', str(error_code) + ' ' + error_line)

        if location:
            self.__setitem__('Location', location)
        


class BaseRequest(object):
    def __init__(self, environ):
        self.query_string = environ.get('QUERY_STRING', '')
        self.params = {}
        self.__parse()

    def __parse(self):
        items = self.query_string.split('&')
        for item in items:
            if not item:
                continue
            tmp = item.split('=')
            if len(tmp) < 2:
                continue
            self.params[tmp[0]] = tmp[1]


    def path(self):
        pass

    def cookie(self):
        pass

    def method(self):
        pass

    def headers(self):
        pass

    def params(self):
        pass

    def json(self):
        pass

class Webserver(threading.Thread):
    def __init__(self):
        super(Webserver, self).__init__()

        self.server = WSGIRefServer()
        self.router = Router()
        self.routes = []

    def set_app(self, app):
        self.app = app
    
    def route(self, path = '', method = 'GET'):
        def decorator(func):
            route = Route(method, path, func)
            self.add_route(route)
            return func
        
        return decorator

    def redirect(self, url):
        return HTTPError(302, "Redirect", url)
    
    def add_route(self,route):
        self.routes.append(route)
        self.router.add(route)
    
    def _handle(self, environ):
        # print '_handle------'
        self.req = BaseRequest(environ)
        self.res = BaseResponse()
        # print 'match ---'
        func = self.router.match(environ)
        # print func
        if not func:
            return HTTPError(404, 'NOT FOUND')
        return func()
    
    def _cast(self, out):
        if not out:
            self.res['Content-Length'] = 0
        
        if isinstance(out, unicode):
            out = out.encode(self.res['charset'])
        
        if isinstance(out, bytes):
            self.res['Content-Length'] = len(out)
        
        if isinstance(out, HTTPError):
            self.res = out
            self.res['Content-Length'] = 0
            return [out.status_line]
        
        return [out]
    
    def wsgi(self, environ, start_response):
        try:
            out = self._cast(self._handle(environ))
            # print self.res
            # start_response('200 OK', [
                        #    ('Content-Length', '5'), ('Content-Type', 'text/html; charset=UTF-8')])
            start_response(self.res.status_line, self.res.headers)
            return out
        except Exception, e:
            print str(e)
    
    def __call__(self, environ, start_response):
        # print '----------------------------'
        return self.wsgi(environ, start_response)

    def run(self):
        self.server.run(self, self.app)

def make_app_wrapper(name, cobj):
    @functools.wraps(getattr(Webserver, name))
    def wrapper(*a, **ka):
        return getattr(cobj, name)(*a, **ka)
    return wrapper
