import '../models/scheme_model.dart';
import '../models/farmer_input_model.dart';
import 'api_service.dart';
import 'local_storage_service.dart';

/// Service to handle scheme matching logic
/// Orchestrates API calls and local caching
class SchemeMatchingService {
  final ApiService _apiService = ApiService();
  final LocalStorageService _localStorageService = LocalStorageService();

  /// Get eligible schemes based on farmer input
  /// Tries API first, falls back to local cache if offline/error
  Future<List<SchemeModel>> getEligibleSchemes(
    FarmerInputModel farmerInput,
  ) async {
    try {
      // Try fetching from API
      final schemes = await _apiService.getEligibleSchemes(farmerInput);

      // If successful, cache the results
      await _localStorageService.cacheSchemes(schemes);

      return schemes;
    } catch (e) {
      print("API request failed: $e. Loading from cache.");
      // Fallback to cache
      return await _localStorageService.getCachedSchemes();
    }
  }

  // Note: getAllSchemes and getSchemeById might need adjustment
  // if we want to support them via API or Cache.
  // For now, we assume user flow is primarily getting eligible schemes.

  // Kept for utility
  double calculateTotalBenefit(List<SchemeModel> schemes) {
    // Logic might need to be adjusted based on new Benefit format (string)
    // For now returning 0 or parsing string if possible
    // Since benefit is now a String like "Rs 5000/ha", we'd need parsing logic.
    return 0.0;
  }
}
