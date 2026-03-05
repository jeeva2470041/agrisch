"""
Document Guide Service
Provides step-by-step guidance on how to apply for common documents
required by Indian government agricultural schemes.
"""

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Comprehensive document application guides
# ---------------------------------------------------------------------------
DOCUMENT_GUIDES = {
    # ── Aadhaar Card ──
    "aadhaar card": {
        "document_name": "Aadhaar Card",
        "description": "Aadhaar is a 12-digit unique identity number issued by UIDAI. It is the most important ID for availing government schemes.",
        "issuing_authority": "Unique Identification Authority of India (UIDAI)",
        "estimated_time": "15–60 days",
        "fee": "Free (first time); ₹50 for update",
        "steps": [
            "Visit the nearest Aadhaar Enrolment Centre (find at uidai.gov.in or any Common Service Centre/CSC).",
            "Carry a proof of identity (Voter ID, PAN, Ration Card, or Passport) and proof of address.",
            "Fill the Aadhaar enrolment form available at the centre.",
            "Submit the form along with your supporting documents.",
            "Your biometrics (fingerprints, iris scan) and photograph will be captured.",
            "You will receive an acknowledgement slip with a 14-digit Enrolment Number.",
            "Track your Aadhaar status at uidai.gov.in using the enrolment number.",
            "Once processed, the Aadhaar card will be sent to your address by post. You can also download the e-Aadhaar from uidai.gov.in."
        ],
        "documents_needed": [
            "Proof of Identity (any one): Voter ID / PAN / Ration Card / Passport / Driving License",
            "Proof of Address (any one): Voter ID / Utility Bill / Bank Statement / Ration Card",
            "Proof of Date of Birth (optional): Birth Certificate / School Certificate"
        ],
        "helpful_links": [
            {"title": "UIDAI Official Website", "url": "https://uidai.gov.in"},
            {"title": "Find Nearest Enrolment Centre", "url": "https://appointments.uidai.gov.in/easearch.aspx"},
            {"title": "Check Aadhaar Status", "url": "https://myaadhaar.uidai.gov.in/check-aadhaar"}
        ],
        "tips": [
            "You can book an appointment online at appointments.uidai.gov.in to avoid long queues.",
            "If you don't have any ID, ask the village head (Sarpanch) for an introduction letter.",
            "e-Aadhaar downloaded from the UIDAI website is equally valid as the physical card."
        ]
    },

    # ── Aadhaar (short form) ──
    "aadhaar": {
        "_alias": "aadhaar card"
    },

    # ── Land Records ──
    "land records": {
        "document_name": "Land Records / Patta / Khata",
        "description": "Land ownership records that prove your right over agricultural land. Known by different names in different states (Patta, Khata, RoR, 7/12 extract, Jamabandi).",
        "issuing_authority": "State Revenue Department / Tehsildar Office",
        "estimated_time": "7–30 days",
        "fee": "₹10–₹100 (varies by state)",
        "steps": [
            "Visit your local Tehsildar / Taluk office or access your state's Bhulekh / land records portal online.",
            "Request a copy of your Record of Rights (RoR) or 7/12 extract or Patta.",
            "Provide your survey number, plot number, or khata number.",
            "Pay the nominal fee at the counter or online.",
            "If applying for mutation (name transfer), submit: sale deed, inheritance documents, or court order.",
            "Collect the certified copy from the office or download from the state portal."
        ],
        "documents_needed": [
            "Existing land documents (if any): old Patta / sale deed / gift deed",
            "Aadhaar Card or other ID proof",
            "Survey number / Plot number of your land",
            "For mutation: death certificate of previous owner (if inherited), legal heir certificate"
        ],
        "helpful_links": [
            {"title": "Digital India Land Records (DILRMP)", "url": "https://dilrmp.gov.in"},
            {"title": "Bhulekh (UP)", "url": "https://upbhulekh.gov.in"},
            {"title": "Bhoomi (Karnataka)", "url": "https://landrecords.karnataka.gov.in"},
            {"title": "Patta Chitta (Tamil Nadu)", "url": "https://eservices.tn.gov.in/eservicesnew/land/patta_english.html"},
            {"title": "Bhulekh (Maharashtra 7/12)", "url": "https://bhulekh.mahabhumi.gov.in"}
        ],
        "tips": [
            "Most states now offer online access to land records — check your state's Bhulekh portal.",
            "Keep a copy of your RoR / 7/12 extract updated regularly.",
            "If your land is not in records, approach the Tehsildar with a written application and witnesses."
        ]
    },

    # ── Bank Account Details ──
    "bank account details": {
        "document_name": "Bank Account & Passbook",
        "description": "A savings bank account is required for receiving scheme benefits through Direct Benefit Transfer (DBT). A cancelled cheque or passbook copy is typically submitted.",
        "issuing_authority": "Any Scheduled Bank / Post Office",
        "estimated_time": "Same day to 7 days",
        "fee": "Free (under Jan Dhan Yojana) or minimal charges",
        "steps": [
            "Visit the nearest bank branch or Post Office.",
            "Ask for a savings account opening form (or open under Pradhan Mantri Jan Dhan Yojana for zero balance).",
            "Fill the form with your personal details.",
            "Submit the form with KYC documents (Aadhaar + one more ID).",
            "Provide two passport-size photographs.",
            "The bank will process your application and issue a passbook and ATM card.",
            "Ensure your Aadhaar is linked to the bank account for DBT benefits."
        ],
        "documents_needed": [
            "Aadhaar Card (mandatory for DBT)",
            "PAN Card (for accounts above ₹50,000 transactions)",
            "Two passport-size photographs",
            "Address proof (if different from Aadhaar): Utility bill / Ration card"
        ],
        "helpful_links": [
            {"title": "PM Jan Dhan Yojana", "url": "https://pmjdy.gov.in"},
            {"title": "India Post Savings Account", "url": "https://www.indiapost.gov.in"}
        ],
        "tips": [
            "Under Jan Dhan Yojana, you can open a zero-balance account with just Aadhaar.",
            "Make sure your bank account is linked with your Aadhaar for scheme money to arrive via DBT.",
            "Keep your passbook updated regularly; it serves as proof for scheme applications."
        ]
    },

    # ── Bank Account (variant) ──
    "bank account": {
        "_alias": "bank account details"
    },
    "bank details": {
        "_alias": "bank account details"
    },

    # ── KCC Card / Kisan Credit Card ──
    "kcc card": {
        "document_name": "Kisan Credit Card (KCC)",
        "description": "KCC provides farmers with affordable credit for agricultural needs. It also acts as an identity for several loan-based schemes.",
        "issuing_authority": "Scheduled Commercial Banks / Cooperative Banks / RRBs",
        "estimated_time": "14–30 days",
        "fee": "Processing fee varies (₹0–₹500 depending on bank)",
        "steps": [
            "Visit your nearest bank branch (any nationalized bank, cooperative bank, or RRB).",
            "Ask for the KCC application form.",
            "Fill in details: name, crop details, land area, expected credit requirement.",
            "Submit the form with required documents.",
            "The bank will verify your land records and conduct a field inspection if needed.",
            "Upon approval, the KCC will be issued with a credit limit based on your land and crop.",
            "You can draw credit as needed and repay after harvest season."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Land Records (RoR / Patta / 7/12 extract)",
            "Passport-size photographs (2)",
            "Bank account details (if existing account)"
        ],
        "helpful_links": [
            {"title": "KCC Scheme Details (RBI)", "url": "https://www.rbi.org.in"},
            {"title": "PM-KISAN KCC Module", "url": "https://pmkisan.gov.in"}
        ],
        "tips": [
            "PM-KISAN beneficiaries can get KCC through a simplified single-page form.",
            "Interest subvention of 2% is available, making effective rate just 4% on timely repayment.",
            "Oral lessees and sharecroppers can also apply — no land document needed in some banks if the village head certifies."
        ]
    },

    # ── Crop Declaration ──
    "crop declaration": {
        "document_name": "Crop Sowing Declaration / Crop Declaration",
        "description": "A declaration of the crops you have sown in the current season, required for crop insurance schemes like PMFBY.",
        "issuing_authority": "Village-level Agriculture Officer / Patwari / Bank",
        "estimated_time": "1–7 days",
        "fee": "Free",
        "steps": [
            "Visit your bank branch or the local agriculture department office.",
            "Inform them about the crops sown, area, and season.",
            "Fill the crop declaration form (usually part of the PMFBY enrollment).",
            "Provide your land records and sowing details.",
            "The declaration is verified by the village agriculture officer.",
            "Once verified, it is submitted along with your insurance application."
        ],
        "documents_needed": [
            "Land Records / RoR / Patta",
            "Aadhaar Card",
            "Bank account details",
            "Details of crop sown (crop name, area, date of sowing)"
        ],
        "helpful_links": [
            {"title": "PMFBY Portal", "url": "https://pmfby.gov.in"},
            {"title": "Crop Insurance App", "url": "https://play.google.com/store/apps/details?id=in.farmguide.pisces"}
        ],
        "tips": [
            "Crop declaration must be done within the enrollment window for the season.",
            "Loanee farmers are automatically enrolled through their bank.",
            "Non-loanee farmers can enrol at the bank or CSC centre with their documents."
        ]
    },

    # ── Income Certificate ──
    "income certificate": {
        "document_name": "Income Certificate",
        "description": "A certificate issued by the state government certifying your annual income. Required for many welfare and subsidy schemes.",
        "issuing_authority": "Tehsildar / Revenue Department / Sub-Divisional Magistrate",
        "estimated_time": "7–21 days",
        "fee": "₹10–₹50 (varies by state)",
        "steps": [
            "Visit the nearest Tehsildar office or apply online through your state's e-District portal.",
            "Obtain and fill the income certificate application form.",
            "Attach self-declaration of annual income from all sources.",
            "Submit supporting documents (ration card, land records, bank statement).",
            "The Tehsildar or an authorized officer may conduct a field verification.",
            "Collect the income certificate once approved, or download from the e-District portal."
        ],
        "documents_needed": [
            "Aadhaar Card / Voter ID",
            "Ration Card",
            "Self-declaration of income",
            "Bank passbook (last 6 months) if applicable",
            "Land records (for agriculture income)"
        ],
        "helpful_links": [
            {"title": "e-District Portal (check your state)", "url": "https://edistrict.gov.in"}
        ],
        "tips": [
            "Many states now issue income certificates online within a week.",
            "The certificate is usually valid for 1 year; renew before it expires.",
            "For farmers, agricultural income shown in land records is sufficient basis."
        ]
    },

    # ── Caste Certificate (SC/ST/OBC) ──
    "caste certificate": {
        "document_name": "Caste Certificate (SC/ST/OBC)",
        "description": "A certificate proving your caste category, required for reserved category schemes and additional benefits.",
        "issuing_authority": "Tehsildar / Revenue Department / SDM Office",
        "estimated_time": "15–30 days",
        "fee": "₹10–₹50",
        "steps": [
            "Visit the Tehsildar office or apply through your state's e-District portal.",
            "Fill the caste certificate application form.",
            "Attach supporting documents proving your caste/community.",
            "Your application may require verification by the village officer.",
            "Once verified, the certificate is issued by the Tehsildar / SDM.",
            "Collect the certificate or download from the portal."
        ],
        "documents_needed": [
            "Aadhaar Card / Voter ID",
            "Ration Card (showing caste)",
            "Father's / Family caste certificate (if available)",
            "School leaving certificate (if caste is mentioned)",
            "Affidavit (in some states)"
        ],
        "helpful_links": [
            {"title": "e-District Portal", "url": "https://edistrict.gov.in"}
        ],
        "tips": [
            "Keep the original safely — many schemes require the original for verification.",
            "In most states, the certificate can be applied for online.",
            "If your father already has a caste certificate, the process is much faster."
        ]
    },

    # ── PAN Card ──
    "pan card": {
        "document_name": "PAN Card (Permanent Account Number)",
        "description": "PAN is a 10-digit alphanumeric identity issued by the Income Tax Department, required for financial transactions above certain limits.",
        "issuing_authority": "Income Tax Department (via NSDL / UTIITSL)",
        "estimated_time": "15–20 days",
        "fee": "₹107 (for Indian address); free via Aadhaar-based instant e-PAN",
        "steps": [
            "Option 1 (Instant e-PAN — FREE): Visit incometax.gov.in → 'Instant e-PAN' → Enter Aadhaar → OTP verification → e-PAN issued instantly.",
            "Option 2 (Physical PAN): Visit onlineservices.nsdl.com or utiitsl.com.",
            "Fill Form 49A for Indian citizens.",
            "Upload photograph, signature, and ID/address proof.",
            "Pay the fee online.",
            "Physical PAN card will be delivered by post within 15–20 days.",
            "You can also apply at any CSC or NSDL/UTI TIN facilitation centre."
        ],
        "documents_needed": [
            "Aadhaar Card (for instant e-PAN, only Aadhaar needed)",
            "Proof of Identity: Aadhaar / Voter ID / Passport",
            "Proof of Address: Aadhaar / Utility Bill / Bank Statement",
            "Proof of Date of Birth: Birth Certificate / Aadhaar",
            "Passport-size photograph and signature"
        ],
        "helpful_links": [
            {"title": "Instant e-PAN (Free)", "url": "https://eportal.incometax.gov.in/iec/foservices/#/pre-login/instant-e-pan"},
            {"title": "NSDL PAN Application", "url": "https://onlineservices.nsdl.com/paam/endUserRegisterContact.html"},
            {"title": "UTIITSL PAN Application", "url": "https://www.pan.utiitsl.com"}
        ],
        "tips": [
            "If you have Aadhaar with mobile linked, get instant e-PAN for FREE in just 10 minutes!",
            "PAN is mandatory for bank accounts with transactions above ₹50,000.",
            "You can use Aadhaar in lieu of PAN for many government scheme applications."
        ]
    },

    # ── Voter ID / Electoral ID ──
    "voter id": {
        "document_name": "Voter ID Card (EPIC)",
        "description": "The Electoral Photo Identity Card issued by the Election Commission of India. Widely accepted as ID proof.",
        "issuing_authority": "Election Commission of India",
        "estimated_time": "30–45 days",
        "fee": "Free",
        "steps": [
            "Visit the National Voters' Service Portal (voters.eci.gov.in) or download the Voter Helpline App.",
            "Fill Form 6 for new voter registration.",
            "Upload passport-size photo, age proof, and address proof.",
            "Submit the form online or at the nearest Electoral Registration Office (ERO).",
            "A Booth Level Officer (BLO) may visit your address for verification.",
            "Once approved, your name is added to the electoral roll.",
            "The Voter ID card (EPIC) will be delivered to your address or can be collected from the ERO."
        ],
        "documents_needed": [
            "Passport-size photograph",
            "Age proof: Birth Certificate / School Certificate / Aadhaar",
            "Address proof: Aadhaar / Utility Bill / Ration Card / Bank Passbook"
        ],
        "helpful_links": [
            {"title": "National Voters' Service Portal", "url": "https://voters.eci.gov.in"},
            {"title": "Voter Helpline App", "url": "https://play.google.com/store/apps/details?id=com.eci.citizen"}
        ],
        "tips": [
            "You can apply online through the NVSP portal — no need to visit the office.",
            "e-EPIC (digital voter ID) can be downloaded from the NVSP portal.",
            "Voter ID is free and serves as one of the strongest identity proofs."
        ]
    },

    # ── Ration Card ──
    "ration card": {
        "document_name": "Ration Card",
        "description": "A government document that allows households to buy subsidized food grains. Also widely used as identity and address proof.",
        "issuing_authority": "State Food & Civil Supplies Department",
        "estimated_time": "15–30 days",
        "fee": "Free to ₹45 (varies by state)",
        "steps": [
            "Visit your state's food department portal or the local Ration Office (Taluk Supply Office).",
            "Download or obtain the ration card application form.",
            "Fill in household details: family members, income, address.",
            "Attach required documents.",
            "Submit the form at the Ration Office or online.",
            "An inspector may visit your home for verification.",
            "Upon approval, the ration card is issued and linked to a fair price shop near you."
        ],
        "documents_needed": [
            "Aadhaar Card of all family members",
            "Address proof: Utility bill / Rental agreement",
            "Income certificate (for BPL/AAY category)",
            "Family photograph",
            "Gas connection details (if applicable)"
        ],
        "helpful_links": [
            {"title": "One Nation One Ration Card", "url": "https://nfsa.gov.in/portal/ration_card_state_portals_702"},
            {"title": "NFSA Portal", "url": "https://nfsa.gov.in"}
        ],
        "tips": [
            "Ration card is one of the most useful documents — it works as both ID and address proof.",
            "Under One Nation One Ration Card, you can use your card in any state.",
            "Categorized as APL (Above Poverty Line), BPL (Below Poverty Line), or AAY (Antyodaya Anna Yojana)."
        ]
    },

    # ── Soil Health Card ──
    "soil health card": {
        "document_name": "Soil Health Card",
        "description": "A government-issued card that provides information on soil nutrient status and recommendations for appropriate fertilizer dosage.",
        "issuing_authority": "Department of Agriculture & Cooperation / State Agriculture Department",
        "estimated_time": "30–60 days (after soil sampling)",
        "fee": "Free",
        "steps": [
            "Register at the Soil Health Card portal (soilhealth.dac.gov.in) or contact your nearest Krishi Vigyan Kendra (KVK).",
            "Provide your land details (survey number, village).",
            "A soil sample will be collected from your field by the agriculture department.",
            "The sample is tested at a government soil testing laboratory.",
            "Based on the results, a Soil Health Card is generated with nutrient status and fertilizer recommendations.",
            "You can view and download your Soil Health Card from the portal."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Land Records / Survey Number",
            "No other documents needed — the government collects and tests soil samples free of cost"
        ],
        "helpful_links": [
            {"title": "Soil Health Card Portal", "url": "https://soilhealth.dac.gov.in"},
            {"title": "Find Nearest Soil Testing Lab", "url": "https://soilhealth.dac.gov.in/PublicReports/SoilTestingLabNearYou"}
        ],
        "tips": [
            "Soil Health Cards are issued free of cost by the government.",
            "Cards are valid for 2 years; after that, get a fresh sample tested.",
            "Following the fertilizer recommendation on your card can save 20-30% on fertilizer costs."
        ]
    },

    # ── Passport-size Photograph ──
    "passport-size photographs": {
        "document_name": "Passport-size Photographs",
        "description": "Standard photographs required for almost all government applications. Can be obtained at any photo studio.",
        "issuing_authority": "Any Photography Studio / Self (via mobile apps)",
        "estimated_time": "Immediate",
        "fee": "₹20–₹50 for a set of photos",
        "steps": [
            "Visit any nearby photography studio or use a mobile app like 'Passport Photo Maker'.",
            "Get photos taken in standard passport size (3.5cm × 4.5cm).",
            "Ensure: white background, front-facing, clear face, no shadows.",
            "Collect printed photos and keep digital copies on your phone."
        ],
        "documents_needed": [
            "No documents needed"
        ],
        "helpful_links": [],
        "tips": [
            "Always keep 10-15 extra passport photos — they're needed for many applications.",
            "Many mobile apps can create passport photos for free which you can print at any shop.",
            "Some e-Seva / CSC centres also provide photo services."
        ]
    },

    # ── Photographs variant ──
    "photographs": {
        "_alias": "passport-size photographs"
    },

    # ── Domicile Certificate ──
    "domicile certificate": {
        "document_name": "Domicile / Residence Certificate",
        "description": "A certificate proving you are a permanent resident of a particular state. Required for state-specific schemes.",
        "issuing_authority": "Tehsildar / Revenue Department",
        "estimated_time": "7–21 days",
        "fee": "₹10–₹50",
        "steps": [
            "Visit the Tehsildar office or your state's e-District portal.",
            "Fill the domicile/residence certificate application form.",
            "Provide proof of residence for the required duration.",
            "Submit the application with supporting documents.",
            "Verification may be done by a village officer.",
            "Collect the certificate from the office or download online."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Ration Card / Voter ID showing current address",
            "School/College certificate (showing state of study)",
            "Electricity bill / Property tax receipt"
        ],
        "helpful_links": [
            {"title": "e-District Portal", "url": "https://edistrict.gov.in"}
        ],
        "tips": [
            "Available online in most states through the e-District portal.",
            "Typically valid for 3 years.",
            "Some state schemes accept Aadhaar address as proof of domicile."
        ]
    },

    # ── Legal Heir Certificate ──
    "legal heir certificate": {
        "document_name": "Legal Heir Certificate",
        "description": "Certifies the legal heirs of a deceased person. Needed when land or scheme benefits need to be transferred after death of the original beneficiary.",
        "issuing_authority": "Tehsildar / Revenue Department / Court",
        "estimated_time": "15–45 days",
        "fee": "₹25–₹100",
        "steps": [
            "Visit the Tehsildar office or apply online through e-District portal.",
            "Fill the legal heir certificate application form.",
            "Provide the death certificate of the deceased.",
            "List all surviving legal heirs with their relationship.",
            "Submit supporting documents.",
            "Verification will be conducted; other heirs may need to provide consent.",
            "Certificate is issued after verification."
        ],
        "documents_needed": [
            "Death Certificate of the deceased",
            "Aadhaar Card of all legal heirs",
            "Ration Card showing family members",
            "Affidavit stating all legal heirs (in some states)"
        ],
        "helpful_links": [
            {"title": "e-District Portal", "url": "https://edistrict.gov.in"}
        ],
        "tips": [
            "This certificate is essential for transferring land records after a family member's death.",
            "All legal heirs must agree and sign the application.",
            "Obtaining this early helps avoid disputes later."
        ]
    },

    # ── Self-Declaration / Affidavit ──
    "self declaration": {
        "document_name": "Self Declaration / Affidavit",
        "description": "A sworn statement on stamp paper, used when specific documents are not available. Common for small and marginal farmers.",
        "issuing_authority": "Notary Public / Judicial Magistrate",
        "estimated_time": "Same day",
        "fee": "₹10–₹100 (stamp paper + notary fee)",
        "steps": [
            "Visit a notary public near the court complex or tehsil office.",
            "State the facts you want to declare (e.g., 'I am a farmer with X acres of land').",
            "The notary will type the affidavit on stamp paper.",
            "Sign the affidavit in front of the notary.",
            "The notary will stamp and sign it as witness.",
            "Keep the original; make photocopies for submission."
        ],
        "documents_needed": [
            "Aadhaar Card / ID proof",
            "Stamp paper (₹10–₹50 depending on state)",
            "No other documents needed"
        ],
        "helpful_links": [],
        "tips": [
            "Self-declarations are accepted by most schemes when you lack specific documents.",
            "Keep the language simple and factual.",
            "Some schemes accept self-declarations without notarisation — check the specific requirements."
        ]
    },
    "affidavit": {
        "_alias": "self declaration"
    },
}


def _normalize_doc_name(doc_name: str) -> str:
    """Normalize document name for lookup."""
    return doc_name.strip().lower()


def get_document_guide(document_name: str) -> dict:
    """Get step-by-step guidance for obtaining a specific document.

    Args:
        document_name: Name of the document (e.g., 'Aadhaar Card', 'Land Records')

    Returns:
        dict with guide information, or error dict if not found
    """
    normalized = _normalize_doc_name(document_name)

    # Direct match
    guide = DOCUMENT_GUIDES.get(normalized)

    # If not found, try partial matching
    if guide is None:
        for key, value in DOCUMENT_GUIDES.items():
            if normalized in key or key in normalized:
                guide = value
                break

    # If still not found, try word-based matching
    if guide is None:
        words = normalized.split()
        for key, value in DOCUMENT_GUIDES.items():
            if any(word in key for word in words if len(word) > 3):
                guide = value
                break

    if guide is None:
        return {
            "error": f"No application guide available for '{document_name}'. Please visit your nearest Common Service Centre (CSC) or government office for assistance."
        }

    # Resolve alias
    if "_alias" in guide:
        guide = DOCUMENT_GUIDES.get(guide["_alias"], guide)

    return {
        "document_name": guide.get("document_name", document_name),
        "description": guide.get("description", ""),
        "issuing_authority": guide.get("issuing_authority", ""),
        "estimated_time": guide.get("estimated_time", ""),
        "fee": guide.get("fee", ""),
        "steps": guide.get("steps", []),
        "documents_needed": guide.get("documents_needed", []),
        "helpful_links": guide.get("helpful_links", []),
        "tips": guide.get("tips", []),
    }


def get_all_supported_documents() -> list:
    """Return a list of all documents for which guides are available."""
    names = set()
    for key, value in DOCUMENT_GUIDES.items():
        if "_alias" not in value:
            names.add(value.get("document_name", key))
    return sorted(names)
