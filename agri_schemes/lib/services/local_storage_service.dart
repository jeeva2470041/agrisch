import 'package:flutter/foundation.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'dart:convert';
import '../models/scheme_model.dart';

class LocalStorageService {
  static const String _boxName = 'schemes_cache';
  static const String _key = 'cached_schemes';

  /// Save schemes to local storage
  Future<void> cacheSchemes(List<SchemeModel> schemes) async {
    final box = await Hive.openBox(_boxName);
    final List<Map<String, dynamic>> jsonList = schemes
        .map((e) => e.toJson())
        .toList();
    // Storing as JSON string to avoid creating TypeAdapters for now
    await box.put(_key, json.encode(jsonList));
  }

  /// Retrieve schemes from local storage
  Future<List<SchemeModel>> getCachedSchemes() async {
    final box = await Hive.openBox(_boxName);
    final String? jsonString = box.get(_key);

    if (jsonString == null) return [];

    try {
      final List<dynamic> jsonList = json.decode(jsonString);
      return jsonList.map((e) => SchemeModel.fromJson(e)).toList();
    } catch (e) {
      debugPrint("Error decoding cached schemes: $e");
      return [];
    }
  }

  /// Clear cache
  Future<void> clearCache() async {
    final box = await Hive.openBox(_boxName);
    await box.clear();
  }
}
