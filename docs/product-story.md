# photo-toolkit product story

## The problem

Preparing a media collection for an archive or self-hosted photo application often involves several different questions: Which files are duplicates? Which dates came from filenames? Are there empty files? Will renaming an image leave its sidecar behind? A one-off shell command can solve one question while making the next one harder to answer.

`photo-toolkit` offers a common command interface and report structure for those preparation tasks. It is alpha software for technically comfortable archivists, photographers, self-hosters, and developers learning careful filesystem automation. It does not claim a customer base, production scale, measured time savings, or an origin in a specific person's private photo collection.

## A hypothetical archive preparation story

Imagine Morgan, a fictional family archivist, preparing **copies** of a collection for a new photo server. Some filenames contain good timestamps, some scanned images have incorrect years, and several exports contain exact duplicates. Morgan first wants evidence, not a bulk destructive cleanup.

Before using a common workflow, Morgan runs separate scripts and manually remembers which paths changed. In a toolkit demonstration, Morgan inventories a disposable staging folder, creates a hash manifest, and reviews date warnings. A plan spells out proposed source and destination names, including sidecars. Applying without `--execute` leaves the media unchanged. After reviewing a synthetic plan, Morgan explicitly executes a move and keeps the report.

If a destination already exists, the execution log records the actual suffixed filename. Undo can then reverse supported completed moves without treating preview rows as changes. This is an intended workflow illustrated with a fictional person; it is not evidence that the tool has safely processed any real archive.

## Concrete value and its limits

| Need | Implemented help |
| --- | --- |
| Inspect before changing | Dry-run defaults and CSV/JSON/text run reports |
| Explain a rename | Date-source fields and reviewable source/destination plans |
| Avoid counting “similar” as identical | Exact SHA-256 duplicate grouping |
| Keep common metadata companions nearby | Sidecar and same-stem Live Photo heuristics |
| Recover simple moves | Conservative undo of completed supported actions |
| Notice partial failures | Error CSVs and nonzero CLI status for recorded errors |

The implementation is in [commands](../photo/commands), [operations.py](../photo/core/operations.py), and [reports.py](../photo/core/reports.py). [Tests](../tests/test_toolkit.py) use temporary synthetic fixtures to prove dry-run and recovery behavior.

The tool cannot judge sentimental value, guarantee an importer will accept every file, restore removed metadata, or undo deletion. It does not detect perceptual duplicates, preserve all conversion metadata, or offer atomic multi-file transactions. File aliases and concurrent writers can undermine naive path assumptions. Backups and copies remain central to responsible use; the tool is not a substitute for them.

## 60–90 second demo narration

“photo-toolkit is an alpha command-line toolbox for inspecting and preparing copies of media before import or archiving. This demonstration uses synthetic files in a temporary folder, not anyone's photo library.

“I start with verify and hash. The reports show file sizes, date sources, and exact duplicate fingerprints. Next I generate a move plan for a timestamped image and its sidecar. The JSON makes the source and destination paths explicit. Applying that plan normally is only a preview, so the original files are still there.

“After review, I add execute. Now the execution report records which changes actually completed. If a destination already existed, it records the actual suffixed destination. That detail matters because undo must reverse the file that moved, not an unrelated file at the original proposed name. Previewed and failed operations are excluded from undo.

“This project teaches cautious filesystem automation: separate inspection from execution, preserve evidence, and admit partial failures. Metadata writes, conversions, and deletions have different recovery limits. The full manual explains those limits and includes failure labs so a maintainer can reason about them before handling important media.”

Read the [technical manual](technical-manual.md) for exact commands, contracts, debugging steps, and extension exercises with solutions.
