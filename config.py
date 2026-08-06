"""
Configuration settings for AI Legal Assistant
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CASES_DIR = DATA_DIR / "cases"
DOCUMENTS_DIR = DATA_DIR / "documents"
UPLOADS_DIR = DATA_DIR / "uploads"

# Create directories if they don't exist
for directory in [DATA_DIR, CASES_DIR, DOCUMENTS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application settings
APP_NAME = "AI Legal Assistant"
APP_VERSION = "2.0.0"

# Court types and jurisdictions for India
COURT_TYPES = [
    "Supreme Court of India",
    "High Court",
    "District Court",
    "Sessions Court",
    "Magistrate Court",
    "Civil Court",
    "Family Court",
    "Consumer Court",
    "Labour Court",
    "Tribunal"
]

JURISDICTIONS = [
    "Delhi",
    "Mumbai",
    "Kolkata",
    "Chennai",
    "Bangalore",
    "Hyderabad",
    "Ahmedabad",
    "Pune",
    "Jaipur",
    "Lucknow",
    "Other"
]

CASE_TYPES = [
    "Criminal",
    "Civil",
    "Family",
    "Labour",
    "Consumer",
    "Constitutional",
    "Corporate",
    "Property",
    "Intellectual Property",
    "Taxation",
    "Other"
]

LEGAL_DOMAINS = [
    "Criminal Law",
    "Civil Law",
    "Family Law",
    "Labour Law",
    "Consumer Protection",
    "Constitutional Law",
    "Corporate Law",
    "Property Law",
    "Contract Law",
    "Tort Law",
    "Other"
]

# Document types for checklist
REQUIRED_DOCUMENTS = {
    "Criminal": [
        "FIR Copy",
        "Chargesheet",
        "Witness Statements",
        "Medical Reports",
        "Forensic Reports",
        "Bail Application",
        "Written Statement"
    ],
    "Civil": [
        "Plaint",
        "Written Statement",
        "Affidavit",
        "Evidence Documents",
        "Property Documents",
        "Correspondence",
        "Court Orders"
    ],
    "Family": [
        "Marriage Certificate",
        "Petition",
        "Financial Documents",
        "Custody Documents",
        "Affidavit",
        "Settlement Agreement"
    ],
    "Default": [
        "Case Summary",
        "Supporting Documents",
        "Affidavit",
        "Legal Notice",
        "Evidence",
        "Court Orders"
    ]
}

# Task templates
TASK_TEMPLATES = {
    "Criminal": [
        {"title": "File FIR", "priority": "High", "status": "pending"},
        {"title": "Gather Evidence", "priority": "High", "status": "pending"},
        {"title": "Witness Statements", "priority": "Medium", "status": "pending"},
        {"title": "Bail Application", "priority": "High", "status": "pending"},
        {"title": "Draft Defense", "priority": "Medium", "status": "pending"}
    ],
    "Civil": [
        {"title": "Draft Plaint", "priority": "High", "status": "pending"},
        {"title": "Collect Evidence", "priority": "High", "status": "pending"},
        {"title": "File Suit", "priority": "High", "status": "pending"},
        {"title": "Serve Notice", "priority": "Medium", "status": "pending"},
        {"title": "Prepare Arguments", "priority": "Medium", "status": "pending"}
    ],
    "Default": [
        {"title": "Case Analysis", "priority": "High", "status": "pending"},
        {"title": "Document Collection", "priority": "High", "status": "pending"},
        {"title": "Legal Research", "priority": "Medium", "status": "pending"},
        {"title": "Draft Documents", "priority": "Medium", "status": "pending"},
        {"title": "File Case", "priority": "High", "status": "pending"}
    ]
}
