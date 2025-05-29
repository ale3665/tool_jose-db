# JOSE Metadata Scraper

This tool extracts metadata from the Journal of Open Source Education (JOSE), including article titles, authors, publication dates, and submission status. The data is stored in an SQLite database.

## Features

- Scrapes article metadata from all listing pages of JOSE
- Extracts:
  - Title
  - Authors
  - Publication date
  - Submission status
  - Article URL
- Saves data into SQLite using SQLAlchemy
- CLI interface via Click

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/tool-jose-db.git
cd tool-jose-db
```

2. Install dependencies using Poetry:

```bash
poetry install
```

## Usage

Run the scraper and save output to jose.db (default):

```bash
poetry run python -m src.main
```
Or specify an output path:
```bash
poetry run python -m src.main --output /path/to/output.db
```

### ✅ `LICENSE` (MIT License)

```text
MIT License

Copyright (c) 2025 Alessandra Vellucci

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
