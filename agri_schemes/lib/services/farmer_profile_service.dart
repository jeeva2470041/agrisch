import 'package:flutter/foundation.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/alert_model.dart';

/// Persists farmer profile data locally using Hive.
/// Stores state, crop preferences, sowing date, soil data, and alert triggers.
class FarmerProfileService extends ChangeNotifier {
  static const _boxName = 'farmer_profile';
  Box? _box;

  // ── Profile fields ──
  String _state = '';
  String _crop = '';
  String _season = '';
  double _landSize = 1.0;
  String _sowingDate = '';
  String _soilType = '';
  double? _soilPh;
  String _waterAvailability = 'Medium';
  double? _lat;
  double? _lon;
  List<PriceTrigger> _priceTriggers = [];
  bool _weatherAlertsEnabled = true;
  bool _priceAlertsEnabled = false;
  Set<String> _completedTasks = {};

  // ── Getters ──
  String get state => _state;
  String get crop => _crop;
  String get season => _season;
  double get landSize => _landSize;
  String get sowingDate => _sowingDate;
  String get soilType => _soilType;
  double? get soilPh => _soilPh;
  String get waterAvailability => _waterAvailability;
  double? get lat => _lat;
  double? get lon => _lon;
  List<PriceTrigger> get priceTriggers => _priceTriggers;
  bool get weatherAlertsEnabled => _weatherAlertsEnabled;
  bool get priceAlertsEnabled => _priceAlertsEnabled;
  Set<String> get completedTasks => _completedTasks;
  bool get hasProfile => _state.isNotEmpty && _crop.isNotEmpty;

  Future<void> init() async {
    _box = await Hive.openBox(_boxName);
    _state = _box?.get('state', defaultValue: '') ?? '';
    _crop = _box?.get('crop', defaultValue: '') ?? '';
    _season = _box?.get('season', defaultValue: '') ?? '';
    _landSize = _box?.get('landSize', defaultValue: 1.0) ?? 1.0;
    _sowingDate = _box?.get('sowingDate', defaultValue: '') ?? '';
    _soilType = _box?.get('soilType', defaultValue: '') ?? '';
    _soilPh = _box?.get('soilPh');
    _waterAvailability =
        _box?.get('waterAvailability', defaultValue: 'Medium') ?? 'Medium';
    _lat = _box?.get('lat');
    _lon = _box?.get('lon');
    _weatherAlertsEnabled =
        _box?.get('weatherAlertsEnabled', defaultValue: true) ?? true;
    _priceAlertsEnabled =
        _box?.get('priceAlertsEnabled', defaultValue: false) ?? false;

    // Load price triggers
    final triggerListRaw = _box?.get('priceTriggers', defaultValue: []);
    if (triggerListRaw is List) {
      _priceTriggers = triggerListRaw
          .map((t) => PriceTrigger.fromJson(Map<String, dynamic>.from(t)))
          .toList();
    }

    // Load completed tasks
    final tasksRaw = _box?.get('completedTasks', defaultValue: <String>[]);
    if (tasksRaw is List) {
      _completedTasks = Set<String>.from(tasksRaw.cast<String>());
    }
  }

  Future<void> updateProfile({
    String? state,
    String? crop,
    String? season,
    double? landSize,
    String? sowingDate,
    String? soilType,
    double? soilPh,
    String? waterAvailability,
    double? lat,
    double? lon,
  }) async {
    if (state != null) _state = state;
    if (crop != null) _crop = crop;
    if (season != null) _season = season;
    if (landSize != null) _landSize = landSize;
    if (sowingDate != null) _sowingDate = sowingDate;
    if (soilType != null) _soilType = soilType;
    if (soilPh != null) _soilPh = soilPh;
    if (waterAvailability != null) _waterAvailability = waterAvailability;
    if (lat != null) _lat = lat;
    if (lon != null) _lon = lon;

    await _box?.put('state', _state);
    await _box?.put('crop', _crop);
    await _box?.put('season', _season);
    await _box?.put('landSize', _landSize);
    await _box?.put('sowingDate', _sowingDate);
    await _box?.put('soilType', _soilType);
    await _box?.put('soilPh', _soilPh);
    await _box?.put('waterAvailability', _waterAvailability);
    await _box?.put('lat', _lat);
    await _box?.put('lon', _lon);
    notifyListeners();
  }

  Future<void> setWeatherAlertsEnabled(bool enabled) async {
    _weatherAlertsEnabled = enabled;
    await _box?.put('weatherAlertsEnabled', enabled);
    notifyListeners();
  }

  Future<void> setPriceAlertsEnabled(bool enabled) async {
    _priceAlertsEnabled = enabled;
    await _box?.put('priceAlertsEnabled', enabled);
    notifyListeners();
  }

  Future<void> updatePriceTriggers(List<PriceTrigger> triggers) async {
    _priceTriggers = triggers;
    await _box?.put(
      'priceTriggers',
      triggers.map((t) => t.toJson()).toList(),
    );
    notifyListeners();
  }

  Future<void> addPriceTrigger(PriceTrigger trigger) async {
    _priceTriggers.add(trigger);
    await _box?.put(
      'priceTriggers',
      _priceTriggers.map((t) => t.toJson()).toList(),
    );
    notifyListeners();
  }

  Future<void> removePriceTrigger(int index) async {
    if (index < _priceTriggers.length) {
      _priceTriggers.removeAt(index);
      await _box?.put(
        'priceTriggers',
        _priceTriggers.map((t) => t.toJson()).toList(),
      );
      notifyListeners();
    }
  }

  // ── Calendar task completion tracking ──
  bool isTaskCompleted(String taskKey) => _completedTasks.contains(taskKey);

  Future<void> toggleTaskCompletion(String taskKey) async {
    if (_completedTasks.contains(taskKey)) {
      _completedTasks.remove(taskKey);
    } else {
      _completedTasks.add(taskKey);
    }
    await _box?.put('completedTasks', _completedTasks.toList());
    notifyListeners();
  }
}
