import json
from typing import Any
from langdetect import detect
from pyzotero import zotero
from bs4 import BeautifulSoup as bs4


def get_conf(key: str) -> Any:
    """Return value from config.json

    Args:
        key (str): Key

    Returns:
        Any: Value
    """
    return json.load(open("config.json", 'r')).get(key, None)


def get_title(data: str) -> str:
    """Get title of website

    Args:
        url (str): Website content

    Returns:
        str: Website title
    """
    soup = bs4(data, "lxml")
    try:
        title = soup.findAll("title")[0].text.strip()
    except:
        title = "Could not extract title"
    return title


def get_language(**kwargs) -> str:
    """Detect language from abstract or title

    Returns:
        str: Return first detected language or an empty string
    """
    for sentence in kwargs.values():
        if sentence:
            return detect(sentence)
    return ""


def get_collection(zot: zotero.Zotero) -> str:
    """Get collection ID from collection name

    Args:
        zot (zotero.Zotero): Zotero session

    Raises:
        KeyError: Throw if collection does not exist

    Returns:
        str: ID of the requested collection
    """
    collections = zot.collections()
    name = get_conf("collection")
    for collection in collections:
        if collection["data"]["name"] == name:
            return collection["key"]
    raise KeyError(f"Could not find collection '{name}'")


def add_to_zotero(data: dict, item_type: str) -> None:
    """Add item to Zotero depending on its type

    Args:
        data (dict): The metadata to be addedd
        item_type (str): The type of the item to be created (book|webpage|document)
    """
    zot = zotero.Zotero(library_id=get_conf("libraryID"), library_type=get_conf("libraryType"),
                        api_key=get_conf("apiKey"))
    match item_type:
        case "book":
            item = zot.item_template("book")
            item["title"] = data["title"]
            item["creators"] = [
                {
                    "creatorType": "author",
                    "name": name
                } for name in data["author"]
            ]
            item["abstractNote"] = data["abstractNote"]
            item["date"] = data["year"]
            item["language"] = data["language"]
            item["accessDate"] = data["accessDate"]
            item["publisher"] = data["publisher"]
            item["collections"] = [get_collection(zot)]
            item["ISBN"] = data["isbn"]
        case "webpage":
            item = zot.item_template("webpage")
            item["title"] = data["title"]
            item["websiteTitle"] = data["title"]
            item["creators"] = [
                {
                    "creatorType": "author",
                    "name": name
                } for name in data["author"]
            ]
            item["abstractNote"] = data["abstractNote"]
            item["date"] = data["date"]
            item["language"] = data["language"]
            item["url"] = data["url"]
            item["accessDate"] = data["accessDate"]
            item["tags"] = [{"tag": tag} for tag in data["tags"]]
            item["collections"] = [get_collection(zot)]
        case "document":
            item = zot.item_template("document")
            item["title"] = data["title"]
            item["date"] = data["date"]
            item["creators"] = [
                {
                    "creatorType": "author",
                    "name": name
                } for name in data["author"]
            ]
            item["abstractNote"] = data["abstractNote"]
            item["url"] = data["url"]
            item["language"] = data["language"]
            item["shortTitle"] = data["shortTitle"]
        case _:
            print(f"[!] Unknown item_type '{item_type}'")
            exit()
    zot.create_items([item])
    print(f"[i] Added item of type {item_type} with title '{item['title']}'")
