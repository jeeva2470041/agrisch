"""
AgriScheme Backend - Add new schemes from JSON file.

Reads agri_schemes_25_production_ready.json, compares against existing
schemes in the database by scheme_name, and only inserts schemes that
do not already exist. Normalises data to match the existing schema
(e.g. "All India" -> "All", null -> defaults, adds descriptions).

Usage:
    python add_new_schemes.py
"""
import json
import os
from db import get_schemes_collection, init_indexes


# ── State normalisation map ─────────────────────────────────────────────────
# The eligibility engine matches on "All" — JSON file uses "All India", etc.
STATE_NORMALISE = {
    "All India": "All",
    "Participating States": "All",  # PDPS applies via participating states
}


def _normalise_states(states_list):
    """Convert state names to match our DB convention."""
    return [STATE_NORMALISE.get(s, s) for s in states_list]


def _normalise_crops(crops_list):
    """Convert crop names to match our DB convention."""
    crop_map = {
        "All Crops": "All",
        "All": "All",
        "All Notified Crops": "All",
        "Food Crops": "All",
        "Agriculture": "All",
    }
    normalised = set()
    for c in crops_list:
        mapped = crop_map.get(c)
        if mapped:
            normalised.add(mapped)
        else:
            normalised.add(c)
    # If "All" is present alongside specific crops, keep "All"
    if "All" in normalised:
        return ["All"]
    return sorted(normalised)


def _normalise_season(season):
    """Normalise season strings."""
    if not season or season in ("All", "all"):
        return "All"
    if season in ("Kharif/Rabi", "kharif/rabi"):
        return "All"  # Applies to both seasons
    return season


# ── Localized description templates ─────────────────────────────────────────
DESCRIPTIONS = {
    "Restructured Weather Based Crop Insurance Scheme (RWBCIS)": {
        "en": "RWBCIS provides weather index-based crop insurance with fast, automated claim settlements triggered by weather parameters rather than crop loss assessment.",
        "hi": "RWBCIS मौसम सूचकांक आधारित फसल बीमा प्रदान करता है जिसमें तेजी से दावा निपटान होता है।",
        "ta": "RWBCIS வானிலை அடிப்படையிலான பயிர் காப்பீடு வழங்குகிறது, விரைவான தீர்வு செயல்முறையுடன்.",
        "ml": "RWBCIS കാലാവസ്ഥ സൂചിക അടിസ്ഥാനമാക്കിയുള്ള വിള ഇൻഷുറൻസ് നൽകുന്നു.",
    },
    "Modified Interest Subvention Scheme (MISS)": {
        "en": "MISS provides interest subvention on short-term crop loans up to Rs 3,00,000. Effective interest rate is reduced to 4% for farmers who repay promptly.",
        "hi": "MISS ₹3,00,000 तक के अल्पकालिक फसल ऋण पर ब्याज सब्सिडी प्रदान करता है। समय पर भुगतान पर प्रभावी ब्याज दर 4% तक कम हो जाती है।",
        "ta": "MISS ₹3,00,000 வரையிலான குறுகிய கால பயிர் கடன்களுக்கு வட்டி மானியம் வழங்குகிறது.",
        "ml": "MISS ₹3,00,000 വരെയുള്ള ഹ്രസ്വകാല വിള വായ്പയ്ക്ക് പലിശ സബ്‌വെൻഷൻ നൽകുന്നു.",
    },
    "Pradhan Mantri Matsya Sampada Yojana (PMMSY)": {
        "en": "PMMSY aims to bring about a Blue Revolution through sustainable development of fisheries sector with 40-60% subsidy for fish farming infrastructure and aquaculture.",
        "hi": "PMMSY मत्स्य पालन क्षेत्र के सतत विकास के लिए 40-60% सब्सिडी प्रदान करता है।",
        "ta": "PMMSY மீன் வளர்ப்பு உள்கட்டமைப்புக்கு 40-60% மானியம் வழங்குகிறது.",
        "ml": "PMMSY മത്സ്യകൃഷി ഇൻഫ്രാസ്ട്രക്ചറിന് 40-60% സബ്‌സിഡി നൽകുന്നു.",
    },
    "Rashtriya Gokul Mission (RGM)": {
        "en": "RGM promotes breed improvement and dairy infrastructure development to enhance milk productivity and preserve indigenous cattle breeds.",
        "hi": "RGM नस्ल सुधार और डेयरी बुनियादी ढांचे के विकास को बढ़ावा देता है।",
        "ta": "RGM இனப்பெருக்க மேம்பாடு மற்றும் பால் பண்ணை உள்கட்டமைப்பை ஊக்குவிக்கிறது.",
        "ml": "RGM ഇനം മെച്ചപ്പെടുത്തലും ഡയറി ഇൻഫ്രാസ്ട്രക്ചർ വികസനവും പ്രോത്സാഹിപ്പിക്കുന്നു.",
    },
    "Digital Agriculture Mission": {
        "en": "Digital Agriculture Mission creates a digital ecosystem for Indian agriculture including Farmer Digital IDs, AgriStack, and AI/ML-based advisory services for crop management.",
        "hi": "डिजिटल कृषि मिशन किसान डिजिटल आईडी, एग्रीस्टैक और एआई-आधारित सलाहकार सेवाएं बनाता है।",
        "ta": "டிஜிட்டல் வேளாண்மை மிஷன் விவசாயி டிஜிட்டல் ஐடி மற்றும் AI ஆலோசனை சேவைகளை உருவாக்குகிறது.",
        "ml": "ഡിജിറ്റൽ അഗ്രിക്കൾച്ചർ മിഷൻ കർഷക ഡിജിറ്റൽ ഐഡിയും AI ഉപദേശ സേവനങ്ങളും സൃഷ്ടിക്കുന്നു.",
    },
    "Price Support Scheme (PSS)": {
        "en": "PSS provides government procurement of pulses, oilseeds, and copra at MSP to protect farmers from price crashes during seasons of excess production.",
        "hi": "PSS दलहन, तिलहन और कोपरा की MSP पर सरकारी खरीद प्रदान करता है।",
        "ta": "PSS பருப்பு வகைகள், எண்ணெய் விதைகள், கொப்பரை ஆகியவற்றை MSP-யில் அரசு கொள்முதல் செய்கிறது.",
        "ml": "PSS പയറുവർഗ്ഗങ്ങൾ, എണ്ണക്കുരുക്കൾ, കൊപ്ര എന്നിവ MSP-യിൽ സർക്കാർ സംഭരണം.",
    },
    "Price Deficiency Payment Scheme (PDPS)": {
        "en": "PDPS pays farmers the difference between MSP and market selling price when commodity prices fall below MSP, without physical procurement by the government.",
        "hi": "PDPS किसानों को MSP और बाजार मूल्य के बीच अंतर का भुगतान करता है।",
        "ta": "PDPS MSP-க்கும் சந்தை விலைக்கும் இடையிலான வேறுபாட்டை விவசாயிகளுக்கு செலுத்துகிறது.",
        "ml": "PDPS MSP-യും വിപണി വിലയും തമ്മിലുള്ള വ്യത്യാസം കർഷകർക്ക് നൽകുന്നു.",
    },
    "Annadatha Sukhibhav Scheme": {
        "en": "Annadatha Sukhibhav provides Rs 20,000 per year income support to all registered farmers in Andhra Pradesh, replacing the earlier YSR Rythu Bharosa payments.",
        "hi": "आंध्र प्रदेश के किसानों को ₹20,000 प्रति वर्ष आय सहायता।",
        "ta": "ஆந்திர பிரதேச விவசாயிகளுக்கு ₹20,000 ஆண்டு வருமான ஆதரவு.",
        "ml": "ആന്ധ്ര കർഷകർക്ക് ₹20,000 വാർഷിക വരുമാന പിന്തുണ.",
    },
    "Rythu Bharosa": {
        "en": "Rythu Bharosa provides Rs 12,000 per acre per year as investment support to all farmer families in Telangana for crop cultivation expenses.",
        "hi": "तेलंगाना में किसानों को प्रति एकड़ ₹12,000/वर्ष निवेश सहायता।",
        "ta": "தெலங்கானா விவசாயிகளுக்கு ஒரு ஏக்கருக்கு ₹12,000/ஆண்டு முதலீட்டு ஆதரவு.",
        "ml": "തെലങ്കാനയിലെ കർഷകർക്ക് ഓരോ ഏക്കറിനും ₹12,000/വർഷം.",
    },
    "KALIA Scheme": {
        "en": "Krushak Assistance for Livelihood and Income Augmentation (KALIA) provides Rs 25,000 financial assistance over 5 seasons to small and marginal farmers in Odisha.",
        "hi": "ओडिशा के छोटे और सीमांत किसानों को 5 सीजन में ₹25,000 सहायता।",
        "ta": "ஒடிசா சிறு மற்றும் குறு விவசாயிகளுக்கு 5 பருவங்களில் ₹25,000 உதவி.",
        "ml": "ഒഡീഷയിലെ ചെറുകിട കർഷകർക്ക് 5 സീസണിൽ ₹25,000 സഹായം.",
    },
    "Mukhya Mantri Kisan Sahay Yojana": {
        "en": "Gujarat's Mukhya Mantri Kisan Sahay Yojana provides Rs 20,000-25,000 per hectare compensation to farmers for crop loss due to natural calamities (max 4 hectares).",
        "hi": "गुजरात में प्राकृतिक आपदाओं से फसल हानि पर ₹20,000-₹25,000/हेक्टेयर मुआवजा।",
        "ta": "குஜராத்தில் இயற்கை பேரழிவால் பயிர் நஷ்டத்திற்கு ₹20,000-₹25,000/ஹெக்டேர் இழப்பீடு.",
        "ml": "ഗുജറാത്തിൽ പ്രകൃതിദുരന്തങ്ങൾ മൂലമുള്ള വിള നഷ്ടത്തിന് ₹20,000-₹25,000/ഹെക്ടർ നഷ്ടപരിഹാരം.",
    },
    "Mukhyamantri Bhavantar Bhugtan Yojana": {
        "en": "MP's Bhavantar Bhugtan Yojana compensates farmers by paying the difference between MSP and market selling price for soybean, maize, wheat, and other notified crops.",
        "hi": "मध्य प्रदेश में सोयाबीन, मक्का, गेहूं के लिए MSP और बाजार मूल्य का अंतर भुगतान।",
        "ta": "மத்திய பிரதேசத்தில் சோயாபீன், மக்காச்சோளம், கோதுமை MSP-சந்தை விலை வேறுபாடு செலுத்தப்படும்.",
        "ml": "മധ്യപ്രദേശിൽ സോയാബീൻ, ചോളം, ഗോതമ്പ് MSP-വിപണി വിലയുടെ വ്യത്യാസം നൽകുന്നു.",
    },
    "Mukhya Mantri Krishi Ashirwad Yojana": {
        "en": "Jharkhand's Krishi Ashirwad Yojana provides Rs 5,000 per acre (max 5 acres) to small and marginal farmers for investment in seeds, fertilizers, and farm inputs.",
        "hi": "झारखंड में छोटे किसानों को ₹5,000/एकड़ (अधिकतम 5 एकड़) सहायता।",
        "ta": "ஜார்கண்ட்டில் சிறு விவசாயிகளுக்கு ₹5,000/ஏக்கர் (அதிகபட்சம் 5 ஏக்கர்) உதவி.",
        "ml": "ജാർഖണ്ഡിൽ ചെറുകിട കർഷകർക്ക് ₹5,000/ഏക്കർ (പരമാവധി 5 ഏക്കർ) സഹായം.",
    },
    "Banglar Shasya Bima": {
        "en": "West Bengal's Banglar Shasya Bima provides 100% state-funded crop insurance for paddy and wheat farmers, with no premium payable by farmers.",
        "hi": "पश्चिम बंगाल में धान और गेहूं के लिए 100% राज्य-वित्त पोषित फसल बीमा, किसानों को कोई प्रीमियम नहीं देना।",
        "ta": "மேற்கு வங்கத்தில் நெல், கோதுமைக்கு 100% மாநில நிதியுதவி பயிர் காப்பீடு.",
        "ml": "പശ്ചിമ ബംഗാളിൽ നെല്ല്, ഗോതമ്പ് കർഷകർക്ക് 100% സംസ്ഥാന ധനസഹായത്തോടെയുള്ള വിള ഇൻഷുറൻസ്.",
    },
    "Krishi Bhagya Scheme": {
        "en": "Karnataka's Krishi Bhagya Scheme provides up to Rs 1,00,000 subsidy for farm ponds, polyhouse construction, and micro-irrigation systems to boost water management.",
        "hi": "कर्नाटक में फार्म तालाब, पॉलीहाउस और सूक्ष्म सिंचाई के लिए ₹1,00,000 तक सब्सिडी।",
        "ta": "கர்நாடகாவில் பண்ணை குளம், பாலிஹவுஸ், நுண்ணீர்ப் பாசனத்திற்கு ₹1,00,000 வரை மானியம்.",
        "ml": "കർണാടകയിൽ ഫാം കുളം, പോളിഹൗസ്, മൈക്രോ ഇറിഗേഷനു ₹1,00,000 വരെ സബ്സിഡി.",
    },
}


def add_new_schemes():
    """Load JSON file, compare with DB, insert only new schemes."""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "agri_schemes_25_production_ready.json",
    )

    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        new_schemes_raw = json.load(f)

    print(f"Loaded {len(new_schemes_raw)} schemes from JSON file.")

    # ── Get existing scheme names from DB ────────────────────────────────
    schemes_col = get_schemes_collection()
    existing_names = set(
        doc["scheme_name"]
        for doc in schemes_col.find({}, {"scheme_name": 1, "_id": 0})
    )
    print(f"Found {len(existing_names)} existing schemes in DB:")
    for name in sorted(existing_names):
        print(f"  - {name}")

    # ── Process and filter new schemes ───────────────────────────────────
    to_insert = []
    skipped = []

    for raw in new_schemes_raw:
        name = raw["scheme_name"]

        # Skip if already exists
        if name in existing_names:
            skipped.append(name)
            continue

        # ── Normalise fields to match DB schema ──────────────────────────
        scheme = {
            "scheme_name": name,
            "type": raw.get("type", "Other"),
            "benefit": raw.get("benefit", ""),
            "benefit_amount": raw.get("benefit_amount") or 0,
            "states": _normalise_states(raw.get("states", ["All"])),
            "crops": _normalise_crops(raw.get("crops", ["All"])),
            "min_land": raw.get("min_land", 0) or 0,
            "max_land": raw.get("max_land") or 100,  # null -> 100 (no limit)
            "season": _normalise_season(raw.get("season")),
            "documents_required": raw.get("documents_required", []),
            "official_link": raw.get("official_link", ""),
            "description": DESCRIPTIONS.get(name, {
                "en": f"{name} - {raw.get('benefit', '')}",
                "hi": f"{name}",
                "ta": f"{name}",
                "ml": f"{name}",
            }),
        }

        to_insert.append(scheme)

    # ── Report ───────────────────────────────────────────────────────────
    print(f"\nSkipping {len(skipped)} duplicate(s):")
    for name in skipped:
        print(f"  [SKIP] {name}")

    if not to_insert:
        print("\nNo new schemes to add. Database is up to date!")
        return

    print(f"\nInserting {len(to_insert)} new scheme(s):")
    for s in to_insert:
        print(f"  [NEW]  {s['scheme_name']}")
        print(f"         Type: {s['type']} | States: {s['states']} | "
              f"Crops: {s['crops']} | Land: {s['min_land']}-{s['max_land']}ha")

    # ── Insert into MongoDB ──────────────────────────────────────────────
    result = schemes_col.insert_many(to_insert)
    print(f"\nInserted {len(result.inserted_ids)} new schemes.")

    # ── Rebuild indexes ──────────────────────────────────────────────────
    init_indexes()

    # ── Final summary ────────────────────────────────────────────────────
    total = schemes_col.count_documents({})
    all_types = sorted(set(
        doc["type"] for doc in schemes_col.find({}, {"type": 1, "_id": 0})
    ))
    all_states = sorted(set(
        st
        for doc in schemes_col.find({}, {"states": 1, "_id": 0})
        for st in doc.get("states", [])
    ))

    print(f"\n{'='*60}")
    print(f"Database now has {total} total schemes.")
    print(f"Types: {', '.join(all_types)}")
    print(f"States: {', '.join(all_states)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    add_new_schemes()
