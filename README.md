# AI Research Assistant (HW1)

A local web application for finding, organizing, reading, and analyzing research papers. It uses OpenAlex for search, SQLite for the local library, PyMuPDF for PDF processing, and Gemini for summaries and questions.

## Features

- Search scholarly papers through the OpenAlex API.
- View title, authors, year, abstract, and a paper link when available.
- Save papers to a local SQLite library and browse them after restarting the app.
- Remove a paper from the library, including its app-managed PDF copy and analysis text.
- Recognize a previously uploaded paper when it is saved again from search, so the library stays free of that duplicate.
- Upload a text-based PDF and review its extracted title, authors, year, and abstract.
- View locally uploaded PDFs or available PDF links from saved search results.
- Attach or import an open-access PDF for a saved search result.
- Summarize a paper and ask questions using its extracted full text through the Gemini API.

## Run locally

Use Python 3.10 or newer. From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For summaries and questions, create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey). Check your project's access and billing tier there. Set the key in the same terminal **before starting the app**. On macOS with zsh, these commands prompt for the key without showing it:

```bash
read -s "GEMINI_API_KEY?Paste Gemini API key: "
echo
export GEMINI_API_KEY
python app.py
```

To use only search, library, and PDF upload, run `python app.py` without setting a key. Open `http://127.0.0.1:5050` in your browser. The app uses port 5050 because macOS Control Center may already use port 5000. Stop it with **Ctrl+C**. On later runs, reactivate the existing `.venv`; you do not need to recreate it or reinstall dependencies unless they change. A new terminal session needs the Gemini key set again.

Never put the real key in the repository, README, or screenshots. API access and quota depend on the key's Google AI Studio project. Use papers you are allowed to send to the service.

## Using the application

### Search and save

Enter a topic or title on **Search**. Results show the title, authors, publication year, abstract, and available links. **View PDF** opens a direct open-access PDF when OpenAlex supplies a PDF URL; **View paper page** opens the DOI, publisher page, or OpenAlex record. When no PDF URL is available, the page link is still shown. Click **Save to library** to store the paper's metadata and links in SQLite. Saving a result alone does **not** download its PDF. The library remains available after a browser refresh or application restart. If a searched paper matches a previously uploaded paper by normalized title, year, and first author, the app reuses the existing library entry.

### Read and analyze a saved paper

Open **My library**, then choose **Open details**. This opens the paper's page inside the app. The small trash icon on a library card asks for confirmation, then removes the saved record, its summary and extracted text, and any PDF copy managed by the app. It does not delete the original PDF on your computer or a remote paper. For a saved search result without processed full text, the **Add full paper text** section offers:

- **Import open-access PDF** when OpenAlex supplied a PDF URL. The app downloads and processes it, trying other listed open-access copies if the first link fails.
- **Attach PDF** to choose a PDF file from your computer. Use this if no import button appears or the available links cannot be downloaded.

After a PDF is processed, the import/attach section disappears. Importing an open-access PDF replaces the saved abstract with the PDF's extracted abstract when one is found, because search-service metadata can be wrong; review it and use **Edit paper details** if extraction made a mistake. **Generate summary** and **Ask about this paper** become available. Gemini uses the extracted paper text rather than just the metadata. Summary and question prompts request page references; the question prompt also asks Gemini to say when the supplied text does not support an answer. Check important claims against the PDF.

### What is sent to Gemini

The app extracts selectable text locally; it does **not** upload the PDF file itself. The original PDF remains in local storage, but text included in a Gemini request leaves your computer.

- **Summary:** The extracted text is sent in one request for a short paper, or in chunks followed by a request combining their summaries for a longer paper, subject to the summary length limit.
- **Question, up to 400,000 characters:** The question and **complete extracted paper text with page markers** are sent in one request.
- **Question, over 400,000 characters:** The app selects up to four pages based on question keywords, also includes page 1, and sends excerpts from those pages. The answer visibly says that it used selected pages rather than the full paper. It may miss evidence elsewhere in the paper.

Full-text questions can use more API input and time than selected-page questions.

### Upload a paper directly

Choose **Upload PDF** in the navigation bar and select a text-based research PDF up to 16 MB. The app extracts selectable text and proposes a title, authors, year, and abstract. Review the fields, correct mistakes, and click **Save paper details**. **Re-extract from PDF** can retry the metadata extraction, but it replaces the current fields. An uploaded PDF is already processed, so it does not need **Import open-access PDF** before summary or Q&A.

### What each link does

| Location | Link or button | Result |
| --- | --- | --- |
| Search result | **View PDF** | Opens a direct open-access PDF when OpenAlex supplies a PDF URL. |
| Search result | **View paper page** | Opens the external DOI, publisher page, or OpenAlex record. |
| Search result | **Save to library** | Stores metadata and links locally; it does not download a PDF. |
| Library | **Open details** | Opens the saved paper page inside this app for metadata, summary, and questions. |
| Library | **View PDF** | Opens a stored local PDF if available; otherwise opens an external PDF link. |
| Library | **View source** | Opens an external source page when that card has no PDF link. |
| Library | **Trash icon** | After confirmation, removes the saved paper and its app-managed PDF and analysis data. |
| Paper details | **View PDF** | Opens the document; after import or upload, this is the local copy. |
| Paper details | **View publication page** | Opens the external DOI, publisher, or paper landing page. It can appear alongside **View PDF** because it is a different destination. |

An external PDF link may open in a browser but block automatic downloading. If import cannot use any listed copy, attach a PDF you are allowed to use. An alternate open-access copy can be a preprint rather than the publisher's final version.

## Structure

- `app.py`: Flask pages and actions, SQLite persistence, uploads, PDF import, and local PDF viewing.
- `openalex.py`: paper search, metadata parsing, and alternate open-access PDF locations.
- `pdf_tools.py`: PDF text and best-effort metadata extraction.
- `gemini_service.py`: text-grounded summaries and answers through Gemini.
- `templates/`, `static/`: HTML interface and styling.
- `requirements.txt`: Python dependencies.
- `instance/papers.sqlite3` and `instance/pdfs/`: local database and saved PDFs, created when needed and excluded from Git.

The browser sends requests to Flask in `app.py`. Search reads OpenAlex; saving and uploading write to SQLite; PDF processing stores extracted text; summary and question actions send that text or labeled excerpts to Gemini. The app runs locally and does not require a GitHub account to use.

## Limits

- Scanned PDFs without selectable text need OCR and are not supported.
- Metadata extraction is best-effort, so review uploaded paper details.
- A search result requires an imported or uploaded PDF before analysis; metadata alone is insufficient.
- A paper provider may block automatic PDF import; attach a local copy instead.
- The summary flow has a length limit. For Q&A, papers over 400,000 characters use selected-page excerpts; those answers may miss relevant information elsewhere in the paper. Gemini API access and quotas depend on your project.
- This is a local course prototype. It does not provide user accounts or production security controls.
