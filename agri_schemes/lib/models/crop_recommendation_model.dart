/// Model for AI crop recommendation results.
class CropRecommendationModel {
  final List<RecommendedCrop> recommendations;
  final String generalAdvice;
  final String bestSowingWindow;

  CropRecommendationModel({
    required this.recommendations,
    required this.generalAdvice,
    required this.bestSowingWindow,
  });

  factory CropRecommendationModel.fromJson(Map<String, dynamic> json) {
    final recList = (json['recommendations'] as List? ?? [])
        .map((r) => RecommendedCrop.fromJson(r))
        .toList();
    return CropRecommendationModel(
      recommendations: recList,
      generalAdvice: json['general_advice'] ?? '',
      bestSowingWindow: json['best_sowing_window'] ?? '',
    );
  }
}

class RecommendedCrop {
  final String crop;
  final int suitabilityScore;
  final String expectedYield;
  final String expectedRevenue;
  final String investmentEstimate;
  final String waterRequirement;
  final String growthDuration;
  final List<String> matchingSchemes;
  final String reasoning;
  final List<String> riskFactors;
  final List<String> tips;

  RecommendedCrop({
    required this.crop,
    required this.suitabilityScore,
    required this.expectedYield,
    required this.expectedRevenue,
    required this.investmentEstimate,
    required this.waterRequirement,
    required this.growthDuration,
    required this.matchingSchemes,
    required this.reasoning,
    required this.riskFactors,
    required this.tips,
  });

  factory RecommendedCrop.fromJson(Map<String, dynamic> json) {
    return RecommendedCrop(
      crop: json['crop'] ?? 'Unknown',
      suitabilityScore: json['suitability_score'] ?? 50,
      expectedYield: json['expected_yield'] ?? 'N/A',
      expectedRevenue: json['expected_revenue'] ?? 'N/A',
      investmentEstimate: json['investment_estimate'] ?? 'N/A',
      waterRequirement: json['water_requirement'] ?? 'Medium',
      growthDuration: json['growth_duration'] ?? 'N/A',
      matchingSchemes: List<String>.from(json['matching_schemes'] ?? []),
      reasoning: json['reasoning'] ?? '',
      riskFactors: List<String>.from(json['risk_factors'] ?? []),
      tips: List<String>.from(json['tips'] ?? []),
    );
  }
}
