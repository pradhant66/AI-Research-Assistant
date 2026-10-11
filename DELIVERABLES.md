# HW1 deliverables checklist

Due October 10, 2026 at 11:59 PM. The application is 60% and the reflection is 40% of the homework grade. Confirm current Brightspace instructions before submission.

You will perform IDE, local environment, and Git/GitHub setup steps manually when I provide instructions. Administrative coordination and those manual steps are excluded from the coding-agent reflection log.

## Application workflow

- [x] Search papers by keyword or topic through an external API; show title, authors, year, abstract, and a paper link when available. Verified in browser screenshots on Oct 7.
- [x] Save a search result to a local database; browse saved papers after refresh and restart. Verified at port 5050 after a full restart on Oct 7.
- [x] Upload a PDF; extract and display title, authors, year, and abstract; retain the paper locally. Verified with two PDFs and corrected review pages on Oct 7.
- [x] Generate an LLM summary grounded in the selected paper's content. Verified in browser for `Attention Is All You Need` on Oct 7; the regenerated plain-text presentation was also verified.
- [x] Ask a natural-language question and get an answer grounded in the selected paper's content. Verified for the Transformer evaluation datasets on Oct 7 and for BEiT's pre-training and ImageNet results on Oct 10; answers were checked against the PDFs.
- [x] Offer View PDF for locally stored papers and for saved search results with an available PDF URL. Isolated route and template checks passed on Oct 10; browser retest pending.
- [x] Verify the complete workflow through the graphical interface. Search, save, persistent library, upload, summary, and Q&A were shown in browser screenshots.
- [x] Keep credentials out of the repository. The key is read from the environment; `.env` and local data are ignored, and a source-file scan found no embedded Gemini key pattern.

## GitHub repository

- **Owner: you.** Set up and manage the repository and GitHub manually, including commits, pulls, and pushes. I will tell you when each action is useful and provide the steps. I will not run Git or access GitHub for this assignment.
- [x] Complete local source code and dependency/configuration files; all required application actions have been browser-verified.
- [x] README with setup and run instructions, major features, and application structure.
- [x] GitHub repository link ready for Brightspace: https://github.com/pradhant66/AI-Research-Assistant (user confirmed first push to `main` on Oct 7).

## Demo video

User reports that the exported video has been reviewed, includes the BERT author correction, and demonstrates removing Adam from the library. The video file has not been inspected by the agent; the checks below reflect the user's report.

- [x] Show a paper search.
- [x] Show saving a paper to the library.
- [x] Show a PDF upload.
- [x] Show a generated paper summary.
- [x] Show at least one question about a paper and its answer.
- [x] Export and review the short video.

## Reflection report

Draft started at `../HW1_REFLECTION_DRAFT.md`. The required Codex interaction screenshots and a final personal review are still needed.

- [ ] Identify the coding agent and explain how it was used throughout development.
- [ ] Describe where it was especially useful, with specific examples.
- [ ] Describe incorrect, incomplete, or unsatisfactory output and how it was corrected.
- [ ] Include screenshots showing the relevant prompt, visible intermediate output if any, proposed solution, follow-up instructions, and improved result.
- [ ] Explain how much code required personal inspection, modification, or debugging.
- [ ] Explain lessons about communicating with and controlling the agent.
- [ ] Check claims against the work log and actual evidence.

## Submission

- **Owner: you.** Record the demo and submit the materials manually.
- [ ] Submit repository link, demo video, and reflection on Brightspace before the deadline.
