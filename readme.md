
# Overview
CLI tool for fetching movies data and their poster images from OMDB API. \
Uses asynchronous programming for maximising the speed and minimising the waiting time for multiple data and images to arrive. \
<br>
Movie data contains information like title, year of release, cast, runtime, director, polt, etc. \

Uses Redis for saving the caches

# Usage
*Note: If you are entering both titels and IDs, provide all titles after `--title` and then all IDs after `--id` \
If you are entering only titels or only IDs, then don't type the other option tag* \
<br>

1. Have Python 3.13+ installed
2. Run the Terminal in the project's root directory, for example by `cd C:\\path\to\omdb-cli-tool`
3. Enter `main.py` and then either `search` or `poster` \
The first one is used for displaing data in a form of a table \
The second one saves poster images of the entered movies
4. Enter `--title` or `--id` \
After `--title` enter movies titles, if the title contains blank spaces (" ") use "+" insted \
E.g. "Blade+Runner+2049" \
After `--id` enter valid IMDb IDs \
Seprate each title and ID with a space
5. If `search` was entered, a table of data from queried movies will be displayed
6. If `poster` was entered, images will be saved to `Posters/` directory within the project's root

### Example prompt
`main.py search --title Inception --id tt9826371 tt7483615 tt6483715` - both --title and --id, multiple queries for --id \
`main.py poster --id tt7261543` - only --id tag \
`main.py search --title Blade+Runner+2049 The+Shawshank+Redemption` - only --title tag, multiple queries

# Key features
- Asynchronous programming
- Redis caching

# Credits
API: https://www.omdbapi.com \
Remade idea from: https://roadmap.sh/projects/tmdb-cli \
Code: https://github.com/piotr-czarnecki07