"""
AgriScheme Backend — Smart Scheme Ranking Service.
Uses TF-IDF vectorization and Cosine Similarity to rank government
schemes by personal relevance to the farmer's profile.
"""
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def _build_farmer_profile(state: str, crop: str, land_size: float, season: str) -> str:
    """Build a text profile describing the farmer's situation."""
    size_category = "small"
    if land_size > 4:
        size_category = "large"
    elif land_size > 2:
        size_category = "medium"

    return (
        f"Farmer in {state} growing {crop} crop during {season} season "
        f"with {land_size} hectares of {size_category} land holding. "
        f"{crop} cultivation in {state} {season}."
    )


def _build_scheme_profile(scheme: dict) -> str:
    """Build a text description from a scheme document for TF-IDF matching."""
    parts = []

    name = scheme.get("scheme_name", "")
    if name:
        parts.append(name)

    scheme_type = scheme.get("type", "")
    if scheme_type:
        parts.append(scheme_type)

    benefit = scheme.get("benefit", "")
    if benefit:
        parts.append(benefit)

    # Description (can be a dict with language keys or a string)
    desc = scheme.get("description", "")
    if isinstance(desc, dict):
        desc = desc.get("en", str(desc))
    if desc:
        parts.append(str(desc))

    # States
    states = scheme.get("states", [])
    if isinstance(states, list):
        parts.append(" ".join(states))

    # Crops
    crops = scheme.get("crops", [])
    if isinstance(crops, list):
        parts.append(" ".join(crops))

    # Season
    season = scheme.get("season", "")
    if season:
        parts.append(season)

    # Land range
    min_land = scheme.get("min_land", 0)
    max_land = scheme.get("max_land", 100)
    if min_land <= 2:
        parts.append("small farmer marginal")
    if max_land >= 10:
        parts.append("large farmer")
    parts.append("medium farmer")

    return " ".join(parts)


def rank_schemes(schemes: list, state: str, crop: str,
                 land_size: float, season: str) -> list:
    """Rank a list of schemes by relevance to the farmer's profile
    using TF-IDF + Cosine Similarity.

    Args:
        schemes: List of scheme dicts from MongoDB.
        state: Farmer's state.
        crop: Farmer's crop.
        land_size: Farmer's land size in hectares.
        season: Farming season.

    Returns:
        List of schemes sorted by relevance_score (descending),
        each augmented with 'relevance_score'.
    """
    if not schemes:
        return schemes

    if len(schemes) == 1:
        schemes[0]["relevance_score"] = 1.0
        return schemes

    try:
        # Build text documents
        farmer_profile = _build_farmer_profile(state, crop, land_size, season)
        scheme_profiles = [_build_scheme_profile(s) for s in schemes]

        # All documents: farmer profile first, then scheme profiles
        all_docs = [farmer_profile] + scheme_profiles

        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
        )
        tfidf_matrix = vectorizer.fit_transform(all_docs)

        # Cosine similarity between farmer profile (index 0) and each scheme
        farmer_vec = tfidf_matrix[0:1]
        scheme_vecs = tfidf_matrix[1:]
        similarities = cosine_similarity(farmer_vec, scheme_vecs).flatten()

        # Combine with benefit_amount for final score
        # Weighted: 60% relevance + 40% normalized benefit
        max_benefit = max(
            (s.get("benefit_amount", 0) for s in schemes), default=1
        )
        if max_benefit == 0:
            max_benefit = 1

        for i, scheme in enumerate(schemes):
            tfidf_score = float(similarities[i])
            benefit_norm = scheme.get("benefit_amount", 0) / max_benefit
            combined_score = 0.6 * tfidf_score + 0.4 * benefit_norm
            scheme["relevance_score"] = round(combined_score, 4)

        # Sort by combined relevance score (highest first)
        schemes.sort(key=lambda s: s.get("relevance_score", 0), reverse=True)

        return schemes

    except Exception as e:
        logger.error("Ranking error: %s", e)
        # Fallback: return schemes as-is with default scores
        for scheme in schemes:
            scheme["relevance_score"] = 0.5
        return schemes
