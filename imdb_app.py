import streamlit as st
from omdb_conn import OmdbAPIConnection
import pandas as pd
from time import sleep

def colored_header(label: str = "Nice title",description: str = "",color_name = "gold",help = "", description_help = " "):
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
def Notif(type = "success",duration = 3, message = "None"):
    '''
    Shows a notification for a certain duration

    Parameters
    ----------
    type : str, optional
        The type of the notification, by default "success"
    duration : int, optional
        The duration of the notification, by default 3
    message : str, optional
        The message of the notification, by default "None"
    '''
    if message == "None":
        message = type 

    if type == "success":
        notif = st.success(message)
    elif type == "error":
        notif = st.error(message)
    elif type == "warning":
        notif = st.warning(message)
    elif type == "info":
        notif = st.info(message)
    else:
        notif = st.write("Notif type not found")

    sleep(duration)
    notif.empty()

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
        help="",
        description="Select the Parameters to Filter the Query",
        color_name="gold",
    )
    type = st.selectbox("Type", ["Movie", "Series"])
    st.session_state.add_type = st.checkbox("Filter Type")
    y = st.number_input("Year", value=2015, min_value=1800)
    st.session_state.add_y = st.checkbox("Filter Year")
    page = st.number_input("Page", value=1 , min_value=1, max_value=100)
    st.session_state.add_page = st.checkbox("Filter Page")
    with st.expander("Advanced Settings",expanded=True):
        st.session_state.full_info = st.checkbox("Full Information",value=True, help="This will also add Graphs" , on_change=st.cache_data.clear() )
        if st.button("Clear Cache",use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            Notif(type="success",message="Cache Cleared")

# Query
# ------------------------------------------------------------------------------
# read the api key from the secrets
api = st.secrets["api_key"]

# create an instance of OmdbAPIConnection
omdb_conn = st.experimental_connection("IMDB Connection", type=OmdbAPIConnection , api_key=api)
# Query
query = f's={st.session_state.movie_name}'
if st.session_state.add_type:
    query = query + f'&type={type}'
if st.session_state.add_y:
    query = query + f'&y={y}'
if st.session_state.add_page:
    query = query + f'&page={page}'

st.markdown(f'**Your query:** `{query}`')
# ---------------------------------------------------------------------------------------
# Search Button
if st.button('Search',help="Tick Full Information from Advanced Settings to get all the info"):
    try:
        # Get results and display them
        df = omdb_conn.query(query, full_information=st.session_state.full_info)
        df.set_index("Title", inplace=True)
        tab1 , tab2 ,tab3 = st.tabs(["Data", "Raw CSV Data", "Download Data as CSV"])
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
                        help="Double click to Increase the size of the image"
                    )
                    },
                    use_container_width=True,
                )
            if st.session_state.full_info:
                with st.expander("Graphs",expanded=True):
                    st.title("Graphs")

                    st.subheader("Movies Runtime")
                    st.bar_chart(df[df["Type"] == "movie"]["Runtime"].str.replace(" min","").astype(int))
                    st.divider()

                    st.subheader("Movies IMDB Ratings")
                    st.bar_chart(df["imdbRating"].astype(float))
                    st.divider()

                    st.subheader("Movies IMDB Votes")
                    st.bar_chart(df["imdbVotes"].str.replace(",","").astype(int))
                    st.divider()

                    st.subheader("Entry Rated")
                    st.bar_chart(df.groupby("Rated").count()["imdbID"])
                    st.divider()


        with tab2:
            csv = df.to_csv(index=True)
            st.code(csv, language="csv")
        
        with tab3:
            st.download_button(
                label="Download Data as CSV ⬇️",
                data=csv,
                file_name=f"{st.session_state.movie_name}_imdb_data.csv",
                mime="text/csv",
            )

        st.session_state.data = df

    except Exception as e:
        st.error(f'API Error: {e}')

# Code
with st.expander("Query Docstring"):
    st.subheader("query()")
    st.code(omdb_conn.query.__doc__)

with st.expander("OmdbAPIConnection Source Code"):
    # read file omdb_conn.py and display it
    with open("omdb_conn.py", "r") as f:
        st.code(f.read())
    