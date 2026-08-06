"""
Case Management System - Data Models and Storage
Hybrid: local JSON + MongoDB (single source of truth)
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict, is_dataclass
from config import CASES_DIR, DOCUMENTS_DIR, UPLOADS_DIR, REQUIRED_DOCUMENTS, TASK_TEMPLATES

try:
    from mongo_service import mongo_service
    MONGO_ENABLED = mongo_service.connected
except Exception:
    MONGO_ENABLED = False
    mongo_service = None


@dataclass
class Task:
    """Represents a legal task"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    priority: str = "Medium"  # High, Medium, Low
    status: str = "pending"   # pending, in_progress, completed
    due_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TimelineEvent:
    """Represents a timeline event"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date: str = ""
    title: str = ""
    description: str = ""
    event_type: str = "general"  # incident, filing, hearing, correspondence, general


@dataclass
class Document:
    """Represents a case document"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    filename: str = ""
    original_name: str = ""
    doc_type: str = ""
    status: str = "uploaded"  # uploaded, processing, analyzed, generated
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    content: str = ""
    file_path: str = ""


@dataclass
class Party:
    """Represents a party in the case"""
    name: str = ""
    role: str = ""  # Plaintiff, Defendant, Witness, etc.
    description: str = ""


@dataclass
class AIInsights:
    """AI-generated insights for a case"""
    case_strength: int = 0  # 0-100
    strength_explanation: str = ""
    themes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    key_arguments: List[str] = field(default_factory=list)
    analyzed_at: Optional[str] = None


@dataclass
class Case:
    """Represents a legal case/matter"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reference_number: str = ""
    case_number: str = ""  # Alias for reference_number for UI compatibility
    title: str = ""
    case_type: str = ""
    legal_domain: str = ""
    status: str = "active"  # active, pending, closed, archived
    
    # Court information
    court_name: str = ""
    court_type: str = ""  # District Court, High Court, Supreme Court, etc.
    jurisdiction: str = ""
    judge_name: str = ""
    court_room: str = ""
    next_hearing: Optional[str] = None
    hearing_date: Optional[str] = None
    
    # Case details
    summary: str = ""
    facts: str = ""
    raw_text: str = ""  # Original uploaded document text
    issues: List[str] = field(default_factory=list)
    
    # Parties
    parties: List[Dict] = field(default_factory=list)
    
    # IPC Sections and Precedents
    ipc_sections: List[Dict] = field(default_factory=list)
    precedents: List[Dict] = field(default_factory=list)
    
    # Documents
    documents: List[Dict] = field(default_factory=list)
    document_checklist: Dict[str, str] = field(default_factory=dict)
    
    # Tasks
    tasks: List[Dict] = field(default_factory=list)
    
    # Timeline
    timeline: List[Dict] = field(default_factory=list)
    
    # AI Insights
    ai_insights: Dict = field(default_factory=dict)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "user"


def generate_reference_number(case_type: str, jurisdiction: str) -> str:
    """Generate a unique reference number for a case"""
    prefix = case_type[:3].upper() if case_type else "GEN"
    jur = jurisdiction[:3].upper() if jurisdiction else "IND"
    year = datetime.now().year
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"{prefix}/{jur}/{year}/{unique_id}"


class CaseManager:
    """Manages case storage and retrieval"""
    
    def __init__(self):
        self.cases_dir = CASES_DIR
        self.cases_dir.mkdir(parents=True, exist_ok=True)
    
    def create_case(self, title: str, case_type: str, legal_domain: str = "General", 
                    jurisdiction: str = "", summary: str = "", **kwargs) -> Case:
        """Create a new case"""
        court_type = kwargs.get('court_type', '')
        case_number = kwargs.get('case_number', '')
        description = kwargs.get('description', '')
        if description and not summary:
            summary = description
        lawyer_email = kwargs.get('lawyer_email', 'user')
        
        case = Case(
            title=title,
            case_type=case_type,
            legal_domain=legal_domain,
            jurisdiction=jurisdiction,
            summary=summary,
            court_type=court_type,
            case_number=case_number,
            created_by=lawyer_email,
            reference_number=generate_reference_number(case_type, jurisdiction)
        )
        
        # Initialize document checklist
        doc_list = REQUIRED_DOCUMENTS.get(case_type, REQUIRED_DOCUMENTS["Default"])
        case.document_checklist = {doc: "missing" for doc in doc_list}
        
        # Initialize tasks
        task_list = TASK_TEMPLATES.get(case_type, TASK_TEMPLATES["Default"])
        case.tasks = [Task(**t).__dict__ for t in task_list]
        
        self.save_case(case)
        return case
    
    def save_case(self, case) -> Dict:
        """Save a case to disk. Accepts Case object or dict."""
        import copy
        
        # Debug logging
        print(f"[DEBUG] save_case called with type: {type(case)}")
        print(f"[DEBUG] Is dict: {isinstance(case, dict)}")
        print(f"[DEBUG] Has __dataclass_fields__: {hasattr(case, '__dataclass_fields__')}")
        
        # Step 1: Convert to dictionary safely
        if isinstance(case, dict):
            case_data = copy.deepcopy(case)
            print(f"[DEBUG] Case is already a dict")
        else:
            # For dataclass objects, use asdict
            print(f"[DEBUG] Converting Case object to dict...")
            try:
                case_data = asdict(case)
                print(f"[DEBUG] asdict() succeeded")
            except Exception as e:
                print(f"[DEBUG] asdict() failed: {e}, trying manual conversion...")
                # Manual conversion if asdict fails
                case_data = {}
                if hasattr(case, '__dataclass_fields__'):
                    for field_name in case.__dataclass_fields__.keys():
                        case_data[field_name] = getattr(case, field_name)
                    print(f"[DEBUG] Manual field extraction succeeded, got {len(case_data)} fields")
                elif hasattr(case, '__dict__'):
                    case_data = copy.deepcopy(vars(case))
                    print(f"[DEBUG] vars() conversion succeeded")
                else:
                    raise TypeError(f"Cannot convert {type(case)} to dict: {str(e)}")
        
        # Step 2: Clean up non-JSON-serializable types
        def clean_value(val):
            """Recursively clean values for JSON serialization"""
            if isinstance(val, uuid.UUID):
                return str(val)
            elif isinstance(val, datetime):
                return val.isoformat()
            elif isinstance(val, dict):
                return {k: clean_value(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [clean_value(item) for item in val]
            else:
                return val
        
        case_data = clean_value(case_data)
        print(f"[DEBUG] Cleaned case_data, type: {type(case_data)}")
        
        # Step 3: Update timestamp
        case_data["updated_at"] = datetime.now().isoformat()
        
        # Step 4: Save to MongoDB (source of truth) first
        if MONGO_ENABLED and mongo_service:
            mongo_service.save_case(case_data)
        
        # Step 5: Write-through to local buffer
        case_file = self.cases_dir / f"{case_data['id']}.json"
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)
        
        print(f"[DEBUG] Case saved successfully to {case_file}")
        
        return case_data
    
    def load_case(self, case_id: str) -> Optional[Case]:
        """Load a case — MongoDB first, local JSON as fallback buffer"""
        data = self.get_case(case_id)
        if data:
            return Case(**data)
        return None
    
    def list_cases(self, lawyer_email: str = None) -> List[Dict]:
        """List all cases — MongoDB first (source of truth), local JSON as fallback"""
        # Try MongoDB first if available
        if MONGO_ENABLED and mongo_service:
            mongo_cases = mongo_service.list_cases(lawyer_email)
            if mongo_cases is not None:  # distinguish [] from None/error
                for c in mongo_cases:
                    c.pop("_id", None)
                return mongo_cases
        
        # Fall back to local JSON files
        cases = []
        for case_file in self.cases_dir.glob("*.json"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Filter by lawyer email if specified
                    if lawyer_email and data.get("created_by") != lawyer_email:
                        continue
                    cases.append(data)
            except Exception:
                continue
        # Sort by updated_at descending
        cases.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return cases
    
    def delete_case(self, case_id: str) -> bool:
        """Delete a case — MongoDB first (source of truth), then local buffer"""
        deleted = False
        # Delete from MongoDB (source of truth) first
        if MONGO_ENABLED and mongo_service:
            deleted = mongo_service.delete_case(case_id)
        # Delete local buffer file
        case_file = self.cases_dir / f"{case_id}.json"
        if case_file.exists():
            case_file.unlink()
            deleted = True
        return deleted
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get a case as a dictionary — MongoDB first (source of truth), local JSON as fallback buffer"""
        # Try MongoDB first (single source of truth)
        if MONGO_ENABLED and mongo_service:
            data = mongo_service.get_case(case_id)
            if data:
                data.pop("_id", None)
                # Write-through to local buffer
                try:
                    case_file = self.cases_dir / f"{case_id}.json"
                    with open(case_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass
                return data
        # Fallback to local JSON buffer
        case_file = self.cases_dir / f"{case_id}.json"
        if not case_file.exists():
            return None
        with open(case_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Update multiple fields in a case — MongoDB first, local buffer second"""
        case_data = self.get_case(case_id)
        if case_data:
            case_data.update(updates)
            case_data["updated_at"] = datetime.now().isoformat()
            # Save to MongoDB (source of truth) first
            if MONGO_ENABLED and mongo_service:
                mongo_service.save_case(case_data)
            # Write-through to local buffer
            case_file = self.cases_dir / f"{case_id}.json"
            with open(case_file, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def update_case_field(self, case_id: str, field: str, value: Any) -> bool:
        """Update a specific field in a case"""
        case = self.load_case(case_id)
        if case and hasattr(case, field):
            setattr(case, field, value)
            self.save_case(case)
            return True
        return False
    
    def add_document(self, case_id: str, document: Document) -> bool:
        """Add a document to a case"""
        case = self.load_case(case_id)
        if case:
            case.documents.append(asdict(document))
            self.save_case(case)
            return True
        return False
    
    def add_task(self, case_id: str, task: Task) -> bool:
        """Add a task to a case"""
        case = self.load_case(case_id)
        if case:
            case.tasks.append(asdict(task))
            self.save_case(case)
            return True
        return False
    
    def update_task_status(self, case_id: str, task_id: str, status: str) -> bool:
        """Update task status"""
        case = self.load_case(case_id)
        if case:
            for task in case.tasks:
                if task.get("id") == task_id:
                    task["status"] = status
                    self.save_case(case)
                    return True
        return False
    
    def add_timeline_event(self, case_id: str, event: TimelineEvent) -> bool:
        """Add a timeline event to a case"""
        case = self.load_case(case_id)
        if case:
            case.timeline.append(asdict(event))
            # Sort timeline by date
            case.timeline.sort(key=lambda x: x.get("date", ""))
            self.save_case(case)
            return True
        return False
    
    def update_document_checklist(self, case_id: str, doc_name: str, status: str) -> bool:
        """Update document checklist status"""
        case = self.load_case(case_id)
        if case and doc_name in case.document_checklist:
            case.document_checklist[doc_name] = status
            self.save_case(case)
            return True
        return False
    
    def update_ai_insights(self, case_id: str, insights: AIInsights) -> bool:
        """Update AI insights for a case"""
        case = self.load_case(case_id)
        if case:
            case.ai_insights = asdict(insights)
            self.save_case(case)
            return True
        return False


# Global instance
case_manager = CaseManager()
