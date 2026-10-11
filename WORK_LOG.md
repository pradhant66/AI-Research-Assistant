# HW1 coding-agent work log

This log records each user prompt, the visible agent work, checks, corrections, and evidence for the reflection report. Record only reasoning or intermediate steps that are actually visible. Screenshot cues will be given in the chat when evidence is worth capturing.

## Evidence convention

- `No screenshot`: routine planning or administration.
- `Screenshot requested`: capture the prompt and visible output before continuing.
- `Captured`: user has confirmed the screenshot is saved; record its filename here.
- For an agent error, preserve both the flawed result and the follow-up correction. Include the prompt, visible intermediate output if any, proposed change, and resulting behavior.

## Prompt entries

### P001 — Plan HW1
- **User request:** Read the syllabus and detailed HW1 PDF, then plan the assignment project without designing the application in detail.
- **Visible agent work:** Read both PDFs and proposed a dated sequence for implementation, verification, demo, and reflection.
- **Outcome/check:** Confirmed the five required application actions and three submission items; no application code was created.
- **Reflection angle:** The agent helped translate assignment requirements into a workable schedule.
- **Evidence:** No screenshot.

### P002 — Design the work log
- **User request:** Track prompts, deliverables, screenshots, intermediate output, and incorrect or incomplete agent work; discuss the method before starting the log.
- **Visible agent work:** Proposed a short entry per prompt, milestone evidence, and a separate deliverables checklist.
- **Outcome/check:** User continued discussing the evidence workflow before development.
- **Evidence:** No screenshot.

### P003 — Clarify checklist ownership
- **User request:** Ask whether they need to do anything for the deliverables checklist.
- **Visible agent work:** Committed to maintaining the checklist and identifying screenshots; user remains responsible for the demo recording and Brightspace submission.
- **Evidence:** No screenshot.

### P004 — Clarify screenshot timing
- **User request:** Ask when to take each screenshot.
- **Visible agent work:** Defined an explicit `Take screenshot now` cue for a flawed result before correction, the follow-up and improved result, and selected successful agent-assisted milestones.
- **Evidence:** No screenshot.

### P005 — Start the assignment record
- **User request:** Ask whether the log and assignment can start or whether preparation is needed.
- **Visible agent work:** Inspected the local workspace. It contained syllabus/reference files and an unrelated LaTeX file, but no Git repository or HW1 application. Created this log and the deliverables checklist in a new HW1 directory.
- **Outcome/check:** Work can begin in the new directory without editing synced `sources/` files.
- **Evidence:** No screenshot for setup.

### P006 — Plan the application
- **User request:** Give a plan and approach for the HW1 application.
- **Visible agent work:** Checked current official documentation for OpenAlex search and work metadata, Flask and SQLite, PDF text extraction, and the OpenAI Responses API. Proposed a single Python web app, local persistence, full-text grounding for AI features, and a six-step build order in `APP_PLAN.md`.
- **Files changed:** `APP_PLAN.md`, `WORK_LOG.md`.
- **Outcome/check:** Planning only; no application behavior has been implemented or verified yet. The LLM provider remains replaceable if the user prefers another API.
- **Reflection angle:** The agent helped turn the feature list into an architecture and identified the missing-full-text case before implementation.
- **Evidence:** No screenshot needed for this planning step.

### P007 — Check LLM API cost
- **User request:** Ask whether the OpenAI Responses API is free or paid.
- **Visible agent work:** Checked current official OpenAI documentation for Responses API pricing and free test requests. Clarified that the endpoint has no separate fee, while model tokens are normally billed; account-specific free credit cannot be assumed.
- **Files changed:** `APP_PLAN.md`, `WORK_LOG.md`.
- **Outcome/check:** Marked the LLM provider decision as provisional. No API call or charge was made.
- **Reflection angle:** Cost review influenced provider selection before implementation.
- **Evidence:** No screenshot needed.

### P008 — Choose a verified free LLM API
- **User request:** Decide on a verified free API now.
- **Visible agent work:** Compared official pricing and model-access documentation for Gemini, Groq, and Hugging Face. Selected Google's stable `gemini-3.5-flash-lite` for its documented free input/output tier and recommendation for new projects. Noted rate limits and the Free Tier data-use condition.
- **Files changed:** `APP_PLAN.md`, `WORK_LOG.md`.
- **Outcome/check:** Provider selected in the plan. Account-specific access and quota have not yet been checked, and no API call was made.
- **Reflection angle:** The agent identified a cost constraint and revised the original provider choice before implementation.
- **Evidence:** No screenshot needed.

### P009 — Begin implementing the application
- **User request:** Pick up work where planning and provider selection ended.
- **Visible agent work:** Implemented the Flask application, OpenAlex search, SQLite library, PDF upload and best-effort metadata extraction, Gemini summaries and paper questions, user interface, dependency list, local setup instructions, and credential exclusions.
- **Files changed:** `app.py`, `openalex.py`, `pdf_tools.py`, `gemini_service.py`, `templates/`, `static/styles.css`, `requirements.txt`, `.gitignore`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** All four Python source files passed syntax parsing. Live browser, OpenAlex, PDF, and Gemini behavior remain unverified because application dependencies are not installed in this workspace and local IDE setup is user-owned.
- **Problem and correction:** No runtime problem has been observed yet. PDF metadata extraction is heuristic and must be checked on a real paper.
- **Reflection angle:** The agent generated multiple integrated components from the assignment requirements; the next step is human-led execution and review.
- **Evidence:** Screenshot requested after the first successful search/save flow, or immediately if a visible error occurs during local execution.

### P010 — Review first browser result and narrow search
- **User request:** Shared a screenshot of the running library after local setup and saving a search result.
- **Visible agent work:** Reviewed the screenshot. It confirms the app rendered a saved item in My library. The item appears to be a software release record rather than a research paper. Checked OpenAlex's current work-type vocabulary and changed search to include articles, preprints, and conference papers with abstracts.
- **Files changed:** `openalex.py`, `WORK_LOG.md`; copied the supplied screenshot to `report_evidence/P010_unfiltered_saved_result.png`.
- **Outcome/check:** Library rendering and initial save are visually verified. Revised search results were subsequently verified in P011. Persistence across restart still needs user verification.
- **Problem and correction:** The initial unfiltered OpenAlex query could return non-paper records. The revised query filters to paper types and records with abstracts. This correction needs a browser retest.
- **Reflection angle:** The coding agent's first API integration met the basic save flow but produced results outside the intended research-paper scope. Human review of the live UI revealed the issue and prompted a targeted API filter.
- **Evidence:** Captured: `report_evidence/P010_unfiltered_saved_result.png` (before correction). See P011 for revised search evidence.

### P011 — Verify filtered search and paper link
- **User request:** Shared screenshots of a Transformer search and an opened paper link.
- **Visible agent work:** Reviewed the screenshots and confirmed that results now show research papers with authors, year, abstract, and save action. The external link opened an IEEE paper landing page.
- **Files changed:** `DELIVERABLES.md`, `WORK_LOG.md`; copied screenshots to `report_evidence/`.
- **Outcome/check:** The search-result display and paper link are visually verified. The IEEE page is a landing page with access controls; it does not establish that a full PDF is available for LLM analysis. Saving a new paper and persistence after restart remain to be checked.
- **Problem and correction:** The narrower OpenAlex query appears to have corrected the non-paper results seen in P010. No new code change was needed.
- **Reflection angle:** A follow-up browser check showed how a targeted API filter improved result relevance while preserving the search workflow.
- **Evidence:** Captured: `report_evidence/P011_filtered_search_results.png`, `report_evidence/P011_paper_link.png` (after correction).

### P012 — Resolve localhost 403 after restart
- **User request:** Reported an HTTP 403 at `127.0.0.1` and supplied terminal output from local setup and server runs.
- **Visible agent work:** Reviewed the terminal output, which showed earlier successful Flask requests and a later restart with no browser request logged. Checked local listeners and found macOS Control Center and Flask both bound to port 5000. Changed the app's default port to 5050 and updated the README.
- **Files changed:** `app.py`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** Port 5050 was free when checked, and `app.py` passed syntax parsing. The browser result on the new port still needs user verification.
- **Problem and correction:** Another service on port 5000 made a port conflict plausible, but the exact source of the browser's 403 was not confirmed. Moving the app's next full start to 5050 reduces that risk.
- **Reflection angle:** Runtime evidence helped distinguish an environment conflict from a code-route bug.
- **Evidence:** Screenshot of the 403 page requested before retry. If including terminal output in the report, crop or redact the Flask debugger PIN.

### P013 — Observe automatic recovery
- **User request:** Shared Flask terminal output and reported that the page began working again without a manual change.
- **Visible agent work:** Read the new `GET /` 200 entry and `Restarting with stat` lines. Explained that Flask's development reloader recovered and kept its original port 5000 until a full stop and restart.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** The home page is confirmed to respond again. The earlier 403 was transient; its precise cause remains unconfirmed. The new default port 5050 is not yet browser-verified.
- **Reflection angle:** The agent revised its diagnosis when new runtime evidence arrived instead of claiming the first explanation was proven.
- **Evidence:** Terminal output supplied in chat; no additional screenshot needed for this observation.

### P014 — Verify library persistence after full restart
- **User request:** Shared a browser screenshot of My library at `127.0.0.1:5050/library` after fully restarting the app.
- **Visible agent work:** Reviewed the screenshot and confirmed previously saved papers still appear on the new port. Updated the deliverables checklist.
- **Files changed:** `DELIVERABLES.md`, `WORK_LOG.md`; copied the screenshot to `report_evidence/P014_library_after_restart.png`.
- **Outcome/check:** Local SQLite persistence after refresh and restart is visually verified. Port 5050 works in the user's browser.
- **Problem and correction:** The port change resolved the observed access issue on the full restart. The exact cause of the earlier transient 403 remains uncertain.
- **Reflection angle:** Running the app exposed an environment issue; checking the terminal and restarting on a free port restored reliable access.
- **Evidence:** Captured: `report_evidence/P014_library_after_restart.png` (after correction and persistence check).

### P015 — Correct PDF extraction after testing two papers
- **User request:** Shared two PDF files and three browser screenshots showing partly incorrect extracted details after upload.
- **Visible agent work:** Compared each PDF's first-page text and layout with the displayed fields. Changed extraction to join title and author lines, use the arXiv identifier or publication header for the year, read the abstract in PDF block order, and stop before Introduction or Scientific Contribution. Added a Re-extract from PDF action on the review page for already uploaded papers.
- **Files changed:** `pdf_tools.py`, `app.py`, `templates/edit.html`, `WORK_LOG.md`; copied the screenshots to `report_evidence/`.
- **Outcome/check:** Direct extraction checks now return the correct two titles, complete author lists, 2023 for LLaMA and 2025 for the journal paper, and clean abstract sections. A temporary-database browser-route test confirmed re-extraction updates an existing record. The user's browser retest remains pending.
- **Problem and correction:** The first heuristic selected a journal page header as a title, treated RESEARCH/Open Access as authors, took 2022 from a citation in the LLaMA paper, and interleaved two text columns in its abstract. The PDF layout and arXiv identifier gave more reliable cues.
- **Reflection angle:** The agent's initial PDF feature was incomplete despite working end to end. Testing against two real papers and comparing the result with source pages exposed several separate heuristic failures; the user review form and re-extraction action support human correction.
- **Evidence:** Before screenshots captured as `report_evidence/P015_journal_extraction_before.png`, `report_evidence/P015_journal_abstract_before.png`, and `report_evidence/P015_llama_extraction_before.png`. Ask the user to capture both corrected edit pages after clicking Re-extract from PDF.

### P016 — Verify corrected PDF details in the browser
- **User request:** Shared browser screenshots of the two re-extracted papers.
- **Visible agent work:** Compared the displayed title, authors, year, and abstract with the supplied PDFs and the corrected extractor's direct results. Stored the screenshots with the before evidence and updated the deliverables checklist.
- **Files changed:** `WORK_LOG.md`, `DELIVERABLES.md`; copied screenshots to `report_evidence/`.
- **Outcome/check:** The journal paper shows its title, four authors, 2025, and an abstract ending before Scientific Contribution. LLaMA shows its title, 2023, and a clean abstract. The author field is visually clipped in the screenshot, but the direct extraction check in P015 returned the full 14-author list.
- **Problem and correction:** The browser retest confirms the P015 correction in the running app. No additional code change was needed.
- **Reflection angle:** A before-and-after comparison on two real PDFs shows how human review caught an incomplete agent-generated extractor and verified its revision.
- **Evidence:** Captured: `report_evidence/P016_journal_extraction_after.png` and `report_evidence/P016_llama_extraction_after.png`.

### P017 — Summary attempt stops at missing API key
- **User request:** Shared screenshots after saving LLaMA details, attempting Generate summary, and viewing the library.
- **Visible agent work:** Reviewed the screenshots and traced the displayed error to the application's missing-key check in `gemini_service.py`. Verified the selected Gemini model still has a documented Free Tier. Stored the screenshots as evidence.
- **Files changed:** `WORK_LOG.md`; copied screenshots to `report_evidence/`.
- **Outcome/check:** LLaMA's complete author list, corrected year, and abstract are visible on its saved detail page, and both uploaded papers appear in the library. The summary did not run because this local app process has no `GEMINI_API_KEY`; Gemini output remains unverified.
- **Problem and correction:** The application reports the missing credential clearly. No code correction is indicated; the next test requires a key in the user's local app environment.
- **Reflection angle:** The UI and error handling make the external-service dependency visible. This distinguishes an untested LLM integration from a failed model response.
- **Evidence:** Captured: `report_evidence/P017_saved_llama_paper.png`, `report_evidence/P017_missing_key_error.png`, and `report_evidence/P017_library_with_uploaded_papers.png`. Capture a successful summary after the key is configured.

### P018 — Clarify links and stored PDFs
- **User request:** Asked whether search and upload save a link or a PDF for each paper.
- **Visible agent work:** Inspected the OpenAlex normalization, database fields, save/upload/import routes, and paper detail template. Explained the different storage behavior for searched and uploaded papers.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Search saves paper metadata plus a landing-page link and an open-access PDF URL when provided; it does not download a PDF at save time. Upload stores the PDF locally plus extracted metadata and text, without an original source link. A searched paper gains a local PDF only after the user imports or attaches one.
- **Reflection angle:** Reviewing the implemented data flow clarified what the app can analyze and what a saved search result alone contains.
- **Evidence:** No screenshot needed for this clarification.

### P019 — Correct extraction for a third PDF layout
- **User request:** Shared the `Attention Is All You Need` PDF and a screenshot showing affiliations in the author field and footnote material in the abstract.
- **Visible agent work:** Compared the PDF's first-page text and line positions with the displayed fields. Updated author extraction to collect names across multiple positioned blocks while skipping affiliations and emails, and updated abstract extraction to stop at contribution footnotes.
- **Files changed:** `pdf_tools.py`, `WORK_LOG.md`; copied the screenshot to `report_evidence/P019_attention_extraction_before.png`.
- **Outcome/check:** Direct extraction now returns the title, all eight authors, 2017, and the abstract ending at “large and limited training data.” It also retained the corrected outputs for the LLaMA and journal PDFs. The user's browser retest of paper 6 remains pending.
- **Problem and correction:** The previous logic treated some affiliations as author names and assumed the abstract ended at a section heading. This PDF has author names arranged in columns and places a long footnote after the abstract instead.
- **Reflection angle:** A third real-world PDF revealed a layout case missed by the first revision; regression checks on all three papers helped preserve earlier fixes.
- **Evidence:** Before screenshot captured as `report_evidence/P019_attention_extraction_before.png`. Ask the user to capture paper 6 after clicking Re-extract from PDF.

### P020 — Decide how general PDF extraction should be
- **User request:** Asked whether every paper will require a separate fix or whether a universal fix is possible.
- **Visible agent work:** Explained that research PDFs have inconsistent layouts and metadata, so no single text rule can guarantee correct fields. Proposed a general extraction pipeline with identifier/metadata lookup where available, layout-based fallback, and the existing human review form.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Design clarification only; no extractor change or new verification in this prompt.
- **Reflection angle:** Testing diverse PDFs changed the approach from patching examples toward layered extraction with explicit uncertainty and human validation.
- **Evidence:** No screenshot needed.

### P021 — Review the PDF processing skill suggestion
- **User request:** Asked whether to use a PDF processing skill mentioned in HW1, with concern about toxic skills.
- **Visible agent work:** Re-read HW1 and inspected the available bundled PDF skill before relying on it. Confirmed that HW1 lists skill search and installation as an optional example of coding-agent use, not an application requirement. The skill provides an agent workflow for inspecting and verifying PDFs; it is not a runtime metadata extractor for the Flask app.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** No external skill was installed or executed. The bundled skill's PDF inspection guidance can support further parser work while the app continues to use its declared Python dependencies.
- **Reflection angle:** The agent treated a suggested skill as untrusted until its instructions and scope were inspected, then separated development guidance from code the application needs at runtime.
- **Evidence:** No screenshot needed.

### P022 — Identify the inspected PDF skill precisely
- **User request:** Asked which PDF skills were inspected.
- **Visible agent work:** Clarified that only the bundled `pdf:pdf` skill's `SKILL.md` was read; no third-party skill or package was inspected or installed for this purpose.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** The prior statement about skill inspection applies only to that one instruction file, not to a wider security audit of PDF tools.
- **Evidence:** No screenshot needed.

### P023 — Clarify Google AI Pro and API model choice
- **User request:** Asked whether a Google AI Pro subscription grants free API access to newer models.
- **Visible agent work:** Checked current official Google subscription, Gemini API billing, key, and model-pricing documentation. Confirmed that an API key belongs to a project with its own billing tier. Google's Free Tier currently lists several Flash-family models, including `gemini-3.6-flash`; the current Pro Preview API model does not list free standard API usage.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** No model or code change. The app still uses `gemini-3.5-flash-lite`; the user has not yet tested a summary with an API key.
- **Reflection angle:** Provider choice remained evidence-based: the subscription name alone did not establish API pricing or access, so the agent checked the specific model and project tier.
- **Evidence:** No screenshot needed for this clarification.

### P024 — Expose a safe Gemini failure category
- **User request:** Reported the app's generic “Gemini could not complete this request” message after setting up a key.
- **Visible agent work:** Checked the installed Google GenAI client's error fields and Google's API troubleshooting guidance. Changed the app to pass `GEMINI_API_KEY` explicitly and display a safe status-specific message for request, permission, billing, model, quota, and temporary service errors without showing the key or raw API response.
- **Files changed:** `gemini_service.py`, `WORK_LOG.md`.
- **Outcome/check:** Mocked success and multiple API-error cases passed. The actual Gemini failure category remains unknown until the user retries in the browser; no successful summary or question answer has been verified yet.
- **Problem and correction:** The original catch-all message hid the error status and prevented targeted debugging. The revised message should identify the next action after one retry.
- **Reflection angle:** A broad error handler made live integration hard to diagnose; improving feedback was necessary before changing models or credentials.
- **Evidence:** User reported the message in chat. Screenshot of the old error requested; capture the revised error or successful summary after retry.

### P025 — Narrow the remaining Gemini failure
- **User request:** Reported the revised message “Could not connect to Gemini” after a live summary attempt.
- **Visible agent work:** Recognized that the fallback handler also covered non-network exceptions. Changed it to report the stage of failure and exception class without displaying raw exception details, paper content, or credentials. Checked the diagnostic behavior with mocked exceptions.
- **Files changed:** `gemini_service.py`, `WORK_LOG.md`.
- **Outcome/check:** The real failure cause is still unknown until the user retries and shares the new safe label. No successful summary has been verified.
- **Problem and correction:** The previous fallback incorrectly suggested an internet issue for every unexpected exception. The new label distinguishes client creation, request submission, and response reading.
- **Reflection angle:** Better observability was needed before making another speculative API or model change.
- **Evidence:** User reported the error text in chat; capture the next precise error or successful summary.

### P026 — Verify Gemini summary and improve its display
- **User request:** Shared two screenshots showing a generated summary for `Attention Is All You Need`.
- **Visible agent work:** Confirmed that the live Gemini request completed and the summary was saved on the paper page. Noted that the UI displayed Markdown markers and LaTeX literally. Added an instruction for plain-text model output and plain section headings, then checked the outgoing prompt without making another API call.
- **Files changed:** `gemini_service.py`, `DELIVERABLES.md`, `WORK_LOG.md`; copied the screenshots to `report_evidence/`.
- **Outcome/check:** Summary generation from the uploaded paper's extracted text is browser-verified. The new output format is not yet browser-verified; the existing saved summary remains in its original format until regenerated.
- **Problem and correction:** The model's Markdown/LaTeX output looked unformatted in the plain-text UI. The new prompt asks for readable text without those markers.
- **Reflection angle:** A live success still exposed a usability flaw that static code checks missed. The follow-up uses the screenshot to refine output presentation before the demo.
- **Evidence:** Captured: `report_evidence/P026_summary_success_top.png` and `report_evidence/P026_summary_raw_formatting.png`. Capture the regenerated summary to verify the formatting change.

### P027 — Verify readable summary and paper Q&A
- **User request:** Shared screenshots of the regenerated plain-text summary and an answer to “What datasets were used to evaluate the Transformer?”
- **Visible agent work:** Compared the answer with the supplied `Attention Is All You Need` PDF. The WMT 2014 English-to-German and English-to-French tasks appear on PDF pages 1 and 8, and the Wall Street Journal/Penn Treebank parsing evaluation appears on pages 9–10. Confirmed the summary no longer shows literal Markdown or LaTeX markers. Stored the screenshots, updated the deliverables checklist, and clarified in the README that the API key must be set before launching the full app.
- **Files changed:** `README.md`, `DELIVERABLES.md`, `WORK_LOG.md`; copied screenshots to `report_evidence/`.
- **Outcome/check:** The Q&A answer is grounded in the uploaded paper and gives page references. All five required application actions have now been demonstrated across browser screenshots. A source-file scan found no embedded Gemini key pattern.
- **Problem and correction:** The prompt-only formatting change from P026 resolved the visibly raw model formatting in the regenerated summary.
- **Reflection angle:** The user’s live retest confirmed both a completed integration and an improvement to presentation quality; PDF comparison supplied a concrete check on answer accuracy.
- **Evidence:** Captured: `report_evidence/P027_plain_summary.png` and `report_evidence/P027_question_answer.png`.

### P028 — View uploaded and saved paper PDFs
- **User request:** Asked for a way to view the PDF for uploaded and saved papers.
- **Visible agent work:** Inspected the database fields and library/detail templates. Added an inline PDF route for locally uploaded, attached, or imported files, plus View PDF links on library cards and paper detail pages. Saved search results use their available external PDF URL; when none is available, the library offers the source page instead.
- **Files changed:** `app.py`, `templates/library.html`, `templates/paper.html`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** An isolated Flask client check confirmed that a local PDF opens inline, its links appear on both pages, an external PDF link appears for a saved search result, and missing or out-of-folder files return 404. Browser retest is pending.
- **Reflection angle:** User review revealed that saving and analyzing a paper did not provide a direct way to read its PDF. The correction reuses the stored PDF information while protecting local file access.
- **Evidence:** Screenshot requested: capture the library showing View PDF, then the PDF opened in a browser tab for an uploaded paper. If a saved search result has a PDF URL, capture that link too.

### P029 — Recover from a blocked publisher PDF download
- **User request:** Shared a screenshot showing “Could not download that PDF. Upload it instead.” after clicking Import open-access PDF for `A survey of transformers`.
- **Visible agent work:** Read the saved record and traced its PDF URL to ScienceDirect. A direct request returned HTTP 403, while the paper's arXiv PDF returned HTTP 200 and PDF content. OpenAlex listed both as locations for the saved work. Added a lookup of alternate OpenAlex PDF locations and made import try each link until a valid PDF is downloaded and processed; the successful URL is stored. Preserved the failed-result screenshot.
- **Files changed:** `openalex.py`, `app.py`, `WORK_LOG.md`; copied the screenshot to `report_evidence/P029_import_pdf_blocked_before.png`.
- **Outcome/check:** An isolated Flask check simulated the publisher's 403 followed by a working arXiv copy. The user's browser screenshot then showed a successful import. The saved record now points to arXiv, its local file begins with a PDF signature, and 63,708 characters of paper text are stored. Opening the PDF in the user's browser remains to be confirmed.
- **Problem and correction:** OpenAlex's preferred open-access PDF can still block automated downloads. The original import gave up after that one URL despite other copies being listed for the paper.
- **Reflection angle:** The user's real browser error exposed a difference between an indexed PDF link and an importable file; the follow-up uses the API's alternate locations rather than requiring a paper-specific URL in the code.
- **Evidence:** Captured: `report_evidence/P029_import_pdf_blocked_before.png` and `report_evidence/P029_import_pdf_success_after.png`. Screenshot requested: click View PDF and capture the PDF open in a browser tab.

### P030 — Prevent duplicate papers across upload and search
- **User request:** Reported that saving a searched LLaMA paper created a second library entry even though the paper had already been uploaded.
- **Visible agent work:** Inspected both local records. The uploaded paper had no OpenAlex ID, so the earlier duplicate check missed it. Confirmed identical title, year, extracted text, and PDF bytes. Added matching by normalized title, publication year, and first author for search and upload flows, and made search results show the already-saved state. Backed up the local database, retained the original uploaded record, linked its OpenAlex/source/PDF URLs, and removed the duplicate library row.
- **Files changed:** `app.py`, `README.md`, `WORK_LOG.md`; local database updated with a backup in `instance/`.
- **Outcome/check:** Isolated Flask checks verified cross-source save and upload matching without a second record. The user's library now contains one LLaMA record, preserving its original PDF and extracted text. Browser refresh remains to be confirmed.
- **Problem and correction:** A unique OpenAlex ID prevents duplicate search saves, but uploaded papers lack that ID. A conservative bibliographic match handles this cross-source case.
- **Reflection angle:** Real user activity exposed a gap between API identifiers and locally uploaded files that the initial save workflow did not cover.
- **Evidence:** User report and inspected records establish the before state. Screenshot requested: refresh the library showing one LLaMA entry, then search LLaMA again and capture the Saved in library label.

### P031 — Clarify library links
- **User request:** Asked what Open details, View source, and View PDF mean in the library.
- **Visible agent work:** Explained that Open details goes to the app's saved-paper page for metadata and analysis; View PDF opens a local PDF when stored or an external PDF URL when available; View source opens the external publisher/DOI page when no PDF URL is available. Each library card shows Open details plus one of the other two links.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Clarification only; no application change or browser verification.
- **Evidence:** No screenshot needed.

### P032 — Clarify two links on the paper detail page
- **User request:** Shared a screenshot of a paper detail page showing both View PDF and Open original paper, after asking what the library links mean.
- **Visible agent work:** Recognized that the prior explanation described library cards, while this screenshot showed a different page. Renamed Open original paper to View publication page so the PDF document and the external DOI/publisher page are clearly distinct.
- **Files changed:** `templates/paper.html`, `WORK_LOG.md`; copied screenshot to `report_evidence/P032_ambiguous_paper_links_before.png`.
- **Outcome/check:** The template now labels the two destinations more clearly. Browser refresh is pending.
- **Problem and correction:** The earlier answer omitted the detail page, and its link wording could imply that both links opened the same paper file.
- **Reflection angle:** User screenshots corrected an incomplete explanation and led to clearer navigation labels.
- **Evidence:** Captured: `report_evidence/P032_ambiguous_paper_links_before.png`. No additional screenshot needed unless this is used as a UI wording example in the report.

### P033 — Clarify when PDF import appears
- **User request:** Asked when Import open-access PDF is shown.
- **Visible agent work:** Checked the paper detail template and explained that the button appears only for a saved paper with an external PDF URL and no processed full text. It disappears after successful import or attachment; uploaded papers already have their PDF processed.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Clarification only; no application change.
- **Evidence:** No screenshot needed.

### P034 — Choose a paper for the import workflow
- **User request:** Asked for a paper to test when Import open-access PDF appears.
- **Visible agent work:** Checked current library titles and live OpenAlex search results for an exact query. Selected `BEiT: BERT Pre-Training of Image Transformers` because it is not in the library, appears as the first result for the suggested search phrase, and OpenAlex provides an arXiv PDF URL.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Recommended a search/save/import path for the user to try; live browser outcome pending.
- **Evidence:** Screenshot requested if using this workflow in the demo: search result, saved paper before import showing the button, and the page after import.

### P035 — Suggest a BEiT question for the demo
- **User request:** Asked for a question to ask about the suggested BEiT paper.
- **Visible agent work:** Chose a question about BEiT's pre-training task and its reported ImageNet-1K comparison with DeiT, which can be checked against the paper abstract.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Question supplied for the app's Q&A flow; the user's generated answer is pending.
- **Evidence:** Screenshot requested after the app answers, if this paper is used in the demo or reflection.

### P036 — Explain the BEiT import button state
- **User request:** Asked again when Import open-access PDF appears.
- **Visible agent work:** Checked the local BEiT record. It already has an arXiv PDF URL, a stored local PDF path, and 13,351 characters of extracted paper text, so the import button has disappeared as designed.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Clarified that the button appears after saving a search result with a PDF URL and before importing its content. BEiT has already passed that state.
- **Evidence:** No new screenshot needed; if showing the before state in the report, use a newly saved paper before clicking import.

### P037 — Expand the README for setup and full workflow
- **User request:** Asked for a clearer README that lets another person understand the application structure and run it, including View PDF, View publication page, and Import open-access PDF.
- **Visible agent work:** Checked the current README, dependency list, UI templates, and Gemini integration. Expanded the README with setup and API-key steps, search/save/upload/import/analysis workflows, a table distinguishing similarly named links, file structure, local data storage, and practical limits.
- **Files changed:** `README.md`, `WORK_LOG.md`.
- **Outcome/check:** Reviewed the revised Markdown against the current UI and route conditions. No runtime behavior changed.
- **Reflection angle:** User feedback about unclear navigation exposed a documentation gap; the revised README describes when controls appear and what each one does.
- **Evidence:** No screenshot needed for the README edit. The README itself is the deliverable.

### P038 — Clarify what is sent to Gemini
- **User request:** Asked whether summary and question actions send the whole PDF to the Gemini API.
- **Visible agent work:** Rechecked the Gemini service implementation. Explained that the app stores the PDF locally and sends extracted text, not PDF bytes. Summary processes extracted text in one or multiple chunks within length limits; Q&A selects up to four relevant pages plus page 1, truncating each selected page. Added this data-flow explanation to the README.
- **Files changed:** `README.md`, `WORK_LOG.md`.
- **Outcome/check:** Clarification and documentation update at that point; P040 subsequently changed Q&A to send the complete extracted text for papers within its limit.
- **Reflection angle:** Reviewing the actual request payload clarified the privacy and grounding boundary of the LLM integration.
- **Evidence:** No screenshot needed.

### P039 — Explain which component selects question pages
- **User request:** Asked whether Gemini or the application selects the four relevant pages for Q&A.
- **Visible agent work:** Explained from `gemini_service.py` that the application extracts keywords from the question, ranks pages by keyword occurrence, takes up to four highest-ranked pages, and also includes page 1. Gemini receives only those selected passages and generates the answer.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Clarification of the behavior at that point; P040 subsequently replaced the page-ranking approach with full extracted text for Q&A.
- **Evidence:** No screenshot needed.

### P040 — Send complete extracted text for paper questions
- **User request:** Asked whether the app could send the whole PDF or the text of the whole paper instead of selecting four pages for Q&A.
- **Visible agent work:** Checked official Gemini model and document guidance and inspected local paper-text sizes. Chose complete extracted text rather than PDF binary so existing page markers and processing remain in use. Replaced keyword page ranking with a single Q&A request containing all extracted text up to a conservative 400,000-character limit, with an explicit error for longer papers. Added an on-page disclosure and updated the README.
- **Files changed:** `gemini_service.py`, `templates/paper.html`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** A mocked Gemini call confirmed that pages at the start, middle, and end of a paper are all included; over-limit input initially gave a clear error. P042 subsequently changed the over-limit behavior to a labeled selected-page fallback. All current saved papers fit under the full-text limit. P041 contains the live Gemini/browser retest.
- **Problem and correction:** Keyword ranking could miss evidence phrased differently from the question. Full extracted text removes that retrieval blind spot for papers within the limit, at the cost of larger API input per question.
- **Reflection angle:** The user challenged an implementation shortcut and prompted a code change better aligned with the model's available context and the task of answering from the whole paper.
- **Evidence:** Screenshot requested: ask a question on a saved paper and capture the answer after this change. Do not expose the API key.

### P041 — Verify BEiT answer after full-text Q&A change
- **User request:** Shared a screenshot showing BEiT's answer to the pre-training and ImageNet-1K comparison question.
- **Visible agent work:** Checked the answer against the saved BEiT PDF and extracted text. Masked image modeling is described on pages 1–4. Table 1 on page 7 supports the reported top-1 accuracy comparisons: BEiT-B 83.2 vs DeiT-B 81.8 at 224 resolution, and BEiT384-B 84.6 vs DeiT384-B 83.1 at 384 resolution. Saved the screenshot.
- **Files changed:** `WORK_LOG.md`; copied screenshot to `report_evidence/P041_beit_full_text_answer.png`.
- **Outcome/check:** The live app returned an answer grounded in the saved paper with correct page references and values. The screenshot alone does not prove the full text was in the request; the prompt-capture check in P040 verifies that behavior.
- **Reflection angle:** Combining live UI evidence with a PDF comparison checks the model's answer instead of treating a fluent response as automatically correct.
- **Evidence:** Captured: `report_evidence/P041_beit_full_text_answer.png`.

### P042 — Add a selected-page fallback for very long papers
- **User request:** Asked whether unusually long papers could use the earlier four-page method instead of showing an error.
- **Visible agent work:** Updated Q&A to send complete extracted text when it fits the 400,000-character limit and otherwise rank pages by question keywords, include up to four ranked pages plus page 1, and send bounded excerpts. The returned answer is prefixed with a clear note naming the selected pages. Updated the on-page disclosure and README.
- **Files changed:** `gemini_service.py`, `templates/paper.html`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** A mocked short-paper request contained the full text. A synthetic long-paper request selected page 1 and a relevant final page, omitted unselected pages, and labeled the answer as partial-context. No live long-paper Gemini/browser test has been run.
- **Problem and correction:** The previous limit produced an error even though a useful, narrower answer was possible. The fallback restores that path while making its coverage visible.
- **Reflection angle:** A user challenge improved a boundary case without hiding the fact that long-paper answers may omit relevant evidence.
- **Evidence:** No screenshot needed unless a genuinely long paper is used in the demo; the earlier BEiT full-text answer remains valid.

### P043 — Make the long-paper fallback clear in the README
- **User request:** Asked to include the long-paper Q&A fallback in the README.
- **Visible agent work:** Confirmed the fallback was already mentioned, then made it a separate “What is sent to Gemini” section with bullets for summary, full-text questions, and selected-page questions over the limit.
- **Files changed:** `README.md`, `WORK_LOG.md`.
- **Outcome/check:** Documentation now makes the two Q&A modes and their limits easy to find. No runtime change.
- **Evidence:** No screenshot needed; the README is the deliverable.

### P044 — Interpret a VL-BERT answer
- **User request:** Asked what the app's answer about VL-BERT pre-training data means.
- **Visible agent work:** Checked the saved paper text against the answer. The paper identifies Conceptual Captions as a visual-linguistic corpus and BooksCorpus plus English Wikipedia as a text-only corpus on PDF pages 2 and 6; Conceptual Captions also appears on page 1. Explained the answer in plain language and clarified that the page numbers refer to the paper.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** The cited datasets and page references match the saved paper text. No app change needed.
- **Evidence:** No screenshot needed; the user supplied the answer text.

### P045 — Check whether page references are required
- **User request:** Asked whether the app has to give page numbers in answers.
- **Visible agent work:** Rechecked the assignment PDF. It requires natural-language answers about selected papers based on their content, but does not require page references. Distinguished the assignment requirement from the app's chosen citation feature.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Page references are optional. They help a reader verify claims against the PDF, but should be checked for accuracy.
- **Evidence:** No screenshot needed.

### P046 — Show direct PDF links in search results
- **User request:** Asked whether open-access search results should link to the PDF when available and otherwise link to the paper page.
- **Visible agent work:** Inspected OpenAlex normalization and the search template. The app already stored a PDF URL but showed only a generic paper-page link in search. Added a direct **View PDF** link when a PDF URL is available and kept a separate **View paper page** link. Also used a PDF URL from the primary OpenAlex location when no best open-access location supplies one. Updated the README.
- **Files changed:** `openalex.py`, `templates/index.html`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** A Flask test-client check confirmed that a result with a PDF shows both links, while a result with only a landing page shows the page link. A listed PDF URL may still be unavailable at its host; the page link remains a fallback.
- **Evidence:** Screenshot suggested for the demo: a search result with **View PDF** and **View paper page** visible. No screenshot captured yet.

### P047 — Plan a two-workflow demo video
- **User request:** Asked for a demo sequence showing both search/save/import of an available open-access PDF and direct PDF upload, with summary and question answering in each workflow.
- **Visible agent work:** Matched the proposed sequence to all five assignment demo actions and checked the current paper and upload screens for exact button labels. Recommended using two distinct papers that are not already in the library so the import and new upload states are visible, checking links and PDF extraction before recording, and showing saved-library persistence with a refresh.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** The recording plan covers search, save, upload, summary, and question answering, with two separate full-text paths. Video capture remains with the user.
- **Evidence:** Record the two workflows in the demo video. Screenshots are optional for this planning prompt; capture any metadata extraction mistake and correction separately if it occurs during the upload.

### P048 — Choose concrete demo papers and questions
- **User request:** Asked for a search paper, an upload paper, and questions for both demo workflows.
- **Visible agent work:** Checked the local library to avoid previously saved titles. Queried the live OpenAlex search for “Deep Residual Learning for Image Recognition”; its 2015 arXiv result (W2949650786) has a direct PDF URL, while the similarly titled 2016 result does not. Confirmed the arXiv PDF returns a PDF response. Selected the BERT paper for upload, verified its arXiv PDF is reachable and about 775 KB, and checked both suggested questions against the papers.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** Search demo: 2015 arXiv entry for Deep Residual Learning, with a question about residual connections. Upload demo: BERT (arXiv 1810.04805), with a question about masked language modeling and next sentence prediction. Neither title is currently in the local library. The user still needs to download the BERT PDF and run both flows in the UI.
- **Evidence:** Demo video should show the selected result, import success, upload review, summaries, and answers. No screenshot captured for this planning prompt.

### P049 — Correct an unrelated search abstract after PDF import
- **User request:** Reported that the ResNet search result's abstract described a curated reading list instead of the paper.
- **Visible agent work:** Queried live OpenAlex results and confirmed that the 2015 arXiv record W2949650786 carries the unrelated abstract despite a valid ResNet PDF URL. Extracted the PDF directly and verified that its abstract starts with the paper's actual discussion of deeper networks and residual learning. Updated the import route to replace the saved abstract with the PDF-extracted abstract when available, while retaining existing metadata if extraction finds none. Updated the README and checked the route with a temporary database and mocked PDF download. Found a cleaner demo search choice: the 2014 arXiv record for “Adam: A Method for Stochastic Optimization” (W1522301498), whose first search result has a matching abstract and a reachable small PDF.
- **Files changed:** `app.py`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** The tested import route now replaces an incorrect search abstract with extracted PDF text. Search results still display OpenAlex metadata before import, which can be wrong; choose the verified Adam record for the recording. No live browser import retest has been run for this change.
- **Problem and correction:** The earlier ResNet recommendation checked PDF access but failed to verify the abstract in the exact OpenAlex record. The user caught the mismatch, prompting both metadata correction on import and a revised demo choice.
- **Reflection angle:** External API metadata can be internally inconsistent. Inspect the actual result, report the limitation, and correct data from the source PDF when possible.
- **Evidence:** If available, capture the incorrect ResNet abstract in search and the corrected abstract after import as a before/after pair. No screenshot captured yet.

### P050 — Remove a paper from the library
- **User request:** Asked for a remove-from-library option.
- **Visible agent work:** Added a **Remove from library** button to each library card with browser confirmation. Added a POST-only route that deletes the selected database record and its app-managed PDF if no other record uses that file. It checks the resolved path against the app's upload folder before deleting a file. Updated styling and README.
- **Files changed:** `app.py`, `templates/library.html`, `static/styles.css`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** Temporary-database checks confirmed button rendering, POST deletion, GET rejection, removal of an app-managed PDF, and preservation of a file outside the app's upload folder. The user's existing library was not modified.
- **Reflection angle:** The request added a correction path for unwanted or mistaken saved records while keeping deletion limited to data managed by this app.
- **Evidence:** Screenshot optional: show a disposable paper in the library, click **Remove from library**, and capture the confirmation or the library after removal. Do not remove a paper needed for the demo.

### P051 — Make library removal less visually dominant
- **User request:** Said the large remove button crowded the library card and asked for a delete icon instead.
- **Visible agent work:** Replaced the text button with a small trash SVG aligned to the right of the card actions. Kept the confirmation dialog, added an accessible label and tooltip, styled hover and keyboard focus, and updated the README wording.
- **Files changed:** `templates/library.html`, `static/styles.css`, `README.md`, `WORK_LOG.md`.
- **Outcome/check:** Flask rendered the library with the labeled SVG icon and confirmation form; the former large text button is absent. No deletion was performed on the user's library.
- **Evidence:** Screenshot optional: capture the refreshed library if the icon placement is useful to show a user-directed UI correction in the reflection.

### P052 — Inspect library after icon change
- **User request:** Shared a screenshot of the library after using the new trash icon.
- **Visible agent work:** Checked the screenshot and current local paper record. The success notice confirms a removal action completed, and the small trash icons appear at the right of library cards. The ResNet paper remains saved as record 15 with an external PDF URL, no local PDF path, no extracted full text, and the unrelated OpenAlex abstract; the PDF-import correction has not run on that record yet.
- **Files changed:** `WORK_LOG.md`; copied the screenshot to `report_evidence/P052_library_trash_and_resnet_before.png`.
- **Outcome/check:** The icon layout is visible. The ResNet abstract remains incorrect until its PDF is imported or the user edits its metadata.
- **Evidence:** Captured: `report_evidence/P052_library_trash_and_resnet_before.png`. For a before/after correction example, capture the ResNet detail page after importing its PDF.

### P053 — Choose a later-page question for Adam
- **User request:** Asked for an Adam question whose answer does not stop at page 2.
- **Visible agent work:** Checked the official Adam PDF's experiments section. Selected a question about the CIFAR-10 convolutional-network experiment, where the paper compares Adam, AdaGrad, and SGD with momentum and discusses Adam's layer-wise learning-rate advantage on PDF page 7.
- **Files changed:** `WORK_LOG.md`.
- **Outcome/check:** The question requires evidence from the experiment section rather than only the abstract or opening method description. The app answer has not yet been run or checked.
- **Evidence:** During the demo, capture the question and answer if the response cites the later experiment page; verify its claims against the PDF.

### P054 — Record demo metadata corrections and library removal
- **User report:** During the demo, changed Adam's year from 2014 to 2015, removed “Google AI Language” from the uploaded BERT authors, saved the corrected BERT details, and deleted Adam to demonstrate removal from the library.
- **Visible agent work:** Checked the local database: Adam is absent; BERT remains with Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova as authors and year 2018. Checked primary bibliographic sources: Adam's arXiv submission is from 2014 and its conference publication was in 2015; BERT's arXiv submission was in 2018 and its NAACL publication was in 2019.
- **Files changed:** `WORK_LOG.md`, `DELIVERABLES.md`.
- **Outcome/check:** The removal and BERT author correction are reflected in local data. Adam 2015 is a valid conference publication year. BERT 2018 is valid for the uploaded arXiv preprint; 2019 is the conference publication year. The video itself has not been reviewed, so video checklist items remain open.
- **Reflection angle:** The user inspected extracted metadata, corrected affiliation text misread as an author, and handled different preprint versus conference years deliberately.
- **Evidence:** Use the video frames showing the initial metadata, edited fields, saved BERT details, and Adam's removal. If these moments are not visible in the recording, capture still screenshots or note the correction accurately in the report without claiming visual evidence.

### P055 — Start the reflection draft after demo review
- **User request:** Confirmed the BERT correction appears in the reviewed demo video and asked to begin the report.
- **Visible agent work:** Read the assignment deliverables, work log, and saved screenshots. Drafted a first-person reflection covering the agent's role, PDF metadata errors, OpenAlex metadata problems, Gemini formatting, the full-text question change, human inspection, and lessons learned. Kept the draft outside the application repository and marked the exact Codex conversation screenshots still needed.
- **Files changed:** `../HW1_REFLECTION_DRAFT.md`, `DELIVERABLES.md`, `WORK_LOG.md`.
- **Outcome/check:** The draft is ready for the user's review and evidence insertion. Based on the user's confirmation, the demo checklist is marked complete as user-reported; the agent has not inspected the video file. Reflection checklist items remain open until screenshots and final review are complete.
- **Evidence:** Add agent-interaction screenshots for the PDF extraction correction and four-page/full-text discussion; app before/after screenshots are already linked in the draft.

## Future entry template

### P___ — Short title
- **User request:**
- **Visible agent work:**
- **Files changed:**
- **Outcome/check:**
- **Problem and correction:**
- **Reflection angle:**
- **Evidence:** No screenshot / Screenshot requested / Captured: filename
