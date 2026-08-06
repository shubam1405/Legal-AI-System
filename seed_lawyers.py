"""
Seed dummy lawyers into MongoDB for testing
"""
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/legal_assistant")
client = MongoClient(uri)
db_name = uri.rsplit("/", 1)[-1].split("?")[0] if "/" in uri else "legal_assistant"
db = client[db_name]

# Dummy lawyers data
DUMMY_LAWYERS = [
    {
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@legalexperts.in",
        "password_hash": "test_hash_1",  # Plain for testing (shouldn't be used)
        "phone": "+91-9876543210",
        "bar_council": "Delhi Bar Council",
        "firm_name": "Kumar & Associates",
        "address": "New Delhi, India",
        "specialization": ["Criminal", "Bail Applications"],
        "bio": "Senior criminal lawyer with expertise in bail applications and criminal defense",
        "experience_years": 18,
        "cases_handled": 450,
        "success_rate": 78,
        "previous_cases": [
            "State v/s Sharma (2023) - Bail granted",
            "CBI v/s Patel (2022) - Acquittal",
            "Murder case Delhi High Court (2021) - Bail granted"
        ],
        "court_types": ["Supreme Court", "High Court", "District Court"],
        "languages": ["Hindi", "English"],
        "rating": 4.8,
        "reviews_count": 42,
        "created_at": (datetime.now() - timedelta(days=730)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@legalexperts.in",
        "password_hash": "test_hash_2",
        "phone": "+91-9876543211",
        "bar_council": "Mumbai Bar Council",
        "firm_name": "Sharma Legal Solutions",
        "address": "Mumbai, Maharashtra, India",
        "specialization": ["Family Law", "Divorce", "Custody"],
        "bio": "Expert in family law with focus on amicable settlements and custody cases",
        "experience_years": 14,
        "cases_handled": 320,
        "success_rate": 85,
        "previous_cases": [
            "Divorce settlement - High Court Mumbai (2023)",
            "Child custody case (2022) - Joint custody awarded",
            "Maintenance dispute resolution (2021)"
        ],
        "court_types": ["High Court", "Family Court", "District Court"],
        "languages": ["Hindi", "English", "Marathi"],
        "rating": 4.9,
        "reviews_count": 58,
        "created_at": (datetime.now() - timedelta(days=640)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Arjun Patel",
        "email": "arjun.patel@legalexperts.in",
        "password_hash": "test_hash_3",
        "phone": "+91-9876543212",
        "bar_council": "Gujarat Bar Council",
        "firm_name": "Patel & Co. Legal",
        "address": "Ahmedabad, Gujarat, India",
        "specialization": ["Corporate Law", "Contract Law", "M&A"],
        "bio": "Corporate lawyer specializing in mergers, acquisitions, and contract negotiations",
        "experience_years": 22,
        "cases_handled": 580,
        "success_rate": 88,
        "previous_cases": [
            "₹500 Cr acquisition deal (2023)",
            "Joint venture agreement negotiation (2022)",
            "IP licensing agreement (2021)"
        ],
        "court_types": ["Supreme Court", "High Court", "Commercial Court"],
        "languages": ["Hindi", "English", "Gujarati"],
        "rating": 4.7,
        "reviews_count": 51,
        "created_at": (datetime.now() - timedelta(days=850)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Meera Gupta",
        "email": "meera.gupta@legalexperts.in",
        "password_hash": "test_hash_4",
        "phone": "+91-9876543213",
        "bar_council": "Bangalore Bar Council",
        "firm_name": "Gupta Intellectual Properties",
        "address": "Bangalore, Karnataka, India",
        "specialization": ["Intellectual Property", "Patent Law", "Trademark"],
        "bio": "Patent attorney and IP specialist with focus on technology startups",
        "experience_years": 16,
        "cases_handled": 290,
        "success_rate": 82,
        "previous_cases": [
            "Patent filing for AI software (2023)",
            "Trademark infringement settlement (2022)",
            "Software copyright protection suit (2021)"
        ],
        "court_types": ["IP Appellate Board", "High Court", "District Court"],
        "languages": ["Hindi", "English"],
        "rating": 4.6,
        "reviews_count": 35,
        "created_at": (datetime.now() - timedelta(days=560)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Vikram Singh",
        "email": "vikram.singh@legalexperts.in",
        "password_hash": "test_hash_5",
        "phone": "+91-9876543214",
        "bar_council": "Chandigarh Bar Council",
        "firm_name": "Singh Criminal Practice",
        "address": "Chandigarh, India",
        "specialization": ["Criminal", "White Collar Crime", "Cyber Crime"],
        "bio": "Specialized in white collar crime and cyber law with government liaison experience",
        "experience_years": 19,
        "cases_handled": 510,
        "success_rate": 74,
        "previous_cases": [
            "Cyber crime case against hacker group (2023)",
            "Embezzlement defense (2022)",
            "Fraud investigation case (2021)"
        ],
        "court_types": ["Supreme Court", "High Court", "District Court", "Cyber Crime Court"],
        "languages": ["Hindi", "English", "Punjabi"],
        "rating": 4.5,
        "reviews_count": 44,
        "created_at": (datetime.now() - timedelta(days=750)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Sunita Desai",
        "email": "sunita.desai@legalexperts.in",
        "password_hash": "test_hash_6",
        "phone": "+91-9876543215",
        "bar_council": "Maharashtra Bar Council",
        "firm_name": "Desai Property Law",
        "address": "Pune, Maharashtra, India",
        "specialization": ["Property Law", "Real Estate", "Inheritance"],
        "bio": "Property lawyer with extensive experience in real estate disputes and inheritance matters",
        "experience_years": 15,
        "cases_handled": 380,
        "success_rate": 80,
        "previous_cases": [
            "Property title dispute resolution (2023)",
            "Complex inheritance settlement (2022)",
            "Real estate fraud case (2021)"
        ],
        "court_types": ["High Court", "District Court", "Civil Court"],
        "languages": ["Hindi", "English", "Marathi"],
        "rating": 4.7,
        "reviews_count": 47,
        "created_at": (datetime.now() - timedelta(days=670)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Deepak Joshi",
        "email": "deepak.joshi@legalexperts.in",
        "password_hash": "test_hash_7",
        "phone": "+91-9876543216",
        "bar_council": "Delhi Bar Council",
        "firm_name": "Joshi Labor Law Experts",
        "address": "New Delhi, India",
        "specialization": ["Labour Law", "Industrial Relations", "Dispute Resolution"],
        "bio": "Labour lawyer specializing in employee rights and industrial dispute resolution",
        "experience_years": 13,
        "cases_handled": 260,
        "success_rate": 84,
        "previous_cases": [
            "Wrongful termination case - Employee won (2023)",
            "Wage dispute settlement (2022)",
            "Industrial accident compensation (2021)"
        ],
        "court_types": ["Labour Court", "High Court", "District Court"],
        "languages": ["Hindi", "English"],
        "rating": 4.8,
        "reviews_count": 39,
        "created_at": (datetime.now() - timedelta(days=580)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Neha Kapoor",
        "email": "neha.kapoor@legalexperts.in",
        "password_hash": "test_hash_8",
        "phone": "+91-9876543217",
        "bar_council": "Punjab Bar Council",
        "firm_name": "Kapoor Civil Practice",
        "address": "Ludhiana, Punjab, India",
        "specialization": ["Civil Law", "Contract Disputes", "Tort Law"],
        "bio": "Civil litigation specialist with strong track record in contract disputes",
        "experience_years": 12,
        "cases_handled": 310,
        "success_rate": 79,
        "previous_cases": [
            "Contract breach case - Plaintiff won (2023)",
            "Construction dispute resolution (2022)",
            "Negligence compensation suit (2021)"
        ],
        "court_types": ["High Court", "District Court", "Civil Court"],
        "languages": ["Hindi", "English", "Punjabi"],
        "rating": 4.6,
        "reviews_count": 36,
        "created_at": (datetime.now() - timedelta(days=420)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Amit Verma",
        "email": "amit.verma@legalexperts.in",
        "password_hash": "test_hash_9",
        "phone": "+91-9876543218",
        "bar_council": "Uttar Pradesh Bar Council",
        "firm_name": "Verma & Associates Law",
        "address": "Lucknow, Uttar Pradesh, India",
        "specialization": ["Criminal", "Bail Applications", "Appeals"],
        "bio": "Criminal law specialist with experience in appellate litigation",
        "experience_years": 17,
        "cases_handled": 420,
        "success_rate": 76,
        "previous_cases": [
            "Appeal granted - Conviction overturned (2023)",
            "Complex bail hearing (2022)",
            "Criminal appeal in High Court (2021)"
        ],
        "court_types": ["High Court", "District Court", "Sessions Court"],
        "languages": ["Hindi", "English"],
        "rating": 4.7,
        "reviews_count": 43,
        "created_at": (datetime.now() - timedelta(days=610)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Anjali Reddy",
        "email": "anjali.reddy@legalexperts.in",
        "password_hash": "test_hash_10",
        "phone": "+91-9876543219",
        "bar_council": "Telangana Bar Council",
        "firm_name": "Reddy Family Law Center",
        "address": "Hyderabad, Telangana, India",
        "specialization": ["Family Law", "Mediation", "Adoption"],
        "bio": "Family law mediator with expertise in amicable resolutions and adoption cases",
        "experience_years": 11,
        "cases_handled": 240,
        "success_rate": 86,
        "previous_cases": [
            "Successful mediation - Divorce settled amicably (2023)",
            "Adoption case processed (2022)",
            "Child support agreement (2021)"
        ],
        "court_types": ["Family Court", "District Court"],
        "languages": ["Hindi", "English", "Telugu"],
        "rating": 4.9,
        "reviews_count": 52,
        "created_at": (datetime.now() - timedelta(days=490)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "name": "Sandeep Mishra",
        "email": "sandeep.mishra@legalexperts.in",
        "password_hash": "test_hash_11",
        "phone": "+91-9876543220",
        "bar_council": "Jharkhand Bar Council",
        "firm_name": "Mishra Corporate Law",
        "address": "Ranchi, Jharkhand, India",
        "specialization": ["Corporate Law", "Taxation", "GST"],
        "bio": "Corporate and tax lawyer specializing in GST compliance and taxation",
        "experience_years": 14,
        "cases_handled": 350,
        "success_rate": 81,
        "previous_cases": [
            "Complex GST case resolution (2023)",
            "Tax assessment appeal (2022)",
            "Income tax dispute settlement (2021)"
        ],
        "court_types": ["High Court", "Tax Tribunal", "GST Appellate Authority"],
        "languages": ["Hindi", "English"],
        "rating": 4.7,
        "reviews_count": 40,
        "created_at": (datetime.now() - timedelta(days=720)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
]

def seed_lawyers():
    """Insert dummy lawyers into MongoDB"""
    try:
        print("🔗 Connecting to MongoDB...")
        
        # Check if lawyers collection exists
        if "lawyers" not in db.list_collection_names():
            print("📝 Creating lawyers collection...")
            db.create_collection("lawyers")
        
        # Clear existing lawyers (optional - uncomment to reset)
        # db.lawyers.delete_many({})
        # print("🗑️  Cleared existing lawyers")
        
        # Insert dummy lawyers
        print(f" Inserting {len(DUMMY_LAWYERS)} dummy lawyers...")
        
        inserted_count = 0
        for lawyer in DUMMY_LAWYERS:
            try:
                # Check if lawyer already exists
                existing = db.lawyers.find_one({"email": lawyer["email"]})
                if not existing:
                    result = db.lawyers.insert_one(lawyer)
                    print(f"   {lawyer['name']} ({lawyer['specialization'][0]}) - {lawyer['experience_years']} years")
                    inserted_count += 1
                else:
                    print(f"  ⊘ {lawyer['name']} already exists (skipped)")
            except Exception as e:
                print(f"   Error inserting {lawyer['name']}: {str(e)}")
        
        print(f"\n Successfully inserted {inserted_count} lawyers!")
        
        # Display summary
        total_lawyers = db.lawyers.count_documents({})
        print(f"\n📊 Total lawyers in database: {total_lawyers}")
        
        # Show sample
        sample = db.lawyers.find_one({})
        if sample:
            print("\n📋 Sample lawyer record:")
            for key, value in sample.items():
                if key != "_id" and key != "password_hash":
                    print(f"  {key}: {value}")
        
        return True
    
    except Exception as e:
        print(f" Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 Seeding Dummy Lawyers into MongoDB")
    print("=" * 60)
    
    seed_lawyers()
    
    print("\n" + "=" * 60)
