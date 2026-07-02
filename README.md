# UCIC — Group Email Summarizer & Insights Generator

An automation that ingests group-email conversations, uses an AI model to extract
structured insight from every thread, and presents it in a single interactive dashboard
with a searchable knowledge repository.

Built for the UCIC RPA & AI Automation task. Covers both task segments end to end.
GOOGLE SHEETS LINK WITH DATA:-https://docs.google.com/spreadsheets/d/e/2PACX-1vSwFreIvY-er1Ze6WRyfrTj6hh5gwRVl92_bNqt11TnTUjgXiVoVUqmKk9bsWKqnIYF-ZP1yTUJzkgT/pub?output=csv

---

## What it does

- Reads incoming group emails and normalizes them into a clean schema.
- Groups emails into conversation threads, then sends each thread to an AI model that
  returns a summary, the tasks with probable owner / due date / status, the decisions
  taken, topic tags, a bottleneck flag, and sentiment.
- Writes the results to a Google Sheet on a schedule.
- Visualizes everything in a dashboard: open tasks, tasks by owner, overdue tasks,
  active discussion topics, conversation volume trend, sentiment, and bottlenecks.
- Provides a searchable knowledge repository over historical decisions, lessons and bottlenecks.

---

## Architecture

```
Group emails
     |
     v
n8n pipeline  (Segment 1)
   Schedule  ->  Group by thread  ->  Groq LLM (Llama 3.3 70B)  ->  Extract JSON
     |
     v
Google Sheet  - single source of truth
   Thread_Insights . Tasks . Candidate_Input_Emails
     |
     v
Dashboard + knowledge repository  (Segment 2)
   Static web app, reads the published CSV
```

The pipeline and the dashboard are deliberately decoupled. n8n does the ingestion and
AI extraction and writes to the Google Sheet; the dashboard only reads that sheet and
renders it. No AI runs at view time, so the dashboard is fast and can be hosted as a
static page. The Google Sheet is the hand-off point between the two halves.

---

## Segment 1 - the automation (n8n)

- **Schedule trigger** runs the workflow on an interval, so the summary stays current.
- **Read + normalize** the incoming emails into a consistent schema.
- **Group by thread** - emails are bucketed by thread ID before the AI step. This is
  both more accurate (a task's owner or due date is often stated several replies later)
  and much cheaper (one AI call per thread instead of per email).
- **Groq LLM (Llama 3.3 70B)** is prompted to return strict JSON per thread: summary,
  tasks (with owner, due date, status), decisions, topic tags, bottleneck flag, sentiment.
- **Write to Google Sheet** - thread-level insights are upserted by thread ID
  (idempotent re-runs), tasks are written to their own tab.

## Segment 2 - the dashboard

A single-page dashboard a department head can open and read at a glance.

- **KPI cards** - threads, open tasks, overdue tasks, active topics, bottlenecks.
  Each card is clickable and expands to the underlying rows.
- **Tasks by Owner** - who is carrying the open workload.
- **Overdue Tasks** - driven by an adjustable as-of date.
- **Active Discussion Topics** - by thread count, with bottleneck topics highlighted.
- **Conversation Volume Trend** - emails per day, from the send timestamps.
- **Sentiment mix** and **task status breakdown**.
- **Department filter** applies across every widget.
- **Knowledge repository** - free-text search over summaries, decisions, tags and
  bottlenecks, so historical context is retrievable instantly.

---

## AI usage

- **Model:** Groq running **Llama 3.3 70B** - an open-source model, matching UCIC's
  direction of in-house open-source LLMs.
- **Prompting:** one call per thread, with a strict JSON schema so the output maps
  directly onto the sheet columns without brittle parsing.
- **Design choice:** thread-level (not email-level) analysis - more accurate and far cheaper.

---

## How to run

### The pipeline (n8n)
1. Import the workflow JSON into n8n.
2. Set the Groq credential (Header Auth: Authorization = Bearer <key>).
3. Point the Google Sheets nodes at your sheet.
4. Run once, or let the schedule trigger it.

### The dashboard
The dashboard reads the Google Sheet's tabs published as CSV
(File -> Share -> Publish to web -> CSV, once per tab).

- Serve it locally over http:  python serve.py  (opens at http://localhost:8000),
  or host the HTML on any static host (e.g. GitHub Pages).
- The three CSV links are set at the top of the HTML file.

Serving over http (rather than opening the file directly) is what lets the browser
fetch the Google Sheet CSVs.

---

## Limitations

- Due dates and owners are only as clear as how people write them; vague commitments
  ("early next week") aren't converted to hard dates.
- No cross-channel de-duplication - the same task in email and chat would appear twice.
- Sentiment and bottleneck flags are thread-level, not fine-grained.
- Free-tier API rate limits mean the pipeline paces itself; a production deployment
  would use paid throughput.

## Scaling to 10,000+ emails

- Grouping by thread first keeps AI calls proportional to conversations, not messages.
- Incremental ingestion so each run only pulls new mail.
- A queue with bounded concurrency and retries instead of one long loop.
- Cache unchanged threads so they aren't re-analyzed.
- Move storage from Sheets to a database (e.g. Postgres) as volume grows, with the
  dashboard querying that instead of a spreadsheet.

---

## Files

- n8n workflow JSON - the automation pipeline.
- dashboard.html - the dashboard and knowledge repository.
- serve.py - small local server for running the dashboard over http during development.
- README.md - this file.
