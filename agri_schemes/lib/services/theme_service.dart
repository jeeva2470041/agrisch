import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';

/// Persists and manages the app theme mode (light / dark).
class ThemeService extends ChangeNotifier {
  static const _boxName = 'app_settings';
  static const _key = 'isDarkMode';
  Box? _box;
  bool _isDarkMode = true; // Default: dark (matches existing screens)

  bool get isDarkMode => _isDarkMode;
  ThemeMode get themeMode => _isDarkMode ? ThemeMode.dark : ThemeMode.light;

  Future<void> init() async {
    _box = await Hive.openBox(_boxName);
    _isDarkMode = _box?.get(_key, defaultValue: true) ?? true;
  }

  Future<void> toggleTheme() async {
    _isDarkMode = !_isDarkMode;
    await _box?.put(_key, _isDarkMode);
    notifyListeners();
  }

  Future<void> setDarkMode(bool value) async {
    if (_isDarkMode == value) return;
    _isDarkMode = value;
    await _box?.put(_key, value);
    notifyListeners();
  }
}
