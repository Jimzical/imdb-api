import streamlit as st
from omdb_conn import OmdbAPIConnection

# title
st.title("Imdb API Connection Example")

# read the api key from the secrets
api = st.secrets["api_key"]

# create an instance of UniProtAPIConnection
uniprot_conn = OmdbAPIConnection("IMDB Connection", api_key=api)

movie_name = st.text_input("Movie Name", value="Batman")

with st.sidebar:
    type = st.selectbox("Type", ["movie", "series", "episode"])
    add_type = st.checkbox("Add Type")
    y = st.number_input("Year", value=2015)
    add_y = st.checkbox("Add Year")
    page = st.number_input("Page", value=1)
    add_page = st.checkbox("Add Page")
    with st.expander("Advanced"):
        full_info = st.checkbox("Full Information", help="You may have to clear the cache to see the changes" , on_change=st.cache_data.clear() )


query = f's={movie_name}'

if add_type:
    query = query + f'&type={type}'
if add_y:
    query = query + f'&y={y}'
if add_page:
    query = query + f'&page={page}'

st.markdown(f'**Your query:** `{query}`')
if st.button('Search'):
    try:
        # Get results and display them
        df = uniprot_conn.query(query, full_information=full_info)
        st.write(df)
        # df, um = uniprot_conn.query(query)
        # st.write(um)
    except Exception as e:
        st.error(f'API Error: {e}')
