# AI Research Assistant (HW1)

A local web application for finding, organizing, and analyzing research papers.

## Features

- Search scholarly papers through the OpenAlex API.
- View title, authors, year, abstract, and a paper link when available.
- Save papers to a local SQLite library and browse them after restarting the app.
- Upload a text-based PDF and review its extracted title, authors, year, and abstract.
- Attach or import an open-access PDF for a saved search result.
- Summarize a paper and ask questions using its extracted full text through the Gemini API.

## Run locally

Use Python 3.10 or newer. From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For summaries and questions, create a **Free Tier** Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey). Check that the key's project is marked Free; do not enable billing unless you choose to. Set the key in the same terminal **before starting the app**:

```bash
export GEMINI_API_KEY="your-key-here"
python app.py
```

To use only search, library, and PDF upload, skip the `export` line and run `python app.py`. Open `http://127.0.0.1:5050` in your browser. The app uses port 5050 because macOS Control Center may already use port 5000. The app creates its database in `instance/papers.sqlite3`. That local data and `.env` are excluded from Git.

Never put the real key in the repository or share it in chat. Gemini Free Tier requests have account-specific rate limits, and Google may use Free Tier content to improve its products. Use papers you are allowed to send to the service.

## Structure

- `app.py`: web routes and SQLite persistence.
- `openalex.py`: paper search and metadata parsing.
- `pdf_tools.py`: PDF text and metadata extraction.
- `gemini_service.py`: text-grounded summaries and answers.
- `templates/`, `static/`: user interface.
- `instance/`: local database and uploaded PDFs.

## Limits

- Scanned PDFs without selectable text need OCR and are not supported.
- Metadata extraction is best-effort, so review uploaded paper details.
- A search result requires an imported or uploaded PDF before analysis; metadata alone is insufficient.
- This is a local course prototype. It does not provide user accounts or production security controls.
