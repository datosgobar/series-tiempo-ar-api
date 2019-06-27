from http.server import SimpleHTTPRequestHandler, test


class MyHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


test(HandlerClass=MyHandler, port=3456)