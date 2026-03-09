import requests
import os
from loguru import logger


def download_pdf(url, save_path=None):
    """
    Downloads a PDF file from a URL and saves it to the specified path.
    
    Args:
        url (str): The URL to download from
        save_path (str): The path where the PDF should be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    save_path = save_path or url.split("/")[-1]
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Error requesting page, status code {response.status_code}")
            return False

        # Create directory if it doesn't exist
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            logger.info(f"Creating directory {directory}")
            os.makedirs(directory)
        
        # Save the PDF file
        with open(save_path, 'wb') as file:
            file.write(response.content)
        
        logger.debug(f"PDF successfully saved to: {save_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error requesting page: {e}")
    except IOError as e:
        logger.error(f"Error saving file: {e}")
    except Exception as e:
        logger.error(f"An unknown exception happened while trying to save file: {e}")
    return False
