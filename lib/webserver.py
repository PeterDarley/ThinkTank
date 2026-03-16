"""
Minimal HTTP server for MicroPython (ESP32).

Place this file in `lib/` and import from your `main.py` or REPL.

Usage (blocking):
    from webserver import WebServer
    srv = WebServer(port=80)
    srv.start()

Usage (background thread):
    srv.start_in_thread()

Serving behavior:
- If `www/index.html` exists on the device, it will be served for `GET /`.
- Otherwise a simple HTML page is returned.
"""

import socket
import os
import gc

try:
    import _thread
    _THREAD = True
except Exception:
    _THREAD = False

class WebServer:
    def __init__(self, host='0.0.0.0', port=80, www_dir='www', debug=False):
        self.host = host
        self.port = port
        self.www_dir = www_dir
        self._sock = None
        self._running = False
        self.debug = debug

    def _handle_client(self, cl_sock):
        try:
            if self.debug:
                try:
                    peer = cl_sock.getpeername()
                    print('websrv: accepted connection from', peer)
                except Exception:
                    pass

            req = cl_sock.recv(2048)
            if not req:
                return
            # parse request line
            first_line = req.split(b"\r\n", 1)[0]
            if self.debug:
                try:
                    print('websrv: request:', first_line)
                except Exception:
                    pass
            parts = first_line.split()
            if len(parts) < 2:
                return
            method = parts[0].decode()
            path = parts[1].decode()

            # only support GET for now
            if method != 'GET':
                if self.debug:
                    print('websrv: unsupported method', method)
                cl_sock.send(b"HTTP/1.0 405 Method Not Allowed\r\n\r\n")
                return

            if path == '/' or path == '/index.html':
                content, content_type = self._load_index()
                if content is None:
                    if self.debug:
                        print('websrv: no index found, returning default page')
                    body = b"<html><body><h1>OK</h1></body></html>"
                    content_type = 'text/html'
                    content = body
            else:
                # very small file serving: map path to www_dir
                safe_path = path.lstrip('/')
                file_path = '/'.join((self.www_dir, safe_path))
                if self._exists(file_path):
                    if self.debug:
                        print('websrv: serving file', file_path)
                    content = self._readfile(file_path)
                    content_type = self._guess_mime(file_path)
                else:
                    if self.debug:
                        print('websrv: file not found', file_path)
                    cl_sock.send(b"HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found")
                    return

            headers = 'HTTP/1.0 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\n\r\n'.format(content_type, len(content))
            cl_sock.send(bytes(headers, 'utf-8'))
            cl_sock.send(content)
        except Exception as e:
            if self.debug:
                try:
                    import sys
                    print('websrv: handler exception:', e)
                except Exception:
                    pass
            try:
                cl_sock.send(b"HTTP/1.0 500 Internal Server Error\r\n\r\n")
            except Exception:
                pass
        finally:
            try:
                cl_sock.close()
            except Exception:
                pass
            gc.collect()

    def _exists(self, path):
        try:
            # prefer stat-like check
            try:
                return self._file_exists(path)
            except Exception:
                return path in os.listdir('/') or ("/" + path) in os.listdir('/')
        except Exception:
            # fallback to try/catch open
            try:
                f = open(path, 'rb')
                f.close()
                return True
            except Exception:
                return False

    def _readfile(self, path):
        try:
            if self.debug:
                print('websrv: reading file', path)
            with open(path, 'rb') as f:
                return f.read()
        except Exception:
            return None

    def _load_index(self):
        idx = self.www_dir + '/index.html'
        if self._file_exists(idx):
            if self.debug:
                print('websrv: found index at', idx)
            data = self._readfile(idx)
            return data, 'text/html'
        return None, None

    def _file_exists(self, path):
        try:
            st = os.stat(path)
            return True
        except Exception:
            return False

    def _guess_mime(self, filename):
        if filename.endswith('.html'):
            return 'text/html'
        if filename.endswith('.css'):
            return 'text/css'
        if filename.endswith('.js'):
            return 'application/javascript'
        if filename.endswith('.png'):
            return 'image/png'
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            return 'image/jpeg'
        return 'application/octet-stream'

    def start(self):
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        self._sock = s
        self._running = True
        print('WebServer listening on', addr)
        if self.debug:
            print('websrv: entering main accept loop')
        try:
            while self._running:
                cl, remote = s.accept()
                # handle in-line (small server). For heavier load, integrate _thread handling.
                if _THREAD:
                    try:
                        if self.debug:
                            print('websrv: spawning thread for client', remote)
                        _thread.start_new_thread(self._handle_client, (cl,))
                    except Exception as e:
                        if self.debug:
                            print('websrv: failed to spawn thread, handling inline', e)
                        self._handle_client(cl)
                else:
                    if self.debug:
                        print('websrv: handling client inline', remote)
                    self._handle_client(cl)
        finally:
            try:
                s.close()
            except Exception:
                pass
            self._running = False

    def start_in_thread(self):
        if not _THREAD:
            raise RuntimeError('threading not available on this build')
        if self.debug:
            print('websrv: starting server in background thread')
        _thread.start_new_thread(self.start, ())

    def stop(self):
        self._running = False
        try:
            if self._sock:
                self._sock.close()
        except Exception:
            pass
        if self.debug:
            print('websrv: stop requested')


# convenience function
def start_simple(port=80, www_dir='www'):
    srv = WebServer(port=port, www_dir=www_dir)
    srv.start()
