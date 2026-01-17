# 🧠 Psychedelic Practitioners Network (PPN) - Research Portal

## Overview
[cite_start]The **PPN Research Portal** is a secure, searchable knowledge repository designed for verified clinicians to research historical treatment protocols for psychedelic therapies[cite: 3, 5]. [cite_start]It allows practitioners to query anonymous patient outcomes, analyze efficacy trends, and contribute new data to the community[cite: 7].

[cite_start]**Note:** This is a **functional prototype** populated with synthetic (mock) data for demonstration purposes[cite: 138].

## Key Features
* [cite_start]**🔍 Search Engine:** Natural language search for treatments (e.g., "Psilocybin for PTSD in 35-year-old males")[cite: 34].
* [cite_start]**📊 AI Analytics:** Real-time visualization of treatment outcomes and demographic trends[cite: 39].
* [cite_start]**📝 Data Entry:** Standardized intake form to append new anonymous records to the dataset[cite: 146].
* [cite_start]**🛡️ Privacy First:** Strictly anonymous architecture (Patient IDs only, no names)[cite: 106].

## Tech Stack
* **Frontend/Backend:** Python (Streamlit)
* **Database:** CSV (Flat-file storage for prototype simplicity)
* **Visualization:** Altair
* **Deployment:** Streamlit Community Cloud

## How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/cabanavip/ppn-research-portal.git](https://github.com/cabanavip/ppn-research-portal.git)
    cd ppn-research-portal
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## Usage
* [cite_start]**Login:** Use `admin` / `password` for the prototype[cite: 30].
* **Search:** Use the sidebar filters or the main search bar to find protocols.
* **Add Record:** Use the "Add New Record" tab to simulate contributing data (saves to local CSV).

## Project Status
* **Current Version:** v7.0 (Gold Release)
* **Status:** Prototype / User Testing
