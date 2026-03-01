"""
PDF Patent Text Extractor - Local extraction (MVP Version)
Uses PyPDF2 and pdfplumber for basic text extraction
Note: Complex layouts may need improvement (marked for future optimization)
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import PDF libraries, provide fallback if not available
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available, falling back to PyPDF2")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available")


class PDFExtractError(Exception):
    """PDF extraction error"""
    pass


class PatentPDFExtractor:
    """
    Extract patent information from PDF files
    MVP: Basic text extraction
    TODO: Improve handling of complex layouts, tables, multi-column text
    """
    
    # Common section headers in patents (Chinese and English)
    SECTION_HEADERS = {
        'abstract': ['摘要', '【摘要】', 'Abstract', 'ABSTRACT'],
        'claims': ['权利要求书', '权利要求', 'Claims', 'CLAIMS', 'What is claimed is:'],
        'description': ['说明书', '技术领域', '背景技术', '发明内容', '附图说明', '具体实施方式',
                       'DETAILED DESCRIPTION', 'Description'],
        'ipc': ['国际专利分类号', 'IPC', 'Int.Cl.', 'Int. Cl.'],
    }
    
    def __init__(self):
        self.extraction_stats = {
            'method_used': None,
            'pages_processed': 0,
            'text_length': 0,
        }
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract patent information from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted patent information
            
        Raises:
            PDFExtractError: If extraction fails
        """
        path = Path(file_path)
        if not path.exists():
            raise PDFExtractError(f"File not found: {file_path}")
        
        if not path.suffix.lower() == '.pdf':
            raise PDFExtractError(f"Not a PDF file: {file_path}")
        
        # Try pdfplumber first (better for complex layouts)
        if PDFPLUMBER_AVAILABLE:
            try:
                return self._extract_with_pdfplumber(file_path)
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
        
        # Fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                return self._extract_with_pypdf2(file_path)
            except Exception as e:
                logger.error(f"PyPDF2 extraction failed: {e}")
                raise PDFExtractError(f"Failed to extract PDF: {e}")
        
        raise PDFExtractError("No PDF extraction library available")
    
    def _extract_with_pdfplumber(self, file_path: str) -> Dict:
        """Extract using pdfplumber (preferred for tables and layouts)"""
        logger.info("Extracting with pdfplumber", file=file_path)
        
        result = {
            'title': None,
            'application_no': None,
            'publication_no': None,
            'ipc': None,
            'applicant': None,
            'inventors': [],
            'abstract': None,
            'claims': [],
            'description': None,
            'raw_text': '',
        }
        
        with pdfplumber.open(file_path) as pdf:
            self.extraction_stats['method_used'] = 'pdfplumber'
            self.extraction_stats['pages_processed'] = len(pdf.pages)
            
            # Extract text from all pages
            all_text = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    all_text.append(text)
            
            full_text = '\n'.join(all_text)
            result['raw_text'] = full_text
            self.extraction_stats['text_length'] = len(full_text)
            
            # Parse patent information
            result['title'] = self._extract_title(full_text)
            result['application_no'] = self._extract_application_no(full_text)
            result['publication_no'] = self._extract_publication_no(full_text)
            result['ipc'] = self._extract_ipc(full_text)
            result['applicant'] = self._extract_applicant(full_text)
            result['inventors'] = self._extract_inventors(full_text)
            result['abstract'] = self._extract_abstract(full_text)
            result['claims'] = self._extract_claims(full_text)
            result['description'] = self._extract_description(full_text)
        
        logger.info("Extraction complete", stats=self.extraction_stats)
        return result
    
    def _extract_with_pypdf2(self, file_path: str) -> Dict:
        """Extract using PyPDF2 (fallback)"""
        logger.info("Extracting with PyPDF2", file=file_path)
        
        result = {
            'title': None,
            'application_no': None,
            'publication_no': None,
            'ipc': None,
            'applicant': None,
            'inventors': [],
            'abstract': None,
            'claims': [],
            'description': None,
            'raw_text': '',
        }
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            self.extraction_stats['method_used'] = 'PyPDF2'
            self.extraction_stats['pages_processed'] = len(reader.pages)
            
            # Extract text from all pages
            all_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)
            
            full_text = '\n'.join(all_text)
            result['raw_text'] = full_text
            self.extraction_stats['text_length'] = len(full_text)
            
            # Parse patent information
            result['title'] = self._extract_title(full_text)
            result['application_no'] = self._extract_application_no(full_text)
            result['publication_no'] = self._extract_publication_no(full_text)
            result['ipc'] = self._extract_ipc(full_text)
            result['applicant'] = self._extract_applicant(full_text)
            result['inventors'] = self._extract_inventors(full_text)
            result['abstract'] = self._extract_abstract(full_text)
            result['claims'] = self._extract_claims(full_text)
            result['description'] = self._extract_description(full_text)
        
        logger.info("Extraction complete", stats=self.extraction_stats)
        return result
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract patent title"""
        # Try to find title after common patterns (Chinese)
        patterns = [
            r'发明名称[：:]\s*([^\n]+)',
            r'标题[：:]\s*([^\n]+)',
            r'\n([^\n]{10,50})\n\s*技术领域',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up title
                title = re.sub(r'^[\d\s]+', '', title)  # Remove leading numbers
                if len(title) > 5:
                    return title
        
        # English patent patterns
        eng_patterns = [
            r'\(\s*54\s*\)\s*([^\n(]+)',  # (54) Title - take first line only
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, text)
            if match:
                title = match.group(1).strip()
                # Clean up - stop at common section markers
                title = re.split(r'\s*\(\s*56\s*\)|References|U\.S\. PATENT', title)[0]
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) > 5 and len(title) < 200:
                    return title
        
        # Fallback: use first non-empty line that's not metadata
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:10]:
            # Skip common header lines
            if any(skip in line for skip in ['专利', '申请号', '公开号', 'IPC', '第', '页', 'Patent', 'United States']):
                continue
            if len(line) > 10 and len(line) < 100:
                return line
        
        return None
    
    def _extract_application_no(self, text: str) -> Optional[str]:
        """Extract application number"""
        # Chinese patterns
        patterns = [
            r'申请号[：:]\s*([\d\.X]+)',
            r'申请号\s*([\d\.X]+)',
            r'CN\d{9,12}\.?\d?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0 if 'CN' in pattern else 1).strip()
        
        # English/US patterns
        eng_patterns = [
            r'\(\s*21\s*\)\s*Appl\.?\s*No\.?[：:]?\s*([\d/,]+)',
            r'Appl\.?\s*No\.?[：:]?\s*([\d/,]+)',
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_publication_no(self, text: str) -> Optional[str]:
        """Extract publication number"""
        # Chinese patterns
        patterns = [
            r'公开号[：:]\s*([\dA-Z\.]+)',
            r'公告号[：:]\s*([\dA-Z\.]+)',
            r'CN\d{9,12}[A-Z]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0 if pattern.startswith('CN') else 1).strip()
        
        # English/US patterns
        eng_patterns = [
            r'Patent\s*No\.?[：:]?\s*(US\s*[\d,]+\s*B?\d?)',
            r'\(\s*45\s*\)\s*Date\s+of\s+Patent.*\n.*?(US\s*[\d,]+\s*B?\d?)',
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                pub_no = match.group(1).strip()
                pub_no = re.sub(r'\s+', '', pub_no)  # Remove spaces
                return pub_no
        
        return None
    
    def _extract_ipc(self, text: str) -> Optional[str]:
        """Extract IPC classification"""
        # Chinese patterns
        patterns = [
            r'IPC[分类号]*[：:]\s*([A-Z]\d{2}[A-Z]\d+/\d+)',
            r'Int\.?Cl\.?[：:]?\s*([A-Z]\d{2}[A-Z]\d+/\d+)',
            r'国际分类号[：:]\s*([A-Z]\d{2}[A-Z]\d+/\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # English/US pattern: find (51) Int. Cl. section
        eng_pattern = r'\(\s*51\s*\)\s*Int\.\s*Cl\.\s*(.+?)(?=\(\s*52\s*\)|\n\(\d+\)|$)'
        match = re.search(eng_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            # Extract first classification code
            ipc_text = match.group(1)
            # Find pattern like H04N 5/93 or HOAN 5/93 (OCR may read 0 as O)
            ipc_match = re.search(r'([A-Z]\d{2}[A-Z])\s*(\d+/\d+)', ipc_text)
            if ipc_match:
                code = f"{ipc_match.group(1)}{ipc_match.group(2)}"
                # Fix common OCR errors
                code = code.replace('O', '0').replace('I', '1')
                return code
        
        # Fallback: search for any classification pattern in first 5000 chars
        fallback_pattern = r'([A-Z]\d{2}[A-Z])\s*(\d+/\d+)'
        match = re.search(fallback_pattern, text[:5000])
        if match:
            code = f"{match.group(1)}{match.group(2)}"
            code = code.replace('O', '0').replace('I', '1')
            return code
        
        # Extract from CPC or other classification fields
        cpc_pattern = r'CPC[\s\.]+([A-Z]\d{2}[A-Z]\s*\d+/\d+)'
        match = re.search(cpc_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().replace(' ', '')
        
        return None
    
    def _extract_applicant(self, text: str) -> Optional[str]:
        """Extract applicant name"""
        # Chinese patterns
        patterns = [
            r'申请人[：:]\s*([^\n]+)',
            r'申请（专利权）人[：:]\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # English patterns
        eng_patterns = [
            r'\(\s*71\s*\)\s*Applicant[：:]?\s*([^\n]+(?:\n[^\n(]+)*)',
            r'\(\s*73\s*\)\s*Assignee[：:]?\s*([^\n]+(?:\n[^\n(]+)*)',
            r'Applicant[：:]\s*([^\n]+)',
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                applicant = match.group(1).strip()
                # Clean up - take first line
                applicant = applicant.split('\n')[0].strip()
                # Remove location info
                applicant = re.sub(r',\s*[A-Z]{2}\s*\(US\)', '', applicant)
                return applicant
        
        return None
    
    def _extract_inventors(self, text: str) -> List[str]:
        """Extract inventor names"""
        # Chinese patterns
        patterns = [
            r'发明人[：:]\s*([^\n]+)',
            r'设计人[：:]\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                inventors_str = match.group(1).strip()
                # Split by common separators
                inventors = re.split(r'[,;，；、]', inventors_str)
                return [i.strip() for i in inventors if i.strip()]
        
        # English patterns
        eng_patterns = [
            r'\(\s*72\s*\)\s*Inventor[：:]?\s*([^\n]+(?:\n[^\n(]+)*)',
            r'Inventor[：:]\s*([^\n]+)',
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inventors_str = match.group(1).strip()
                # Split by comma or newline
                inventors = re.split(r'[,;]|\n', inventors_str)
                # Clean up each name
                cleaned = []
                for inv in inventors:
                    inv = inv.strip()
                    # Remove location info
                    inv = re.sub(r',\s*[A-Z]{2}\s*\(US\)', '', inv)
                    inv = re.sub(r',\s*[A-Z]{2}$', '', inv)
                    # Remove patent references
                    inv = re.sub(r'\s+\d+.*$', '', inv)
                    # Skip lines that are clearly not names
                    if (inv and len(inv) > 2 and len(inv) < 50 and 
                        not re.match(r'^[\d/]+$', inv) and
                        not re.match(r'^[\d\s]+A?\s*\*', inv) and
                        'Patent' not in inv and 'Examiner' not in inv):
                        cleaned.append(inv)
                return cleaned[:5]  # Limit to 5 inventors
        
        return []
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract"""
        # Chinese patterns
        patterns = [
            r'摘要[：:]\s*([^\n]{50,500})',
            r'【摘要】\s*([^\n]{50,500})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # Clean up
                abstract = re.sub(r'\s+', ' ', abstract)
                return abstract[:500]  # Limit length
        
        # English patterns
        eng_patterns = [
            r'\(\s*57\s*\)\s*ABSTRACT\s*([^\n]{50,1000})',
            r'ABSTRACT\s*([^\n]{50,1000})',
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # Clean up
                abstract = re.sub(r'\s+', ' ', abstract)
                # Stop at next section
                abstract = re.split(r'\n\s*\(|REFERENCES|CLAIMS', abstract)[0]
                return abstract[:800]
        
        return None
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract patent claims - MVP: Simple line-based extraction"""
        claims = []
        
        # Find claims section
        claims_start = None
        for header in self.SECTION_HEADERS['claims']:
            match = re.search(rf'{header}', text, re.IGNORECASE)
            if match:
                claims_start = match.end()
                break
        
        if claims_start:
            # Extract claims text (up to next major section or end)
            claims_text = text[claims_start:claims_start + 25000]
            
            # Simple pattern: find lines starting with number + period
            # This works for both English and Chinese patents
            lines = claims_text.split('\n')
            current_claim = None
            current_num = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line starts with a claim number
                match = re.match(r'^(\d+)[\.\s]+(.+)', line)
                if match:
                    # Save previous claim
                    if current_claim and len(current_claim) > 30:
                        claims.append(current_claim)
                    
                    current_num = int(match.group(1))
                    current_claim = match.group(2)
                elif current_claim is not None:
                    # Continue previous claim
                    current_claim += ' ' + line
                
                # Limit to 20 claims
                if len(claims) >= 20:
                    break
            
            # Don't forget the last claim
            if current_claim and len(current_claim) > 30 and len(claims) < 20:
                claims.append(current_claim)
            
            # Clean up claims
            cleaned_claims = []
            for claim in claims:
                # Remove patent number headers
                claim = re.sub(r'^US\s+\d+,\d+,\d+\s+B\d+\s*', '', claim)
                claim = re.sub(r'^\d+\s+\d+\s*', '', claim)
                # Normalize whitespace
                claim = re.sub(r'\s+', ' ', claim).strip()
                # Filter out short or header-only claims
                if len(claim) > 40 and not claim.startswith('('):
                    cleaned_claims.append(claim)
            
            return cleaned_claims
        
        return claims
    
    def _extract_description(self, text: str) -> Optional[str]:
        """Extract description section"""
        # Find description start
        desc_start = None
        for header in self.SECTION_HEADERS['description']:
            match = re.search(rf'{header}', text, re.IGNORECASE)
            if match:
                desc_start = match.start()
                break
        
        if desc_start:
            # Extract up to reasonable length
            description = text[desc_start:desc_start + 5000]
            description = re.sub(r'\s+', ' ', description)
            return description[:3000]
        
        return None
    
    def get_quality_score(self) -> int:
        """
        Calculate extraction quality score (0-100)
        MVP: Simple heuristic based on extracted fields
        TODO: Improve scoring algorithm
        """
        score = 50  # Base score
        
        # Bonus for each successfully extracted field
        if self.extraction_stats['text_length'] > 1000:
            score += 20
        if self.extraction_stats['text_length'] > 5000:
            score += 10
        
        # Method bonus
        if self.extraction_stats['method_used'] == 'pdfplumber':
            score += 10
        
        return min(score, 100)


def extract_patent_from_pdf(file_path: str) -> Tuple[Dict, int]:
    """
    Convenience function to extract patent and get quality score
    
    Returns:
        Tuple of (extraction_result, quality_score)
    """
    extractor = PatentPDFExtractor()
    result = extractor.extract(file_path)
    quality = extractor.get_quality_score()
    return result, quality
