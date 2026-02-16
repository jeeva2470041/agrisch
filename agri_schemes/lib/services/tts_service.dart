import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// Service to handle Text-to-Speech functionality
/// Syncs with app locale to speak in the selected language
class TtsService extends ChangeNotifier {
  final FlutterTts _flutterTts = FlutterTts();

  // Track if TTS is currently speaking
  bool _isSpeaking = false;
  bool get isSpeaking => _isSpeaking;

  // Current language for TTS
  String _currentLanguage = 'en-IN';

  static const String _defaultLanguage = 'en-IN';

  /// Initialize the TTS engine with default settings
  Future<void> init() async {
    // Set default speech rate (0.5 is normal speed)
    await _flutterTts.setSpeechRate(0.45);

    // Set volume (1.0 is maximum)
    await _flutterTts.setVolume(1.0);

    // Set pitch (1.0 is normal pitch)
    await _flutterTts.setPitch(1.0);

    // Ensure the plugin waits until speech ends before completing
    await _flutterTts.awaitSpeakCompletion(true);

    // Set up completion handler
    _flutterTts.setCompletionHandler(() {
      _isSpeaking = false;
      notifyListeners();
    });

    // Set up error handler
    _flutterTts.setErrorHandler((message) {
      debugPrint('TTS Error: $message');
      _isSpeaking = false;
      notifyListeners();
    });

    // Set up start handler
    _flutterTts.setStartHandler(() {
      _isSpeaking = true;
      notifyListeners();
    });

    // Set up cancel handler
    _flutterTts.setCancelHandler(() {
      _isSpeaking = false;
      notifyListeners();
    });
  }

  /// Update the TTS language to match the app locale
  /// [languageCode] should be like 'en-IN' or 'ta-IN'
  Future<void> setLanguage(String languageCode) async {
    final languagePrefix = _getLanguagePrefix(languageCode);
    final languageCandidates = <String>[
      languageCode,
      if (languageCode != languagePrefix) languagePrefix,
    ];

    // Try exact locale first (ta-IN), then language-only fallback (ta)
    for (final candidate in languageCandidates) {
      final isAvailable =
          _toBool(await _flutterTts.isLanguageAvailable(candidate));
      if (isAvailable) {
        _currentLanguage = candidate;
        await _flutterTts.setLanguage(candidate);
        await _setMatchingVoice(candidate);
        debugPrint('TTS language set to: $candidate (requested: $languageCode)');
        return;
      }
    }

    // If locale checks fail, still try to select a voice by language prefix.
    final matchingVoice = await _findMatchingVoice(languagePrefix);
    if (matchingVoice != null) {
      final voiceLocale = matchingVoice['locale']!;
      _currentLanguage = voiceLocale;
      await _flutterTts.setLanguage(voiceLocale);
      await _flutterTts.setVoice(matchingVoice);
      debugPrint(
          'TTS language set by voice fallback: $voiceLocale (requested: $languageCode)');
      return;
    }

    // Final fallback
    _currentLanguage = _defaultLanguage;
    await _flutterTts.setLanguage(_defaultLanguage);
    await _setMatchingVoice(_defaultLanguage);
    debugPrint(
        'TTS language $languageCode not available, using $_defaultLanguage');
  }

  /// Get the current TTS language
  String get currentLanguage => _currentLanguage;

  /// Speak the given text
  /// Stops any ongoing speech before starting new one
  Future<void> speak(String text) async {
    if (text.isEmpty) return;

    // Stop any ongoing speech
    await stop();

    // Ensure the engine is still using the selected locale
    await _flutterTts.setLanguage(_currentLanguage);

    // Start speaking
    _isSpeaking = true;
    notifyListeners();

    final result = await _flutterTts.speak(text);
    if (result != 1) {
      _isSpeaking = false;
      notifyListeners();
    }
  }

  /// Stop the current speech
  Future<void> stop() async {
    await _flutterTts.stop();
    _isSpeaking = false;
    notifyListeners();
  }

  /// Pause the current speech (if supported)
  Future<void> pause() async {
    await _flutterTts.pause();
    _isSpeaking = false;
    notifyListeners();
  }

  /// Get list of available languages
  Future<List<dynamic>> getAvailableLanguages() async {
    return await _flutterTts.getLanguages;
  }

  /// Attempt to pick a voice that matches the desired language
  Future<void> _setMatchingVoice(String languageCode) async {
    try {
      final matchingVoice =
          await _findMatchingVoice(_getLanguagePrefix(languageCode),
              preferredLocale: languageCode.toLowerCase());
      if (matchingVoice != null) {
        await _flutterTts.setVoice(matchingVoice);
        debugPrint(
            'TTS voice set to ${matchingVoice['name']} (${matchingVoice['locale']})');
      } else {
        debugPrint('No matching TTS voice found for $languageCode');
      }
    } catch (e) {
      debugPrint('Error setting TTS voice for $languageCode: $e');
    }
  }

  String _getLanguagePrefix(String languageCode) {
    return languageCode.split('-').first.toLowerCase();
  }

  bool _toBool(dynamic value) {
    if (value is bool) return value;
    if (value is int) return value == 1;
    if (value is String) {
      final normalized = value.toLowerCase();
      return normalized == 'true' || normalized == '1';
    }
    return false;
  }

  Future<Map<String, String>?> _findMatchingVoice(
    String languagePrefix, {
    String? preferredLocale,
  }) async {
    final voices = await _flutterTts.getVoices;
    if (voices is! List) return null;

    final normalizedPreferred = preferredLocale?.toLowerCase();
    Map<String, String>? prefixVoice;

    for (final voice in voices) {
      if (voice is! Map) continue;

      final normalizedVoice = Map<String, String>.from(
        voice.map((key, value) => MapEntry('$key', '$value')),
      );

      final locale = (normalizedVoice['locale'] ?? '').toLowerCase();
      if (locale.isEmpty) continue;

      if (normalizedPreferred != null && locale == normalizedPreferred) {
        return normalizedVoice;
      }

      if (prefixVoice == null && locale.startsWith(languagePrefix)) {
        prefixVoice = normalizedVoice;
      }
    }

    return prefixVoice;
  }

  /// Dispose the TTS engine
  @override
  void dispose() {
    _flutterTts.stop();
    super.dispose();
  }
}
