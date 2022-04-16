#!/usr/bin/env python3
from newspaper import Article
from htmldate import find_date
from time import strftime
from isbntools import app as ISBN
import sys
import re
from typing import Callable, Dict
import nltk
import tempfile
import requests
import PyPDF2
from methods import *


def analyze_url(url: str) -> None:
    """Retrieve metadata for given URL

    Args:
        url (str): Extracted metadata
    """
    # Download NLTK files; skip if already done.
    nltk.download("punkt")
    print("[i] Analyzing URL ->", url)
    article = Article(url)
    try:
        article.download()
        article.parse()
    except:
        print("[!] Please enter a valid URL")
        exit(1)
    article.nlp()
    try:
        date = article.publish_date.strftime("%d-%m-%Y")
    except:
        date = find_date(article.html)
    data = {
        "title": get_title(article.html),
        "author": article.authors,
        "abstractNote": article.summary,
        "date": date,
        "accessDate": strftime("%Y-%m-%d"),
        "url": url,
        "tags": article.keywords
    }
    data["language"] = get_language(
        abstract=data["abstractNote"], title=data["title"])
    add_to_zotero(data=data, item_type="webpage")


def analyze_isbn(isbn: str) -> None:
    """Retrieve metadata for given ISBN

    Args:
        isbn (str): Extracted metadata
    """
    print("[i] Analyzing ISBN ->", isbn)
    metadata = ISBN.meta(ISBN.isbn_from_words(isbn))
    data = {
        "title": metadata.get("Title"),
        "author": metadata.get("Authors"),
        "publisher": metadata.get("Publisher"),
        "year": metadata.get("Year"),
        "language": metadata.get("Language"),
        "abstractNote": ISBN.desc(isbn),
        "accessDate": strftime("%Y-%m-%d"),
        "isbn": isbn
    }
    add_to_zotero(data=data, item_type="book")


def analyze_pdf(url: str) -> None:
    """Retrieve metadata for the given PDF

    Args:
        url (str): URL to the PDF file
    """
    fname = url[::-1][:url[::-1].find("/")][::-1].split(".pdf")[0]+".pdf"
    print("[i] Analyzing PDF ->", fname)
    content = requests.get(url, allow_redirects=get_conf(
        "allow_redirects"), verify=get_conf("verify")).content
    fp = tempfile.TemporaryFile()
    fp.write(content)
    pdf = PyPDF2.PdfFileReader(fp)
    metadata = pdf.getDocumentInfo()
    date = metadata.get("/CreationDate")
    if not date:
        date = metadata.get("/ModDate")
    try:
        date = date[2:6] + "-" + date[6:8] + "-" + date[8:10]
    except:
        date = None
    try:
        authors = metadata.author.split(",")
    except:
        authors = None
    data = {
        "author": authors,
        "title": metadata.title,
        "abstractNote": metadata.subject,
        "date": date,
        "url": url,
        "language": get_language(subject=metadata.subject),
        "shortTitle": fname
    }
    for k, v in data.items():
        if not v:
            data[k] = input(f"Enter value for '{k}': ")

    if type(data["author"]) != list:
        data["author"] = data["author"].split(",")

    add_to_zotero(data=data, item_type="document")
    fp.close()


def read_from_webcam(*args) -> None:
    """Use webcam to retrieve ISBN from a book and enrich its metadata via `analyze_isbn()`.
    """
    # TODO: Find out, why preview window has disappeared.
    isbn = capture_from_webcam()
    if isbn:
        analyze_isbn(isbn)
    else:
        print("Could not read ISBN from webcam.")
        exit(1)


def help(*args):
    """Print help
    """
    if args:
        print(f"[!] Could not determine type of '{args[0]}'")
    cmd = sys.argv[0]
    print("Usage:")
    print(f"  Add from ISBN:")
    print(f"    Manual input:    {cmd} <isbn>")
    print(f"    Scan via webcam: {cmd} cam")
    print(f"  Add URL:")
    print(f"    Manual input:    {cmd} <url>")
    print(f"  Add PDF:")
    print(f"    From URL:        {cmd} <url containing .pdf>")
    exit(1)


REGEX: Dict[re.Pattern, Callable] = {
    re.compile(r'^http[s]?://.*\.pdf.*$'): analyze_pdf,
    re.compile(r'^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$'): analyze_isbn,
    re.compile(r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$'): analyze_url,
    re.compile(r'^cam$'): read_from_webcam,
    re.compile(r'^.*$'): help
}


def main():
    """Main function
    """
    if len(sys.argv) != 2:
        help()

    query = sys.argv[1]
    for reg in REGEX:
        if reg.match(query):
            REGEX[reg](query)
            break


if __name__ == "__main__":
    main()
