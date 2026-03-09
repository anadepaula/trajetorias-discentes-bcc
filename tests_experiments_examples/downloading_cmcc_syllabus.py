from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
from unidecode import unidecode
from loguru import logger

from src.utils import download_pdf
from concurrent.futures import ThreadPoolExecutor, as_completed


PLANOS_ENSINO_PAGE_URL = "https://cds2.cmcc.ufabc.edu.br/planoensino/files"

def get_page(max_retries=5):
    logger.info(F"extraindo pagina {PLANOS_ENSINO_PAGE_URL}")
    tries = 1
    while True:
        try:
            planos_ensino_response = requests.get(PLANOS_ENSINO_PAGE_URL)
        except requests.exceptions.ConnectionError as e:
            if tries <= max_retries:
                logger.error(f"trying again ({tries}/{max_retries})")
                tries += 1
            else:
                raise e
        else:
            return planos_ensino_response.text

def clean_column_names(og_column):
    return unidecode(og_column).lower().strip()

def assemble_download_link(row):
    return f"{PLANOS_ENSINO_PAGE_URL}/{row['quadrimestre']}_{row['turma']}.pdf"

def get_planos_ensino(save=False):
    planos_ensino_html = get_page()

    if save:
        with open("planos_ensino.html", "w") as f:
            f.write(planos_ensino_html)

    soup = BeautifulSoup(
        planos_ensino_html,
        'html.parser'
    )

    planos_por_quadri = soup.find_all('table', class_='table tabelas_planos')
    quadrimestres = [
        re.search(r"\d+", card.get("id")).group(0)
        for card in soup.find_all("div", class_="card-header")
    ]
    assert len(planos_por_quadri) == len(quadrimestres)

    dfs = pd.read_html(StringIO(str(planos_por_quadri)))

    for quadri, plano in zip(quadrimestres, dfs):
        plano.columns = map(clean_column_names, plano.columns)
        plano["quadrimestre"] = quadri
        plano["download"] = plano.apply(assemble_download_link, axis=1)

    df = pd.concat(dfs, ignore_index=True)

    return df

def download_planos_ensino(df):
    df.sort_values(
        ["quadrimestre", "disciplina", "turma"], 
        ascending=[False, True, True], 
        inplace=True,
    )

    def download_single_plano(row):
        logger.info(f"[{row.quadrimestre}] {row.disciplina} - {row.professor} ({row.turma} - {row.download})")
        if not download_pdf(row.download):
            return row.Index
        return None
    
    indexes_with_errors = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(download_single_plano, row): row for row in df.itertuples()}
        for future in as_completed(futures):
            result = future.result()
            if result is False:
                indexes_with_errors.append(result)
    
    logger.error(
        f"The following files cound not be downloaded: {
            list(df.loc[indexes_with_errors][['quadrimestre', 'turma']].value_counts().reset_index().itertuples())
        }"
    )

    return indexes_with_errors
