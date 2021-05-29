import asyncio
from pyppeteer import launch
import time
import requests
import json
from urllib import request


async def main(urls):
    currentip='1.1.1.1'
    while True:
        if currentip != request.urlopen('https://ident.me').read().decode('utf8'):
            currentip = request.urlopen('https://ident.me').read().decode('utf8')
            url = "https://proxy-spider.com/api/rotating-proxies.json?api_key=160-f4e9e6247cb00be3128af4697ab965&action=set_authorized_ips&authorized_ips="+currentip
            requests.get(url=url)
            print("newIP: "+str(currentip))
        browser = await launch(args=['--ignore-certificate-errors', '--no-sandbox','--proxy-server=rotating.proxy-spider.com:1501'])
        for url in urls:
            try:
                print(url)
                page = await browser.newPage()
                await page.goto(url)
                await page.waitForNavigation(args=['networkidle0'])
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
        print("new loop")
        time.sleep(2)

with open('urls.txt') as f:
    urls = f.read().splitlines()
    print(urls)
    asyncio.get_event_loop().run_until_complete(main(urls))
