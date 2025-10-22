import logging
import json
import re
from datetime import datetime
from fastapi import HTTPException
import anthropic

from com.mhire.app.config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractAnalyzer:
    def __init__(self):
        try:
            config = Config()
            self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
            self.model = config.model_name
        except Exception as e:
            logger.error(f"Error initializing ContractAnalyzer: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")

    def _normalize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD"""
        if not date_str or date_str.lower() in ['null', 'none', 'n/a', '']:
            return None
        
        try:
            # Remove extra spaces
            date_str = date_str.strip()
            
            # Common date patterns
            patterns = [
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2024-07-01
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 07/01/2024
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # 01-07-2024
                r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2024/07/01
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # Year first
                        year, month, day = groups
                    else:  # Month or day first
                        month, day, year = groups
                    
                    # Create date object and format
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
            
            return None
        except:
            return None

    def _process_analysis_data(self, data: dict) -> dict:
        """Process analysis data to normalize dates and handle nulls"""
        try:
            # Process key_sections for dates
            if 'key_sections' in data:
                for section in data['key_sections']:
                    date_fields = ['contract_start', 'contract_end', 'Notice_Deadline', 'Upcoming_Renewal']
                    for field in date_fields:
                        if field in section and section[field]:
                            normalized = self._normalize_date(str(section[field]))
                            section[field] = normalized
            
            return data
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return data

    async def analyze_contract(self, contract_text: str) -> dict:
        try:
            prompt = f"""Analyze the following contract text and provide a comprehensive analysis in JSON format.

Contract Text:
{contract_text}

Please provide your analysis in the following JSON structure. IMPORTANT: If any field value is not found in the contract, set it to null:

{{
    "document_type": "Type of contract (e.g., Rental Agreement, Employment Contract, Service Agreement)",
    "key_sections": [
        {{
            "section_name": "Name of the section (e.g., Payment Terms, Term Duration, etc.)",
            "contract_start": "Contract start date in YYYY-MM-DD format or null",
            "contract_end": "Contract end date in YYYY-MM-DD format or null",
            "Notice_Deadline": "Notice deadline date in YYYY-MM-DD format or null",
            "Upcoming_Renewal": "Upcoming renewal date in YYYY-MM-DD format or null",
            "contract_value": "Total contract value with currency symbol (e.g., $24000) or null",
            "term_length": "Length of contract term (e.g., 12 months, 2 years) or null",
            "Payment_type": "Payment method (e.g., cash, check, bank transfer) or null",
            "governing_law": "Governing law or jurisdiction or null",
            "location": "Where in document this section is found"
        }}
    ],
    "red_flags": [
        {{
            "issue": "Brief description of the concerning clause",
            "severity": "High/Medium/Low",
            "location": "Where in document",
            "explanation": "Why this is concerning and potential impact"
        }}
    ],
    "suggested_questions": [
        {{
            "question": "Question to ask before signing",
            "reason": "Why this question is important",
            "section": "Related section"
        }}
    ],
    "alternative_wordings": [
        {{
            "original_clause": "The problematic or unclear original text",
            "location": "Where in document",
            "issue": "What's wrong with the original",
            "suggested_wording": "Clearer, safer alternative wording",
            "benefit": "How this protects the signer"
        }}
    ]
}}

CRITICAL RULES:
- Extract ALL dates and convert them to YYYY-MM-DD format
- If a field is not mentioned in the contract, use null (not empty string)
- Create multiple key_sections if there are different important sections
- For contract_value, include currency symbol
- Identify at least 3-5 red flags if present
- Suggest at least 5 important questions
- Provide at least 3 alternative wordings
- Return ONLY valid JSON, no additional text or markdown"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            
            analysis_data = json.loads(json_str)
            
            # Process and normalize dates
            analysis_data = self._process_analysis_data(analysis_data)
            
            return analysis_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
        except Exception as e:
            logger.error(f"Error analyzing contract: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    async def summarize_text(self, text: str) -> str:
        try:
            prompt = f"""Please provide a concise summary of the following text. The summary should:
- Capture the main points and key information
- Be clear and easy to understand
- Be approximately 10-15 sentences long
- Focus on the most important aspects

Text to summarize:
{text}

Provide only the summary, no additional commentary."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = message.content[0].text.strip()
            return summary

        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")