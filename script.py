import threading
import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib import request
import base64
import random
import json
import time
import os
import asyncio
from pyppeteer import launch
import requests


pausetime = 1
isRunning = True
rotatingproxy_url = 'http://falcon.proxyrotator.com:51337/'
rotatingproxy_apikey = 'h6nteVyuk3NUXZKLgQmwMGJvrRxsHPjD'
rotatingproxy_params = dict(apiKey=rotatingproxy_apikey, get="true")

async def puppet(url, proxy, useragent):
    browser = await launch(args=['--ignore-certificate-errors', '--no-sandbox', '--proxy-server=' + proxy,
                                 '--user-agent=' + useragent])
    try:
        page = await browser.newPage()
        await page.goto(url, timeout=2000)
        dimensions = await page.evaluate('''() => {
           return {
               width: document.documentElement.clientWidth,
               height: document.documentElement.clientHeight,
               deviceScaleFactor: window.devicePixelRatio,
           }
       }''')
        print(dimensions)
    except Exception as e:
        print(e)
    await browser.close()


def run():
    global isRunning
    global pausetime
    while True:
        while isRunning:
            resp = requests.get(url=rotatingproxy_url, params=rotatingproxy_params)
            data = json.loads(resp.text)
            proxy = str(data['proxy'])
            with open('urls.txt') as f:
                urls = f.read().splitlines()
                for url in urls:
                    url = base64.urlsafe_b64decode(url)
                    url = url.decode("utf-8")
                    for i in range(2):
                        asyncio.get_event_loop().run_until_complete(puppet(url, proxy, get_user_agent()))
                        rnd = random.randrange(int(pausetime)+1, (int(pausetime)*2)+2)
                        time.sleep(rnd)
            rnd = random.randrange(int(pausetime)+1, (int(pausetime)*2)+1)
            time.sleep(rnd)
        time.sleep(2)


def get_user_agent():
    with open('user-agents.txt') as f:
        lines = [line.rstrip() for line in f]
        return random.choice(lines)


def toggle():
    global isRunning
    if isRunning:
        isRunning = False
    else:
        isRunning = True


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global pausetime
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        query_components = parse_qs(urlparse(self.path).query)
        status = "TEST"
        if 'key' in query_components:
            if query_components["key"][0] == "wellplayed":
                if 'urls' in query_components:
                    urls = query_components["urls"][0]
                    with open('urls.txt', "w") as f:
                        f.seek(0)
                        f.write(urls)
                        f.truncate()
                if 'toggle' in query_components:
                    toggle()
                if 'time' in query_components:
                    ptime = query_components["time"][0]
                    pausetime = ptime
                if 'status' in query_components:
                    status = ""
        self.wfile.write(bytes(status, "utf8"))
        return


handler_object = MyHttpRequestHandler
PORT = os.environ['PORT']
my_server = socketserver.TCPServer(("", int(PORT)), handler_object)
threading.Thread(target=my_server.serve_forever).start()
run()
