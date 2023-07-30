import streamlit as st
from omdb_conn import OmdbAPIConnection
import pandas as pd


def colored_header(label: str = "Nice title",description: str = "",color_name = "gold",help = " ", description_help = " "):
    """
    Shows a header with a colored underline and an optional description.
    """
    st.title(
        body=label,
        help=help,
    )
    st.write(
        f'<hr style="background-color: {color_name}; margin-top: 0;'
        ' margin-bottom: 0; height: 3px; border: none; border-radius: 3px;">',
        unsafe_allow_html=True,
    )
    if description:
        st.caption(description,help=description_help)


# set page config
st.set_page_config(
    page_title="OMDB Experimental Connector",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "http://www.omdbapi.com/",
        "Report a bug": "https://github.com/Jimzical/imdb-api/issues",
        "About": " Using the st.experimental_connection to connect to the OMDB API for the Streamlit Hackathon",
    }
)


# initialize the session state
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()
if "movie_name" not in st.session_state:
    st.session_state.movie_name = ""
if "full_info" not in st.session_state:
    st.session_state.full_info = False
if "add_type" not in st.session_state:
    st.session_state.add_type = False
if "add_y" not in st.session_state:
    st.session_state.add_y = False
if "add_page" not in st.session_state:
    st.session_state.add_page = False

# read the api key from the secrets
api = st.secrets["api_key"]

# create an instance of OmdbAPIConnection
omdb_conn = OmdbAPIConnection("IMDB Connection", api_key=api)

# Build the UI
# title
colored_header(
    label="OMDB Experimental Connector",
    color_name="gold",
)
st.markdown(
   '''
    <h4>This is an example on how to use the OMDB Experimental Connector</h4>
    <p>For more information on the OMDB API, please visit <a href="http://www.omdbapi.com/">API Docs</a></p>
   '''
    , unsafe_allow_html=True
)

# Movie Name
st.session_state.movie_name = st.text_input("Movie Name", value="Batman")

# Filters
with st.sidebar:
    colored_header(
        label="Parameters",
        description="Select the Parameters to Filter the Query",
        color_name="gold",
    )
    type = st.selectbox("Type", ["Movie", "Series", "Episode"])
    st.session_state.add_type = st.checkbox("Filter Type")
    y = st.number_input("Year", value=2015)
    st.session_state.add_y = st.checkbox("Filter Year")
    page = st.number_input("Page", value=1)
    st.session_state.add_page = st.checkbox("Filter Page")
    with st.expander("Advanced"):
        st.session_state.full_info = st.checkbox("Full Information", help="You may have to wait for some time" , on_change=st.cache_data.clear() )


# Query
query = f's={st.session_state.movie_name}'
if st.session_state.add_type:
    query = query + f'&type={type}'
if st.session_state.add_y:
    query = query + f'&y={y}'
if st.session_state.add_page:
    query = query + f'&page={page}'

st.markdown(f'**Your query:** `{query}`')

# Search Button
if st.button('Search'):
    try:
        # Get results and display them
        df = omdb_conn.query(query, full_information=st.session_state.full_info)
        tab1 , tab2 ,tab3 = st.tabs(["Data", "Raw CSV Data", "Download Data"])
        if tab1:
            colored_header(
                label="Data",
                color_name="gold",
                help="The Dataframe with the results from the query"
            )                
            st.data_editor(
                    df,
                    column_config={
                        
                    "Poster" : st.column_config.ImageColumn(
                        "Poster",
                        help="Poster"
                    )
                    }
                )
        with tab2:
            csv = df.to_csv(index=False)
            st.code(csv, language="csv")
        
        with tab3:
            st.download_button(
                label="Download Data",
                data=csv,
                file_name=f"{st.session_state.movie_name}_imdb_data.csv",
                mime="text/csv",
            )

        st.session_state.data = df

    except Exception as e:
        st.error(f'API Error: {e}')

# Code
with st.expander("Query Docstring"):
    st.code(omdb_conn.query.__doc__)

with st.expander("OmdbAPIConnection Source Code"):
    st.code(''' 
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

        ''')
