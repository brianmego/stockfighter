import asyncio
import aiohttp
import pprint
import sys


API_URL = 'https://api.stockfighter.io/ob/api'


running_processes = {
    'heartbeat': False,
    'venue_check': False,
    'help': True,
}

input_options = {
    'h': 'help',
    'b': 'heartbeat',
    'v': 'venue_check',
}


async def check_api_status():
    while True:
        url = '{}/heartbeat'.format(API_URL)
        if running_processes['heartbeat']:
            response = await aiohttp.request('GET', url)
            content = await response.json()
            if content.get('ok') is True:
                print('Heartbeat: Good')
            else:
                print('Heartbeat: Bad')
        await asyncio.sleep(2)


async def print_help():
    while True:
        if running_processes['help']:
            for key, val in input_options.items():
                print('{} ({})'.format(val, key))
            print()
            running_processes['help'] = False
        await asyncio.sleep(1)


async def check_venue():
    while True:
        if running_processes['venue_check']:
            venue = input('Venue: ').upper()
            stock = input('Stock symbol, blank for all: ').strip().upper()
            failure_message = 'Venue {} is DOWN'.format(venue)
            if not stock:
                url = '{}/venues/{}/stocks'.format(API_URL, venue)
            else:
                url = '{}/venues/{}/stocks/{}'.format(API_URL, venue, stock)
            response = await aiohttp.request('GET', url)

            if response.status == 200:
                content = await response.json()
                if content.get('ok') is True:
                    pprint.pprint(content)
                else:
                    print(failure_message)
            else:
                print(failure_message)

            running_processes['venue_check'] = False
        await asyncio.sleep(1)


def process_stdin(q):
    asyncio.async(q.put(sys.stdin.readline()))


async def print_stdin(q):
    while True:
        stdin = await q.get()
        input_str = stdin.strip()
        if input_str in input_options:
            proc = input_options[input_str]
            if running_processes[proc]:
                running_processes[proc] = False
            else:
                running_processes[proc] = True
        await asyncio.sleep(1)


def main():
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, process_stdin, q)
    loop.run_until_complete(
        asyncio.gather(
            check_api_status(),
            print_stdin(q),
            check_venue(),
            print_help()
        )
    )
    loop.close()

if __name__ == '__main__':
    main()
