"""
Test script for PDF patent extraction
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services import extract_patent_from_pdf, PDFExtractError


def test_extraction(pdf_path: str):
    """Test PDF extraction"""
    print(f"\n{'='*60}")
    print(f"Testing PDF extraction: {pdf_path}")
    print('='*60)
    
    try:
        result, quality = extract_patent_from_pdf(pdf_path)
        
        print(f"\n[OK] Extraction successful!")
        print(f"Quality Score: {quality}/100")
        print(f"\nExtracted Information:")
        print(f"  Title: {result.get('title') or 'N/A'}")
        print(f"  Application No: {result.get('application_no') or 'N/A'}")
        print(f"  Publication No: {result.get('publication_no') or 'N/A'}")
        print(f"  IPC: {result.get('ipc') or 'N/A'}")
        print(f"  Applicant: {result.get('applicant') or 'N/A'}")
        print(f"  Inventors: {', '.join(result.get('inventors') or []) or 'N/A'}")
        abstract = result.get('abstract') or 'N/A'
        print(f"  Abstract: {abstract[:100]}...")
        print(f"  Claims Count: {len(result.get('claims') or [])}")
        print(f"  Raw Text Length: {len(result.get('raw_text', ''))} chars")
        
        return True
        
    except PDFExtractError as e:
        print(f"\n[FAIL] Extraction failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("PDF Patent Extractor Test")
    print("=" * 60)
    
    # Check if test file provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        success = test_extraction(pdf_path)
    else:
        print("\nUsage: python test_pdf_extraction.py <path_to_pdf_file>")
        print("\nNo PDF file provided. Running basic import test...")
        
        # Test import
        try:
            from app.services.pdf_extractor import PatentPDFExtractor
            print("[OK] Import successful")
            print(f"[OK] PDFPlumber available")
            success = True
        except Exception as e:
            print(f"[FAIL] Import failed: {e}")
            success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
