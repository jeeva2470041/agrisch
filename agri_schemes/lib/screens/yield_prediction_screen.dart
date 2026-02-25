import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

/// Yield Prediction Screen — Predict crop yield using RandomForest ML model.
/// User selects crop, state, season and optionally enters rainfall.
class YieldPredictionScreen extends StatefulWidget {
  const YieldPredictionScreen({super.key});

  @override
  State<YieldPredictionScreen> createState() => _YieldPredictionScreenState();
}

class _YieldPredictionScreenState extends State<YieldPredictionScreen> {
  final _api = ApiService();
  final _rainfallController = TextEditingController();

  String? _selectedCrop;
  String? _selectedState;
  String? _selectedSeason;
  bool _isLoading = false;
  Map<String, dynamic>? _result;

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  // Crops supported by the yield model
  static const _supportedCrops = [
    'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Soybean',
    'Groundnut', 'Mustard', 'Pulses', 'Coconut', 'Tea', 'Coffee',
    'Millets', 'Jute', 'Spices',
  ];

  // States with training data
  static const _supportedStates = [
    'Tamil Nadu', 'Kerala', 'Karnataka', 'Maharashtra', 'Punjab',
    'Haryana', 'Uttar Pradesh', 'Madhya Pradesh', 'Rajasthan',
    'Gujarat', 'West Bengal', 'Bihar', 'Andhra Pradesh', 'Telangana',
    'Odisha', 'Assam', 'Jharkhand', 'Chhattisgarh',
  ];

  Future<void> _predict() async {
    if (_selectedCrop == null ||
        _selectedState == null ||
        _selectedSeason == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(AppLocalizations.of(context).pleaseSelectAllFields),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _result = null;
    });

    double? rainfall;
    if (_rainfallController.text.isNotEmpty) {
      rainfall = double.tryParse(_rainfallController.text);
    }

    final result = await _api.predictYield(
      crop: _selectedCrop!,
      state: _selectedState!,
      season: _selectedSeason!,
      rainfall: rainfall,
    );

    if (mounted) {
      setState(() {
        _isLoading = false;
        _result = result;
      });
    }
  }

  @override
  void dispose() {
    _rainfallController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);

    return Scaffold(
      backgroundColor: _darkBg,
      appBar: AppBar(
        backgroundColor: _primaryGreen,
        title: Text(
          l.translate('yieldPrediction'),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Input card
            _buildInputCard(l),
            const SizedBox(height: 20),

            // Predict button
            SizedBox(
              width: double.infinity,
              height: 54,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _predict,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.analytics_rounded),
                label: Text(
                  l.translate('yieldPredict'),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _accentGreen,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Result
            if (_result != null) _buildResultCard(l),
          ],
        ),
      ),
    );
  }

  Widget _buildInputCard(AppLocalizations l) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Crop
          _buildLabel(Icons.grass_rounded, l.cropType),
          const SizedBox(height: 8),
          _buildDropdown(
            value: _selectedCrop,
            hint: l.selectCrop,
            items: _supportedCrops,
            onChanged: (v) => setState(() => _selectedCrop = v),
          ),
          const SizedBox(height: 20),

          // State
          _buildLabel(Icons.location_on_rounded, l.state),
          const SizedBox(height: 8),
          _buildDropdown(
            value: _selectedState,
            hint: l.selectState,
            items: _supportedStates,
            onChanged: (v) => setState(() => _selectedState = v),
          ),
          const SizedBox(height: 20),

          // Season
          _buildLabel(Icons.wb_sunny_rounded, l.season),
          const SizedBox(height: 8),
          _buildDropdown(
            value: _selectedSeason,
            hint: l.selectSeason,
            items: const ['Kharif', 'Rabi', 'Zaid'],
            onChanged: (v) => setState(() => _selectedSeason = v),
          ),
          const SizedBox(height: 20),

          // Rainfall (optional)
          _buildLabel(Icons.water_drop_rounded, l.translate('yieldRainfall')),
          const SizedBox(height: 8),
          TextField(
            controller: _rainfallController,
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: l.translate('yieldRainfallHint'),
              hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.4)),
              filled: true,
              fillColor: Colors.white.withValues(alpha: 0.05),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: _accentGreen),
              ),
              suffixText: 'mm',
              suffixStyle: const TextStyle(color: Colors.white54),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLabel(IconData icon, String label) {
    return Row(
      children: [
        Icon(icon, size: 18, color: _accentGreen),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildDropdown({
    required String? value,
    required String hint,
    required List<String> items,
    required ValueChanged<String?> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          hint: Text(hint, style: TextStyle(color: Colors.white.withValues(alpha: 0.4))),
          isExpanded: true,
          dropdownColor: const Color(0xFF1E3320),
          style: const TextStyle(color: Colors.white, fontSize: 15),
          icon: const Icon(Icons.arrow_drop_down, color: _accentGreen),
          items: items
              .map((item) => DropdownMenuItem(value: item, child: Text(item)))
              .toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildResultCard(AppLocalizations l) {
    final predictedYield = _result!['predicted_yield'] ?? 0.0;
    final lowerBound = _result!['lower_bound'] ?? 0.0;
    final upperBound = _result!['upper_bound'] ?? 0.0;
    final category = _result!['category'] ?? 'average';
    final avgYield = _result!['average_yield'] ?? 0.0;
    final rainfall = _result!['rainfall_mm'] ?? 0;
    final unit = _result!['yield_unit'] ?? 'tonnes/hectare';

    final categoryColor = category == 'above_average'
        ? _accentGreen
        : category == 'below_average'
            ? Colors.red
            : Colors.orange;

    final categoryLabel = category == 'above_average'
        ? l.translate('yieldAboveAvg')
        : category == 'below_average'
            ? l.translate('yieldBelowAvg')
            : l.translate('yieldAverage');

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: categoryColor.withValues(alpha: 0.5), width: 2),
      ),
      child: Column(
        children: [
          // Main yield value
          Text(
            predictedYield.toStringAsFixed(2),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 48,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            unit,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.6),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),

          // Category badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: categoryColor.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              categoryLabel,
              style: TextStyle(
                color: categoryColor,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Confidence range
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildStatItem(l.translate('yieldLower'), lowerBound.toStringAsFixed(2), Colors.orange),
              _buildStatItem(l.translate('yieldPredicted'), predictedYield.toStringAsFixed(2), _accentGreen),
              _buildStatItem(l.translate('yieldUpper'), upperBound.toStringAsFixed(2), Colors.blue),
            ],
          ),
          const SizedBox(height: 16),

          Divider(color: Colors.white.withValues(alpha: 0.1)),
          const SizedBox(height: 12),

          // Additional info
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l.translate('yieldAvgHistorical'),
                style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 13),
              ),
              Text(
                '$avgYield $unit',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l.translate('yieldRainfall'),
                style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 13),
              ),
              Text(
                '${rainfall.toStringAsFixed(0)} mm',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.5),
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}
