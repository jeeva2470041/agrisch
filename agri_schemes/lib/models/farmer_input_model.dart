/// Model class representing farmer input data
/// Used to collect and pass farmer information for scheme matching
class FarmerInputModel {
  /// Type of crop the farmer is growing
  final String cropType;

  /// Size of land in hectares
  final double landSize;

  /// Growing season (Kharif or Rabi)
  final String season;

  /// State where the farm is located
  final String state;

  const FarmerInputModel({
    required this.cropType,
    required this.landSize,
    required this.season,
    required this.state,
  });

  /// Convert to map for easy data passing
  Map<String, dynamic> toMap() {
    return {
      'cropType': cropType,
      'landSize': landSize,
      'season': season,
      'state': state,
    };
  }

  /// Convert to JSON for API
  Map<String, dynamic> toJson() {
    return {
      'state': state,
      'crop': cropType,
      'land_size': landSize,
      'season': season,
      'district': 'All', // Defaulting to All as district isn't in UI yet
    };
  }

  /// Create from map
  factory FarmerInputModel.fromMap(Map<String, dynamic> map) {
    return FarmerInputModel(
      cropType: map['cropType'] as String,
      landSize: map['landSize'] as double,
      season: map['season'] as String,
      state: map['state'] as String,
    );
  }

  @override
  String toString() {
    return 'FarmerInputModel(cropType: $cropType, landSize: $landSize, season: $season, state: $state)';
  }
}
