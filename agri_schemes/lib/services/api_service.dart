import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../models/farmer_input_model.dart';
import '../models/scheme_model.dart';

class ApiService {
  // For physical device via ADB reverse: localhost tunnels through USB.
  // For Wi-Fi testing, call updateBaseUrl() with your PC's LAN IP.
  static String _baseUrlPhysical = 'http://localhost:5000';
  static const String _baseUrlWeb = 'http://localhost:5000';

  String get baseUrl {
    if (kIsWeb) return _baseUrlWeb;
    return _baseUrlPhysical;
  }

  /// Update the base URL dynamically (for testing different IPs without rebuild)
  void updateBaseUrl(String newIp) {
    _baseUrlPhysical = 'http://$newIp:5000';
    debugPrint('API URL updated to: $_baseUrlPhysical');
  }

  /// Check if the backend is reachable
  Future<bool> checkHealth() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/api/'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Health check failed: $e');
      return false;
    }
  }

  Future<List<SchemeModel>> getEligibleSchemes(FarmerInputModel input) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/getEligibleSchemes'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(input.toJson()),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> body = json.decode(response.body);
        final List<dynamic> data = body['schemes'] ?? [];
        return data.map((json) => SchemeModel.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load schemes: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error connecting to API: $e');
    }
  }

  // ─────────────────────────────────────────────────
  // Weather API
  // ─────────────────────────────────────────────────
  Future<Map<String, dynamic>?> getWeather(double lat, double lon) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/weather?lat=$lat&lon=$lon'),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      debugPrint('Weather API error: $e');
      return null;
    }
  }

  // ─────────────────────────────────────────────────
  // Market Prices API
  // ─────────────────────────────────────────────────
  Future<Map<String, dynamic>?> getMarketPrices(
    String state, {
    String? crop,
  }) async {
    try {
      String url =
          '$baseUrl/api/market-prices?state=${Uri.encodeComponent(state)}';
      if (crop != null) url += '&crop=${Uri.encodeComponent(crop)}';

      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      debugPrint('Market Prices API error: $e');
      return null;
    }
  }

  // ─────────────────────────────────────────────────
  // Ask AI API
  // ─────────────────────────────────────────────────
  Future<String> askAi({
    required String question,
    required String schemeContext,
    String language = 'en',
  }) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/api/ask-ai'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'question': question,
              'scheme_context': schemeContext,
              'language': language,
            }),
          )
          .timeout(const Duration(seconds: 30));

      final body = json.decode(response.body) as Map<String, dynamic>;

      if (response.statusCode == 200 && body['success'] == true) {
        return body['answer'] as String;
      } else {
        return body['error'] as String? ?? 'Failed to get AI response';
      }
    } catch (e) {
      debugPrint('Ask AI error: $e');
      return 'Could not connect to AI service. Please try again.';
    }
  }
}
