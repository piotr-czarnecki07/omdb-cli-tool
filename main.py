try:
    from Resources import functions
except (ImportError, ModuleNotFoundError):
    print('Faild to import resources\nfunctions.py file was probably removed form \\Resources directory')
    exit(1)
from dotenv import dotenv_values
import argparse
import asyncio

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('function')
    args, unknown_args = parser.parse_known_args()

    parameter_parser = argparse.ArgumentParser()
    parameter_parser.add_argument(
        '--title',
        nargs='+',
        required=False,
        help='Enter movie titles (one or more)'
    )
    parameter_parser.add_argument(
        '--id',
        nargs='+',
        required=False,
        help='Enter valid IMDb IDs (one or more)'
    )
    parsed = parameter_parser.parse_args(unknown_args)

    queries = []
    if parsed.title is not None:
        queries += parsed.title
    if parsed.id is not None:
        queries += parsed.id
    if queries is None:
        print('No parameters were provided')
        exit(1)

    config = dotenv_values('.env')

    if args.function == 'search':
        asyncio.run(functions.search(queries, config))
    elif args.function == 'poster':
        asyncio.run(functions.poster(queries, config))
    else:
        print('Invalid command, try "search" or "poster"')