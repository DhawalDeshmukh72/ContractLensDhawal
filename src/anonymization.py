import fitz
import re

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import SpacyNlpEngine
import spacy

# Load optimized SpaCy model excluding heavy components to save RAM
nlp = spacy.load("en_core_web_sm", exclude=["parser", "attribute_ruler", "lemmatizer"])

class LoadedSpacyNlpEngine(SpacyNlpEngine):
    def __init__(self, loaded_model):
        self.nlp = {"en": loaded_model}

nlp_engine = LoadedSpacyNlpEngine(loaded_model=nlp)
global_analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

# -------- CUSTOM PATTERNS --------
aadhaar_pattern = Pattern(
    name="aadhaar_pattern",
    regex=r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    score=0.7
)

pan_pattern = Pattern(
    name="pan_pattern",
    regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    score=0.7
)

ifsc_pattern = Pattern(
    name="ifsc_pattern",
    regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    score=0.7
)

bank_pattern = Pattern(
    name="bank_pattern",
    regex=r"\b\d{9,18}\b",
    score=0.5
)

phone_pattern = Pattern(
    name="phone_pattern",
    regex=r"\b[6-9]\d{9}\b",
    score=0.6
)

# -------- CREATE RECOGNIZERS --------
aadhaar_recognizer = PatternRecognizer(
    supported_entity="AADHAAR",
    patterns=[aadhaar_pattern]
)

pan_recognizer = PatternRecognizer(
    supported_entity="PAN",
    patterns=[pan_pattern]
)

ifsc_recognizer = PatternRecognizer(
    supported_entity="IFSC",
    patterns=[ifsc_pattern]
)

bank_recognizer = PatternRecognizer(
    supported_entity="BANK_ACCOUNT",
    patterns=[bank_pattern]
)

phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[phone_pattern]
)

# -------- ADD TO REGISTRY --------
global_analyzer.registry.add_recognizer(aadhaar_recognizer)
global_analyzer.registry.add_recognizer(pan_recognizer)
global_analyzer.registry.add_recognizer(ifsc_recognizer)
global_analyzer.registry.add_recognizer(bank_recognizer)
global_analyzer.registry.add_recognizer(phone_recognizer)


def anonymize_pdf(pdf_path):

    # -------- READ PDF --------
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    # -------- CLEAN EXTRA WHITESPACE --------
    text = re.sub(r'\s+', ' ', text)

    # -------- ANALYZE TEXT --------
    results = global_analyzer.analyze(
        text=text,
        entities=[
            "PERSON",
            "LOCATION",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "AADHAAR",
            "PAN",
            "IFSC",
            "BANK_ACCOUNT"
        ],
        language="en"
    )

    # -------- ANONYMIZE WITH MAPPING --------

    # Sort results in descending order of start index to do safe in-place replacement
    sorted_results = sorted(results, key=lambda x: x.start, reverse=True)

    pii_map = {}
    value_to_placeholder = {}
    entity_counters = {}

    anonymized_text = text
    for res in sorted_results:
        start, end = res.start, res.end
        entity_type = res.entity_type
        original_val = text[start:end]
        
        # Don't map empty strings
        if not original_val.strip():
            continue
            
        if original_val in value_to_placeholder:
            placeholder = value_to_placeholder[original_val]
        else:
            counter = entity_counters.get(entity_type, 1)
            placeholder = f"<{entity_type}_{counter}>"
            entity_counters[entity_type] = counter + 1
            value_to_placeholder[original_val] = placeholder
            pii_map[placeholder] = original_val
            
        anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]

    # -------- CLEAN DUPLICATES & FORMAT --------

    anonymized_text = anonymized_text.replace("LockIin", "Lock-in")

    return anonymized_text, pii_map

# from mask_pdf import anonymize_pdf

# pdf_path = "sample_rent_agreement_contract.pdf"

# masked_text = anonymize_pdf(pdf_path)

# print(masked_text)