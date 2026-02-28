"""
AgriScheme Backend — Database seeder.
Populates the schemes collection with comprehensive, real-world government
agriculture scheme data including all required fields.

Usage:
    python seed_db.py
"""
from pprint import pprint
from db import get_schemes_collection, init_indexes


def seed_database():
    """Drop existing data and insert 33 schemes with full field coverage."""
    try:
        schemes_col = get_schemes_collection()

        # Clear existing data
        schemes_col.drop()
        print("Dropped existing schemes collection.")

        schemes = [
            # ───────────────────────────────────────────────────────────
            # 1. PM-KISAN  (Income Support — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                "type": "Income Support",
                "benefit": "₹6,000 per year (₹2,000 × 3 installments)",
                "benefit_amount": 6000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Ownership Records",
                    "Bank Account (linked to Aadhaar)",
                    "Mobile Number",
                ],
                "official_link": "https://pmkisan.gov.in",
                "description": {
                    "en": "PM-KISAN is a central sector scheme with 100% funding from Government of India. It provides income support of ₹6,000 per year to all landholding farmer families directly into their bank accounts in three equal installments of ₹2,000 each.",
                    "hi": "पीएम-किसान भारत सरकार से 100% वित्त पोषण के साथ एक केंद्रीय क्षेत्र की योजना है। यह सभी भूमिधारक किसान परिवारों को ₹6,000 प्रति वर्ष की आय सहायता सीधे उनके बैंक खातों में ₹2,000 की तीन समान किस्तों में प्रदान करता है।",
                    "ta": "PM-KISAN என்பது இந்திய அரசாங்கத்தின் 100% நிதியுதவியுடன் கூடிய ஒரு மத்திய துறைத் திட்டமாகும். இது அனைத்து நிலம் வைத்திருக்கும் விவசாயக் குடும்பங்களுக்கும் ஆண்டுக்கு ₹6,000 வருமான உதவியை மூன்று சம தவணைகளாக ₹2,000 வீதம் நேரடியாக அவர்களின் வங்கிக் கணக்குகளில் வழங்குகிறது.",
                    "ml": "ഇന്ത്യാ ഗവൺമെന്റിൽ നിന്നുള്ള 100% ധനസഹായത്തോടെയുള്ള ഒരു കേന്ദ്ര മേഖലാ പദ്ധതിയാണ് PM-KISAN. ഭൂമിയുള്ള എല്ലാ കർഷക കുടുംബങ്ങൾക്കും അവരുടെ ബാങ്ക് അക്കൗണ്ടുകളിലേക്ക് നേരിട്ട് വർഷം തോറും 6,000 രൂപ വീതം 2,000 രൂപ വീതമുള്ള മൂന്ന് ഗഡുക്കളായി നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 2. PMFBY  (Insurance — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "type": "Insurance",
                "benefit": "Comprehensive Crop Insurance up to ₹2,00,000",
                "benefit_amount": 200000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records / Tenancy Agreement",
                    "Bank Account Details",
                    "Sowing Certificate from Patwari",
                    "Crop Declaration Form",
                ],
                "official_link": "https://pmfby.gov.in",
                "description": {
                    "en": "PMFBY provides comprehensive insurance coverage against failure of the crop thus helping in stabilizing the income of the farmers. Premium is very low: 2% for Kharif crops, 1.5% for Rabi crops, and 5% for commercial/horticultural crops.",
                    "hi": "PMFBY फसल की विफलता के खिलाफ व्यापक बीमा कवरेज प्रदान करता है, जिससे किसानों की आय को स्थिर करने में मदद मिलती है। प्रीमियम बहुत कम है: खरीफ फसलों के लिए 2%, रबी फसलों के लिए 1.5% और वाणिज्यिक/बागवानी फसलों के लिए 5%।",
                    "ta": "PMFBY பயிர் தோல்விக்கு எதிரான விரிவான காப்பீட்டுத் தொகையை வழங்குகிறது. பிரீமியம் மிகவும் குறைவு: காரீஃப் பயிர்களுக்கு 2%, ரபி பயிர்களுக்கு 1.5% மற்றும் வணிக/தோட்டக்கலை பயிர்களுக்கு 5%.",
                    "ml": "വിളനാശത്തിനെതിരെ PMFBY സമഗ്രമായ ഇൻഷുറൻസ് പരിരക്ഷ നൽകുന്നു. പ്രീമിയം വളരെ കുറവാണ്: ഖാരിഫ് വിളകൾക്ക് 2%, റാബി വിളകൾക്ക് 1.5%, വാണിജ്യ/ഹോർട്ടികൾച്ചറൽ വിളകൾക്ക് 5%.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 3. KCC  (Loan — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Kisan Credit Card (KCC)",
                "type": "Loan",
                "benefit": "Low Interest Loan up to ₹3,00,000 (Eff. 4%)",
                "benefit_amount": 300000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "PAN Card",
                    "Land Ownership Documents",
                    "Passport Size Photos",
                    "Bank Account Details",
                ],
                "official_link": "https://pmkisan.gov.in/KCC.aspx",
                "description": {
                    "en": "Kisan Credit Card scheme provides adequate and timely credit support to farmers for their cultivation and other needs. Beneficiaries get loans at 7% interest, with 3% subvention for prompt repayment (effective 4%).",
                    "hi": "किसान क्रेडिट कार्ड योजना किसानों को उनकी खेती और अन्य जरूरतों के लिए पर्याप्त और समय पर ऋण सहायता प्रदान करती है। लाभार्थियों को 7% ब्याज पर ऋण मिलता है, जिसमें समय पर भुगतान के लिए 3% की छूट मिलती है।",
                    "ta": "கிசான் கிரெடிட் கார்டு திட்டம் விவசாயிகளுக்கு 7% வட்டியில் கடன் வழங்குகிறது, உடனடித் திருப்பிசெலுத்தலுக்கு 3% மானியம் (பயனுள்ள 4%).",
                    "ml": "കിസാൻ ക്രെഡിറ്റ് കാർഡ് പദ്ധതി 7% പലിശ നിരക്കിൽ വായ്പ നൽകുന്നു, കൃത്യസമയത്ത് തിരിച്ചടയ്ക്കുന്നതിന് 3% സബ്സിഡി (ഫലപ്രദമായ 4%).",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 4. Soil Health Card  (Service — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Soil Health Card (SHC)",
                "type": "Service",
                "benefit": "Free Soil Health Report & Recommendations",
                "benefit_amount": 500,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Village / Block Details",
                ],
                "official_link": "https://soilhealth.dac.gov.in",
                "description": {
                    "en": "The scheme issues soil health cards to farmers every 3 years with information on 12 parameters (N,P,K, etc.) and recommendations on fertilizer usage.",
                    "hi": "यह योजना हर 3 साल में किसानों को मृदा स्वास्थ्य कार्ड जारी करती है।",
                    "ta": "ஒவ்வொரு 3 வருடத்திற்கும் விவசாயிகளுக்கு மண் ஆரோக்கிய அட்டை வழங்கப்படுகிறது.",
                    "ml": "ഓരോ 3 വർഷത്തിലും കർഷകർക്ക് സോയിൽ ഹെൽത്ത് കാർഡ് നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 5. PMKSY  (Subsidy — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
                "type": "Subsidy",
                "benefit": "55% subsidy on micro irrigation for small farmers",
                "benefit_amount": 50000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Bank Account Details",
                    "Irrigation Equipment Quotation",
                ],
                "official_link": "https://pmksy.gov.in",
                "description": {
                    "en": "PMKSY - Per Drop More Crop promotes efficient water use through drip and sprinkler irrigation. Subsidy up to 55% for small/marginal farmers and 45% for others.",
                    "hi": "PMKSY - प्रति बूंद अधिक फसल। छोटे किसानों के लिए 55% तक सब्सिडी।",
                    "ta": "PMKSY - ஒரு சொட்டுக்கு அதிக பயிர். சிறு விவசாயிகளுக்கு 55% வரை மானியம்.",
                    "ml": "PMKSY - ചെറുകിട കർഷകർക്ക് 55% വരെ സബ്സിഡി.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 6. e-NAM  (Marketing — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "e-National Agriculture Market (e-NAM)",
                "type": "Marketing",
                "benefit": "Online Trading Platform for Better Prices",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Bank Account Details",
                    "Mobile Number",
                ],
                "official_link": "https://enam.gov.in",
                "description": {
                    "en": "e-NAM is a pan-India electronic trading portal networking existing APMC mandis to create a unified national market for agricultural commodities.",
                    "hi": "e-NAM एक अखिल भारतीय इलेक्ट्रॉनिक ट्रेडिंग पोर्टल है।",
                    "ta": "e-NAM என்பது ஒரு பான்-இந்திய மின்னணு வர்த்தக தளமாகும்.",
                    "ml": "e-NAM ഒരു പാൻ-ഇന്ത്യ ഇലക്ട്രോണിക് ട്രേഡിംഗ് പോർട്ടലാണ്.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 7. PKVY  (Subsidy — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Paramparagat Krishi Vikas Yojana (PKVY)",
                "type": "Subsidy",
                "benefit": "₹50,000/ha for Organic Farming (3 years)",
                "benefit_amount": 50000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Organic Farming Declaration",
                    "Cluster Group Registration",
                ],
                "official_link": "https://pgsindia-ncof.gov.in",
                "description": {
                    "en": "Promotes organic farming through a cluster approach. ₹50,000/hectare for 3 years, of which ₹31,000 goes directly to farmers via DBT.",
                    "hi": "क्लस्टर दृष्टिकोण के माध्यम से जैविक खेती को बढ़ावा देता है।",
                    "ta": "கிளஸ்டர் அணுகுமுறை மூலம் இயற்கை விவசாயத்தை ஊக்குவிக்கிறது.",
                    "ml": "ക്ലസ്റ്റർ സമീപനത്തിലൂടെ ജൈവകൃഷി പ്രോത്സാഹിപ്പിക്കുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 8. AIF  (Loan — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Agriculture Infrastructure Fund (AIF)",
                "type": "Loan",
                "benefit": "3% interest subvention on loans up to ₹2 Crore",
                "benefit_amount": 20000000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "PAN Card",
                    "Land Records",
                    "Project Report",
                    "Bank Account Details",
                ],
                "official_link": "https://agriinfra.dac.gov.in",
                "description": {
                    "en": "AIF provides medium-to-long term debt financing for post-harvest management infrastructure. 3% interest subvention on loans up to ₹2 crore.",
                    "hi": "AIF फसल कटाई के बाद प्रबंधन ढांचे के लिए ₹2 करोड़ तक ऋण पर 3% ब्याज छूट देता है।",
                    "ta": "AIF அறுவடைக்குப் பிந்தைய கட்டமைப்புக்கான கடனுக்கு 3% வட்டி மானியம்.",
                    "ml": "AIF വിളവെടുപ്പിനുശേഷമുള്ള ഇൻഫ്രയ്ക്ക് 2 കോടി വരെ 3% പലിശ ഇളവ്.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 9. PM-AASHA  (Subsidy — All India — Kharif)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "PM Annadata Aay Sanrakshan Abhiyan (PM-AASHA)",
                "type": "Subsidy",
                "benefit": "MSP-based price support for oilseeds, pulses, copra",
                "benefit_amount": 25000,
                "states": ["All"],
                "crops": ["Groundnut", "Soybean", "Sunflower", "Moong", "Urad", "Tur", "Copra"],
                "min_land": 0,
                "max_land": 100,
                "season": "Kharif",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Bank Account Details",
                    "Crop Sowing Declaration",
                ],
                "official_link": "https://agricoop.nic.in",
                "description": {
                    "en": "PM-AASHA ensures MSP-based price support for oilseeds, pulses, and copra farmers when market prices fall below MSP.",
                    "hi": "PM-AASHA तिलहन, दलहन और कोपरा किसानों के लिए MSP-आधारित मूल्य समर्थन।",
                    "ta": "PM-AASHA எண்ணெய் வித்துக்கள், பருப்பு வகைகள் விவசாயிகளுக்கு MSP ஆதரவு.",
                    "ml": "PM-AASHA എണ്ണക്കുരുക്കൾ, പയർ കർഷകർക്ക് MSP ആധാരമായ വില പിന്തുണ.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 10. SMAM  (Subsidy — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Sub-Mission on Agricultural Mechanization (SMAM)",
                "type": "Subsidy",
                "benefit": "40-50% subsidy on farm machinery",
                "benefit_amount": 75000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Bank Account Details",
                    "Caste Certificate (if SC/ST)",
                    "Machine Purchase Quotation",
                ],
                "official_link": "https://agrimachinery.nic.in",
                "description": {
                    "en": "SMAM provides 40-50% subsidy on purchase of farm machinery and equipment to promote mechanization. Higher assistance for SC/ST, NE states.",
                    "hi": "SMAM कृषि मशीनरी खरीद पर 40-50% सब्सिडी देता है।",
                    "ta": "SMAM விவசாய இயந்திரங்கள் வாங்குவதற்கு 40-50% மானியம்.",
                    "ml": "SMAM കാർഷിക യന്ത്രങ്ങൾ വാങ്ങുന്നതിന് 40-50% സബ്സിഡി.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 11. NABARD Watershed (Subsidy — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "NABARD Watershed Development Fund",
                "type": "Subsidy",
                "benefit": "₹12,000/ha for watershed development",
                "benefit_amount": 12000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Community Group Registration",
                ],
                "official_link": "https://www.nabard.org",
                "description": {
                    "en": "NABARD Watershed Development Fund supports integrated watershed management for sustainable agriculture and natural resource conservation.",
                    "hi": "NABARD जलसंभर विकास कोष सतत कृषि के लिए जलसंभर प्रबंधन का समर्थन करता है।",
                    "ta": "NABARD நீர்நிலை மேம்பாட்டு நிதி நிலையான விவசாயத்தை ஆதரிக்கிறது.",
                    "ml": "NABARD വാട്ടർഷെഡ് ഡെവലപ്മെന്റ് ഫണ്ട് സുസ്ഥിര കൃഷിയെ പിന്തുണയ്ക്കുന്നു.",
                },
            },

            # ═══════════════════════════════════════════════════════════
            # STATE-SPECIFIC SCHEMES (for realistic eligibility filtering)
            # ═══════════════════════════════════════════════════════════

            # ───────────────────────────────────────────────────────────
            # 12. Tamil Nadu — Rice Insurance  (State-specific, Kharif)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Tamil Nadu Crop Insurance (State Supplementary)",
                "type": "Insurance",
                "benefit": "Additional ₹25,000 crop insurance top-up",
                "benefit_amount": 25000,
                "states": ["Tamil Nadu"],
                "crops": ["Rice", "Sugarcane", "Cotton"],
                "min_land": 0,
                "max_land": 10,
                "season": "Kharif",
                "documents_required": [
                    "Aadhaar Card",
                    "Patta (Land Document)",
                    "Chitta & Adangal",
                    "Bank Passbook",
                    "PMFBY Enrollment Proof",
                ],
                "official_link": "https://www.tn.gov.in/scheme",
                "description": {
                    "en": "State supplementary crop insurance scheme providing additional coverage on top of PMFBY for Tamil Nadu farmers growing rice, sugarcane and cotton.",
                    "hi": "तमिलनाडु राज्य पूरक फसल बीमा योजना।",
                    "ta": "தமிழ்நாடு அரசின் கூடுதல் பயிர் காப்பீட்டுத் திட்டம் - PMFBY மேல் கூடுதல் காப்பீடு.",
                    "ml": "തമിഴ്‌നാട് സംസ്ഥാന അധിക വിള ഇൻഷുറൻസ് പദ്ധതി.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 13. Kerala — Coconut Subsidy  (State-specific)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Kerala Coconut Palm Insurance Scheme",
                "type": "Insurance",
                "benefit": "₹900/palm insurance coverage",
                "benefit_amount": 900,
                "states": ["Kerala"],
                "crops": ["Coconut"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records (Pattayam)",
                    "Coconut Palm Count Certificate",
                    "Bank Account Details",
                ],
                "official_link": "https://keralaagriculture.gov.in",
                "description": {
                    "en": "Insurance coverage for coconut palms in Kerala against natural calamities, pests, and diseases. Premium is heavily subsidized by the state government.",
                    "hi": "केरल नारियल ताड़ बीमा योजना।",
                    "ta": "கேரளா தேங்காய் மரக் காப்பீட்டுத் திட்டம்.",
                    "ml": "കേരള തെങ്ങ് ഇൻഷുറൻസ് പദ്ധതി — പ്രകൃതി ദുരന്തങ്ങൾ, കീടങ്ങൾ എന്നിവയ്ക്കെതിരെ.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 14. Punjab — Wheat Bonus  (State-specific, Rabi)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Punjab Wheat MSP Bonus Scheme",
                "type": "Subsidy",
                "benefit": "₹200/quintal bonus over MSP for wheat",
                "benefit_amount": 20000,
                "states": ["Punjab"],
                "crops": ["Wheat"],
                "min_land": 0,
                "max_land": 100,
                "season": "Rabi",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records (Fard / Jamabandi)",
                    "Mandi Purchase Receipt",
                    "Bank Account Details",
                ],
                "official_link": "https://punjab.gov.in",
                "description": {
                    "en": "Punjab state provides an additional ₹200/quintal bonus over the central MSP for wheat sold through authorized mandis during the Rabi procurement season.",
                    "hi": "पंजाब राज्य रबी सीजन में गेहूं के लिए केंद्रीय MSP से ₹200/क्विंटल अतिरिक्त बोनस प्रदान करता है।",
                    "ta": "பஞ்சாப் மாநிலம் ரபி பருவத்தில் கோதுமைக்கு MSP மேல் ₹200/குவிண்டால் போனஸ்.",
                    "ml": "പഞ്ചാബ് റാബി സീസണിൽ ഗോതമ്പിന് MSP-യ്ക്ക് മുകളിൽ ₹200/ക്വിന്റൽ ബോണസ്.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 15. Maharashtra — Jalyukt Shivar Abhiyan (Water conservation)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Jalyukt Shivar Abhiyan (Maharashtra)",
                "type": "Subsidy",
                "benefit": "Free farm pond & water conservation structures",
                "benefit_amount": 75000,
                "states": ["Maharashtra"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 50,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "7/12 Extract (Land Record)",
                    "Bank Account Details",
                    "Gram Panchayat Certificate",
                ],
                "official_link": "https://maharashtra.gov.in",
                "description": {
                    "en": "Jalyukt Shivar Abhiyan provides farm ponds, check dams, and water conservation structures for drought-prone villages in Maharashtra.",
                    "hi": "जलयुक्त शिवार अभियान महाराष्ट्र में सूखाग्रस्त गांवों में तालाब और जल संरक्षण संरचनाएं प्रदान करता है।",
                    "ta": "மகாராஷ்டிராவில் வறட்சிப் பகுதிகளில் குளம் மற்றும் நீர் பாதுகாப்பு கட்டமைப்பு.",
                    "ml": "മഹാരാഷ്ട്രയിലെ വരൾച്ചാ ബാധിത ഗ്രാമങ്ങളിൽ ഫാം കുളങ്ങളും ജല സംരക്ഷണ സൗകര്യങ്ങളും.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 16. Small/Marginal Farmer Support (land < 2 ha)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Small and Marginal Farmers Support Scheme",
                "type": "Subsidy",
                "benefit": "₹10,000 annual input subsidy for small farmers",
                "benefit_amount": 10000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 2,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records (≤ 2 hectares)",
                    "Income Certificate",
                    "Bank Account Details",
                ],
                "official_link": "https://agricoop.nic.in",
                "description": {
                    "en": "Annual input subsidy of ₹10,000 for small and marginal farmers (holding ≤ 2 hectares) to support purchase of seeds, fertilizers, and farm inputs.",
                    "hi": "छोटे और सीमांत किसानों (≤ 2 हेक्टेयर) के लिए ₹10,000 वार्षिक इनपुट सब्सिडी।",
                    "ta": "சிறு மற்றும் குறு விவசாயிகளுக்கு (≤ 2 ஹெக்டேர்) ₹10,000 ஆண்டு உள்ளீடு மானியம்.",
                    "ml": "ചെറുകിട കർഷകർക്ക് (≤ 2 ഹെക്ടർ) ₹10,000 വാർഷിക ഇൻപുട്ട് സബ്സിഡി.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 17. Andhra Pradesh — YSR Rythu Bharosa
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "YSR Rythu Bharosa (Andhra Pradesh)",
                "type": "Income Support",
                "benefit": "₹13,500 per year investment support",
                "benefit_amount": 13500,
                "states": ["Andhra Pradesh"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records (Webland / Pahani)",
                    "Bank Account Details",
                    "Caste Certificate (if applicable)",
                ],
                "official_link": "https://navasakam.ap.gov.in",
                "description": {
                    "en": "YSR Rythu Bharosa provides ₹13,500/year investment support to AP farmers — ₹7,500 from state + ₹6,000 from PM-KISAN.",
                    "hi": "YSR रायथु भरोसा आंध्र प्रदेश किसानों को ₹13,500/वर्ष निवेश सहायता देता है।",
                    "ta": "YSR ரைத்து பரோசா ஆந்திர விவசாயிகளுக்கு ₹13,500/ஆண்டு.",
                    "ml": "YSR റൈത്തു ഭരോസ ആന്ധ്ര കർഷകർക്ക് ₹13,500/വർഷം.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 18. Telangana — Rythu Bandhu
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Rythu Bandhu (Telangana)",
                "type": "Income Support",
                "benefit": "₹10,000/acre/year for investment support",
                "benefit_amount": 10000,
                "states": ["Telangana"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Pattadar Passbook",
                    "Bank Account Details",
                ],
                "official_link": "https://rythubandhu.telangana.gov.in",
                "description": {
                    "en": "Telangana Rythu Bandhu provides ₹10,000 per acre per year (₹5,000 per season) to all landholding farmers for investment support.",
                    "hi": "तेलंगाना रायथु बंधु प्रति एकड़ ₹10,000/वर्ष निवेश सहायता।",
                    "ta": "தெலங்கானா ரைத்து பந்து ஒரு ஏக்கருக்கு ₹10,000/ஆண்டு.",
                    "ml": "തെലങ്കാന റൈത്തു ബന്ധു ഓരോ ഏക്കറിനും ₹10,000/വർഷം.",
                },
            },

            # ═══════════════════════════════════════════════════════════
            # NEW SCHEMES (from agri_schemes_25_production_ready.json)
            # ═══════════════════════════════════════════════════════════

            # ───────────────────────────────────────────────────────────
            # 19. RWBCIS (Weather Index Insurance — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Restructured Weather Based Crop Insurance Scheme (RWBCIS)",
                "type": "Insurance",
                "benefit": "Weather-based fast claim settlement",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Bank Account Details",
                ],
                "official_link": "https://pmfby.gov.in",
                "description": {
                    "en": "RWBCIS provides weather index-based crop insurance with fast, automated claim settlements triggered by weather parameters rather than crop loss assessment.",
                    "hi": "RWBCIS मौसम सूचकांक आधारित फसल बीमा प्रदान करता है जिसमें तेजी से दावा निपटान होता है।",
                    "ta": "RWBCIS வானிலை அடிப்படையிலான பயிர் காப்பீடு வழங்குகிறது, விரைவான தீர்வு செயல்முறையுடன்.",
                    "ml": "RWBCIS കാലാവസ്ഥ സൂചിക അടിസ്ഥാനമാക്കിയുള്ള വിള ഇൻഷുറൻസ് നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 20. MISS (Interest Subvention — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Modified Interest Subvention Scheme (MISS)",
                "type": "Loan",
                "benefit": "Interest reduced to 4% on prompt repayment",
                "benefit_amount": 300000,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "KCC Card",
                    "Bank Account Details",
                ],
                "official_link": "https://agricoop.nic.in",
                "description": {
                    "en": "MISS provides interest subvention on short-term crop loans up to Rs 3,00,000. Effective interest rate is reduced to 4% for farmers who repay promptly.",
                    "hi": "MISS ₹3,00,000 तक के अल्पकालिक फसल ऋण पर ब्याज सब्सिडी प्रदान करता है।",
                    "ta": "MISS ₹3,00,000 வரையிலான குறுகிய கால பயிர் கடன்களுக்கு வட்டி மானியம் வழங்குகிறது.",
                    "ml": "MISS ₹3,00,000 വരെയുള്ള ഹ്രസ്വകാല വിള വായ്പയ്ക്ക് പലിശ സബ്‌വെൻഷൻ നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 21. PMMSY (Fisheries — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Pradhan Mantri Matsya Sampada Yojana (PMMSY)",
                "type": "Subsidy",
                "benefit": "40%-60% subsidy for fisheries",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["Fisheries"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Project Proposal",
                    "Bank Account Details",
                ],
                "official_link": "https://www.myscheme.gov.in/schemes/pmmsy",
                "description": {
                    "en": "PMMSY aims to bring about a Blue Revolution through sustainable development of fisheries sector with 40-60% subsidy for fish farming infrastructure and aquaculture.",
                    "hi": "PMMSY मत्स्य पालन क्षेत्र के सतत विकास के लिए 40-60% सब्सिडी प्रदान करता है।",
                    "ta": "PMMSY மீன் வளர்ப்பு உள்கட்டமைப்புக்கு 40-60% மானியம் வழங்குகிறது.",
                    "ml": "PMMSY മത്സ്യകൃഷി ഇൻഫ്രാസ്ട്രക്ചറിന് 40-60% സബ്‌സിഡി നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 22. RGM (Animal Husbandry — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Rashtriya Gokul Mission (RGM)",
                "type": "Subsidy",
                "benefit": "Breed improvement & dairy infrastructure support",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["Livestock"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Livestock Details",
                ],
                "official_link": "https://dahd.nic.in",
                "description": {
                    "en": "RGM promotes breed improvement and dairy infrastructure development to enhance milk productivity and preserve indigenous cattle breeds.",
                    "hi": "RGM नस्ल सुधार और डेयरी बुनियादी ढांचे के विकास को बढ़ावा देता है।",
                    "ta": "RGM இனப்பெருக்க மேம்பாடு மற்றும் பால் பண்ணை உள்கட்டமைப்பை ஊக்குவிக்கிறது.",
                    "ml": "RGM ഇനം മെച്ചപ്പെടുത്തലും ഡയറി ഇൻഫ്രാസ്ട്രക്ചർ വികസനവും പ്രോത്സാഹിപ്പിക്കുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 23. Digital Agriculture Mission (All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Digital Agriculture Mission",
                "type": "Service",
                "benefit": "Farmer Digital ID & AgriStack Access",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                ],
                "official_link": "https://agriwelfare.gov.in",
                "description": {
                    "en": "Digital Agriculture Mission creates a digital ecosystem for Indian agriculture including Farmer Digital IDs, AgriStack, and AI/ML-based advisory services for crop management.",
                    "hi": "डिजिटल कृषि मिशन किसान डिजिटल आईडी, एग्रीस्टैक और एआई-आधारित सलाहकार सेवाएं बनाता है।",
                    "ta": "டிஜிட்டல் வேளாண்மை மிஷன் விவசாயி டிஜிட்டல் ஐடி மற்றும் AI ஆலோசனை சேவைகளை உருவாக்குகிறது.",
                    "ml": "ഡിജിറ്റൽ അഗ്രിക്കൾച്ചർ മിഷൻ കർഷക ഡിജിറ്റൽ ഐഡിയും AI ഉപദേശ സേവനങ്ങളും സൃഷ്ടിക്കുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 24. PSS (MSP Procurement — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Price Support Scheme (PSS)",
                "type": "Subsidy",
                "benefit": "Government procurement at MSP",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["Pulses", "Oilseeds", "Copra"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                ],
                "official_link": "https://www.myscheme.gov.in/schemes/pss",
                "description": {
                    "en": "PSS provides government procurement of pulses, oilseeds, and copra at MSP to protect farmers from price crashes during seasons of excess production.",
                    "hi": "PSS दलहन, तिलहन और कोपरा की MSP पर सरकारी खरीद प्रदान करता है।",
                    "ta": "PSS பருப்பு வகைகள், எண்ணெய் விதைகள், கொப்பரை ஆகியவற்றை MSP-யில் அரசு கொள்முதல் செய்கிறது.",
                    "ml": "PSS പയറുവർഗ്ഗങ്ങൾ, എണ്ണക്കുരുക്കൾ, കൊപ്ര എന്നിവ MSP-യിൽ സർക്കാർ സംഭരണം.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 25. PDPS (Price Compensation — All India)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Price Deficiency Payment Scheme (PDPS)",
                "type": "Subsidy",
                "benefit": "Difference between MSP & market price",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["Oilseeds", "Pulses"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Market Sale Receipt",
                ],
                "official_link": "https://agricoop.nic.in",
                "description": {
                    "en": "PDPS pays farmers the difference between MSP and market selling price when commodity prices fall below MSP, without physical procurement by the government.",
                    "hi": "PDPS किसानों को MSP और बाजार मूल्य के बीच अंतर का भुगतान करता है।",
                    "ta": "PDPS MSP-க்கும் சந்தை விலைக்கும் இடையிலான வேறுபாட்டை விவசாயிகளுக்கு செலுத்துகிறது.",
                    "ml": "PDPS MSP-യും വിപണി വിലയും തമ്മിലുള്ള വ്യത്യാസം കർഷകർക്ക് നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 26. Annadatha Sukhibhav (Andhra Pradesh)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Annadatha Sukhibhav Scheme",
                "type": "Income Support",
                "benefit": "₹20,000 per year",
                "benefit_amount": 20000,
                "states": ["Andhra Pradesh"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                    "Bank Account Details",
                ],
                "official_link": "https://apagriculture.gov.in",
                "description": {
                    "en": "Annadatha Sukhibhav provides Rs 20,000 per year income support to all registered farmers in Andhra Pradesh.",
                    "hi": "आंध्र प्रदेश के किसानों को ₹20,000 प्रति वर्ष आय सहायता।",
                    "ta": "ஆந்திர பிரதேச விவசாயிகளுக்கு ₹20,000 ஆண்டு வருமான ஆதரவு.",
                    "ml": "ആന്ധ്ര കർഷകർക്ക് ₹20,000 വാർഷിക വരുമാന പിന്തുണ.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 27. Rythu Bharosa (Telangana — different from Rythu Bandhu)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Rythu Bharosa",
                "type": "Income Support",
                "benefit": "₹12,000 per acre per year",
                "benefit_amount": 12000,
                "states": ["Telangana"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Ownership Certificate",
                ],
                "official_link": "https://agriculture.telangana.gov.in",
                "description": {
                    "en": "Rythu Bharosa provides Rs 12,000 per acre per year as investment support to all farmer families in Telangana for crop cultivation expenses.",
                    "hi": "तेलंगाना में किसानों को प्रति एकड़ ₹12,000/वर्ष निवेश सहायता।",
                    "ta": "தெலங்கானா விவசாயிகளுக்கு ஒரு ஏக்கருக்கு ₹12,000/ஆண்டு முதலீட்டு ஆதரவு.",
                    "ml": "തെലങ്കാനയിലെ കർഷകർക്ക് ഓരോ ഏക്കറിനും ₹12,000/വർഷം.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 28. KALIA Scheme (Odisha)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "KALIA Scheme",
                "type": "Income Support",
                "benefit": "₹25,000 over 5 seasons",
                "benefit_amount": 25000,
                "states": ["Odisha"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "SECC Data",
                    "Bank Account Details",
                ],
                "official_link": "https://kalia.odisha.gov.in",
                "description": {
                    "en": "Krushak Assistance for Livelihood and Income Augmentation (KALIA) provides Rs 25,000 financial assistance over 5 seasons to small and marginal farmers in Odisha.",
                    "hi": "ओडिशा के छोटे और सीमांत किसानों को 5 सीजन में ₹25,000 सहायता।",
                    "ta": "ஒடிசா சிறு மற்றும் குறு விவசாயிகளுக்கு 5 பருவங்களில் ₹25,000 உதவி.",
                    "ml": "ഒഡീഷയിലെ ചെറുകിട കർഷകർക്ക് 5 സീസണിൽ ₹25,000 സഹായം.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 29. Mukhya Mantri Kisan Sahay Yojana (Gujarat)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Mukhya Mantri Kisan Sahay Yojana",
                "type": "Subsidy",
                "benefit": "₹20,000–₹25,000 per hectare",
                "benefit_amount": 25000,
                "states": ["Gujarat"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 4,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                ],
                "official_link": "https://ikhedut.gujarat.gov.in",
                "description": {
                    "en": "Gujarat's Mukhya Mantri Kisan Sahay Yojana provides Rs 20,000-25,000 per hectare compensation to farmers for crop loss due to natural calamities (max 4 hectares).",
                    "hi": "गुजरात में प्राकृतिक आपदाओं से फसल हानि पर ₹20,000-₹25,000/हेक्टेयर मुआवजा।",
                    "ta": "குஜராத்தில் இயற்கை பேரழிவால் பயிர் நஷ்டத்திற்கு ₹20,000-₹25,000/ஹெக்டேர் இழப்பீடு.",
                    "ml": "ഗുജറാത്തിൽ പ്രകൃതിദുരന്തങ്ങൾ മൂലമുള്ള വിള നഷ്ടത്തിന് ₹20,000-₹25,000/ഹെക്ടർ നഷ്ടപരിഹാരം.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 30. Mukhyamantri Bhavantar Bhugtan Yojana (Madhya Pradesh)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Mukhyamantri Bhavantar Bhugtan Yojana",
                "type": "Subsidy",
                "benefit": "MSP–Market price difference paid",
                "benefit_amount": 0,
                "states": ["Madhya Pradesh"],
                "crops": ["Soybean", "Maize", "Wheat"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Market Receipt",
                ],
                "official_link": "https://mpkrishi.mp.gov.in",
                "description": {
                    "en": "MP's Bhavantar Bhugtan Yojana compensates farmers by paying the difference between MSP and market selling price for soybean, maize, wheat, and other notified crops.",
                    "hi": "मध्य प्रदेश में सोयाबीन, मक्का, गेहूं के लिए MSP और बाजार मूल्य का अंतर भुगतान।",
                    "ta": "மத்திய பிரதேசத்தில் சோயாபீன், மக்காச்சோளம், கோதுமை MSP-சந்தை விலை வேறுபாடு செலுத்தப்படும்.",
                    "ml": "മധ്യപ്രദേശിൽ സോയാബീൻ, ചോളം, ഗോതമ്പ് MSP-വിപണി വിലയുടെ വ്യത്യാസം നൽകുന്നു.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 31. Mukhya Mantri Krishi Ashirwad Yojana (Jharkhand)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Mukhya Mantri Krishi Ashirwad Yojana",
                "type": "Income Support",
                "benefit": "₹5,000 per acre (max 5 acres)",
                "benefit_amount": 25000,
                "states": ["Jharkhand"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 5,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                ],
                "official_link": "https://agri.jharkhand.gov.in",
                "description": {
                    "en": "Jharkhand's Krishi Ashirwad Yojana provides Rs 5,000 per acre (max 5 acres) to small and marginal farmers for investment in seeds, fertilizers, and farm inputs.",
                    "hi": "झारखंड में छोटे किसानों को ₹5,000/एकड़ (अधिकतम 5 एकड़) सहायता।",
                    "ta": "ஜார்கண்ட்டில் சிறு விவசாயிகளுக்கு ₹5,000/ஏக்கர் (அதிகபட்சம் 5 ஏக்கர்) உதவி.",
                    "ml": "ജാർഖണ്ഡിൽ ചെറുകിട കർഷകർക്ക് ₹5,000/ഏക്കർ (പരമാവധി 5 ഏക്കർ) സഹായം.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 32. Banglar Shasya Bima (West Bengal)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Banglar Shasya Bima",
                "type": "Insurance",
                "benefit": "100% premium paid by state",
                "benefit_amount": 0,
                "states": ["West Bengal"],
                "crops": ["Rice", "Wheat"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Records",
                ],
                "official_link": "https://banglashasyabima.net",
                "description": {
                    "en": "West Bengal's Banglar Shasya Bima provides 100% state-funded crop insurance for rice and wheat farmers, with no premium payable by farmers.",
                    "hi": "पश्चिम बंगाल में धान और गेहूं के लिए 100% राज्य-वित्त पोषित फसल बीमा।",
                    "ta": "மேற்கு வங்கத்தில் நெல், கோதுமைக்கு 100% மாநில நிதியுதவி பயிர் காப்பீடு.",
                    "ml": "പശ്ചിമ ബംഗാളിൽ നെല്ല്, ഗോതമ്പ് കർഷകർക്ക് 100% സംസ്ഥാന ധനസഹായത്തോടെയുള്ള വിള ഇൻഷുറൻസ്.",
                },
            },

            # ───────────────────────────────────────────────────────────
            # 33. Krishi Bhagya Scheme (Karnataka)
            # ───────────────────────────────────────────────────────────
            {
                "scheme_name": "Krishi Bhagya Scheme",
                "type": "Subsidy",
                "benefit": "Up to ₹1,00,000 subsidy",
                "benefit_amount": 100000,
                "states": ["Karnataka"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": [
                    "Aadhaar Card",
                    "Land Ownership Proof",
                ],
                "official_link": "https://raitamitra.karnataka.gov.in",
                "description": {
                    "en": "Karnataka's Krishi Bhagya Scheme provides up to Rs 1,00,000 subsidy for farm ponds, polyhouse construction, and micro-irrigation systems to boost water management.",
                    "hi": "कर्नाटक में फार्म तालाब, पॉलीहाउस और सूक्ष्म सिंचाई के लिए ₹1,00,000 तक सब्सिडी।",
                    "ta": "கர்நாடகாவில் பண்ணை குளம், பாலிஹவுஸ், நுண்ணீர்ப் பாசனத்திற்கு ₹1,00,000 வரை மானியம்.",
                    "ml": "കർണാടകയിൽ ഫാം കുളം, പോളിഹൗസ്, മൈക്രോ ഇറിഗേഷനു ₹1,00,000 വരെ സബ്സിഡി.",
                },
            },
        ]

        result = schemes_col.insert_many(schemes)
        print(f"\n✅ Inserted {len(result.inserted_ids)} schemes into the database.")

        # Re-initialise indexes
        print("Re-initializing indexes...")
        init_indexes()

        print(f"\nDatabase seeded successfully with {len(schemes)} schemes.")
        print("Scheme types: " + ", ".join(sorted(set(s["type"] for s in schemes))))
        print("States covered: " + ", ".join(sorted(set(
            st for s in schemes for st in s["states"]
        ))))

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        if hasattr(e, "details"):
            print("Error details:")
            pprint(e.details)


if __name__ == "__main__":
    seed_database()
