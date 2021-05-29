import asyncio
from pyppeteer import launch
import time
import requests
from urllib import request
import string
import random


async def main(urls, users):
    currentip='1.1.1.1'
    while True:
        try:
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
                    user = random.choice(users)
                    first = ''.join(random.choices(string.ascii_uppercase + string.digits, k=13))
                    second = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
                    await page.setExtraHTTPHeaders({
                        'Referer': 'http://'+str(first)+'.'+str(second),
                        'Origin': 'http://'+str(first)+'.'+str(second),
                        'user-agent': ''+str(user),
                        'upgrade-insecure-requests': '1',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9,en;q=0.8'
                    })
                    await page.goto(url, timeout=12000)
                    await page.waitForNavigation(args=['networkidle0'])
                    #await page.screenshot({'path': 'example.png'})
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
        except Exception as e:
            print(e)


with open('urls.txt') as f:
    urls = f.read().splitlines()
    print(urls)
    with open('users.txt') as k:
        users = k.read().splitlines()
        print(users)
        while True:
            try:
                asyncio.get_event_loop().run_until_complete(main(urls, users))
            except Exception as e:
                print(e)
