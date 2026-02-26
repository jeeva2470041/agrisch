import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_recognition_error.dart';

/// Service to handle Speech-to-Text functionality.
/// Provides voice-input capability in the user's selected language.
///
/// On Flutter Web, initialization is deferred to the first user-triggered
/// [startListening] call because the browser requires a user gesture before
/// granting microphone access.
class SttService extends ChangeNotifier {
  final SpeechToText _speech = SpeechToText();

  bool _isInitialized = false;
  bool _isAvailable = false;
  bool _isListening = false;
  String _lastWords = '';
  String _currentLocaleId = 'en_IN';
  double _confidence = 0.0;
  String _errorMessage = '';

  // Public getters
  bool get isAvailable => _isAvailable;
  bool get isListening => _isListening;
  String get lastWords => _lastWords;
  double get confidence => _confidence;
  String get errorMessage => _errorMessage;

  /// Try to initialize eagerly (works on mobile, may fail silently on web).
  Future<void> init() async {
    await _tryInitialize();
  }

  /// Internal init — safe to call multiple times.
  Future<bool> _tryInitialize() async {
    if (_isInitialized && _isAvailable) return true;

    try {
      _isAvailable = await _speech.initialize(
        onError: _onError,
        onStatus: _onStatus,
        debugLogging: false,
      );
      _isInitialized = true;
      debugPrint('STT initialized: available=$_isAvailable');
    } catch (e) {
      _isAvailable = false;
      _isInitialized = false;
      debugPrint('STT init error: $e');
    }
    notifyListeners();
    return _isAvailable;
  }

  /// Set the recognition locale.
  /// [languageCode] format: 'en-IN' → converted to 'en_IN' internally.
  void setLanguage(String languageCode) {
    _currentLocaleId = languageCode.replaceAll('-', '_');
    debugPrint('STT language set to: $_currentLocaleId');
  }

  /// Start listening for speech input.
  /// Lazily initializes on first call (important for web — needs user gesture).
  /// [onResult] is called with recognized text (partial + final).
  /// Returns false if STT is unavailable so the caller can show feedback.
  Future<bool> startListening({required ValueChanged<String> onResult}) async {
    _errorMessage = '';

    // Lazy init on first use (this IS inside a user gesture → mic allowed)
    if (!_isAvailable) {
      final ok = await _tryInitialize();
      if (!ok) {
        _errorMessage = 'Speech recognition is not available on this device.';
        notifyListeners();
        return false;
      }
    }

    _lastWords = '';
    _isListening = true;
    notifyListeners();

    try {
      await _speech.listen(
        onResult: (SpeechRecognitionResult result) {
          _lastWords = result.recognizedWords;
          _confidence = result.confidence;
          onResult(_lastWords);
          notifyListeners();
        },
        localeId: _currentLocaleId,
        listenFor: const Duration(seconds: 60),
        pauseFor: const Duration(seconds: 5),
      );
    } catch (e) {
      debugPrint('STT listen error: $e');
      _isListening = false;
      _errorMessage = 'Could not start listening. Please try again.';
      notifyListeners();
      return false;
    }

    return true;
  }

  /// Stop listening.
  Future<void> stopListening() async {
    try {
      await _speech.stop();
    } catch (_) {}
    _isListening = false;
    notifyListeners();
  }

  /// Cancel listening (discards partial results).
  Future<void> cancelListening() async {
    try {
      await _speech.cancel();
    } catch (_) {}
    _isListening = false;
    _lastWords = '';
    notifyListeners();
  }

  // ── Internal handlers ──

  void _onError(SpeechRecognitionError error) {
    debugPrint('STT error: ${error.errorMsg} (permanent: ${error.permanent})');
    _isListening = false;
    if (error.permanent) {
      _errorMessage =
          'Microphone access denied. Please allow microphone permission.';
    }
    notifyListeners();
  }

  void _onStatus(String status) {
    debugPrint('STT status: $status');
    if (status == 'done' || status == 'notListening') {
      _isListening = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _speech.stop();
    super.dispose();
  }
}
