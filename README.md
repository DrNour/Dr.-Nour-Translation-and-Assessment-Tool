# EduApp – Translation and Localisation Lab

**EduApp** is a Streamlit-based teaching and assessment application for translation, machine translation post-editing, localisation, and classroom analytics. It is designed for university-level translation courses, especially English–Arabic translation and post-editing pedagogy.

The app supports both **student practice** and **instructor management**, including translation exercises, MT post-editing tasks, localisation activities, adaptive feedback, basic analytics, leaderboard gamification, and optional AI-assisted feedback.

---

## Features

### Student Features

* Complete translation tasks
* Post-edit machine translation output
* View automatic metrics after submission
* Receive adaptive feedback based on edit patterns and linguistic checks
* View track-changes-style comparison for post-editing tasks
* Track progress across exercises
* Complete localisation tasks
* Submit reflections on translation and localisation decisions
* View leaderboard ranking

### Instructor Features

* Create, edit, and delete exercises
* Add source texts and optional MT outputs
* Manage sticker, text, and image localisation tasks
* Download individual student submissions as Word files
* Export class metrics as Excel files
* View class-level performance snapshots
* Check AI feedback backend status
* Manage classroom data through local JSON storage

---

## Main Modules

The app contains two main modules:

1. **Core Translation Lab**

   * Translation tasks
   * MT post-editing tasks
   * Student submission tracking
   * Metrics and adaptive feedback
   * Word and Excel exports

2. **Localisation Lab**

   * Translation vs localisation activities
   * Cultural adaptation tasks
   * Date, unit, and currency convention tasks
   * UX and app store localisation tasks
   * Sticker, text, and image localisation tasks

---

## Metrics and Feedback

EduApp calculates several useful classroom analytics:

* **Length Ratio**
  Compares target-text length with source-text length.

* **Edit Counts**
  Counts additions, deletions, and total edits in post-editing tasks.

* **BLEU**
  Available when a reference translation is provided and `sacrebleu` is installed.

* **chrF++**
  Available when a reference translation is provided and `sacrebleu` is installed.

* **BERTScore F1**
  Available when a reference translation is provided and `bert-score` is installed.

* **Time Spent**
  Tracks time spent on each task.

* **Characters Typed**
  Records the number of characters in the submitted text.

The app also provides rule-based feedback on issues such as:

* Missing numbers
* Missing key terms or proper names
* Unbalanced brackets or quotation marks
* Very high or very low length ratio
* Excessive post-editing changes

---

## Optional AI Feedback

EduApp can provide optional AI-generated feedback on student submissions.

The app supports:

* **OpenAI / ChatGPT API**
* **Hugging Face Inference API**

OpenAI is preferred automatically when both are configured.

To enable OpenAI feedback, set:

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

To enable Hugging Face feedback, set:

```bash
HF_API_TOKEN=your_huggingface_token
```

AI feedback is optional. The app continues to work without any AI backend.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

---

## Suggested `requirements.txt`

Use the following as a starting point:

```txt
streamlit
pandas
python-docx
openpyxl
sacrebleu
bert-score
matplotlib
openai
requests
```

Some dependencies are optional. For example, the app will still run without `sacrebleu`, `bert-score`, `matplotlib`, `openai`, or `requests`, but some advanced features may be unavailable.

---

## Instructor Password Setup

For security, the instructor password should not be hard-coded in the app.

You can configure the password using environment variables.

### Option 1: Plain password

```bash
INSTRUCTOR_PASSWORD_PLAIN=your_password
```

### Option 2: SHA-256 hashed password

```bash
INSTRUCTOR_PASSWORD_SHA256=your_sha256_hash
```

### Option 3: Local development mode

```bash
INSTRUCTOR_DEV_MODE=1
```

When development mode is enabled, the fallback password is:

```txt
admin123
```

This should only be used for local testing.

---

## Streamlit Secrets

When deploying on Streamlit Community Cloud, add secrets through the Streamlit dashboard.

Example:

```toml
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-4o-mini"
HF_API_TOKEN = "your_huggingface_token"
INSTRUCTOR_PASSWORD_PLAIN = "your_password"
```

Do not commit API keys or passwords to GitHub.

---

## Data Storage

EduApp stores classroom data locally in the `data/` folder:

```txt
data/
├── exercises.json
├── submissions.json
├── leaderboard.json
├── loc_stickers.json
└── stickers/
```

The app uses JSON files with basic locking and atomic writes.

This is suitable for classroom demos, small-scale use, and local deployment. For larger deployments or multi-user institutional use, a database backend is recommended.

---

## Recommended `.gitignore`

Before pushing to GitHub, create a `.gitignore` file:

```txt
__pycache__/
*.pyc
venv/
.env
data/
.streamlit/secrets.toml
.DS_Store
```

This prevents private submissions, passwords, local data, and environment files from being uploaded.

---

## Project Structure

A suggested structure is:

```txt
eduapp/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
└── data/
    ├── exercises.json
    ├── submissions.json
    ├── leaderboard.json
    ├── loc_stickers.json
    └── stickers/
```

---

## Important Note on Localisation Exercises

The current version includes the main localisation framework and instructor-managed sticker/text/image tasks.

If the full exercise functions for Localisation Lab activities 1–7 are stored separately, they should be added back into the `localisation_lab()` section before deployment.

The placeholder message:

```python
st.info("Localisation exercise functions omitted here for brevity; plug in your existing ones.")
```

should be replaced with the actual exercise functions before using the app with students.

---

## Classroom Use Cases

EduApp can be used for:

* Translation practice
* MT post-editing assessment
* Localisation training
* English–Arabic translation pedagogy
* Data-informed translation teaching
* Student reflection and process-oriented assessment
* Classroom research on editing effort, time, and translation quality

---

## Research and Pedagogical Value

EduApp supports a data-informed approach to translation teaching by combining textual output, process indicators, and feedback. It helps instructors examine not only the final translation product but also indicators of editing effort, time investment, and revision behaviour.

This makes it useful for:

* Post-editing research
* Translation pedagogy
* Localisation teaching
* Classroom-based analytics
* Student self-reflection

---

## Disclaimer

This app is intended for educational and research purposes. Automatic metrics such as BLEU, chrF++, and BERTScore should not be treated as complete measures of translation quality. They are best used alongside instructor judgment, student reflection, and qualitative feedback.

AI-generated feedback is experimental and should be reviewed critically by students and instructors.

---

## Author

Dr. Noureldin Abdelaal
---

## License

Attribution-NonCommercial 4.0 International
```
