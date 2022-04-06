#!/usr/bin/env python3
from newspaper import Article
from htmldate import find_date
from time import strftime
from isbntools import app as ISBN
import sys
import re
from typing import Callable, Dict
from methods import *
import nltk


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


def help(*args):
    if args:
        print(f"[!] Could not determine type of '{args[0]}'")
    print(f"Usage: {sys.argv[0]} <url|isbn>")
    exit(1)


REGEX: Dict[re.Pattern, Callable] = {
    re.compile(r'^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$'): analyze_isbn,
    re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'): analyze_url,
    re.compile(r'.*'): help
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