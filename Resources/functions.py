import redis.asyncio as aioredis
import redis.exceptions
import asyncio
import aiohttp
import json
import pandas
import os

from PIL import Image
from io import BytesIO

# get response with 'query' key form api
async def make_request(query: str, session: aiohttp.ClientSession, r: aioredis.Redis, config) -> dict:
    if query[:2] == 'tt' and query[3:].isnumeric() and len(query) == 9: # user entered imdb id
        param = 'i'
    else: # user entered movie title
        param = 't'
    url = config.get('API') + config.get('API_KEY') + param + '=' + query

    # make request to API (all exceptions will be passed to the caller)
    async with session.get(url) as response:
        if response.status == 200:
            response_json = await response.json()
            if response_json.get('Error') is not None:
                print(f'Movie {query} not found')
                return response_json

            data = {} # remove unwanted data
            for key, value in response_json.items():
                if key not in ('Poster', 'Website', 'Response', 'Ratings'): # ratings removed becouse of containing a list insted of key-value
                    data[key] = value
        else:
            print(f'Data from an API was not recived\nAPI returned status code:{response.status}')
            return {'Error': 'Recived no response'}

    # save to Redis
    try:
        ok = await r.execute_command('set', query, json.dumps(data))
        if not ok:
            print('Responses were not saved to Redis')

    except redis.exceptions.RedisError:
        print('Unable to save responses to Redis')

    return data

# display table with data from provided movies
async def search(args: list, config) -> None:
    # connect to Redis
    r = aioredis.Redis(
        host=config.get('REDIS_HOST'),
        port=config.get('REDIS_PORT'),
        username='default',
        password=config.get('REDIS_PASSWORD'),
        decode_responses=True,
    )

    # get cached data from Redis
    try:
        responses = []
        to_request = []
        for item in args:
           response = await r.execute_command('get', item)
           if response is not None:
               responses.append(json.loads(response))
           else:
               to_request.append(item)

    except TypeError:
        print('Argument is None.')
        exit(1)

    except redis.exceptions.RedisError:
        print('Unable to connect to Redis\nRequesting each query from an API')
        to_request = args

    try:
        # use make_request coroutine to acquire data
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(query, session, r, config) for query in to_request]
            results = await asyncio.gather(*tasks)
            responses += results

            output = list(filter(lambda response: response.get('Error') is None, responses))

    except aiohttp.ClientConnectionError:
        print('Connection error ocured while trying to connect to the API')

    except aiohttp.InvalidURL:
        print("API's URL had been changed")

    except (aiohttp.ClientResponseError, aiohttp.ClientPayloadError):
        print('Response from API was damaged')

    except aiohttp.ServerDisconnectedError:
        print('Server terminated the connection')

    except aiohttp.ClientError:
        print('An error ocured while trying to connect to the API')

    except asyncio.TimeoutError:
        print('Server is not responding')

    except WindowsError:
        print('Too many requests')

    else:
        if output:
            print(pandas.DataFrame(output))
        else:
            print('No movies with provided titles and/or IDs were found')

    finally:
        await r.close()

# get poster with 'query' key url from api
async def get_poster_url(query: str, session: aiohttp.ClientSession, r: aioredis.Redis, config) -> dict:
    if query[:2] == 'tt' and query[3:].isnumeric() and len(query) == 9:
        param = 'i'
    else:
        param = 't'
    url = config.get('API') + config.get('API_KEY') + param + '=' + query

    async with session.get(url) as response:
        if response.status == 200:
            response_json = await response.json()
            if response_json.get('Error') is not None:
                print(f'Movie {query} was not found')
                return response_json

            poster_url = response_json.get('Poster')
            if poster_url == 'N/A' or poster_url is None:
                print(f'Movie {query} has no poster')
                return {'Error': 'Movie has no poster'}
        else:
            print('Recived no response while trying to connect to the API')
            return {'Error': 'Did not recive 200'}
    
    try:
        ok = await r.execute_command('set', query+'poster', poster_url.encode())
        if not ok:
            print('Poster url was not saved to Redis')

    except redis.exceptions.RedisError:
        print('Unable to connect to Redis db')

    return {'title': query, 'url': poster_url}

# download poster from url and save it to \Posters folder
async def download_poster(url: dict, cwd: str, session: aiohttp.ClientSession) -> bool:
    # find image file extension
    for i in range(len(url['url']) - 1, 0, -1):
        if url['url'][i] == '.': # first dot from the right specifies image extension
            break

    # fix file title
    title = ''
    for char in url['title']:
        title += ' ' if char == '+' else char

    async with session.get(url.get('url')) as response:
        if response.status == 200:
            # download file and save it to \Posters with a correct extension
            content = await response.read()

            # open and resize image to 1080x1920
            image = Image.open(BytesIO(content))
            image = image.resize((1080, 1920), Image.LANCZOS)
            image.save(f'{cwd}\\Posters\\{title}{url['url'][i:]}')

            print(f'Poster {title}{url['url'][i:]} downloaded')
            return True
        else:
            print(f'Unable to save the image, recived HTTP status code: {response.status}')
            return False

# download posters from selected movies
async def poster(args: list, config) -> None:
    r = aioredis.Redis(
        host=config.get('REDIS_HOST'),
        port=config.get('REDIS_PORT'),
        username='default',
        password=config.get('REDIS_PASSWORD'),
        decode_responses=True,
    )

    try: # napraw by zapisywało OBRAZY do redisa a nie linki
        urls = []
        to_request = []
        for item in args:
            response = await r.execute_command('get', item+'poster')
            if response is not None:
                urls.append({'title': item, 'url': response})
            else:
                to_request.append(item)

    except redis.exceptions.RedisError:
        print('Unable to connect to Redis\nRequesting each query from an API')
        to_request = args

    try:
        async with aiohttp.ClientSession() as session:
            # get urls from rest of the queries
            tasks = [get_poster_url(query, session, r, config) for query in to_request]
            results = await asyncio.gather(*tasks)

            # filter error messages
            for result in results:
                if result.get('Error') is None:
                    urls.append({'title': result.get('title'), 'url': result.get('url')})

            # get current working directory
            cwd = os.getcwd()
            if not os.path.exists(cwd+'\\Posters'):
                os.mkdir(cwd+'\\Posters')

            # download posters
            tasks = [download_poster(url, cwd, session) for url in urls]
            completed = await asyncio.gather(*tasks)

            count = sum(1 for x in completed if x)
            print(f'Downloaded {count}/{len(completed)} posters')

    except aiohttp.ClientConnectionError:
        print('Connection error ocured while trying to connect to the API')

    except aiohttp.InvalidURL:
        print("API's URL had been changed")

    except (aiohttp.ClientResponseError, aiohttp.ClientPayloadError):
        print('Response from API was damaged')

    except aiohttp.ServerDisconnectedError:
        print('Server terminated the connection')

    except aiohttp.ClientError:
        print('An error ocured while trying to connect to the API')

    except asyncio.TimeoutError:
        print('Server is not responding')

    except WindowsError:
        print('Too many requests')

    finally:
        await r.close()