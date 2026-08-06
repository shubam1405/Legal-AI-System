"""
Seed script — populates PostgreSQL with test users, lawyers, and cases.
Run: python seed.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from backend.database.database import SessionLocal, create_tables
from backend.database.repositories.user_repository import UserRepository
from backend.database.repositories.lawyer_repository import LawyerRepository
from backend.database.repositories.case_repository import CaseRepository

def seed():
    print("Creating tables if not exist...")
    create_tables()

    db = SessionLocal()
    user_repo = UserRepository(db)
    lawyer_repo = LawyerRepository(db)
    case_repo = CaseRepository(db)

    print("Seeding users...")

    # Public user
    try:
        user1 = user_repo.create_user(
            email="rahul.sharma@example.com",
            password="test1234",
            name="Rahul Sharma",
            role="public"
        )
        print(f"  Created user: {user1.email}")
    except Exception as e:
        print(f"  User already exists or error: {e}")
        user1 = user_repo.get_by_email("rahul.sharma@example.com")

    # Lawyer users
    lawyer_users_data = [
        ("aditi.verma@lawfirm.com",   "Aditi Verma"),
        ("rajan.mehta@lawfirm.com",   "Rajan Mehta"),
        ("priya.nair@lawfirm.com",    "Priya Nair"),
        ("suresh.rao@lawfirm.com",    "Suresh Rao"),
        ("kavita.joshi@lawfirm.com",  "Kavita Joshi"),
    ]

    lawyer_users = []
    for email, name in lawyer_users_data:
        try:
            u = user_repo.create_user(email=email, password="test1234", name=name, role="lawyer")
            print(f"  Created lawyer user: {u.email}")
        except Exception:
            u = user_repo.get_by_email(email)
            print(f"  Already exists: {email}")
        lawyer_users.append(u)

    print("\nSeeding lawyer profiles...")

    lawyers_data = [
        {
            "name": "Aditi Verma",
            "bar_council_number": "BAR/DL/2010/1234",
            "phone": "+91-9876543210",
            "firm_name": "Verma & Associates",
            "address": "Connaught Place, New Delhi",
            "specializations": ["Criminal Law", "Constitutional Law"],
            "experience_years": 14,
            "cases_handled": 320,
            "success_rate": 78.5,
            "court_types": ["High Court", "Supreme Court"],
            "languages": ["English", "Hindi"],
            "bio": "Senior criminal lawyer with 14 years of experience in High Court and Supreme Court matters.",
            "rating": 4.8,
            "reviews_count": 95,
        },
        {
            "name": "Rajan Mehta",
            "bar_council_number": "BAR/MH/2015/5678",
            "phone": "+91-9123456789",
            "firm_name": "Mehta Legal Solutions",
            "address": "Bandra West, Mumbai",
            "specializations": ["Family Law", "Civil Law"],
            "experience_years": 9,
            "cases_handled": 210,
            "success_rate": 82.0,
            "court_types": ["Family Court", "Civil Court"],
            "languages": ["English", "Hindi", "Marathi"],
            "bio": "Family law specialist handling divorce, custody, and matrimonial disputes across Maharashtra.",
            "rating": 4.6,
            "reviews_count": 78,
        },
        {
            "name": "Priya Nair",
            "bar_council_number": "BAR/KL/2012/9012",
            "phone": "+91-9988776655",
            "firm_name": "Nair Law Chambers",
            "address": "MG Road, Kochi",
            "specializations": ["Property Law", "Civil Law", "Contract Law"],
            "experience_years": 12,
            "cases_handled": 275,
            "success_rate": 85.0,
            "court_types": ["Civil Court", "High Court"],
            "languages": ["English", "Malayalam", "Hindi"],
            "bio": "Expert in property disputes, land acquisition cases, and civil litigation in Kerala.",
            "rating": 4.9,
            "reviews_count": 112,
        },
        {
            "name": "Suresh Rao",
            "bar_council_number": "BAR/KA/2008/3456",
            "phone": "+91-9876501234",
            "firm_name": "Rao & Partners",
            "address": "Indiranagar, Bengaluru",
            "specializations": ["Corporate Law", "Labour Law", "Intellectual Property"],
            "experience_years": 16,
            "cases_handled": 430,
            "success_rate": 80.0,
            "court_types": ["High Court", "Tribunal", "NCLT"],
            "languages": ["English", "Kannada", "Telugu"],
            "bio": "Corporate and labour law attorney with extensive experience in NCLT proceedings and employment disputes.",
            "rating": 4.7,
            "reviews_count": 134,
        },
        {
            "name": "Kavita Joshi",
            "bar_council_number": "BAR/RJ/2018/7890",
            "phone": "+91-9001122334",
            "firm_name": "Joshi Legal Aid",
            "address": "Vaishali Nagar, Jaipur",
            "specializations": ["Consumer Protection", "Family Law", "Labour Law"],
            "experience_years": 6,
            "cases_handled": 145,
            "success_rate": 76.0,
            "court_types": ["Consumer Forum", "Family Court", "Labour Court"],
            "languages": ["English", "Hindi", "Rajasthani"],
            "bio": "Passionate advocate for consumer rights and family welfare. Specializes in affordable legal aid.",
            "rating": 4.5,
            "reviews_count": 60,
        },
    ]

    for i, data in enumerate(lawyers_data):
        user = lawyer_users[i]
        try:
            existing = lawyer_repo.get_by_user_id(user.id)
            if existing:
                print(f"  Profile already exists for {data['name']}")
                continue
            lawyer = lawyer_repo.create_profile(user_id=user.id, **data)
            print(f"  Created lawyer: {lawyer.name} — {lawyer.specializations}")
        except Exception as e:
            print(f"  Error creating lawyer {data['name']}: {e}")

    print("\nSeeding cases...")

    if user1:
        cases_data = [
            {
                "title": "Landlord Eviction Dispute",
                "case_type": "Civil",
                "legal_domain": "Property Law",
                "summary": "Tenant illegally evicted without proper notice. Security deposit withheld.",
                "status": "active",
            },
            {
                "title": "Workplace Harassment Complaint",
                "case_type": "Labour",
                "legal_domain": "Labour Law",
                "summary": "Employee facing repeated harassment by employer. Seeking remedy under POSH Act.",
                "status": "pending",
            },
        ]

        for c in cases_data:
            try:
                case = case_repo.create_case(created_by_user_id=user1.id, **c)
                print(f"  Created case: {case.title}")
            except Exception as e:
                print(f"  Error creating case: {e}")

    db.close()
    print("\nSeeding complete!")

if __name__ == "__main__":
    seed()
