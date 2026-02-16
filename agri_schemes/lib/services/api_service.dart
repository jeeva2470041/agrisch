import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../models/farmer_input_model.dart';
import '../models/scheme_model.dart';

class ApiService {
  // Use localhost for Web, 10.0.2.2 for Android Emulator
  // For physical device, change this to your machine's local IP (e.g., 192.168.1.x)
  static const String _baseUrlAndroidEmulator = 'http://10.0.2.2:5000';
  static const String _baseUrlWeb = 'http://localhost:5000';

  String get baseUrl => kIsWeb ? _baseUrlWeb : _baseUrlAndroidEmulator;

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
}
