
import threading

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

class BaseResponse(object):
    def __init__(self, body = ''):
        self._header = {}
        self._cookie = None
        self.body    = body

        self._status_line = 'OK'
        self._status_code = 200

class BaseRequest(object):
    def __init__(self):
        pass

class Webserver(threading.Thread):
    def __init__(self):
        super(Webserver, self).__init__()

        self.server = WSGIRefServer()
    
    def route(self, path = '', method = 'GET'):
        print path, method
        pass
    
    def _handle(self, environ):
        pass
    
    def wsgi(self, environ, start_response):
        try:
            print environ
            print environ['wsgi.multithread']
            print environ['PATH_INFO']
            start_response('200 OK', [
                           ('Content-Length', '5'), ('Content-Type', 'text/html; charset=UTF-8')])
            return ["hello"]
        except Exception, e:
            print str(e)
    
    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def run(self):
        self.server.run(self)


    

    
