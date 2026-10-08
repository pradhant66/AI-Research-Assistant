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

## Future entry template

### P___ — Short title
- **User request:**
- **Visible agent work:**
- **Files changed:**
- **Outcome/check:**
- **Problem and correction:**
- **Reflection angle:**
- **Evidence:** No screenshot / Screenshot requested / Captured: filename
