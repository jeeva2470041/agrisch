import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/farmer_profile_service.dart';
import '../models/crop_recommendation_model.dart';
import '../l10n/app_localizations.dart';

/// Smart Crop Recommendation Screen — recommends optimal crops
/// based on soil, weather, market prices and available schemes.
class CropRecommendationScreen extends StatefulWidget {
  final String? soilType;
  final double? soilPh;

  const CropRecommendationScreen({super.key, this.soilType, this.soilPh});

  @override
  State<CropRecommendationScreen> createState() =>
      _CropRecommendationScreenState();
}

class _CropRecommendationScreenState extends State<CropRecommendationScreen> {
  final _api = ApiService();

  bool _loading = false;
  CropRecommendationModel? _result;
  String? _error;

  String _state = '';
  String _season = '';
  String _soilType = '';
  double _soilPh = 7.0;
  String _waterSource = '';
  double _landSize = 1.0;

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

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  @override
  void initState() {
    super.initState();
    // Pre-fill from soil analysis if navigated from there
    if (widget.soilType != null && _soilTypes.contains(widget.soilType)) {
      _soilType = widget.soilType!;
    }
    if (widget.soilPh != null) _soilPh = widget.soilPh!;

    // Pre-fill from farmer profile (only if value exists in dropdown list)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final profile =
          Provider.of<FarmerProfileService>(context, listen: false);
      setState(() {
        if (_state.isEmpty && profile.state.isNotEmpty && _states.contains(profile.state)) {
          _state = profile.state;
        }
        if (_season.isEmpty && profile.season.isNotEmpty && _seasons.contains(profile.season)) {
          _season = profile.season;
        }
        if (_soilType.isEmpty && profile.soilType.isNotEmpty && _soilTypes.contains(profile.soilType)) {
          _soilType = profile.soilType;
        }
        if (widget.soilPh == null && (profile.soilPh ?? 0) > 0) {
          _soilPh = profile.soilPh!;
        }
        if (profile.waterAvailability.isNotEmpty && _waterSources.contains(profile.waterAvailability)) {
          _waterSource = profile.waterAvailability;
        }
        if (profile.landSize > 0) _landSize = profile.landSize;
      });
    });
  }

  Future<void> _getRecommendations() async {
    if (_state.isEmpty || _season.isEmpty) {
      setState(() => _error = 'Please select at least State and Season.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    final profile =
        Provider.of<FarmerProfileService>(context, listen: false);
    final langCode =
        AppLocalizations.of(context)?.locale.languageCode ?? 'en';

    final resp = await _api.recommendCrop(
      state: _state,
      season: _season,
      soilType: _soilType.isEmpty ? '' : _soilType,
      ph: _soilPh,
      waterAvailability: _waterSource.isEmpty ? 'Medium' : _waterSource,
      landSize: _landSize,
      lat: profile.lat,
      lon: profile.lon,
      language: langCode,
    );

    setState(() {
      _loading = false;
      if (resp.containsKey('error')) {
        _error = resp['error'];
      } else {
        _result = CropRecommendationModel.fromJson(resp);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context)!;
    return Scaffold(
      backgroundColor: _darkBg,
      appBar: AppBar(
        backgroundColor: _primaryGreen,
        title: Text(l.translate('cropRecommendation')),
      ),
      body: _result != null ? _buildResults(l) : _buildForm(l),
    );
  }

  Widget _buildForm(AppLocalizations l) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [_primaryGreen, Colors.teal.shade700],
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              const Icon(Icons.auto_awesome, color: Colors.amber, size: 40),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l.translate('smartCropRecommender'),
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(l.translate('cropRecommenderDesc'),
                        style: const TextStyle(
                            color: Colors.white70, fontSize: 12)),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        // Input fields
        _buildDropdownField(l.translate('state'), _states, _state,
            (v) => setState(() => _state = v ?? '')),
        const SizedBox(height: 12),
        _buildDropdownField(l.translate('season'), _seasons, _season,
            (v) => setState(() => _season = v ?? '')),
        const SizedBox(height: 12),
        _buildDropdownField(l.translate('soilType'), _soilTypes, _soilType,
            (v) => setState(() => _soilType = v ?? '')),
        const SizedBox(height: 12),
        _buildDropdownField(l.translate('waterSource'), _waterSources, _waterSource,
            (v) => setState(() => _waterSource = v ?? '')),
        const SizedBox(height: 12),
        // pH slider
        _buildSliderField('${l.translate('phValue')}: ${_soilPh.toStringAsFixed(1)}',
            _soilPh, 0, 14, (v) => setState(() => _soilPh = v)),
        const SizedBox(height: 12),
        // Land size slider
        _buildSliderField(
            '${l.translate('landSize')}: ${_landSize.toStringAsFixed(1)} ${l.translate('acres')}',
            _landSize,
            0.5,
            50,
            (v) => setState(() => _landSize = v)),
        const SizedBox(height: 24),
        if (_error != null) ...[
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red.shade900.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(_error!, style: const TextStyle(color: Colors.red)),
          ),
          const SizedBox(height: 12),
        ],
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: !_loading ? _getRecommendations : null,
            icon: _loading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2))
                : const Icon(Icons.auto_awesome),
            label: Text(_loading
                ? l.translate('analyzing')
                : l.translate('getRecommendations')),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepPurple,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14)),
              textStyle:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildResults(AppLocalizations l) {
    final rec = _result!;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Back to form
        TextButton.icon(
          onPressed: () => setState(() => _result = null),
          icon: const Icon(Icons.arrow_back, color: _accentGreen),
          label: Text(l.translate('changeInputs'),
              style: const TextStyle(color: _accentGreen)),
        ),
        const SizedBox(height: 8),
        // General advice
        if (rec.generalAdvice.isNotEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade900.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.blue.shade700.withValues(alpha: 0.4)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lightbulb_rounded, color: Colors.amber),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(rec.generalAdvice,
                      style: const TextStyle(
                          color: Colors.white70, fontSize: 13)),
                ),
              ],
            ),
          ),
        if (rec.bestSowingWindow.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                const Icon(Icons.calendar_today, color: _accentGreen, size: 20),
                const SizedBox(width: 10),
                Text('Best sowing: ',
                    style: const TextStyle(color: Colors.white54, fontSize: 13)),
                Text(rec.bestSowingWindow,
                    style: const TextStyle(
                        color: Colors.white, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
        const SizedBox(height: 20),
        // Crop cards
        ...rec.recommendations.asMap().entries.map((e) => _buildCropCard(e.key, e.value)),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildCropCard(int rank, RecommendedCrop crop) {
    final scoreColor = crop.suitabilityScore >= 80
        ? Colors.green
        : crop.suitabilityScore >= 60
            ? Colors.lightGreen
            : crop.suitabilityScore >= 40
                ? Colors.orange
                : Colors.red;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: rank == 0
              ? Colors.amber.withValues(alpha: 0.5)
              : _accentGreen.withValues(alpha: 0.2),
          width: rank == 0 ? 2 : 1,
        ),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: rank == 0
                  ? Colors.amber.withValues(alpha: 0.08)
                  : Colors.transparent,
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: rank == 0
                        ? Colors.amber
                        : _accentGreen.withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Text('#${rank + 1}',
                        style: TextStyle(
                            color: rank == 0 ? Colors.black : Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 14)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    crop.crop,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold),
                  ),
                ),
                // Score badge
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: scoreColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: scoreColor.withValues(alpha: 0.6)),
                  ),
                  child: Text(
                    '${crop.suitabilityScore}%',
                    style: TextStyle(
                        color: scoreColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 16),
                  ),
                ),
              ],
            ),
          ),
          // Score bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: crop.suitabilityScore / 100,
                backgroundColor: Colors.white12,
                valueColor: AlwaysStoppedAnimation(scoreColor),
                minHeight: 6,
              ),
            ),
          ),
          const SizedBox(height: 12),
          // Key metrics
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _buildMetric(Icons.grass, 'Yield', crop.expectedYield),
                _buildMetric(Icons.currency_rupee, 'Revenue', crop.expectedRevenue),
                _buildMetric(Icons.water_drop, 'Water', crop.waterRequirement),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _buildMetric(Icons.schedule, 'Duration', crop.growthDuration),
                _buildMetric(
                    Icons.account_balance_wallet, 'Investment', crop.investmentEstimate),
              ],
            ),
          ),
          // Reasoning
          if (crop.reasoning.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              child: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: _darkBg,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline, color: Colors.white38, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(crop.reasoning,
                          style: const TextStyle(
                              color: Colors.white54, fontSize: 12)),
                    ),
                  ],
                ),
              ),
            ),
          // Risk factors
          if (crop.riskFactors.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Wrap(
                spacing: 6,
                runSpacing: 6,
                children: crop.riskFactors.map((r) {
                  return Chip(
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    label: Text(r,
                        style:
                            const TextStyle(color: Colors.white70, fontSize: 11)),
                    backgroundColor: Colors.red.shade900.withValues(alpha: 0.4),
                    avatar: const Icon(Icons.warning_amber_rounded,
                        color: Colors.amber, size: 14),
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                  );
                }).toList(),
              ),
            ),
          // Matching schemes
          if (crop.matchingSchemes.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Wrap(
                spacing: 6,
                runSpacing: 6,
                children: crop.matchingSchemes.map((s) {
                  return Chip(
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    label: Text(s,
                        style: const TextStyle(
                            color: Colors.lightGreenAccent, fontSize: 11)),
                    backgroundColor: _primaryGreen.withValues(alpha: 0.4),
                    avatar: const Icon(Icons.verified_rounded,
                        color: Colors.lightGreenAccent, size: 14),
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                  );
                }).toList(),
              ),
            ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildMetric(IconData icon, String label, String value) {
    return Expanded(
      child: Row(
        children: [
          Icon(icon, color: Colors.white38, size: 14),
          const SizedBox(width: 4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: const TextStyle(color: Colors.white38, fontSize: 10)),
                Text(value,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                    overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownField(String label, List<String> items, String value,
      ValueChanged<String?> onChanged) {
    return DropdownButtonFormField<String>(
      value: value.isEmpty ? null : value,
      dropdownColor: _cardBg,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white54),
        filled: true,
        fillColor: _cardBg,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: _accentGreen.withValues(alpha: 0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _accentGreen),
        ),
      ),
      items: items
          .map((s) => DropdownMenuItem(value: s, child: Text(s)))
          .toList(),
      onChanged: onChanged,
    );
  }

  Widget _buildSliderField(
      String label, double value, double min, double max, ValueChanged<double> onChanged) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Colors.white54, fontSize: 14)),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: ((max - min) * 2).toInt(),
            activeColor: _accentGreen,
            inactiveColor: Colors.white12,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
