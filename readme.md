# IMPORTANT

Redis might not be available due to the free database plan and Redis policy, which removes unused free databases after a period of inactivity.

# Overview

CLI tool for fetching movie data and their poster images from the OMDB API.  
Uses asynchronous programming to maximize speed and minimize waiting time when fetching multiple pieces of data and images.  

Movie data includes information such as title, year of release, cast, runtime, director, plot, etc.  
Redis is used for caching to improve performance.

# Usage

*Note: If you are entering both titles and IDs, provide all titles after `--title` and then all IDs after `--id`.  
If you are entering only titles or only IDs, omit the unused option tag.*

1. Ensure Python 3.13+ is installed.
2. Install dependencies from `requirements.txt`
3. Create a `.env` file based on the `.env.example` in the same directory as `.env.example` (UWAGA: na potrzeby rekrutacji wzór pliku `.env` jest dostępny w [HASLA](./HASLA.md)). 
4. Open the Terminal in the project's root directory, for example, by running `cd C:\\path\to\omdb-cli-tool`.
5. Enter `main.py` followed by either `search` or `poster`:  
   - `search`: Displays movie data in a table format.  
   - `poster`: Saves poster images of the entered movies.
6. Enter `--title` or `--id`:  
   - After `--title`, enter movie titles. If a title contains spaces, replace them with `+`.  
     Example: `"Blade+Runner+2049"`.  
   - After `--id`, enter valid IMDb IDs.  
     Separate each title and ID with a space.
7. If `search` is used, a table of data for the queried movies will be displayed.
8. If `poster` is used, images will be saved to the `Posters/` directory within the project's root.

### Example Prompts

```bash
main.py search --title Inception --id tt9826371 tt7483615 tt6483715
# Both --title and --id, multiple queries for --id.

main.py poster --id tt7261543
# Only --id tag.

main.py search --title Blade+Runner+2049 The+Shawshank+Redemption
# Only --title tag, multiple queries.
```

# Key features
- Asynchronous programming
- Redis caching

# Credits
- API: https://www.omdbapi.com \
- Remade idea from: https://roadmap.sh/projects/tmdb-cli \
- Code: https://github.com/piotr-czarnecki07