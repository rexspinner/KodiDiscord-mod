import requests
from config import DEFAULT_POSTER_URL
from .custom_logger import logger
from .globals import TMDB_API_KEY, port

"""
A collection of functions for interacting with The Movie Database (TMDb) API.

Args:
    info (dict): A dictionary containing information about the media.
    media_type (str): The type of media ('tv', 'movie', etc.).
    url (str): The URL to make the API request.
    tv_show_id (int): The ID of the TV show.
    tmdb_id (int): The TMDb ID of the media.
    tmdb_id (int): The TMDb ID of the media.
    media_type (str): The type of media ('tv', 'movie', etc.).

Returns:
    str: The media type ('tv' or 'movie').
    int: The TMDb ID of the media.
    dict: The API response in JSON format.
    str: The URL of the image.
    str: The URL of the TMDb page.
"""

def get_media_type(info):
    media_type = info['type']
    return 'tv' if media_type == 'episode' else media_type

def get_tmdb_id_tmdb(info, media_type):
    if media_type == 'channel':
        return None
    return (
        get_tmdb_id_for_tv_show(info)
        if media_type == 'tv'
        else get_tmdb_id_for_media(info)
    )

def get_tmdb_id_for_tv_show(info):
    tv_show_id = info.get('tvshowid', -1)
    show_title = info.get('showtitle')  # Get show title from info

    # If tv_show_id is -1, search for the TMDb ID using show_title
    if tv_show_id == -1 and show_title:
        return search_tmdb_by_showtitle(show_title)
    
    # If tv_show_id is valid, get TMDb ID from the details
    return get_tmdb_id_from_tv_show_details(tv_show_id)

def make_api_request(url):
    response = requests.get(url).json()
    logger.debug(f"API Response: {response}")
    return response

def search_tmdb_by_showtitle(show_title):
    search_url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={show_title}"
    response = make_api_request(search_url)

    # Log the search response
    logger.debug(f"Search Response for title '{show_title}': {response}")

    if response.get('results'):
        # Assuming you want the first result
        show_info = response['results'][0]
        tmdb_id = show_info.get('id')
        logger.debug(f"Found TMDb ID for title '{show_title}': {tmdb_id}")
        return tmdb_id
    
    logger.debug(f"No results found for title '{show_title}'")
    return None

def get_tmdb_id_from_tv_show_details(tv_show_id):
    tv_show_url = f"http://localhost:{port}/jsonrpc?request={{%22jsonrpc%22:%222.0%22,%22method%22:%22VideoLibrary.GetTVShowDetails%22,%22params%22:{{%22tvshowid%22:{tv_show_id},%22properties%22:[%22uniqueid%22]}},%22id%22:%22libTvShow%22}}"
    response = make_api_request(tv_show_url)
    return response.get('result', {}).get('tvshowdetails', {}).get('uniqueid', {}).get('tmdb')

def get_tmdb_id_for_media(info):
    # Try to get the TMDb ID from the uniqueid field
    tmdb_id = info.get('uniqueid', {}).get('tmdb')

    # If TMDb ID is not found, extract the title and search TMDb
    if not tmdb_id:
        title = info.get('title')  # Extract the title from info
        if title:
            logger.debug(f"TMDb ID not found for media. Searching TMDb using title: {title}")
            tmdb_id = search_tmdb_by_movietitle(title)
        else:
            logger.debug("No title found to search TMDb.")
    
    return tmdb_id

def search_tmdb_by_movietitle(title):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = make_api_request(search_url)

    # Log the search response
    logger.debug(f"Search Response for title '{title}': {response}")

    if response.get('results'):
        # Assuming you want the first result
        show_info = response['results'][0]
        tmdb_id = show_info.get('id')
        logger.debug(f"Found TMDb ID for title '{title}': {tmdb_id}")
        return tmdb_id
    
    logger.debug(f"No results found for title '{title}'")
    return None

def get_image_url(tmdb_id, media_type):
    return get_image_url_from_tmdb(tmdb_id, media_type) if tmdb_id else DEFAULT_POSTER_URL

def get_image_url_from_tmdb(tmdb_id, media_type):
    tmdb_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = make_api_request(tmdb_url)
    return f"https://image.tmdb.org/t/p/w185{response['poster_path']}" if 'poster_path' in response and response['poster_path'] else DEFAULT_POSTER_URL
    
def get_original_title_or_original_name_from_tmdb(tmdb_id, media_type): #Rex
    tmdb_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = make_api_request(tmdb_url)
    if not response:
        return None
    if media_type == 'movie':
        return response.get('original_title')
    else:
        return response.get('original_name')
        
def get_episode_name_from_tmdb(tmdb_id, media_type, season_number, episode_number): #Rex
    tmdb_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/season/{season_number}/episode/{episode_number}?api_key={TMDB_API_KEY}"
    response = make_api_request(tmdb_url)
    if not response:
        return None
    if media_type == 'tv':
        return response.get('name')

def get_tmdb_url(tmdb_id, media_type):
    return f"https://www.themoviedb.org/{media_type}/{tmdb_id}" if tmdb_id else None
