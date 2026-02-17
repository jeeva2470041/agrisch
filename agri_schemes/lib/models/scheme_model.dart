/// Model class representing a government scheme
/// Matches the structure returned by the backend API
class SchemeModel {
  /// Name of the scheme
  final String name;

  /// Type of scheme (loan, subsidy, insurance)
  final String type;

  /// Benefit description/amount (human readable)
  final String benefit;

  /// Localized description map (e.g. {'en': '...', 'hi': '...'})
  final Map<String, dynamic> description;

  /// Documents required (English for MVP)
  final List<String> documentsRequired;

  /// Official scheme page / application URL
  final String officialLink;

  /// States where scheme applies (e.g. ['All'] or ['Punjab'])
  final List<String> states;

  /// Crops covered by the scheme
  final List<String> crops;

  /// Minimum and maximum land (hectares) for eligibility
  final double minLand;
  final double maxLand;

  /// Season (Kharif/Rabi/All)
  final String season;

  /// Numeric benefit amount (if available)
  final int benefitAmount;

  const SchemeModel({
    required this.name,
    required this.type,
    required this.benefit,
    required this.description,
    this.documentsRequired = const [],
    this.officialLink = '',
    this.states = const ['All'],
    this.crops = const ['All'],
    this.minLand = 0.0,
    this.maxLand = 100.0,
    this.season = 'All',
    this.benefitAmount = 0,
  });

  /// Factory constructor to create SchemeModel from JSON
  factory SchemeModel.fromJson(Map<String, dynamic> json) {
    return SchemeModel(
      name: json['scheme_name'] ?? '',
      type: json['type'] ?? '',
      benefit: json['benefit'] ?? '',
      description: json['description'] is Map
          ? Map<String, dynamic>.from(json['description'])
          : {},
      documentsRequired: json['documents_required'] is List
          ? List<String>.from(json['documents_required'])
          : const [],
      officialLink: json['official_link'] ?? '',
      states: json['states'] is List ? List<String>.from(json['states']) : const ['All'],
      crops: json['crops'] is List ? List<String>.from(json['crops']) : const ['All'],
      minLand: json['min_land'] is num ? (json['min_land'] as num).toDouble() : 0.0,
      maxLand: json['max_land'] is num ? (json['max_land'] as num).toDouble() : 100.0,
      season: json['season'] ?? 'All',
      benefitAmount: json['benefit_amount'] is num ? (json['benefit_amount'] as num).toInt() : 0,
    );
  }

  /// Convert to JSON (useful for caching)
  Map<String, dynamic> toJson() {
    return {
      'scheme_name': name,
      'type': type,
      'benefit': benefit,
      'description': description,
      'documents_required': documentsRequired,
      'official_link': officialLink,
      'states': states,
      'crops': crops,
      'min_land': minLand,
      'max_land': maxLand,
      'season': season,
      'benefit_amount': benefitAmount,
    };
  }

  /// Helper to get description in current locale
  String getDescription(String localeCode) {
    if (description.containsKey(localeCode)) {
      return description[localeCode] as String;
    }
    // Fallback to English, then any available, then empty
    return description['en'] ?? (description.isNotEmpty ? description.values.first as String : '');
  }

  /// Convenience helpers for UI
  bool hasDocuments() => documentsRequired.isNotEmpty;

  /// Basic eligibility check against farmer input
  bool isApplicableFor(String state, String crop, double landSize, String seasonInput) {
    final stateOk = states.contains('All') || states.contains(state);
    final cropOk = crops.contains('All') || crops.contains(crop);
    final landOk = landSize >= minLand && landSize <= maxLand;
    final seasonOk = season == 'All' || season == seasonInput || seasonInput == 'All';
    return stateOk && cropOk && landOk && seasonOk;
  }
}
