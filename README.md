# IMDB-api  [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://imdb-api.streamlit.app/)

[![hackathon](https://global.discourse-cdn.com/business7/uploads/streamlit/optimized/3X/d/6/d6e06e08c5eae258e58f8e71e9bb0db8c77a9db1_2_750x750.jpeg)](https://discuss.streamlit.io/t/connections-hackathon/47574)
<br/>
Made for the Streamlit Hackathon
Uses the OMDB api to get data from IMDB in the form of a DataFrame
<br/>

## How to Run Locally
- Clone the repo
  ```bash
  git clone https://github.com/Jimzical/imdb-api.git
  ```
-  Install the requirements
      ```bash
    pip install -r requirements.txt
      ```
-   Run the imdb_app.py file
    ```bash
    streamlit run imdb_app.py
    ```
- Enjoy!

## Screenshots
![Screenshot 1](https://github.com/Jimzical/imdb-api/blob/media/home.png)

## Example Code
- `example.py`
```python
import streamlit as st
from omdb_conn import OmdbAPIConnection
import pandas as pd

# read the api key from the secrets
api = st.secrets["api_key"]

# create an instance of OmdbAPIConnection
omdb_conn = st.experimental_connection("IMDB Connection", type=OmdbAPIConnection , api_key=api)

# Query
query = f's=batman&type=movie&page=2'

# Get results and display them
df = omdb_conn.query(query)

st.title("OMDB Experimental Connector")
st.dataframe(df)
```

- `.streamlit\secrets.toml`
```toml
api_key = "YOUR_API_KEY"

```

## Usage

- `query()` Docstring
```python
    Queries the API .

Parameters:
    query (str): The query string ["s={movie_name}"  Required] 
    {QueryFormat -> "s={movie_name}&type={movie/series/episode}&y={release_year}&page={page_number}"}

    cache_time (int): The time to cache the data in seconds (Default: 3600)

    full_information (bool): If True, returns the full information about the movie
    {Warning: This will make the query slower}

    **kwargs (Any): Any additional arguments to pass to the query

Returns:
    pd.DataFrame: The results of the query in a dataframe
    for full_information = False -> {Title, Year, imdbID, Type, Poster}
    for full_information = True -> {Title, Year, imdbID, Type, Poster, Rated, Released, Runtime, Genre, Director, Writer, Actors, Plot, Language, Country, Awards,  Metascore, imdbRating, imdbVotes, imdbID, Type, DVD, BoxOffice, Production, Website, totalSeasons}

Raises:
    Exception: If the API returns an error

Examples:
    >>> imdb_conn = st.experimental_connection("IMDB Connection", type=OmdbAPIConnection , api_key=api)
    OR
    >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
    
    >>> query = f's=Batman' # Search for Batman
    >>> df = imdb_conn.query(query)

    >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
    >>> query = f's=Batman&type=movie' # Search for Batman and filter by type movie
    >>> df = imdb_conn.query(query)

    >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
    >>> query = f's=Batman&y=2015' # Search for Batman and filter by year 2015
    >>> df = imdb_conn.query(query)

    >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
    >>> query = f's=Batman&type=movie&y=2015' # Search for Batman and filter by type movie and year 2015
    >>> df = imdb_conn.query(query)

    >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
    >>> query = f's=Batman&type=movie&y=2015&page=2' # Search for Batman and filter by type movie and year 2015 and page 2 results
    >>> df = imdb_conn.query(query)

    >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
    >>> query = f's=Batman&type=movie&y=2015&page=1' # Search for Batman and filter by type movie and year 2015 and page 1
    >>> df = imdb_conn.query(query, full_information = True) # Get all the information about the movie
```
