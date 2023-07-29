from typing import Any,List
import json
import requests
import pandas as pd
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data
from requests.adapters import HTTPAdapter
from urllib3 import Retry



class OmdbAPIConnection(ExperimentalBaseConnection[requests.Session]):
    """Basic st.experimental_connection implementation for IMDB API"""


    def __init__(
        self,
        connection_name: str,
        api_key: str,
        base_url: str = "http://www.omdbapi.com/",
        total_retries: int = 5,
        backoff_factor: float = 0.25,
        status_forcelist: List[int] = None,
        **kwargs,
    ):
        self.base_url = base_url
        self.api_key = api_key

        if status_forcelist is None:
            status_forcelist = [500, 502, 503, 504]
        self.retries = Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )

        super().__init__(connection_name, **kwargs)

    def _connect(
        self, 
        **kwargs: Any
        ) -> requests.Session:
        """
        Connects to the Session

        returns: 
            requests.Session: session
        """
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=self.retries))
        return session

        def full_info(
            self,
            basic_df: pd.DataFrame,
            **kwargs: Any
            ) -> pd.DataFrame:
            """
            Gets the full information about the movie

            Parameters:
                basic_df (pd.DataFrame): The basic dataframe with the imdb ids
                **kwargs (Any): Any additional arguments to pass to the query

            Returns:
                pd.DataFrame: The dataframe with the full information

            """
            for index, row in basic_df.iterrows():
                params = {}
                params["apikey"] = api
                params["i"] = row["IMDb ID"]
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                json_response = json.loads(response.text)
                for key in json_response:
                    if key == "Response" or key =="Ratings":
                        break
                    basic_df.at[index, key] = json_response[key]

            return basic_df

    def query(
        self, 
        query: str, 
        cache_time: int = 3600, 
        full_information = False,
        **kwargs: Any
        ) -> pd.DataFrame:
        """
        Queries the API .
        
        Parameters:
            query (str): The query string [Required]
            cache_time (int): The time to cache the data in seconds (Default: 3600)
            full_information (bool): If True, returns the full information about the movie (Default: False) {Warning: This will make the query slower}
            **kwargs (Any): Any additional arguments to pass to the query

        Returns:
            pd.DataFrame: The results of the query

        Raises:
            Exception: If the API returns an error

        Examples:
            >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
            >>> query = f's=Batman' # Search for Batman
            >>> df = imdb_conn.query(query)

            >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
            >>> query = f's=Batman&type=movie' # Search for Batman and filter by type movie
            >>> df = imdb_conn.query(query)

            >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
            >>> query = f's=Batman&type=movie&y=2015' # Search for Batman and filter by type movie and year 2015
            >>> df = imdb_conn.query(query)

            >>> imdb_conn = OmdbAPIConnection("IMDB Connection" , api_key = api)
            >>> query = f's=Batman&type=movie&y=2015&page=1' # Search for Batman and filter by type movie and year 2015 and page 1
            >>> df = imdb_conn.query(query)
        """


        @cache_data(ttl=cache_time)
        def _query(search: str, **kwargs: Any) -> pd.DataFrame:
            url = (
                self.base_url + "?apikey=" + self.api_key + "&" + search
            )

            response = self._instance.get(url)
            response.raise_for_status()
            

            if json.loads(response.text)["Response"] == "False":
                raise Exception(json.loads(response.text)["Error"])
            else:
                result = pd.DataFrame(json.loads(response.text)["Search"])

            if full_information:
                print("full information")   
                for index, row in result.iterrows():
                    params = {}
                    params["apikey"] = self.api_key
                    params["i"] = row["imdbID"]
                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()
                    json_response = json.loads(response.text)
                    for key in json_response:
                        if key == "Response" or key =="Ratings":
                            break
                        result.at[index, key] = json_response[key]


            return result

        return _query(query, **kwargs)
