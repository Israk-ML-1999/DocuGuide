from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    contract_text: str

class KeySection(BaseModel):
    section_name: str
    contract_start: Optional[str] = None
    contract_end: Optional[str] = None
    Notice_Deadline: Optional[str] = None
    Upcoming_Renewal: Optional[str] = None
    contract_value: Optional[str] = None
    term_length: Optional[str] = None
    Payment_type: Optional[str] = None
    governing_law: Optional[str] = None
    location: str

class RedFlag(BaseModel):
    issue: str
    severity: str
    location: str
    explanation: str

class Question(BaseModel):
    question: str
    reason: str
    section: str

class AlternativeWording(BaseModel):
    original_clause: str
    location: str
    issue: str
    suggested_wording: str
    benefit: str

class AnalyzeResponse(BaseModel):
    document_type: str
    key_sections: List[KeySection]
    red_flags: List[RedFlag]
    suggested_questions: List[Question]
    alternative_wordings: List[AlternativeWording]

class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str