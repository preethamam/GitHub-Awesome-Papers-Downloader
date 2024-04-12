import logging
import os
from typing import Dict, List

import requests
from tqdm import tqdm

logging.basicConfig(
    filename="File_Download_Error.log",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    filemode="w+",
    force=True,
)
import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
    }
)

"""
## 2D Diffusion with Pretraining
### Text-to-3D Object Generation
- [DreamFusion: Text-to-3D using 2D Diffusion](https://arxiv.org/abs/2209.14988), Poole et al., Arxiv 2022
- [Magic3D: High-Resolution Text-to-3D Content Creation](https://arxiv.org/abs/2211.10440), Lin et al., Arxiv 2022
### Text-to-3D Scene Generation
- [Text2Room: Extracting Textured 3D Meshes from 2D Text-to-Image Models](https://arxiv.org/abs/2303.11989), Höllein et al., Arxiv 2023
- [SceneScape: Text-Driven Consistent Scene Generation](https://arxiv.org/abs/2302.01133), Fridman et al., Arxiv 2023
- [Compositional 3D Scene Generation using Locally Conditioned Diffusion](https://arxiv.org/abs/2303.12218), Po and Wetzstein, Arxiv 2023

Required format: [2023tr-ax] DreamFusion- Text-to-3D using 2D Diffusion.pdfconda 
"""
README_FILE_PATH = "./papers.txt"
OUTPUT_DIRECTORY = "../All_Papers/"


class FileRecord:
    def __init__(self, fname, p_name, p_url, pdf_url, p_conf, p_year) -> None:
        self.filename = fname
        self.name = p_name
        self.url = p_url
        self.url_pdf = pdf_url
        self.conf = p_conf
        self.year = p_year


def read_source_file(filepath: str) -> List[str]:
    with open(filepath, "r") as f:
        lines = f.readlines()
        return lines


def process_source_file(contents: List[str]) -> Dict:
    metadata = {}
    heading, subheading = None, None
    """
    metadata
    - ## Heading1 (folder)
        - ### Subheading 1 (folder)
            - File 1 (process + rename + fetch)
            - File 2
    """
    for content in contents:
        if content.startswith("## "):
            heading = content.removeprefix("## ").strip()
        elif content.startswith("### "):
            subheading = content.removeprefix("### ").strip()
        elif content.startswith("- "):
            if heading not in metadata:
                metadata[heading] = {}

            if subheading not in metadata[heading]:
                metadata[heading][subheading] = []

            paper = content.removeprefix("- ").strip(" \n").split("), ")
            p_name, p_link = paper[0][1:].split("](")

            conf_year = paper[-1].split(", ")[-1].split(" ")
            p_conf, p_year = conf_year[-2], conf_year[-1]

            if "arxiv" in p_link:
                pdf_link = p_link.replace("abs", "pdf") + ".pdf"
            else:
                pdf_link = p_link

            if "arxiv" in p_conf.lower():
                f_name = f'[{p_year}tr-ax] {p_name.replace(":", "-")}.pdf'
            else:
                f_name = f'[{p_year}tr-cp] {p_name.replace(":", "-")}.pdf'

            metadata[heading][subheading].append(
                FileRecord(f_name, p_name, p_link, pdf_link, p_conf, p_year)
            )

    return metadata


def create_dir(dir: str, sub_dir: str) -> str:
    output_path = os.path.join(OUTPUT_DIRECTORY, dir, sub_dir)
    os.makedirs(output_path, exist_ok=True)
    return output_path


def download_file(record: FileRecord, output_path: str):
    try:
        if os.path.exists(os.path.join(output_path, record.filename)):
            print(
                "[SKIPPING] File exists -", os.path.join(output_path, record.filename)
            )
            return

        # Request URL and get response object
        response = requests.get(record.url_pdf, stream=True)

        # isolate PDF filename from URL
        file_path = os.path.join(output_path, record.filename)
        if response.status_code == 200:
            # Save in current working directory
            with open(file_path, "wb") as pdf_object:
                pdf_object.write(response.content)
    except:
        err = ["Downloading Content Failed:", record.name, record.url_pdf]
        logging.debug(err)


def fetch_files(metadata: Dict[str, Dict[str, FileRecord]]) -> None:
    for heading in metadata:
        for subheading in metadata[heading]:
            output_path = create_dir(heading, subheading)
            for record in tqdm(metadata[heading][subheading]):
                download_file(record, output_path)


def main():
    contents = read_source_file(filepath=README_FILE_PATH)
    metadata = process_source_file(contents)
    fetch_files(metadata)


if __name__ == "__main__":
    main()
