/// Model class representing a government scheme
/// Matches the structure returned by the backend API
class SchemeModel {
  /// Name of the scheme
  final String name;

  /// Type of scheme (loan, subsidy, insurance)
  final String type;

  /// Benefit description/amount
  final String benefit;

  /// Description in multiple languages
  final Map<String, dynamic> description;

  const SchemeModel({
    required this.name,
    required this.type,
    required this.benefit,
    required this.description,
  });

  /// Factory constructor to create SchemeModel from JSON
  factory SchemeModel.fromJson(Map<String, dynamic> json) {
    return SchemeModel(
      name: json['scheme_name'] ?? '',
      type: json['type'] ?? '',
      benefit: json['benefit'] ?? '',
      description: json['description'] is Map ? json['description'] : {},
    );
  }

  /// Convert to JSON (useful for caching)
  Map<String, dynamic> toJson() {
    return {
      'scheme_name': name,
      'type': type,
      'benefit': benefit,
      'description': description,
    };
  }

  /// Helper to get description in current locale
  String getDescription(String localeCode) {
    if (description.containsKey(localeCode)) {
      return description[localeCode];
    }
    // Fallback to English, then any available, then empty
    return description['en'] ?? description.isNotEmpty
        ? description.values.first
        : '';
  }
}
