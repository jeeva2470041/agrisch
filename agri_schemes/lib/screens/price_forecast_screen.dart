import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

/// Price Forecast Screen — Shows 7-day market price forecast for a crop
/// using Facebook Prophet / statistical forecasting.
class PriceForecastScreen extends StatefulWidget {
  final String? initialCrop;
  const PriceForecastScreen({super.key, this.initialCrop});

  @override
  State<PriceForecastScreen> createState() => _PriceForecastScreenState();
}

class _PriceForecastScreenState extends State<PriceForecastScreen> {
  final _api = ApiService();

  String? _selectedCrop;
  bool _isLoading = false;
  Map<String, dynamic>? _forecast;

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  static const _crops = [
    'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Soybean',
    'Groundnut', 'Mustard', 'Jowar', 'Bajra', 'Ragi', 'Tur',
    'Moong', 'Urad', 'Coconut', 'Tea', 'Coffee', 'Jute',
    'Tobacco', 'Rubber', 'Millets', 'Pulses', 'Sunflower', 'Spices',
  ];

  @override
  void initState() {
    super.initState();
    if (widget.initialCrop != null && _crops.contains(widget.initialCrop)) {
      _selectedCrop = widget.initialCrop;
      _loadForecast();
    }
  }

  Future<void> _loadForecast() async {
    if (_selectedCrop == null) return;

    setState(() {
      _isLoading = true;
      _forecast = null;
    });

    final result = await _api.getPriceForecast(_selectedCrop!);

    if (mounted) {
      setState(() {
        _isLoading = false;
        _forecast = result;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);

    return Scaffold(
      backgroundColor: _darkBg,
      appBar: AppBar(
        backgroundColor: _primaryGreen,
        title: Text(
          l.translate('priceForecast'),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Crop selector
            _buildCropSelector(l),
            const SizedBox(height: 20),

            if (_isLoading)
              const Padding(
                padding: EdgeInsets.only(top: 40),
                child: CircularProgressIndicator(color: _accentGreen),
              ),

            if (_forecast != null && !_isLoading) ...[
              _buildSummaryCard(l),
              const SizedBox(height: 16),
              _buildForecastList(l),
              const SizedBox(height: 16),
              _buildHistoryCard(l),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCropSelector(AppLocalizations l) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: _selectedCrop,
                  hint: Text(
                    l.selectCrop,
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.4)),
                  ),
                  isExpanded: true,
                  dropdownColor: const Color(0xFF1E3320),
                  style: const TextStyle(color: Colors.white, fontSize: 15),
                  icon: const Icon(Icons.arrow_drop_down, color: _accentGreen),
                  items: _crops
                      .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                      .toList(),
                  onChanged: (v) {
                    setState(() => _selectedCrop = v);
                    _loadForecast();
                  },
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          ElevatedButton(
            onPressed: _isLoading ? null : _loadForecast,
            style: ElevatedButton.styleFrom(
              backgroundColor: _accentGreen,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Icon(Icons.show_chart_rounded),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(AppLocalizations l) {
    final crop = _forecast!['crop'] ?? '';
    final baseMsp = _forecast!['base_msp'] ?? 0;
    final trendPct = _forecast!['trend_pct'] ?? 0.0;
    final trend = _forecast!['trend'] ?? 'stable';
    final bestDay = _forecast!['best_selling_day'] ?? '';
    final bestPrice = _forecast!['best_predicted_price'] ?? 0;
    final method = _forecast!['method'] ?? '';

    final trendColor = trend == 'up'
        ? _accentGreen
        : trend == 'down'
            ? Colors.red
            : Colors.orange;
    final trendIcon = trend == 'up'
        ? Icons.trending_up_rounded
        : trend == 'down'
            ? Icons.trending_down_rounded
            : Icons.trending_flat_rounded;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: trendColor.withValues(alpha: 0.4), width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                '${_cropEmoji(crop)} $crop',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: trendColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(trendIcon, color: trendColor, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '${trendPct > 0 ? '+' : ''}$trendPct%',
                      style: TextStyle(
                        color: trendColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildInfoRow(l.translate('forecastMSP'), '₹$baseMsp/quintal'),
          _buildInfoRow(l.translate('forecastBestDay'), bestDay),
          _buildInfoRow(l.translate('forecastBestPrice'), '₹${bestPrice.toStringAsFixed(0)}/quintal'),
          _buildInfoRow(l.translate('forecastMethod'), method == 'prophet' ? 'Facebook Prophet' : 'Statistical'),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 13),
          ),
          Text(
            value,
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildForecastList(AppLocalizations l) {
    final forecastDays = (_forecast!['forecast'] as List?) ?? [];

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l.translate('forecastNext7Days'),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ...forecastDays.map<Widget>((day) {
            final date = day['date'] ?? '';
            final price = day['predicted_price'] ?? 0;
            final lower = day['lower_bound'] ?? 0;
            final upper = day['upper_bound'] ?? 0;
            final isBest = date == _forecast!['best_selling_day'];

            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: isBest
                    ? _accentGreen.withValues(alpha: 0.15)
                    : Colors.white.withValues(alpha: 0.03),
                borderRadius: BorderRadius.circular(12),
                border: isBest
                    ? Border.all(color: _accentGreen.withValues(alpha: 0.5))
                    : null,
              ),
              child: Row(
                children: [
                  // Date
                  SizedBox(
                    width: 90,
                    child: Text(
                      date,
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.7),
                        fontSize: 13,
                      ),
                    ),
                  ),
                  // Price
                  Expanded(
                    child: Text(
                      '₹${price.toStringAsFixed(0)}',
                      style: TextStyle(
                        color: isBest ? _accentGreen : Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  // Range
                  Text(
                    '₹${lower.toStringAsFixed(0)} - ₹${upper.toStringAsFixed(0)}',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.4),
                      fontSize: 11,
                    ),
                  ),
                  if (isBest) ...[
                    const SizedBox(width: 8),
                    const Icon(Icons.star_rounded, color: _accentGreen, size: 18),
                  ],
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildHistoryCard(AppLocalizations l) {
    final history = (_forecast!['historical'] as List?) ?? [];
    if (history.isEmpty) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l.translate('forecastHistory'),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ...history.map<Widget>((h) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    h['ds'] ?? '',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.5),
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    '₹${(h['y'] ?? 0).toStringAsFixed(0)}',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontWeight: FontWeight.w500,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  String _cropEmoji(String crop) {
    const map = {
      'Rice': '🌾', 'Wheat': '🌾', 'Maize': '🌽', 'Cotton': '🏵️',
      'Sugarcane': '🎋', 'Soybean': '🫘', 'Groundnut': '🥜',
      'Mustard': '🌻', 'Coconut': '🥥', 'Tea': '🍵', 'Coffee': '☕',
      'Rubber': '🌳', 'Jute': '🧵', 'Tobacco': '🍂', 'Spices': '🌶️',
      'Millets': '🌾', 'Pulses': '🫘', 'Sunflower': '🌻',
    };
    return map[crop] ?? '🌱';
  }
}
