import streamlit as st
from omdb_conn import OmdbAPIConnection
from streamlit_extras.chart_container import chart_container
import pandas as pd

# title
st.title("Imdb API Connection Example")

# read the api key from the secrets
api = st.secrets["api_key"]


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


# create an instance of OmdbAPIConnection
omdb_conn = OmdbAPIConnection("IMDB Connection", api_key=api)

st.session_state.movie_name = st.text_input("Movie Name", value="Batman")

with st.sidebar:
    type = st.selectbox("Type", ["movie", "series", "episode"])
    st.session_state.add_type = st.checkbox("Add Type")
    y = st.number_input("Year", value=2015)
    st.session_state.add_y = st.checkbox("Add Year")
    page = st.number_input("Page", value=1)
    st.session_state.add_page = st.checkbox("Add Page")
    with st.expander("Advanced"):
        st.session_state.full_info = st.checkbox("Full Information", help="You may have to clear the cache to see the changes" , on_change=st.cache_data.clear() )
    st.write(st.session_state)

query = f's={st.session_state.movie_name}'

if st.session_state.add_type:
    query = query + f'&type={type}'
if st.session_state.add_y:
    query = query + f'&y={y}'
if st.session_state.add_page:
    query = query + f'&page={page}'

st.markdown(f'**Your query:** `{query}`')

if st.button('Search'):
    try:
        # Get results and display them
        df = omdb_conn.query(query, full_information=st.session_state.full_info)
        st.data_editor(
            df,
            column_config={
                
            "Poster" : st.column_config.ImageColumn(
                "Poster",
                help="Poster"
            )
            }
        )
        
        st.session_state.data = df

    except Exception as e:
        st.error(f'API Error: {e}')

