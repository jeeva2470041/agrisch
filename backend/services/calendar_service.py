"""
AgriScheme Backend — Crop Calendar Service.
Provides crop growth phase timelines, tasks, and schedules
based on crop, state, season, and sowing date.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ─── Crop Calendar Data ───
# Each crop has phases with relative week offsets from sowing date.
# Tasks within each phase are offset as days from the phase start.

_CROP_CALENDARS = {
    "Rice": {
        "total_weeks": 20,
        "phases": [
            {
                "name": "Nursery Preparation",
                "start_week": 0,
                "end_week": 3,
                "color": "#8BC34A",
                "tasks": [
                    {"title": "Prepare nursery bed", "day_offset": 0, "description": "Level the nursery area. Apply 10 tonnes FYM/hectare."},
                    {"title": "Seed treatment", "day_offset": 1, "description": "Treat seeds with Carbendazim (2g/kg seed) to prevent seed-borne diseases."},
                    {"title": "Sow seeds in nursery", "day_offset": 2, "description": "Sow pre-germinated seeds at 40-60 kg/hectare in wet nursery beds."},
                    {"title": "Apply nursery fertilizer", "day_offset": 10, "description": "Apply DAP at 75g per sq.meter if seedlings appear pale."},
                ]
            },
            {
                "name": "Land Preparation",
                "start_week": 2,
                "end_week": 4,
                "color": "#795548",
                "tasks": [
                    {"title": "Plough the main field", "day_offset": 0, "description": "Plough 2-3 times to create fine tilth. Incorporate previous crop residue."},
                    {"title": "Level the field", "day_offset": 5, "description": "Proper leveling ensures uniform water distribution. Use laser leveler if available."},
                    {"title": "Apply basal fertilizer", "day_offset": 7, "description": "Apply NPK (50:25:25 kg/hectare) as basal dose before transplanting."},
                    {"title": "Flood the field", "day_offset": 10, "description": "Maintain 2-3 cm standing water for puddling. Puddle 2 days before transplanting."},
                ]
            },
            {
                "name": "Transplanting",
                "start_week": 4,
                "end_week": 5,
                "color": "#4CAF50",
                "tasks": [
                    {"title": "Uproot seedlings", "day_offset": 0, "description": "Uproot 25-30 day old seedlings gently. Trim leaf tips if too tall."},
                    {"title": "Transplant seedlings", "day_offset": 1, "description": "Transplant 2-3 seedlings/hill at 20×15cm spacing. Plant shallow (2-3cm depth)."},
                    {"title": "Gap filling", "day_offset": 7, "description": "Fill gaps within 7 days of transplanting to maintain plant population."},
                ]
            },
            {
                "name": "Vegetative Growth",
                "start_week": 5,
                "end_week": 10,
                "color": "#2E7D32",
                "tasks": [
                    {"title": "First weeding", "day_offset": 5, "description": "Remove weeds manually or apply Butachlor (1.5 kg/ha) within 5 days of transplanting."},
                    {"title": "First top dressing", "day_offset": 14, "description": "Apply 25 kg Urea/hectare at 15 days after transplanting (DAT)."},
                    {"title": "Second weeding", "day_offset": 21, "description": "Hand weed or use rotary weeder between rows."},
                    {"title": "Second top dressing", "day_offset": 28, "description": "Apply 25 kg Urea/hectare at 40-45 DAT (tillering stage)."},
                    {"title": "Monitor for pests", "day_offset": 35, "description": "Check for stem borer, leaf folder, BPH. Use pheromone traps."},
                ]
            },
            {
                "name": "Flowering",
                "start_week": 10,
                "end_week": 14,
                "color": "#FF9800",
                "tasks": [
                    {"title": "Maintain water level", "day_offset": 0, "description": "Maintain 5cm standing water during flowering. Do NOT drain the field."},
                    {"title": "Monitor for blast disease", "day_offset": 7, "description": "Check for neck blast. Spray Tricyclazole (0.6g/L) if symptoms appear."},
                    {"title": "Final top dressing", "day_offset": 3, "description": "Apply 12.5 kg Urea/hectare at panicle initiation stage."},
                ]
            },
            {
                "name": "Grain Filling",
                "start_week": 14,
                "end_week": 18,
                "color": "#FFC107",
                "tasks": [
                    {"title": "Reduce water gradually", "day_offset": 0, "description": "Start reducing irrigation. Allow intermittent wetting and drying."},
                    {"title": "Bird scaring", "day_offset": 7, "description": "Install bird scarers or reflective tape to protect filling grains."},
                    {"title": "Stop irrigation", "day_offset": 21, "description": "Stop irrigation 10-15 days before expected harvest."},
                ]
            },
            {
                "name": "Harvest & Post-Harvest",
                "start_week": 18,
                "end_week": 20,
                "color": "#F44336",
                "tasks": [
                    {"title": "Check moisture for harvest", "day_offset": 0, "description": "Harvest when 80% grains are straw-colored. Grain moisture should be 20-22%."},
                    {"title": "Harvest the crop", "day_offset": 3, "description": "Use combine harvester or manual harvesting. Avoid delays to prevent shattering."},
                    {"title": "Dry the grains", "day_offset": 5, "description": "Sun-dry to 14% moisture for safe storage. Spread in thin layers."},
                    {"title": "Store properly", "day_offset": 8, "description": "Store in clean, dry godown. Use hermetic bags for long-term storage."},
                ]
            }
        ]
    },
    "Wheat": {
        "total_weeks": 18,
        "phases": [
            {
                "name": "Land Preparation",
                "start_week": 0,
                "end_week": 1,
                "color": "#795548",
                "tasks": [
                    {"title": "Plough and level field", "day_offset": 0, "description": "Plough 2-3 times followed by planking. Create fine tilth for good germination."},
                    {"title": "Apply basal fertilizer", "day_offset": 3, "description": "Apply 60 kg N + 30 kg P2O5 + 30 kg K2O per hectare as basal dose."},
                    {"title": "Pre-sowing irrigation", "day_offset": 5, "description": "Give one pre-sowing irrigation (Paleva) for optimum moisture at sowing depth."},
                ]
            },
            {
                "name": "Sowing",
                "start_week": 1,
                "end_week": 2,
                "color": "#4CAF50",
                "tasks": [
                    {"title": "Seed treatment", "day_offset": 0, "description": "Treat seeds with Vitavax (2.5g/kg) + Chlorpyriphos (4ml/kg) before sowing."},
                    {"title": "Sow seeds", "day_offset": 1, "description": "Sow at 100 kg/hectare using seed drill at 20cm row spacing, 5cm depth."},
                ]
            },
            {
                "name": "Crown Root Initiation",
                "start_week": 2,
                "end_week": 5,
                "color": "#8BC34A",
                "tasks": [
                    {"title": "First irrigation (CRI)", "day_offset": 14, "description": "CRITICAL: Give first irrigation at 21 days (Crown Root Initiation stage). Most important irrigation."},
                    {"title": "First top dressing", "day_offset": 15, "description": "Apply 30 kg Urea/hectare immediately after first irrigation."},
                    {"title": "Weed management", "day_offset": 18, "description": "Apply Sulfosulfuron (25g/ha) or manual weeding within 30-35 days of sowing."},
                ]
            },
            {
                "name": "Tillering",
                "start_week": 5,
                "end_week": 8,
                "color": "#2E7D32",
                "tasks": [
                    {"title": "Second irrigation", "day_offset": 0, "description": "Give second irrigation at 40-45 days after sowing (tillering stage)."},
                    {"title": "Scout for aphids/termites", "day_offset": 10, "description": "Monitor for aphids on leaves. Spray Imidacloprid (0.5ml/L) if threshold exceeded."},
                    {"title": "Second top dressing", "day_offset": 2, "description": "Apply remaining 30 kg Urea/hectare after second irrigation."},
                ]
            },
            {
                "name": "Jointing & Booting",
                "start_week": 8,
                "end_week": 11,
                "color": "#FF9800",
                "tasks": [
                    {"title": "Third irrigation", "day_offset": 0, "description": "Irrigate at jointing stage (60-65 DAS). Critical for ear development."},
                    {"title": "Monitor for rust", "day_offset": 7, "description": "Check for yellow/brown rust. Spray Propiconazole (1ml/L) at first appearance."},
                    {"title": "Fourth irrigation", "day_offset": 14, "description": "Irrigate at booting/heading stage for proper grain formation."},
                ]
            },
            {
                "name": "Flowering & Grain Filling",
                "start_week": 11,
                "end_week": 15,
                "color": "#FFC107",
                "tasks": [
                    {"title": "Fifth irrigation (flowering)", "day_offset": 0, "description": "Irrigate at flowering. Water stress now can reduce yield by 20-30%."},
                    {"title": "Monitor for Karnal Bunt", "day_offset": 7, "description": "If humid weather during flowering, spray Propiconazole to prevent Karnal Bunt."},
                    {"title": "Sixth irrigation (milking)", "day_offset": 14, "description": "Last irrigation at milking/dough stage for grain filling."},
                ]
            },
            {
                "name": "Harvest & Post-Harvest",
                "start_week": 15,
                "end_week": 18,
                "color": "#F44336",
                "tasks": [
                    {"title": "Check harvest readiness", "day_offset": 0, "description": "Harvest when grains are hard and straw turns golden. Moisture should be 14-16%."},
                    {"title": "Harvest", "day_offset": 5, "description": "Use combine harvester or manual cutting. Avoid shattering losses."},
                    {"title": "Threshing & cleaning", "day_offset": 8, "description": "Thresh within 2-3 days. Clean grains and sun-dry to 12% moisture."},
                    {"title": "Storage", "day_offset": 12, "description": "Store in clean jute bags or metal bins. Fumigate with Aluminium Phosphide if needed."},
                ]
            }
        ]
    },
    "Cotton": {
        "total_weeks": 24,
        "phases": [
            {
                "name": "Land Preparation",
                "start_week": 0,
                "end_week": 2,
                "color": "#795548",
                "tasks": [
                    {"title": "Deep ploughing", "day_offset": 0, "description": "Deep plough (30cm) to break hardpan. Follow with 2 harrowings."},
                    {"title": "Apply FYM", "day_offset": 3, "description": "Apply 10-12 tonnes FYM per hectare and incorporate in soil."},
                    {"title": "Form ridges and furrows", "day_offset": 7, "description": "Form ridges at 90-120cm spacing depending on variety."},
                ]
            },
            {
                "name": "Sowing",
                "start_week": 2,
                "end_week": 3,
                "color": "#4CAF50",
                "tasks": [
                    {"title": "Seed treatment", "day_offset": 0, "description": "Treat with Imidacloprid (5ml/kg) + Thiram (3g/kg) for pest and disease protection."},
                    {"title": "Sow seeds", "day_offset": 1, "description": "Sow 2 seeds/hill on ridges. Seed rate: 2.5 kg/hectare for Bt cotton."},
                    {"title": "Refuge planting", "day_offset": 2, "description": "Plant 20% non-Bt cotton around the field as refuge (for Bt cotton)."},
                ]
            },
            {
                "name": "Seedling & Establishment",
                "start_week": 3,
                "end_week": 6,
                "color": "#8BC34A",
                "tasks": [
                    {"title": "Thinning", "day_offset": 10, "description": "Thin to one plant per hill at 15-20 days after sowing."},
                    {"title": "First weeding", "day_offset": 14, "description": "Intercultivate and hand weed. Keep field weed-free for first 60 days."},
                    {"title": "First irrigation", "day_offset": 7, "description": "Irrigate if no rain within 7 days of sowing. Maintain consistent moisture."},
                ]
            },
            {
                "name": "Vegetative Growth",
                "start_week": 6,
                "end_week": 12,
                "color": "#2E7D32",
                "tasks": [
                    {"title": "First top dressing", "day_offset": 0, "description": "Apply 30 kg Urea + 25 kg MOP per hectare at 30 DAS."},
                    {"title": "Second weeding", "day_offset": 14, "description": "Intercultivate and hand weed. Earthing up around plants."},
                    {"title": "Monitor for bollworms", "day_offset": 21, "description": "Install pheromone traps. Check for American bollworm eggs on terminals."},
                    {"title": "Second top dressing", "day_offset": 28, "description": "Apply 30 kg Urea/hectare at 60 DAS (squaring stage)."},
                ]
            },
            {
                "name": "Flowering & Boll Formation",
                "start_week": 12,
                "end_week": 18,
                "color": "#FF9800",
                "tasks": [
                    {"title": "Critical irrigation", "day_offset": 0, "description": "Maintain regular irrigation at 10-12 day intervals during boll development."},
                    {"title": "Pest monitoring intensified", "day_offset": 7, "description": "Check for pink bollworm, whitefly, jassids. Use IPM strategies."},
                    {"title": "Foliar spray", "day_offset": 14, "description": "Spray 2% DAP + 1% KCl for better boll development and fiber quality."},
                ]
            },
            {
                "name": "Boll Opening",
                "start_week": 18,
                "end_week": 22,
                "color": "#FFC107",
                "tasks": [
                    {"title": "Reduce irrigation", "day_offset": 0, "description": "Reduce irrigation frequency to promote boll opening."},
                    {"title": "Defoliant application (optional)", "day_offset": 14, "description": "Apply defoliant if machine picking planned. Promotes uniform opening."},
                    {"title": "First picking", "day_offset": 21, "description": "Pick when 60% bolls open. Early morning picking gives better fiber quality."},
                ]
            },
            {
                "name": "Harvest & Post-Harvest",
                "start_week": 22,
                "end_week": 24,
                "color": "#F44336",
                "tasks": [
                    {"title": "Final picking", "day_offset": 0, "description": "Complete picking in 3-4 rounds at 10-15 day intervals."},
                    {"title": "Dry cotton", "day_offset": 3, "description": "Sun-dry picked cotton to 8-10% moisture. Remove trash and stained cotton."},
                    {"title": "Stalk destruction", "day_offset": 10, "description": "MANDATORY: Destroy cotton stalks by 15th February to control pink bollworm."},
                ]
            }
        ]
    },
    "Sugarcane": {
        "total_weeks": 44,
        "phases": [
            {
                "name": "Land Preparation",
                "start_week": 0,
                "end_week": 2,
                "color": "#795548",
                "tasks": [
                    {"title": "Deep ploughing", "day_offset": 0, "description": "Deep plough followed by 2-3 harrowings. Open furrows at 90cm spacing."},
                    {"title": "Apply basal fertilizer", "day_offset": 5, "description": "Apply 75 kg N + 75 kg P2O5 + 75 kg K2O/hectare in furrows."},
                    {"title": "Apply FYM", "day_offset": 3, "description": "Apply 25 tonnes FYM/hectare in furrows before planting."},
                ]
            },
            {
                "name": "Planting",
                "start_week": 2,
                "end_week": 3,
                "color": "#4CAF50",
                "tasks": [
                    {"title": "Sett treatment", "day_offset": 0, "description": "Treat 3-budded setts in Carbendazim solution for 15 minutes."},
                    {"title": "Plant setts", "day_offset": 1, "description": "Place setts end-to-end in furrows. Use 6-8 tonnes setts/hectare."},
                    {"title": "Irrigation after planting", "day_offset": 2, "description": "Give immediate light irrigation after planting."},
                ]
            },
            {
                "name": "Germination",
                "start_week": 3,
                "end_week": 8,
                "color": "#8BC34A",
                "tasks": [
                    {"title": "Gap filling", "day_offset": 14, "description": "Fill gaps with pre-sprouted setts within 30 days of planting."},
                    {"title": "First weeding", "day_offset": 21, "description": "Hand weed or apply Atrazine (2 kg/ha) pre-emergence within 3 days of planting."},
                    {"title": "Irrigate regularly", "day_offset": 7, "description": "Irrigate every 7-10 days during germination phase."},
                ]
            },
            {
                "name": "Tillering",
                "start_week": 8,
                "end_week": 16,
                "color": "#2E7D32",
                "tasks": [
                    {"title": "First top dressing", "day_offset": 0, "description": "Apply 75 kg Urea/hectare at 45 days after planting."},
                    {"title": "Earthing up", "day_offset": 14, "description": "Earth up soil around cane base to promote tillering and prevent lodging."},
                    {"title": "Second top dressing", "day_offset": 28, "description": "Apply 75 kg Urea/hectare at 90 days. Last nitrogen application."},
                    {"title": "Propping", "day_offset": 42, "description": "Prop tall canes with bamboo to prevent lodging."},
                ]
            },
            {
                "name": "Grand Growth",
                "start_week": 16,
                "end_week": 32,
                "color": "#FF9800",
                "tasks": [
                    {"title": "Regular irrigation", "day_offset": 0, "description": "Irrigate every 10-15 days. This is the maximum water requirement phase."},
                    {"title": "Detrashing", "day_offset": 30, "description": "Remove dry leaves from lower portion. Improves air circulation and reduces pests."},
                    {"title": "Monitor for borers", "day_offset": 14, "description": "Check for internode borer, top shoot borer. Release Trichogramma parasitoids."},
                ]
            },
            {
                "name": "Maturity & Ripening",
                "start_week": 32,
                "end_week": 42,
                "color": "#FFC107",
                "tasks": [
                    {"title": "Stop irrigation", "day_offset": 0, "description": "Withhold irrigation 3-4 weeks before harvest to increase sugar content."},
                    {"title": "Apply ripening spray", "day_offset": 7, "description": "Spray Ethephon (750 ppm) at 8 months for early maturity if needed."},
                    {"title": "Check sugar content", "day_offset": 42, "description": "Test with hand refractometer. Harvest when brix reading is above 18%."},
                ]
            },
            {
                "name": "Harvest",
                "start_week": 42,
                "end_week": 44,
                "color": "#F44336",
                "tasks": [
                    {"title": "Harvest at ground level", "day_offset": 0, "description": "Cut cane close to ground level. Remove tops and trash."},
                    {"title": "Transport to mill", "day_offset": 1, "description": "Send to sugar mill within 24 hours of harvest. Longer delay reduces sugar recovery."},
                    {"title": "Ratoon care", "day_offset": 3, "description": "If taking ratoon: level the field, apply 25% more fertilizer, irrigate within 7 days."},
                ]
            }
        ]
    },
    "Maize": {
        "total_weeks": 14,
        "phases": [
            {
                "name": "Land Preparation",
                "start_week": 0,
                "end_week": 1,
                "color": "#795548",
                "tasks": [
                    {"title": "Plough and prepare bed", "day_offset": 0, "description": "Plough twice. Form raised beds at 60-75cm spacing for Kharif or flat beds for Rabi."},
                    {"title": "Apply basal fertilizer", "day_offset": 3, "description": "Apply 60 kg N + 30 kg P2O5 + 30 kg K2O/hectare as basal dose."},
                ]
            },
            {
                "name": "Sowing",
                "start_week": 1,
                "end_week": 2,
                "color": "#4CAF50",
                "tasks": [
                    {"title": "Seed treatment", "day_offset": 0, "description": "Treat seeds with Thiram (2g/kg) + Imidacloprid (2ml/kg)."},
                    {"title": "Sow seeds", "day_offset": 1, "description": "Sow 20 kg/hectare at 60×20cm spacing using seed drill. Optimum: 5cm depth."},
                ]
            },
            {
                "name": "Vegetative Growth",
                "start_week": 2,
                "end_week": 7,
                "color": "#2E7D32",
                "tasks": [
                    {"title": "Thinning", "day_offset": 7, "description": "Thin to one healthy plant per hill at 10-12 days after sowing."},
                    {"title": "First top dressing", "day_offset": 14, "description": "Apply 30 kg Urea/hectare at 25 DAS (knee-high stage)."},
                    {"title": "Earthing up", "day_offset": 21, "description": "Earth up soil around base at 30-35 DAS to anchor roots."},
                    {"title": "Second top dressing", "day_offset": 28, "description": "Apply 30 kg Urea/hectare at 45 DAS (tasseling stage)."},
                    {"title": "Fall armyworm check", "day_offset": 10, "description": "Monitor whorl stage for Fall Armyworm. Apply Emamectin Benzoate (0.4g/L) if found."},
                ]
            },
            {
                "name": "Tasseling & Silking",
                "start_week": 7,
                "end_week": 9,
                "color": "#FF9800",
                "tasks": [
                    {"title": "Ensure adequate irrigation", "day_offset": 0, "description": "CRITICAL: Do not allow water stress. Yield loss can be 40-60% if stressed now."},
                    {"title": "Detasseling (if hybrid seed)", "day_offset": 5, "description": "Remove tassels from female parent rows for hybrid seed production."},
                ]
            },
            {
                "name": "Grain Filling",
                "start_week": 9,
                "end_week": 12,
                "color": "#FFC107",
                "tasks": [
                    {"title": "Continue irrigation", "day_offset": 0, "description": "Maintain irrigation at 8-10 day intervals for proper grain filling."},
                    {"title": "Monitor for stalk rot", "day_offset": 14, "description": "Check for Charcoal rot in lower stalk. Remove affected plants."},
                ]
            },
            {
                "name": "Harvest",
                "start_week": 12,
                "end_week": 14,
                "color": "#F44336",
                "tasks": [
                    {"title": "Check maturity", "day_offset": 0, "description": "Harvest when husks dry and grains are hard. Black layer visible at grain base."},
                    {"title": "Harvest and shelling", "day_offset": 5, "description": "Harvest cobs manually. Shell using maize sheller. Sun-dry to 12-14% moisture."},
                    {"title": "Storage", "day_offset": 8, "description": "Store in airtight containers or bins. Fumigation for long-term storage."},
                ]
            }
        ]
    },
    "Groundnut": {
        "total_weeks": 17,
        "phases": [
            {
                "name": "Land Preparation",
                "start_week": 0,
                "end_week": 1,
                "color": "#795548",
                "tasks": [
                    {"title": "Plough and pulverize", "day_offset": 0, "description": "Plough 2 times. Groundnut needs fine, well-drained sandy loam soil."},
                    {"title": "Apply gypsum and basal dose", "day_offset": 3, "description": "Apply 200 kg Gypsum + 25 kg N + 50 kg P2O5 + 25 kg K2O per hectare."},
                ]
            },
            {
                "name": "Sowing",
                "start_week": 1,
                "end_week": 2,
                "color": "#4CAF50",
                "tasks": [
                    {"title": "Seed treatment", "day_offset": 0, "description": "Treat with Rhizobium + PSB culture and Thiram (3g/kg)."},
                    {"title": "Sow seeds", "day_offset": 1, "description": "Sow 100-120 kg kernels/hectare at 30×10cm spacing. Depth: 5cm."},
                ]
            },
            {
                "name": "Vegetative Growth",
                "start_week": 2,
                "end_week": 6,
                "color": "#2E7D32",
                "tasks": [
                    {"title": "First weeding", "day_offset": 10, "description": "Hand weed at 15-20 DAS. Keep weed-free up to 45 days."},
                    {"title": "Earthing up", "day_offset": 21, "description": "Earth up soil at 30 DAS to promote peg penetration into soil."},
                    {"title": "Apply gypsum", "day_offset": 25, "description": "Apply remaining 200 kg Gypsum/hectare at flowering (45 DAS). Critical for pod filling."},
                ]
            },
            {
                "name": "Flowering & Pegging",
                "start_week": 6,
                "end_week": 10,
                "color": "#FF9800",
                "tasks": [
                    {"title": "Ensure moisture", "day_offset": 0, "description": "Maintain adequate moisture for peg development. Irrigate every 8-10 days."},
                    {"title": "Monitor for leaf spot", "day_offset": 14, "description": "Check for tikka disease. Spray Mancozeb (2.5g/L) at first appearance."},
                ]
            },
            {
                "name": "Pod Development",
                "start_week": 10,
                "end_week": 15,
                "color": "#FFC107",
                "tasks": [
                    {"title": "Continue irrigation", "day_offset": 0, "description": "Ensure soil moisture for pod filling. Stress reduces oil content."},
                    {"title": "Monitor for stem rot", "day_offset": 14, "description": "Check base of plants for white fungal growth. Remove and burn affected plants."},
                    {"title": "Stop irrigation before harvest", "day_offset": 28, "description": "Withhold irrigation 10-15 days before harvest for easier lifting."},
                ]
            },
            {
                "name": "Harvest",
                "start_week": 15,
                "end_week": 17,
                "color": "#F44336",
                "tasks": [
                    {"title": "Check maturity", "day_offset": 0, "description": "Harvest when inner shell shows dark tanning. 75% pods should be mature."},
                    {"title": "Lift and dry", "day_offset": 3, "description": "Lift entire plant. Stack with pods facing up for field drying (3-4 days)."},
                    {"title": "Strip and store", "day_offset": 7, "description": "Strip pods. Sun-dry to 8% moisture. Store in gunny bags in well-ventilated room."},
                ]
            }
        ]
    },
}

# Default calendar for crops not in the detailed database
_DEFAULT_CALENDAR = {
    "total_weeks": 16,
    "phases": [
        {
            "name": "Land Preparation",
            "start_week": 0,
            "end_week": 2,
            "color": "#795548",
            "tasks": [
                {"title": "Prepare the field", "day_offset": 0, "description": "Plough and level the field. Apply FYM at 10 tonnes/hectare."},
                {"title": "Apply basal fertilizer", "day_offset": 5, "description": "Apply recommended NPK dose based on soil test results."},
            ]
        },
        {
            "name": "Sowing / Planting",
            "start_week": 2,
            "end_week": 3,
            "color": "#4CAF50",
            "tasks": [
                {"title": "Seed/seedling treatment", "day_offset": 0, "description": "Treat seeds with fungicide and bio-agents before sowing."},
                {"title": "Sow / transplant", "day_offset": 1, "description": "Sow at recommended spacing and depth for your crop variety."},
            ]
        },
        {
            "name": "Vegetative Growth",
            "start_week": 3,
            "end_week": 8,
            "color": "#2E7D32",
            "tasks": [
                {"title": "First weeding", "day_offset": 10, "description": "Remove weeds by hand or use recommended herbicide."},
                {"title": "First top dressing", "day_offset": 14, "description": "Apply nitrogen fertilizer as top dressing."},
                {"title": "Pest monitoring", "day_offset": 21, "description": "Scout for pests and diseases. Apply IPM measures."},
                {"title": "Second top dressing", "day_offset": 28, "description": "Apply second dose of nitrogen if needed."},
            ]
        },
        {
            "name": "Flowering & Fruiting",
            "start_week": 8,
            "end_week": 12,
            "color": "#FF9800",
            "tasks": [
                {"title": "Ensure irrigation", "day_offset": 0, "description": "Do not allow water stress during flowering. Critical growth period."},
                {"title": "Disease management", "day_offset": 7, "description": "Monitor and spray appropriate fungicide if diseases appear."},
            ]
        },
        {
            "name": "Maturity & Harvest",
            "start_week": 12,
            "end_week": 16,
            "color": "#F44336",
            "tasks": [
                {"title": "Reduce irrigation", "day_offset": 0, "description": "Gradually reduce irrigation as crop approaches maturity."},
                {"title": "Harvest at optimal moisture", "day_offset": 14, "description": "Harvest when crop shows full maturity signs. Check moisture content."},
                {"title": "Post-harvest processing", "day_offset": 18, "description": "Clean, dry, and store properly to avoid post-harvest losses."},
            ]
        }
    ]
}


def get_crop_calendar(crop: str, state: str = "", season: str = "",
                      sowing_date: str = None) -> dict:
    """Get the crop calendar with calculated dates.

    Args:
        crop: Crop name (e.g., 'Rice', 'Wheat').
        state: State name (for region-specific adjustments).
        season: Season (Kharif/Rabi/Zaid).
        sowing_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        dict with phases, tasks with absolute dates, and summary.
    """
    try:
        # Get calendar template
        calendar_data = _CROP_CALENDARS.get(crop, _DEFAULT_CALENDAR)

        # Parse sowing date
        if sowing_date:
            try:
                sow_date = datetime.strptime(sowing_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                sow_date = datetime.now()
        else:
            sow_date = datetime.now()

        # Build absolute-dated calendar
        phases = []
        all_tasks = []
        total_tasks = 0
        today = datetime.now()

        for phase in calendar_data["phases"]:
            phase_start = sow_date + timedelta(weeks=phase["start_week"])
            phase_end = sow_date + timedelta(weeks=phase["end_week"])

            tasks = []
            for task in phase["tasks"]:
                task_date = phase_start + timedelta(days=task["day_offset"])
                is_past = task_date.date() < today.date()
                is_today = task_date.date() == today.date()

                task_entry = {
                    "title": task["title"],
                    "description": task["description"],
                    "date": task_date.strftime("%Y-%m-%d"),
                    "display_date": task_date.strftime("%d %b %Y"),
                    "is_past": is_past,
                    "is_today": is_today,
                    "phase": phase["name"],
                }
                tasks.append(task_entry)
                all_tasks.append(task_entry)
                total_tasks += 1

            # Determine current phase flag
            is_current = phase_start.date() <= today.date() <= phase_end.date()

            phases.append({
                "name": phase["name"],
                "start_date": phase_start.strftime("%Y-%m-%d"),
                "end_date": phase_end.strftime("%Y-%m-%d"),
                "display_start": phase_start.strftime("%d %b"),
                "display_end": phase_end.strftime("%d %b"),
                "color": phase["color"],
                "is_current": is_current,
                "tasks": tasks,
            })

        # Determine current phase
        current_phase = "Not started"
        days_into_cycle = (today - sow_date).days
        total_days = calendar_data["total_weeks"] * 7

        for phase in phases:
            if phase["is_current"]:
                current_phase = phase["name"]
                break
        else:
            if days_into_cycle >= total_days:
                current_phase = "Harvest Complete"
            elif days_into_cycle < 0:
                current_phase = f"Sowing in {abs(days_into_cycle)} days"

        # Upcoming tasks (next 7 days)
        upcoming = []
        for t in all_tasks:
            t_date = datetime.strptime(t["date"], "%Y-%m-%d")
            diff = (t_date.date() - today.date()).days
            if 0 <= diff <= 7:
                upcoming.append(t)

        progress = max(0, min(100, int((days_into_cycle / total_days) * 100))) if total_days > 0 else 0

        expected_harvest = sow_date + timedelta(weeks=calendar_data["total_weeks"])

        return {
            "crop": crop,
            "state": state,
            "season": season,
            "sowing_date": sow_date.strftime("%Y-%m-%d"),
            "expected_harvest": expected_harvest.strftime("%Y-%m-%d"),
            "display_harvest": expected_harvest.strftime("%d %b %Y"),
            "total_weeks": calendar_data["total_weeks"],
            "current_phase": current_phase,
            "progress_percent": progress,
            "days_into_cycle": max(0, days_into_cycle),
            "total_days": total_days,
            "phases": phases,
            "upcoming_tasks": upcoming,
            "total_tasks": total_tasks,
        }

    except Exception as e:
        logger.error("Crop calendar error: %s", e)
        return {"error": f"Failed to generate calendar: {e}"}
