ZOTadd
===

# What & How
ZOTadd allows you to add books and websites to your **Zotero collection** easily. You need to have a Zotero account and have syncing enabled in your desktop app.

For books, the metadata for the assigned ISBN gets extracted using [**isbntools**](https://github.com/xlcnd/isbntools).

For URLs, the metadata gets extracted using [**htmldate**](https://htmldate.readthedocs.io/en/latest/index.html) and [**newspaper3k**](https://newspaper.readthedocs.io/en/latest/).

# Installation
```sh
git clone https://github.com/js-on/zotadd
cd zotadd/
pip3 install -r requirements.txt
```
Set the correct values in *config.json*. You need your library ID and API key to connect to Zotero. See their docs on how to get both.

The first run may take a while, as the *newspaper3k* package needs some NLTK specs. You can manually download the required files by running the following commands in a python shell:

```py
import nltk
nltk.download("punkt")
```

# Usage
- Add URL: `python3 zotadd.py "https://example.com/blog/very-interesting-article"`
- Add Book: `python3 zotadd.py "9876543210123"`
- Add Book by scanning ISBN from webcam: `python3 zotadd.py cam`
- Add PDF: `python3 zotadd.py "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf"` (NSWF due to weak metadata extraction)
- Add PDF from file: `python3 zotadd.py /path/to/file.pdf`

> This is not failsafe. Please check the generated Zotero entries and add the missing information. In case you observe some general problems, please open an issue.

# Note
This is just something I wrote whilst working on my bachelor thesis. There might be bugs. In case you find any unexpected behaviour or failures, open an issue or pull the fixed code ;)

Maybe I'll find some time to review the code and add more functionality, but at the moment, it fits all my needs.
