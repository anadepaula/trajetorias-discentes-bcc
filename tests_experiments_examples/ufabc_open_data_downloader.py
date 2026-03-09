from bs4 import BeautifulSoup
import requests

from src.utils.file_downloader import download_file

URL_ROOT = 'http://dados.ufabc.edu.br'

def download_all_data(database_url: str):
    response = requests.get(database_url)

    soup = BeautifulSoup(
        response.text,
        'html.parser'
    )

    paragraphs = soup.find_all("p")

    csv_files = []

    for paragraph in paragraphs:
        children = paragraph.find_all()
        if (
            len(children) == 1 
            and children[0].attrs.get("href") is not None 
        ):
            file_path = children[0].attrs.get("href")
            if file_path.strip().endswith("csv"):
                if not file_path.startswith("http"):
                    file_path = URL_ROOT + file_path

                csv_files.append(file_path)

    for file in csv_files:
        download_file(file)

def get_paragraphs(url:str):
    response = requests.get(url)
    soup = BeautifulSoup(
        response.text,
        'html.parser'
    )
    paragraphs = soup.find_all("p")
    return paragraphs


HTTP = "http"
SLASH = "/"
HREF = "href"
CSV = "csv"
PDF = "pdf"

def get_file_type(_file):
    file = _file.strip().lower()
    if file.endswith(CSV):
        return CSV
    if file.endswith(PDF):
        return PDF

def get_links_from_paragraphs(paragraphs):
    paragraphs_with_no_children = sum(
        filter(
            lambda q: len(q)==1, 
            map(
                lambda p: p.find_all(), 
                paragraphs
            )
        ), 
        [],
    )
    raw_links = filter(
        None, 
        map(
            lambda r: r.attrs.get(HREF),
            paragraphs_with_no_children,
        )
    )

    links = []
    for link in raw_links:
        if not link.startswith(HTTP) and link.startswith(SLASH):
            link = URL_ROOT + link
        links.append(link)

    return links
