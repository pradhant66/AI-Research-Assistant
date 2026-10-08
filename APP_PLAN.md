# HW1 application approach

## Goal

Build a small local-first AI Research Assistant that completes all five required user actions: search, save, upload, summarize, and ask questions. Favor a clear end-to-end workflow and reliable demo over optional features.

## Proposed stack

- **One Python web app:** Flask with server-rendered HTML, CSS, and a little JavaScript for a graphical interface and backend routes.
- **Search:** OpenAlex Works API for paper metadata and open-access locations.
- **Storage:** SQLite for the library and paper metadata; local files for uploaded PDFs and extracted text. Both survive restart.
- **PDF processing:** PyMuPDF for page text; metadata extracted from the first pages, with an editable review step when fields are uncertain.
- **LLM:** Google Gemini API with the stable `gemini-3.5-flash-lite` model on its documented Free Tier. Keep the key in a local environment variable and never commit it. Use one server-side integration module so a provider change remains contained.

Google's published pricing lists free input and output tokens for this model, subject to account-specific free-tier rate limits. Do not enable billing for this project without the user's decision. The user's own access and current quota will be checked when they create the key in Google AI Studio. Google says Free Tier content may be used to improve its products, so use only papers that are appropriate to send to that service.

## Critical content rule

Summaries and answers must use extracted paper text. A saved search result with only metadata is not enough. When a searchable paper has an accessible PDF, the app can obtain and process it. If full text is unavailable, the interface asks the user to upload the PDF before enabling summary and Q&A. Answers should show source page numbers and say when the available text does not support an answer.

## Build order and completion checks

1. **Working shell:** App starts and shows Search and Library views. Check that a second person can start it from the README.
2. **Search and save:** Search OpenAlex, display required metadata, save a result, and see it after refresh and restart.
3. **PDF upload:** Accept a PDF, extract text and required metadata, let the user correct uncertain metadata, and show it in the library.
4. **Summary:** Generate a summary from paper text. For long PDFs, summarize sections or chunks and combine them.
5. **Questions:** Select relevant paper passages, ask the LLM with those passages, and show an answer with page references.
6. **Full workflow review:** Exercise all five actions through the UI, handle API failures and missing/empty PDF text, check the README, record demo, and write reflection from the work log.

## Boundaries

- No account system, shared library, or complex frontend build is needed for this homework.
- Text-based PDFs are the first target. Scanned/image-only PDFs should get a clear error unless OCR is added later.
- Public deployment can follow a stable local demo if time allows; the detailed assignment submission asks for a repository link, video, and reflection.

## Manual actions and evidence

The user performs IDE/environment setup and all Git/GitHub actions when given instructions. Those administrative steps are not recorded in the coding-agent reflection log. Agent work on application planning, implementation, debugging, and corrections is recorded. Screenshot cues are given in chat at meaningful evidence points.
