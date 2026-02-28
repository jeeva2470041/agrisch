import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../services/farmer_profile_service.dart';
import '../services/theme_service.dart';
import '../l10n/app_localizations.dart';

/// Settings Screen — profile editing, location, theme toggle.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  String _state = '';
  String _crop = '';
  String _season = '';
  double _landSize = 1.0;
  String _soilType = '';
  double _soilPh = 7.0;
  String _waterAvailability = 'Medium';
  double? _lat;
  double? _lon;
  String _locationLabel = '';
  bool _detectingLocation = false;
  bool _saved = false;

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  final _states = [
    'Tamil Nadu',
    'Andhra Pradesh',
    'Karnataka',
    'Kerala',
    'Maharashtra',
    'Madhya Pradesh',
    'Uttar Pradesh',
    'Punjab',
    'Haryana',
    'Rajasthan',
    'Gujarat',
    'Bihar',
    'West Bengal',
    'Odisha',
    'Telangana',
  ];

  final _seasons = ['Kharif', 'Rabi', 'Zaid', 'Whole Year'];

  final _crops = [
    'Rice',
    'Wheat',
    'Maize',
    'Cotton',
    'Sugarcane',
    'Groundnut',
    'Soybean',
    'Pulses',
    'Millets',
    'Vegetables',
    'Fruits',
    'Spices',
    'Oilseeds',
    'Jute',
    'Tea',
    'Coffee',
    'Rubber',
    'Coconut',
    'Banana',
    'Turmeric',
  ];

  final _soilTypes = [
    'Alluvial',
    'Black Cotton',
    'Red',
    'Laterite',
    'Sandy',
    'Clay',
    'Loam',
    'Sandy Loam',
    'Clay Loam',
    'Silt',
  ];

  final _waterSources = [
    'Canal',
    'Borewell',
    'Rain-fed',
    'River',
    'Tank',
    'Drip Irrigation',
    'Sprinkler',
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadProfile());
  }

  void _loadProfile() {
    final profile = Provider.of<FarmerProfileService>(context, listen: false);
    setState(() {
      _state = _states.contains(profile.state) ? profile.state : '';
      _crop = _crops.contains(profile.crop) ? profile.crop : '';
      _season = _seasons.contains(profile.season) ? profile.season : '';
      _landSize = profile.landSize > 0 ? profile.landSize : 1.0;
      _soilType =
          _soilTypes.contains(profile.soilType) ? profile.soilType : '';
      _soilPh = (profile.soilPh ?? 7.0).clamp(3.0, 10.0);
      _waterAvailability =
          _waterSources.contains(profile.waterAvailability)
              ? profile.waterAvailability
              : '';
      _lat = profile.lat;
      _lon = profile.lon;
      if (_lat != null && _lon != null) {
        _locationLabel =
            '${_lat!.toStringAsFixed(4)}, ${_lon!.toStringAsFixed(4)}';
      }
    });
  }

  Future<void> _detectLocation() async {
    setState(() => _detectingLocation = true);
    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.deniedForever ||
          permission == LocationPermission.denied) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Location permission denied')),
        );
        setState(() => _detectingLocation = false);
        return;
      }

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.low,
      );
      _lat = pos.latitude;
      _lon = pos.longitude;

      String label =
          '${_lat!.toStringAsFixed(4)}, ${_lon!.toStringAsFixed(4)}';
      try {
        final placemarks =
            await placemarkFromCoordinates(_lat!, _lon!);
        if (placemarks.isNotEmpty) {
          final p = placemarks.first;
          label =
              '${p.locality ?? ''}, ${p.administrativeArea ?? ''}';
          // Auto-fill state if it matches a known state
          final adminArea = p.administrativeArea ?? '';
          if (_states.contains(adminArea) && _state.isEmpty) {
            _state = adminArea;
          }
        }
      } catch (_) {}

      setState(() {
        _locationLabel = label;
        _detectingLocation = false;
      });
    } catch (e) {
      setState(() => _detectingLocation = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not detect location: $e')),
      );
    }
  }

  Future<void> _saveProfile() async {
    final profile = Provider.of<FarmerProfileService>(context, listen: false);
    await profile.updateProfile(
      state: _state,
      crop: _crop,
      season: _season,
      landSize: _landSize,
      soilType: _soilType,
      soilPh: _soilPh,
      waterAvailability: _waterAvailability,
      lat: _lat,
      lon: _lon,
    );
    setState(() => _saved = true);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.white),
            SizedBox(width: 8),
            Text('Profile saved successfully!'),
          ],
        ),
        backgroundColor: _accentGreen,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted) setState(() => _saved = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);
    final themeService = Provider.of<ThemeService>(context);
    final isDark = themeService.isDarkMode;

    final bgColor = isDark ? _darkBg : const Color(0xFFF5F5F5);
    final cardColor = isDark ? _cardBg : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final subtextColor = isDark ? Colors.white70 : Colors.black54;
    final borderColor =
        isDark ? Colors.white24 : Colors.grey.shade300;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: _primaryGreen,
        title: Text(l.translate('settings')),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ── Appearance ──
          _sectionHeader(l.translate('appearance'), textColor),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: borderColor),
            ),
            child: Row(
              children: [
                Icon(
                  isDark ? Icons.dark_mode_rounded : Icons.light_mode_rounded,
                  color: _accentGreen,
                  size: 28,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(l.translate('darkMode'),
                          style: TextStyle(
                              color: textColor,
                              fontWeight: FontWeight.w600,
                              fontSize: 15)),
                      const SizedBox(height: 2),
                      Text(l.translate('darkModeDesc'),
                          style:
                              TextStyle(color: subtextColor, fontSize: 12)),
                    ],
                  ),
                ),
                Switch.adaptive(
                  value: isDark,
                  activeColor: _accentGreen,
                  onChanged: (_) => themeService.toggleTheme(),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ── Location ──
          _sectionHeader(l.translate('location'), textColor),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: borderColor),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.location_on_rounded,
                        color: _accentGreen, size: 22),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _locationLabel.isEmpty
                            ? l.translate('locationNotSet')
                            : _locationLabel,
                        style: TextStyle(color: textColor, fontSize: 14),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: _detectingLocation ? null : _detectLocation,
                    icon: _detectingLocation
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2))
                        : const Icon(Icons.my_location_rounded),
                    label: Text(_detectingLocation
                        ? l.translate('detecting')
                        : l.translate('detectLocation')),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _accentGreen,
                      side: BorderSide(color: _accentGreen.withValues(alpha: 0.5)),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ── Farmer Profile ──
          _sectionHeader(l.translate('farmerProfile'), textColor),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: borderColor),
            ),
            child: Column(
              children: [
                // State
                _dropdown(
                  label: l.translate('state'),
                  value: _state,
                  items: _states,
                  icon: Icons.map_rounded,
                  textColor: textColor,
                  borderColor: borderColor,
                  cardColor: cardColor,
                  onChanged: (v) => setState(() => _state = v ?? ''),
                ),
                const SizedBox(height: 14),

                // Crop
                _dropdown(
                  label: l.translate('cropType'),
                  value: _crop,
                  items: _crops,
                  icon: Icons.grass_rounded,
                  textColor: textColor,
                  borderColor: borderColor,
                  cardColor: cardColor,
                  onChanged: (v) => setState(() => _crop = v ?? ''),
                ),
                const SizedBox(height: 14),

                // Season
                _dropdown(
                  label: l.translate('season'),
                  value: _season,
                  items: _seasons,
                  icon: Icons.wb_sunny_rounded,
                  textColor: textColor,
                  borderColor: borderColor,
                  cardColor: cardColor,
                  onChanged: (v) => setState(() => _season = v ?? ''),
                ),
                const SizedBox(height: 14),

                // Soil type
                _dropdown(
                  label: l.translate('soilType'),
                  value: _soilType,
                  items: _soilTypes,
                  icon: Icons.terrain_rounded,
                  textColor: textColor,
                  borderColor: borderColor,
                  cardColor: cardColor,
                  onChanged: (v) => setState(() => _soilType = v ?? ''),
                ),
                const SizedBox(height: 14),

                // Water source
                _dropdown(
                  label: l.translate('waterSource'),
                  value: _waterAvailability,
                  items: _waterSources,
                  icon: Icons.water_drop_rounded,
                  textColor: textColor,
                  borderColor: borderColor,
                  cardColor: cardColor,
                  onChanged: (v) =>
                      setState(() => _waterAvailability = v ?? 'Medium'),
                ),
                const SizedBox(height: 18),

                // Land size slider
                _sliderField(
                  label:
                      '${l.translate('landSize')}: ${_landSize.toStringAsFixed(1)} ha',
                  value: _landSize,
                  min: 0.1,
                  max: 50.0,
                  textColor: textColor,
                  onChanged: (v) =>
                      setState(() => _landSize = double.parse(v.toStringAsFixed(1))),
                ),
                const SizedBox(height: 12),

                // Soil pH slider
                _sliderField(
                  label: '${l.translate('soilPh')}: ${_soilPh.toStringAsFixed(1)}',
                  value: _soilPh,
                  min: 3.0,
                  max: 10.0,
                  textColor: textColor,
                  onChanged: (v) =>
                      setState(() => _soilPh = double.parse(v.toStringAsFixed(1))),
                ),
              ],
            ),
          ),

          const SizedBox(height: 28),

          // ── Save button ──
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton.icon(
              onPressed: _saveProfile,
              icon: Icon(_saved ? Icons.check_rounded : Icons.save_rounded),
              label: Text(
                l.translate('saveProfile'),
                style:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _accentGreen,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
                elevation: 2,
              ),
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // ── Helpers ──

  Widget _sectionHeader(String title, Color textColor) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title.toUpperCase(),
        style: TextStyle(
          color: _accentGreen,
          fontWeight: FontWeight.bold,
          fontSize: 13,
          letterSpacing: 1.2,
        ),
      ),
    );
  }

  Widget _dropdown({
    required String label,
    required String value,
    required List<String> items,
    required IconData icon,
    required Color textColor,
    required Color borderColor,
    required Color cardColor,
    required ValueChanged<String?> onChanged,
  }) {
    return DropdownButtonFormField<String>(
      value: value.isEmpty ? null : value,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: textColor.withValues(alpha: 0.7)),
        prefixIcon: Icon(icon, color: _accentGreen, size: 20),
        filled: true,
        fillColor: cardColor,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: borderColor),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: borderColor),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      ),
      dropdownColor: cardColor,
      style: TextStyle(color: textColor, fontSize: 14),
      items: items
          .map((e) => DropdownMenuItem(value: e, child: Text(e)))
          .toList(),
      onChanged: onChanged,
    );
  }

  Widget _sliderField({
    required String label,
    required double value,
    required double min,
    required double max,
    required Color textColor,
    required ValueChanged<double> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label,
            style: TextStyle(
                color: textColor, fontWeight: FontWeight.w500, fontSize: 14)),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: ((max - min) * 10).round(),
          activeColor: _accentGreen,
          label: value.toStringAsFixed(1),
          onChanged: onChanged,
        ),
      ],
    );
  }
}
