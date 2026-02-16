import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service to manage language selection and persistence
/// Uses SharedPreferences to store the selected language locally
class LanguageService extends ChangeNotifier {
  // Key for storing language preference in SharedPreferences
  static const String _languageKey = 'selected_language';

  // Default language is English
  Locale _currentLocale = const Locale('en', 'IN');

  /// Get the current locale
  Locale get currentLocale => _currentLocale;

  /// Get the current language code (en or ta)
  String get languageCode => _currentLocale.languageCode;

  /// Check if current language is Tamil
  bool get isTamil => _currentLocale.languageCode == 'ta';

  /// Initialize the service and load saved language preference
  Future<void> init() async {
    await _loadSavedLanguage();
  }

  /// Load the saved language from SharedPreferences
  Future<void> _loadSavedLanguage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedLanguage = prefs.getString(_languageKey);

      if (savedLanguage != null) {
        _currentLocale = Locale(savedLanguage, 'IN');
        notifyListeners();
      }
    } catch (e) {
      // If loading fails, use default English
      debugPrint('Error loading saved language: $e');
    }
  }

  /// Change the app language and save to SharedPreferences
  /// [languageCode] should be 'en' for English or 'ta' for Tamil
  Future<void> setLanguage(String languageCode) async {
    if (!['en', 'ta', 'hi', 'ml'].contains(languageCode)) {
      debugPrint('Invalid language code: $languageCode');
      return;
    }

    _currentLocale = Locale(languageCode, 'IN');

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_languageKey, languageCode);
    } catch (e) {
      debugPrint('Error saving language preference: $e');
    }

    // Notify listeners to rebuild widgets with new locale
    notifyListeners();
  }

  /// Get the TTS language code for the current locale
  /// Returns 'en-IN' for English and 'ta-IN' for Tamil
  String get ttsLanguageCode {
    return '${_currentLocale.languageCode}-IN';
  }
}
