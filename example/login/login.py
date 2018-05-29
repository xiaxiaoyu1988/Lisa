import os
import sys

sys.path.append(r"../../src")
from lisa import App, route, wserver, redirect

@route('/login')
def login():
	username = wserver.req.params['username']
	password = wserver.req.params['password']
	if username == 'admin' and password == '123':
		return '{"code":0}'
	else:
		return '{"code":1}'

def main():
    app = App()
    client_path = "file://" +  os.getcwd() + "/client/login.html"
    app.init(client_path, debug=True)
    app.run()

if __name__ == '__main__':
    main()

