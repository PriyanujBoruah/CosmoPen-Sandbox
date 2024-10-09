import streamlit as st
import mysql.connector
from datetime import date, timedelta
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import docx 
from docx.shared import Pt
import io
from docx import Document
from app_prompt_functions import *

st.set_page_config(page_title="CosmoPen", page_icon="logo.png", layout="wide", initial_sidebar_state="collapsed", menu_items=None)

st.markdown(
    f"""
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Display:ital,wght@0,100..900;1,100..900&family=Noto+Sans:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Display:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mali:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;1,200;1,300;1,400;1,500;1,600;1,700&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mali:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;1,200;1,300;1,400;1,500;1,600;1,700&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@300..700&family=Mali:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;1,200;1,300;1,400;1,500;1,600;1,700&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
</head>
    """,unsafe_allow_html=True)

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)



#primaryColor="#000EEF"
#backgroundColor="#FFFFFF"
#secondaryBackgroundColor = "#EFF3F6"
#textColor = "#000000"


GOOGLE_API_KEY = 'AIzaSyDmF4D2f_ibz6UZi_sFZyydkSmUrz7x8_k'
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.0-pro')
modelx = genai.GenerativeModel('gemini-1.5-flash')

valid = False

connection = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "2mF9jreccF49KBR.root",
  password = "Jcwu6U9eVVSwRTjt",
  database = "userlist",
  ssl_ca = "isrgrootx1.pem",
  ssl_verify_cert = True,
  ssl_verify_identity = True
)

USERS = {
    "user1": ['Basic',240, 1001],
    "user2": ['Plus', 240, 1002],
    "user3": ['Advanced', 240, 1003],
    "user4": ['Basic', 240, 1004],
    "user5": ['Plus', 240, 1005],
    "user6": ['Plus', 240, 1006],
    "user7": ['Advanced', 240, 1007],
    "user8": ['Advanced', 240, 1008],
    "user9": ['Plus', 240, 1009],
    "user10": ['Basic', 240, 1010],   
}




def email_exists(connection, email):
    cursor = connection.cursor()
    sql = "SELECT 1 FROM users WHERE email = %s"
    values = (email,) 

    cursor.execute(sql, values)
    result = cursor.fetchone()

    return bool(result)  # True if a row was found, False otherwise

def get_pilot_id_by_email(connection, email):
    cursor = connection.cursor()
    sql = "SELECT pilot_id FROM users WHERE email = %s" 
    values = (email,)

    cursor.execute(sql, values)
    result = cursor.fetchone()

    return result[0] if result else None  # If a result was found, return the pilot_id, otherwise return None

def get_tier_by_email(connection, email):
    cursor = connection.cursor()
    sql = "SELECT tier FROM users WHERE email = %s" 
    values = (email,)

    cursor.execute(sql, values)
    result = cursor.fetchone()

    return result[0] if result else None  # If a result was found, return the tier, otherwise return None


def check_credit(connection, email):
    """Checks and prints the daily_remaining and total_remaining rate limits 
       for a given email on the CURRENT date.
    """

    cursor = connection.cursor()
    sql = """
        SELECT credit 
        FROM users
        WHERE email = %s;
    """
    values = (email,) 

    cursor.execute(sql, values)
    result = cursor.fetchone()

    if result:
        CREDIT = result[0]  # Extract the first element from the tuple
        return CREDIT
    else:
        return "Error: No rate limit information found"
    
def decrease_credit_1(connection, email):
    cursor = connection.cursor()
    sql = "UPDATE users SET credit = credit - 1 WHERE email = %s"
    values = (email,)

    try:
        cursor.execute(sql, values)
        connection.commit()  # Important to save the changes
        return True
    except Exception as e:
        print(f"Error decreasing credit: {e}")
        connection.rollback()  # Revert changes if an error occurred
        return False
def decrease_credit_2(connection, email):
    cursor = connection.cursor()
    sql = "UPDATE users SET credit = credit - 2 WHERE email = %s"
    values = (email,)

    try:
        cursor.execute(sql, values)
        connection.commit()  # Important to save the changes
        return True
    except Exception as e:
        print(f"Error decreasing credit: {e}")
        connection.rollback()  # Revert changes if an error occurred
        return False
def decrease_credit_3(connection, email):
    cursor = connection.cursor()
    sql = "UPDATE users SET credit = credit - 3 WHERE email = %s"
    values = (email,)

    try:
        cursor.execute(sql, values)
        connection.commit()  # Important to save the changes
        return True
    except Exception as e:
        print(f"Error decreasing credit: {e}")
        connection.rollback()  # Revert changes if an error occurred
        return False
    
def insert_prompt_history(connection, email, prompt):
    """Inserts an email and prompt into a table named 'history'.

    Args:
        connection: The database connection object.
        email (str): The email address to insert.
        prompt (str): The prompt text to insert.

    Returns:
        bool: True if the insertion was successful, False otherwise.
    """
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO history (email, prompt) VALUES (%s, %s)"
        values = (email, prompt)
        cursor.execute(sql, values)
        connection.commit()  # Save the changes
        return True

    except Exception as e:
        print(f"Error inserting into history: {e}")
        connection.rollback()  # Revert changes if an error occurred
        return False

def get_recent_prompts(connection, email, limit=10):
    """Retrieves the most recent prompts for a given email from the 'history' table.

    Args:
        connection: The database connection object.
        email (str): The email address to retrieve prompts for.
        limit (int, optional): The maximum number of prompts to retrieve. 
                               Defaults to 20.

    Returns:
        list: A list of strings representing the retrieved prompts, 
              or an empty list if none are found.
    """

    try:
        cursor = connection.cursor()
        sql = """
            SELECT prompt
            FROM history
            WHERE email = %s
            ORDER BY prompt_id DESC
            LIMIT %s;
        """
        values = (email, limit) 
        cursor.execute(sql, values)
        results = cursor.fetchall()

        # Extract prompts from the result tuples
        prompts = [row[0] for row in results] 
        return prompts

    except Exception as e:
        print(f"Error retrieving prompts: {e}")
        return []  # Return an empty list in case of an error
    

    

def login_page():
    st.title("Welcome to CosmoPen")
    with st.container(border=True):
        email = st.text_input("Please enter your email:")
        if st.button("Login"):
            email_to_check = email
            if email_exists(connection, email_to_check):
                st.session_state.email = email  # Store name in session state
                st.session_state.page = "two"  # Navigate to page two
            else:
                st.warning("Invalid Email")


def dashboard():
    if "email" in st.session_state:
        EMAIL = st.session_state.email
        PILOT_ID = get_pilot_id_by_email(connection, EMAIL)
        CREDIT = check_credit(connection, EMAIL)
        TIER = get_tier_by_email(connection, EMAIL)

    else:
        st.write("Name not found. Please go back to Page One.")

    return EMAIL, PILOT_ID, CREDIT, TIER


def READ_ROWS(uploaded_file, num_rows=250):
    """Reads the top 'num_rows' from various file types using pandas.

    Args:
        uploaded_file (st.UploadedFile): The uploaded file object from Streamlit.
        num_rows (int, optional): The number of rows to read. Defaults to 2500.

    Returns:
        pandas.DataFrame or None: A DataFrame containing the top rows,
                                   or None if an error occurs.
    """
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower() 

        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file, nrows=num_rows)
        elif file_extension == 'xlsx':
            df = pd.read_excel(uploaded_file, nrows=num_rows, engine='openpyxl')
        elif file_extension == 'tsv':
            df = pd.read_csv(uploaded_file, sep='\t', nrows=num_rows)
        else:
            st.error("Unsupported file type. Please upload a CSV, XLSX, or TSV file.")
            return None

        return df

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
    

def DF_TO_STR(df):
    """Converts a pandas DataFrame to a string.

    Args:
        df (pandas.DataFrame): The DataFrame to convert.

    Returns:
        str: A string representation of the DataFrame,
             or an empty string if the input is not a DataFrame.
    """
    if isinstance(df, pd.DataFrame):
        return df.to_csv(index=False)
    else:
        print("Error: Input is not a pandas DataFrame.")
        return ""

def GET_DOCX(CONTENT):
    document = Document()
    document.add_paragraph(CONTENT)
    bio = io.BytesIO()
    document.save(bio)
    return bio.getvalue()





if "page" not in st.session_state:
    st.session_state.page = "one" 

if st.session_state.page == "one":
    login_page()
elif st.session_state.page == "two":
    EMAIL, PILOT_ID, CREDIT, TIER = dashboard()
    TIER_NAME = "None"
    if TIER == 1:
        TIER_NAME = "Advanced"
    elif TIER == 2:
        TIER_NAME = "Plus"
    elif TIER == 3:
        TIER_NAME = "Basic"

    st.html("<h2 class='logo'><span style='color:#071b33'>Cosmo</span>Pen</h2>")

    with st.expander("About", expanded=False):
        EXPAND_COL1, EXPAND_COL2 = st.columns(2)
        EXPAND_COL1.html(f"""
                <p class='acc_info1'>Email: <span class='acc_info2'>{EMAIL}</span></p>
                <p class='acc_info1'>Pilot Number: <span class='acc_info2'>{PILOT_ID}</span></p>
                """)
        EXPAND_COL2.html(f"""
                <p class='acc_info1'>Pilot Tier: <span class='acc_info2'>{TIER_NAME}</span></p>
                <p class='acc_info1'>Remaining Credits: <span class='acc_info2'>{CREDIT}</span></p>
                """)


    HEAD_COL1, HEAD_COL2 = st.columns(2, vertical_alignment="bottom", gap="medium")

    with HEAD_COL1.popover(f"**System Mode**", help="Note: Selecting the mode will reset the content.", use_container_width=True):
        MAIN_MODE = st.radio(
            "**Filter by**",
            ["AI Sandbox", "Creative Mode", "AI Partner", "Prompt History"],
            captions=[
                "Text content-based manipulation.",
                "Document-based manipulation.",
                "Data-based manipulation.",
                "Last 10 prompts."],
            )

    with HEAD_COL2.popover(f"**Prompt Type**", help="Note: Selecting the mode will reset the content.", use_container_width=True):
        
        if MAIN_MODE == "AI Sandbox":
            MODE_SELECTION = st.radio(
            "**Filter by**",
            ["**Text Prompt**", "**Document Prompt**", "**Data Prompt**", "**Code Prompt**"],
            captions=[
                "Text content-based manipulation.",
                "Document-based manipulation.",
                "Data-based manipulation.",
                "Code-based manipulation."],
            )

        elif MAIN_MODE == "Creative Mode":
            MODE_SELECTION = st.radio(
            "**Filter by**",
            ["**Text Prompt**", "**Document Prompt**", "**Data Prompt**", "**Code Prompt**"],
            captions=[
                "Content creation based on text.",
                "Content creation based on document.",
                "Content creation based on data.",
                "Content creation based on code."],
            )

    HERO_COL1, HERO_COL2, HERO_COL3, HERO_COL4 = st.columns(4, vertical_alignment="center")




    CONTAINER = st.container(border=True)


    if MAIN_MODE == "AI Sandbox":

        if MODE_SELECTION == "**Text Prompt**":
            COSMO_PROMPT = CONTAINER.text_area("**Prompt**", placeholder="eg. inspirations for my new book based on sci-fi novels", height=100)
            if COSMO_PROMPT:
                valid = True

        elif MODE_SELECTION == "**Document Prompt**":
            PROMPT_COL1, PROMPT_COL2 = CONTAINER.columns([2,1])    # R O W S
            COSMO_PROMPT = PROMPT_COL1.text_area("**Prompt**", placeholder="eg. summarize me this document", height=100)
            COSMO_DOCUMENT_FILE = PROMPT_COL2.file_uploader("**UPLOAD PDF DOCUMENT**", type="pdf")
            if COSMO_DOCUMENT_FILE is not None:
                reader = PdfReader(COSMO_DOCUMENT_FILE)
                TEXT = """"""
                PAGE = ""
                number_of_pages = len(reader.pages)
                for i in range(number_of_pages):
                    PAGE = f"\n\n\n- - - - - - Page Number {i+1} - - - - - -\n\n"
                    TEXT = TEXT + PAGE
                    page = reader.pages[i]
                    text = page.extract_text()
                    TEXT = TEXT + text
                COSMO_DOCUMENT = TEXT
            if COSMO_PROMPT and COSMO_DOCUMENT:
                valid = True

        elif MODE_SELECTION == "**Data Prompt**":
            PROMPT_COL1, PROMPT_COL2 = CONTAINER.columns([2,1])    # R O W S
            COSMO_PROMPT = PROMPT_COL1.text_area("**Prompt**", placeholder="eg. give me the count and values of outliers in this dataset", height=100)
            COSMO_DATA_FILE = PROMPT_COL2.file_uploader("**UPLOAD DATA**", type=["csv", "tsv", "xlsx"])
            if COSMO_DATA_FILE is not None:
                DATASET = READ_ROWS(COSMO_DATA_FILE)
                if DATASET is not None:
                    COSMO_DATA = DATASET.to_csv(index=False)
            if COSMO_PROMPT and COSMO_DATA:
                valid = True

        elif MODE_SELECTION == "**Code Prompt**":
            PROMPT_COL1, PROMPT_COL2 = CONTAINER.columns([2,1])    # R O W S
            COSMO_PROMPT = PROMPT_COL1.text_area("**Prompt**", placeholder="eg. optimize this code to make it more readable", height=100)
            COSMO_CODE = PROMPT_COL2.text_area("**Paste your code here**", placeholder="enter or paste your content here", height=100)
            if COSMO_PROMPT and COSMO_CODE:
                valid = True


    elif MAIN_MODE == "Creative Mode":

        if MODE_SELECTION == "**Text Prompt**":
            CONTAINER.text("Prompt")
            COSMO_PROMPT = CONTAINER.text_area("**Prompt**", placeholder="eg. create a blog on travel and food.", height=100, label_visibility="collapsed")
            if COSMO_PROMPT:
                valid = True

        elif MODE_SELECTION == "**Document Prompt**":
            COSMO_PROMPT = CONTAINER.text_area("**Prompt**", placeholder="eg. create a mock business plan for my AI startup (1500 words)", height=100)
            if COSMO_PROMPT:
                valid = True

        elif MODE_SELECTION == "**Data Prompt**":
            COSMO_PROMPT = CONTAINER.text_area("**Prompt**", placeholder="eg. generate a customer reviews dataset for a sentiment analysis", height=100)
            if COSMO_PROMPT:
                valid = True

        elif MODE_SELECTION == "**Code Prompt**":
            COSMO_PROMPT = CONTAINER.text_area("**Prompt**", placeholder="eg. create a python script for a recommendation engine", height=100)
            if COSMO_PROMPT:
                valid = True


    elif MAIN_MODE == "AI Partner":
        PARTNER_COL1, PARTNER_COL2 = CONTAINER.columns([1,3])    # R O W S
        COSMO_ABOUT = PARTNER_COL1.text_area("**Describe your work**", placeholder="eg. i work as a software engineer in a big tech company", height=100)
        COSMO_PROMPT = PARTNER_COL2.text_area("**Prompt**", placeholder="eg. my project requires me to develop a web app. please guide me through the process", height=100)
        if COSMO_ABOUT and COSMO_PROMPT:
            valid = True


    elif MAIN_MODE == "Prompt History":
        PROMPTS = get_recent_prompts(connection, EMAIL)
        for i in range(len(PROMPTS)):
            PROMPT = PROMPTS[i]
            with st.expander(f"**Prompt {i+1}**", expanded=False):
                st.write(PROMPT)


    BUTTON_COL1, BUTTON_COL2, BUTTON_COL3, BUTTON_COL4, BUTTON_COL5 = st.columns(5)

    if valid:
        BUTTON = BUTTON_COL3.button("**✦**", use_container_width=True, type="primary")
    else:
        BUTTON = BUTTON_COL3.button("**✦**", use_container_width=True, type="primary", disabled=True)

    if BUTTON:
        
        OUTPUT_CONTAINER = st.container(border=True)

        if MAIN_MODE == "AI Sandbox":
            if MODE_SELECTION == "**Text Prompt**":
                OUTPUT = SANDBOX_TEXT(COSMO_PROMPT)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)
            elif MODE_SELECTION == "**Document Prompt**":
                OUTPUT = SANDBOX_DOCUMENT(COSMO_PROMPT, COSMO_DOCUMENT)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)
            elif MODE_SELECTION == "**Data Prompt**":
                OUTPUT = SANDBOX_DATA(COSMO_PROMPT, COSMO_DATA)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)
            elif MODE_SELECTION == "**Code Prompt**":
                OUTPUT = SANDBOX_CODE(COSMO_PROMPT, COSMO_CODE)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)

        elif MAIN_MODE == "Creative Mode":
            if MODE_SELECTION == "**Text Prompt**":
                OUTPUT = CREATIVE_TEXT(COSMO_PROMPT)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)
            
            elif MODE_SELECTION == "**Document Prompt**":
                OUTPUT = CREATIVE_DOCUMENT(COSMO_PROMPT)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)
                DOWNLOAD_COL2.download_button("Download as DOCX (MS Word)", data=GET_DOCX(OUTPUT), file_name="OUTPUT.docx", mime="docx", use_container_width=True)

            elif MODE_SELECTION == "**Data Prompt**":
                OUTPUT = CREATIVE_DATA(COSMO_PROMPT)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download Dataset", OUTPUT, use_container_width=True)
            
            elif MODE_SELECTION == "**Code Prompt**":
                OUTPUT = CREATIVE_CODE(COSMO_PROMPT)
                DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
                DOWNLOAD_COL1.download_button("Download Code", OUTPUT, use_container_width=True)

        elif MAIN_MODE == "AI Partner":
            OUTPUT = AI_PARTNER(COSMO_ABOUT, COSMO_PROMPT)
            DOWNLOAD_COL1, DOWNLOAD_COL2, DOWNLOAD_COL3, DOWNLOAD_COL4, DOWNLOAD_COL5 = OUTPUT_CONTAINER.columns(5)
            DOWNLOAD_COL1.download_button("Download as TXT", OUTPUT, use_container_width=True)
            DOWNLOAD_COL2.download_button("Download as DOCX (MS Word)", data=GET_DOCX(OUTPUT), file_name="OUTPUT.docx", mime="docx", use_container_width=True)


        OUTPUT_CONTAINER.write(OUTPUT)

        decrease_credit_1(connection, EMAIL)
        insert_prompt_history(connection, EMAIL, OUTPUT)
        CREDIT = check_credit(connection, EMAIL)


        