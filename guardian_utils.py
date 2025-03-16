import os
import logging
import requests
import pandas as pd
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{", datefmt="%Y-%m-%d %H:%M:%S")


def from_guardian_api(
        search_term,
        api_key,
        from_date=None, 
        to_date=None, 
        page = 1,
        page_size = 200,
        show_fields = "body"
        ):
    """
    This function gets data from the search endpoint on theguardianapi website

    Parameters
    ----------
    search_term
        The term you want to search for
    api_key
        Your api key
    from_date
        Return only content published on or after that date (format YYYY-MM-DD)
    to_date
        Return only content published on or before that date (format YYYY-MM-DD)
    page
        Return only the result set from a particular page
    page_size
        The number of items that a page should return
    show_fields
        Add fields associated with the content (e.g body, thumbnail, etc)
        Check the guardianapi for more information
    
    Returns
    -------
    json
        The response from the api    
    """

    BASE_URL = "https://content.guardianapis.com"
    ENDPOINT = "/search"

    params = {
        "q": search_term,
        "api-key": api_key,
        "from-date": from_date,
        "to-date": to_date,
        "page": page,
        "page-size": page_size,
        "show-fields": show_fields
    }

    response = requests.get(url=BASE_URL + ENDPOINT, params=params, timeout=5)
    logging.debug(f"url:: {response.request.url}")

    if response.status_code == 200:
        page_no = response.json()["response"]["currentPage"]
        logging.info(f"Page NO {page_no}:: Request successful")
        return response.json()
    else:
        logging.error(f"Status code: {response.status_code}")
        logging.error(response.json())
        return None
    

def get_total_results(api_resp) -> int:
    """
    Gets the total number of results from the api response

    Parameters
    ----------
    api_resp
        The json response returned by the call to the api
    
    Returns
    -------
    int
        The total number of results
    """
    return api_resp["response"]["total"]


def get_total_pages(api_resp) -> int:
    """
    Gets the total number of pages from the api response

    This is the total nubmer fo pages you have to loop through in order
    to be able to extract all the data based on your search results

    Parameters
    ----------
    api_resp
        The json response returned by the call to the api
    
    Returns
    -------
    int
        The total number of pages
    """
    return api_resp["response"]["pages"]



def get_current_page_no(api_resp) -> int:
    """
    Gets the current page number from the api response

    Parameters
    ----------
    api_resp
        The json response returned by the call to the api
    
    Returns
    -------
    int
        The current page number
    """
    return api_resp["response"]["currentPage"]


def get_articles(api_resp):
    """
    Extracts required information from each article in the api response

    This function gets the current_page_number, date_posted, 
    article_title, article_url and article body from the api response

    Parameters
    ----------
    api_resp
        The json response returned by the call to the api

    Returns
    -------
    List[Dixt]
        A list containing multiple dictionaries which contains information
        about each article

    """
    curr_page_no = get_current_page_no(api_resp)
    results = api_resp["response"]["results"]
    
    logging.info(f"Found {len(results)} results on current page")
    logging.info("Extracting articles")
    
    output = []

    for article in results:
        g = {
            "page_no": curr_page_no,
            "date_posted" : article["webPublicationDate"],
            "article_title" : article["webTitle"],
            "article_url" : article["webUrl"],
            "article_body" : article["fields"]["body"]
        }
        output.append(g)
        
    logging.info("Extraction successful")
    
    return output



def to_csv_file(filename: str, input) -> None:
    """
    Appends extracted results to a CSV file.

    Parameters
    ----------
    filename: str
        The name of the CSV file to append the extracted results.
        If the filename does not have ".csv" suffix, it will be added automatically.

    input:
        The output from the get_articles function (a list of dictionaries).

    Returns
    -------
    None
    """

    # Create folder for extracted files
    output_folder = Path("extracted_files")
    output_folder.mkdir(exist_ok=True)

    # Check that the output folder has .csv suffix
    file = output_folder / filename
    if file.suffix != ".csv":
        file = file.with_suffix(".csv")

    # Create CSV file with headers if it does not exist
    if not file.exists():
        logging.info(f"Creating new CSV file: {file.name}")
        cols = input[0].keys()  # Get column names from the first item in the input
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    
    # Append articles to the CSV file
    df = pd.DataFrame(input)
    logging.info(f"Appending {len(df)} articles to {file.name}")
    df.to_csv(file, mode="a", index=False, header=False)
    logging.info(f"Successfully updated {file.name}\n")

    return None
