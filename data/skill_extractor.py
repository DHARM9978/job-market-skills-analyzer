"""
Extracts structured skill keywords from free-text job descriptions.
Used to backfill the Skills column for Adzuna API-sourced data
(which has no structured skills field — only description text).
"""

import re
import logging

import pandas as pd

from utils.constants import COL_SKILLS, COL_SKILLS_LIST

logger = logging.getLogger(__name__)

# Master skill keyword list — matched case-insensitively with word boundaries
SKILL_KEYWORDS = [
    "Python","Java","JavaScript","TypeScript","C++","C#","Go","Rust","Kotlin",
    "Swift","PHP","Ruby","Scala","R","MATLAB","Perl",
    "React","Angular","Vue.js","Next.js","HTML","CSS","Tailwind CSS","Bootstrap",
    "jQuery","Redux",
    "Django","Flask","FastAPI","Spring Boot","Node.js","Express.js","GraphQL","REST API",
    "SQL","MySQL","PostgreSQL","MongoDB","Redis","Oracle","SQLite","Cassandra",
    "DynamoDB","Snowflake","BigQuery","Elasticsearch",
    "Machine Learning","Deep Learning","TensorFlow","PyTorch","Scikit-learn",
    "Pandas","NumPy","Keras","NLP","Computer Vision","Data Science","Statistics",
    "OpenCV","LLM","Hugging Face",
    "Tableau","Power BI","Excel","DAX","Looker","Qlik","SAS",
    "Data Visualization","ETL","Spark","Hadoop","Kafka","Airflow",
    "AWS","Azure","GCP","Docker","Kubernetes","Jenkins","Terraform","Ansible",
    "CI/CD","Linux","Git","GitHub","GitLab","Nginx","Microservices",
    "Prometheus","Grafana",
    "Android","iOS","Flutter","React Native","SwiftUI",
    "Agile","Scrum","Kanban","JIRA","Product Management","Six Sigma",
    "Stakeholder Management","Risk Management",
    "Figma","Adobe XD","Sketch","UI/UX Design","Photoshop","Illustrator",
    "SEO","Google Analytics","Digital Marketing","Content Marketing","Salesforce",
    "SAP","CRM","Negotiation","Financial Modeling","Accounting","Budgeting",
    "Forecasting","Communication Skills","Leadership","Team Management",
    "Customer Service","Cybersecurity","Penetration Testing","Selenium",
    "Manual Testing","Automation Testing","QA",
]

# Pre-compile all patterns once at import time for speed
_PATTERNS = [
    (skill, re.compile(
        r"(?<![a-zA-Z0-9])"
        + re.escape(skill).replace(r"\ ", r"[\s\-]+")
        + r"(?![a-zA-Z0-9])",
        re.IGNORECASE,
    ))
    for skill in SKILL_KEYWORDS
]


def extract_skills(text: str) -> list:
    """Return the list of known skills found in a block of free text."""
    if not text or not isinstance(text, str):
        return []
    return [skill for skill, pat in _PATTERNS if pat.search(text)]


def enrich_with_skills(df: pd.DataFrame, text_col: str = "Description") -> pd.DataFrame:
    """
    Adds Skills and Skills_List columns derived from a free-text column.
    No-op if the source already has a real, populated Skills column.
    """
    df = df.copy()

    has_real_skills = (
        COL_SKILLS in df.columns
        and df[COL_SKILLS].astype(str).str.strip().ne("").mean() > 0.5
    )

    if has_real_skills:
        logger.debug("Skills column already populated — skipping extraction")
        return df

    if text_col not in df.columns:
        logger.warning("Text column '%s' not found — cannot extract skills", text_col)
        df[COL_SKILLS_LIST] = [[] for _ in range(len(df))]
        df[COL_SKILLS]      = ""
        return df

    logger.info("Extracting skills from '%s' column for %d rows …", text_col, len(df))
    df[COL_SKILLS_LIST] = df[text_col].apply(extract_skills)
    df[COL_SKILLS]      = df[COL_SKILLS_LIST].apply(lambda lst: ", ".join(lst))

    coverage = (df[COL_SKILLS].str.strip() != "").mean() * 100
    logger.info("Skill extraction complete — %.0f%% coverage", coverage)
    return df
