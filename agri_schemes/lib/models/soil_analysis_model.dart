/// Model for soil health analysis results.
class SoilAnalysisModel {
  final String soilType;
  final double phEstimate;
  final String organicMatter;
  final String moistureLevel;
  final String drainage;
  final String colorAnalysis;
  final String textureAnalysis;
  final int healthScore;
  final List<String> deficiencies;
  final List<String> recommendations;
  final List<String> suitableCrops;
  final double confidence;
  final Map<String, String>? npkStatus;

  SoilAnalysisModel({
    required this.soilType,
    required this.phEstimate,
    required this.organicMatter,
    required this.moistureLevel,
    required this.drainage,
    required this.colorAnalysis,
    required this.textureAnalysis,
    required this.healthScore,
    required this.deficiencies,
    required this.recommendations,
    required this.suitableCrops,
    required this.confidence,
    this.npkStatus,
  });

  factory SoilAnalysisModel.fromJson(Map<String, dynamic> json) {
    return SoilAnalysisModel(
      soilType: json['soil_type'] ?? 'Unknown',
      phEstimate: (json['ph_estimate'] ?? 7.0).toDouble(),
      organicMatter: json['organic_matter'] ?? 'Medium',
      moistureLevel: json['moisture_level'] ?? 'Moderate',
      drainage: json['drainage'] ?? 'Moderate',
      colorAnalysis: json['color_analysis'] ?? '',
      textureAnalysis: json['texture_analysis'] ?? '',
      healthScore: json['health_score'] ?? 5,
      deficiencies: List<String>.from(json['deficiencies'] ?? []),
      recommendations: List<String>.from(json['recommendations'] ?? []),
      suitableCrops: List<String>.from(json['suitable_crops'] ?? []),
      confidence: (json['confidence'] ?? 0.5).toDouble(),
      npkStatus: json['npk_status'] != null
          ? Map<String, String>.from(json['npk_status'])
          : null,
    );
  }

  String get healthLabel {
    if (healthScore >= 8) return 'Excellent';
    if (healthScore >= 6) return 'Good';
    if (healthScore >= 4) return 'Average';
    if (healthScore >= 2) return 'Poor';
    return 'Very Poor';
  }
}
