import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/farmer_profile_service.dart';
import '../models/alert_model.dart';
import '../l10n/app_localizations.dart';

/// Alert Settings & Notifications Screen — weather + price alerts.
class AlertSettingsScreen extends StatefulWidget {
  const AlertSettingsScreen({super.key});

  @override
  State<AlertSettingsScreen> createState() => _AlertSettingsScreenState();
}

class _AlertSettingsScreenState extends State<AlertSettingsScreen>
    with SingleTickerProviderStateMixin {
  final _api = ApiService();
  late TabController _tabCtrl;

  // Weather alerts
  bool _loadingWeather = false;
  AlertsResponse? _weatherAlerts;
  String? _weatherError;

  // Price alerts
  bool _loadingPrices = false;
  List<Map<String, dynamic>>? _priceAlertResults;
  String? _priceError;

  // New trigger form
  final _cropCtrl = TextEditingController();
  final _priceCtrl = TextEditingController();
  String _direction = 'above';

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    _cropCtrl.dispose();
    _priceCtrl.dispose();
    super.dispose();
  }

  Future<void> _checkWeatherAlerts() async {
    final profile = Provider.of<FarmerProfileService>(context, listen: false);
    if (profile.lat == null || profile.lon == null) {
      setState(
          () => _weatherError = 'Location not set. Please update your profile with location.');
      return;
    }

    setState(() {
      _loadingWeather = true;
      _weatherError = null;
    });

    final resp =
        await _api.getWeatherAlerts(profile.lat!, profile.lon!);

    setState(() {
      _loadingWeather = false;
      if (resp == null) {
        _weatherError = 'Could not fetch weather alerts. Please try again.';
      } else if (resp.containsKey('error')) {
        _weatherError = resp['error'];
      } else {
        _weatherAlerts = AlertsResponse.fromJson(resp);
      }
    });
  }

  Future<void> _checkPriceAlerts() async {
    final profile = Provider.of<FarmerProfileService>(context, listen: false);
    if (profile.state.isEmpty) {
      setState(() => _priceError = 'State not set. Please update your profile.');
      return;
    }
    if (profile.priceTriggers.isEmpty) {
      setState(() => _priceError = 'No price triggers set. Add a trigger below.');
      return;
    }

    setState(() {
      _loadingPrices = true;
      _priceError = null;
    });

    final triggers =
        profile.priceTriggers.map((t) => t.toJson()).toList();
    final resp =
        await _api.checkPriceAlerts(state: profile.state, triggers: triggers);

    setState(() {
      _loadingPrices = false;
      if (resp == null) {
        _priceError = 'Could not fetch price alerts. Please try again.';
      } else if (resp.containsKey('error')) {
        _priceError = resp['error'];
      } else {
        final alerts = resp['alerts'];
        if (alerts is List) {
          _priceAlertResults = alerts.cast<Map<String, dynamic>>();
        }
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
        title: Text(l.translate('alertSettings')),
        bottom: TabBar(
          controller: _tabCtrl,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          tabs: [
            Tab(
                icon: const Icon(Icons.thunderstorm_rounded),
                text: l.translate('weatherAlerts')),
            Tab(
                icon: const Icon(Icons.trending_up_rounded),
                text: l.translate('priceAlerts')),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabCtrl,
        children: [
          _buildWeatherTab(l),
          _buildPriceTab(l),
        ],
      ),
    );
  }

  Widget _buildWeatherTab(AppLocalizations l) {
    final profile = Provider.of<FarmerProfileService>(context);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Toggle
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _cardBg,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Row(
            children: [
              const Icon(Icons.notifications_active, color: Colors.amber),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l.translate('weatherAlertsEnabled'),
                        style: const TextStyle(
                            color: Colors.white, fontWeight: FontWeight.w600)),
                    Text(l.translate('weatherAlertsDesc'),
                        style: const TextStyle(
                            color: Colors.white54, fontSize: 12)),
                  ],
                ),
              ),
              Switch(
                value: profile.weatherAlertsEnabled,
                activeColor: _accentGreen,
                onChanged: (v) => profile.setWeatherAlertsEnabled(v),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Check now button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: !_loadingWeather ? _checkWeatherAlerts : null,
            icon: _loadingWeather
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2))
                : const Icon(Icons.refresh),
            label: Text(_loadingWeather
                ? l.translate('checking')
                : l.translate('checkNow')),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepOrange.shade700,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        if (_weatherError != null) ...[
          const SizedBox(height: 16),
          _buildErrorBox(_weatherError!),
        ],
        if (_weatherAlerts != null) ...[
          const SizedBox(height: 16),
          _buildWeatherSummary(_weatherAlerts!),
          const SizedBox(height: 12),
          ..._weatherAlerts!.alerts.map(_buildWeatherAlertCard),
        ],
      ],
    );
  }

  Widget _buildWeatherSummary(AlertsResponse alerts) {
    final hasCritical = alerts.criticalCount > 0;
    final hasHigh = alerts.highCount > 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: hasCritical
            ? Colors.red.shade900.withValues(alpha: 0.3)
            : hasHigh
                ? Colors.orange.shade900.withValues(alpha: 0.3)
                : Colors.green.shade900.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: hasCritical
              ? Colors.red.withValues(alpha: 0.5)
              : hasHigh
                  ? Colors.orange.withValues(alpha: 0.5)
                  : Colors.green.withValues(alpha: 0.5),
        ),
      ),
      child: Row(
        children: [
          Icon(
            hasCritical
                ? Icons.dangerous_rounded
                : hasHigh
                    ? Icons.warning_rounded
                    : Icons.check_circle_rounded,
            color: hasCritical
                ? Colors.red
                : hasHigh
                    ? Colors.orange
                    : Colors.green,
            size: 32,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alerts.alerts.isEmpty
                      ? 'No alerts'
                      : '${alerts.alerts.length} alert(s) found',
                  style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.bold),
                ),
                Text(alerts.summary,
                    style: const TextStyle(
                        color: Colors.white70, fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherAlertCard(WeatherAlert alert) {
    final severityColor = alert.severity == 'critical'
        ? Colors.red
        : alert.severity == 'high'
            ? Colors.orange
            : Colors.amber;
    final icon = alert.type == 'storm'
        ? Icons.thunderstorm
        : alert.type == 'heat'
            ? Icons.wb_sunny_rounded
            : alert.type == 'frost'
                ? Icons.ac_unit
                : alert.type == 'rain'
                    ? Icons.water_drop
                    : Icons.warning_rounded;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: severityColor.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: severityColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: severityColor, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(alert.title,
                          style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14)),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: severityColor.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        alert.severity.toUpperCase(),
                        style: TextStyle(
                            color: severityColor,
                            fontSize: 10,
                            fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(alert.description,
                    style: const TextStyle(
                        color: Colors.white54, fontSize: 12)),
                if (alert.action.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.tips_and_updates,
                          color: Colors.amber, size: 14),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(alert.action,
                            style: const TextStyle(
                                color: Colors.amber, fontSize: 11)),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceTab(AppLocalizations l) {
    final profile = Provider.of<FarmerProfileService>(context);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Toggle
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _cardBg,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Row(
            children: [
              const Icon(Icons.price_change_rounded, color: _accentGreen),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l.translate('priceAlertsEnabled'),
                        style: const TextStyle(
                            color: Colors.white, fontWeight: FontWeight.w600)),
                    Text(l.translate('priceAlertsDesc'),
                        style: const TextStyle(
                            color: Colors.white54, fontSize: 12)),
                  ],
                ),
              ),
              Switch(
                value: profile.priceAlertsEnabled,
                activeColor: _accentGreen,
                onChanged: (v) => profile.setPriceAlertsEnabled(v),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Existing triggers
        Text(l.translate('yourPriceTriggers'),
            style: const TextStyle(
                color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        if (profile.priceTriggers.isEmpty)
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(l.translate('noPriceTriggers'),
                  style: const TextStyle(color: Colors.white38)),
            ),
          )
        else
          ...profile.priceTriggers.asMap().entries.map((e) {
            final trigger = e.value;
            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _cardBg,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    trigger.direction == 'above'
                        ? Icons.trending_up
                        : Icons.trending_down,
                    color: trigger.direction == 'above'
                        ? Colors.green
                        : Colors.red,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      '${trigger.crop} ${trigger.direction} ₹${trigger.thresholdPrice.toStringAsFixed(0)}/quintal',
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.red, size: 20),
                    onPressed: () => profile.removePriceTrigger(e.key),
                  ),
                ],
              ),
            );
          }),
        const SizedBox(height: 16),
        // Add trigger form
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _cardBg,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: _accentGreen.withValues(alpha: 0.2)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(l.translate('addPriceTrigger'),
                  style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              TextField(
                controller: _cropCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: l.translate('cropName'),
                  labelStyle: const TextStyle(color: Colors.white54),
                  hintText: 'e.g., Rice, Wheat',
                  hintStyle: const TextStyle(color: Colors.white24),
                  filled: true,
                  fillColor: _darkBg,
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10)),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Colors.white24),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _priceCtrl,
                keyboardType: TextInputType.number,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: '${l.translate('thresholdPrice')} (₹/quintal)',
                  labelStyle: const TextStyle(color: Colors.white54),
                  hintText: 'e.g., 2500',
                  hintStyle: const TextStyle(color: Colors.white24),
                  filled: true,
                  fillColor: _darkBg,
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10)),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Colors.white24),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Text(l.translate('alertWhen'),
                      style: const TextStyle(color: Colors.white54)),
                  const SizedBox(width: 12),
                  ChoiceChip(
                    label: Text(l.translate('above')),
                    selected: _direction == 'above',
                    selectedColor: Colors.green.shade800,
                    labelStyle: const TextStyle(color: Colors.white),
                    onSelected: (_) => setState(() => _direction = 'above'),
                  ),
                  const SizedBox(width: 8),
                  ChoiceChip(
                    label: Text(l.translate('below')),
                    selected: _direction == 'below',
                    selectedColor: Colors.red.shade800,
                    labelStyle: const TextStyle(color: Colors.white),
                    onSelected: (_) => setState(() => _direction = 'below'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    final crop = _cropCtrl.text.trim();
                    final price = double.tryParse(_priceCtrl.text.trim());
                    if (crop.isEmpty || price == null) return;
                    profile.addPriceTrigger(PriceTrigger(
                      crop: crop,
                      thresholdPrice: price,
                      direction: _direction,
                    ));
                    _cropCtrl.clear();
                    _priceCtrl.clear();
                  },
                  icon: const Icon(Icons.add),
                  label: Text(l.translate('addTrigger')),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _accentGreen,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Check price alerts button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: !_loadingPrices ? _checkPriceAlerts : null,
            icon: _loadingPrices
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2))
                : const Icon(Icons.search),
            label: Text(_loadingPrices
                ? l.translate('checking')
                : l.translate('checkPriceAlerts')),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal.shade700,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        if (_priceError != null) ...[
          const SizedBox(height: 16),
          _buildErrorBox(_priceError!),
        ],
        if (_priceAlertResults != null) ...[
          const SizedBox(height: 16),
          ..._priceAlertResults!.map(_buildPriceAlertCard),
        ],
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildPriceAlertCard(Map<String, dynamic> alert) {
    final triggered = alert['triggered'] == true;
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: triggered
            ? Colors.amber.withValues(alpha: 0.1)
            : _cardBg,
        borderRadius: BorderRadius.circular(12),
        border: triggered
            ? Border.all(color: Colors.amber.withValues(alpha: 0.5))
            : null,
      ),
      child: Row(
        children: [
          Icon(
            triggered ? Icons.notifications_active : Icons.notifications_off,
            color: triggered ? Colors.amber : Colors.white24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert['crop'] ?? '',
                  style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.bold),
                ),
                Text(
                  alert['message'] ?? 'No data available',
                  style: TextStyle(
                    color: triggered ? Colors.amber : Colors.white54,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          if (alert['current_price'] != null)
            Text(
              '₹${alert['current_price']}',
              style: TextStyle(
                color: triggered ? Colors.amber : Colors.white54,
                fontWeight: FontWeight.bold,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildErrorBox(String msg) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade900.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade700),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 20),
          const SizedBox(width: 8),
          Expanded(child: Text(msg, style: const TextStyle(color: Colors.red))),
        ],
      ),
    );
  }
}
