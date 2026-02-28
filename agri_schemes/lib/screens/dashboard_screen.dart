import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';
import 'farmer_input_screen.dart';
import 'disease_detection_screen.dart';
import 'yield_prediction_screen.dart';
import 'price_forecast_screen.dart';
import 'soil_analysis_screen.dart';
import 'crop_recommendation_screen.dart';
import 'crop_calendar_screen.dart';
import 'alert_settings_screen.dart';
import 'settings_screen.dart';

/// Dashboard Screen — The new home screen after landing.
/// Shows Weather, Market Prices and a CTA to Find Schemes.
class DashboardScreen extends StatefulWidget {
  final int initialTab;
  const DashboardScreen({super.key, this.initialTab = 0});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with TickerProviderStateMixin {
  int _selectedIndex = 0;
  final _api = ApiService();

  // Location
  double? _lat, _lon;
  String _locationName = '';
  String _stateName = 'Tamil Nadu'; // Default

  // Data
  Map<String, dynamic>? _weather;
  Map<String, dynamic>? _market;
  bool _loadingWeather = true;
  bool _loadingMarket = true;

  late AnimationController _fadeCtrl;
  late Animation<double> _fadeAnim;

  // Theme
  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialTab.clamp(0, 2);
    _fadeCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);
    _fadeCtrl.forward();
    _fetchLocation();
  }

  @override
  void dispose() {
    _fadeCtrl.dispose();
    super.dispose();
  }

  Future<void> _fetchLocation() async {
    try {
      final permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        await Geolocator.requestPermission();
      }

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.low,
      );
      _lat = pos.latitude;
      _lon = pos.longitude;

      // Reverse geocode
      try {
        final placemarks = await placemarkFromCoordinates(_lat!, _lon!);
        if (placemarks.isNotEmpty) {
          final p = placemarks.first;
          _locationName = '${p.locality ?? ''}, ${p.administrativeArea ?? ''}';
          _stateName = p.administrativeArea ?? 'Tamil Nadu';
        }
      } catch (_) {
        _locationName = 'India';
      }

      // Fetch weather & market in parallel
      _fetchWeather();
      _fetchMarket();
    } catch (e) {
      // Fallback: use default location (Chennai)
      _lat = 13.0827;
      _lon = 80.2707;
      _locationName = 'Chennai, Tamil Nadu';
      _stateName = 'Tamil Nadu';
      _fetchWeather();
      _fetchMarket();
    }
  }

  Future<void> _fetchWeather() async {
    if (_lat == null || _lon == null) return;
    final data = await _api.getWeather(_lat!, _lon!);
    if (mounted) {
      setState(() {
        _weather = data;
        _loadingWeather = false;
      });
    }
  }

  Future<void> _fetchMarket() async {
    final data = await _api.getMarketPrices(_stateName);
    if (mounted) {
      setState(() {
        _market = data;
        _loadingMarket = false;
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
        title: const Text(
          'AgriTrust',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
            letterSpacing: 0.5,
            color: Colors.white,
          ),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () {
              setState(() {
                _loadingWeather = true;
                _loadingMarket = true;
              });
              _fetchWeather();
              _fetchMarket();
            },
          ),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.3),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex:
              _selectedIndex + 1, // Offset by 1 because Home is index 0
          onTap: (index) {
            if (index == 0) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const FarmerInputScreen()),
              );
            } else if (index == 4) {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            } else {
              setState(() => _selectedIndex = index - 1);
            }
          },
          backgroundColor: const Color(0xFF122214),
          selectedItemColor: _accentGreen,
          unselectedItemColor: Colors.white54,
          type: BottomNavigationBarType.fixed,
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.search_rounded),
              label: l.findSchemes,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.cloud_outlined),
              activeIcon: const Icon(Icons.cloud),
              label: l.weather,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.storefront_outlined),
              activeIcon: const Icon(Icons.storefront),
              label: l.marketPrices,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.auto_awesome_outlined),
              activeIcon: const Icon(Icons.auto_awesome),
              label: l.translate('aiTools'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.settings_outlined),
              activeIcon: const Icon(Icons.settings),
              label: l.translate('settings'),
            ),
          ],
        ),
      ),
      body: FadeTransition(
        opacity: _fadeAnim,
        child: IndexedStack(
          index: _selectedIndex,
          children: [
            // ── Weather Tab ──
            RefreshIndicator(
              color: _accentGreen,
              onRefresh: () async {
                setState(() => _loadingWeather = true);
                await _fetchWeather();
              },
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                children: [
                  _buildLocationBar(),
                  const SizedBox(height: 20),
                  _buildSectionTitle('🌤️', l.weather),
                  const SizedBox(height: 10),
                  _buildWeatherCard(),
                  const SizedBox(height: 24),
                  if (_weather != null &&
                      _weather!['daily'] != null &&
                      (_weather!['daily'] as List).isNotEmpty) ...[
                    _buildSectionTitle('📅', l.forecast),
                    const SizedBox(height: 10),
                    _buildForecastRow(),
                  ],
                  const SizedBox(height: 32),
                ],
              ),
            ),

            // ── Market Prices Tab ──
            RefreshIndicator(
              color: _accentGreen,
              onRefresh: () async {
                setState(() => _loadingMarket = true);
                await _fetchMarket();
              },
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                children: [
                  _buildLocationBar(),
                  const SizedBox(height: 20),
                  _buildSectionTitle('📈', l.marketPrices),
                  const SizedBox(height: 10),
                  _buildMarketPrices(),
                  const SizedBox(height: 32),
                ],
              ),
            ),

            // ── AI Tools Tab ──
            ListView(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
              children: [
                _buildSectionTitle('✨', l.translate('aiTools')),
                const SizedBox(height: 20),
                _buildAiToolCard(
                  title: l.translate('diseaseDetection'),
                  subtitle: 'Upload photo of crop to detect diseases',
                  icon: Icons.local_florist_rounded,
                  color: Colors.red.shade400,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const DiseaseDetectionScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _buildAiToolCard(
                  title: l.translate('yieldPrediction'),
                  subtitle: 'Estimate crop yield based on conditions',
                  icon: Icons.analytics_rounded,
                  color: Colors.orange.shade400,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const YieldPredictionScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _buildAiToolCard(
                  title: l.translate('priceForecast'),
                  subtitle: 'Predict future market prices for crops',
                  icon: Icons.show_chart_rounded,
                  color: Colors.blue.shade400,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const PriceForecastScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _buildAiToolCard(
                  title: l.translate('soilAnalysis'),
                  subtitle: 'Analyze soil health from photo or test values',
                  icon: Icons.terrain_rounded,
                  color: Colors.brown.shade400,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const SoilAnalysisScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _buildAiToolCard(
                  title: l.translate('cropRecommendation'),
                  subtitle: 'AI-powered crop suggestions for your land',
                  icon: Icons.auto_awesome,
                  color: Colors.deepPurple.shade400,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const CropRecommendationScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _buildAiToolCard(
                  title: l.translate('cropCalendar'),
                  subtitle: 'Growth phases, tasks & timeline for your crop',
                  icon: Icons.calendar_month_rounded,
                  color: Colors.teal.shade400,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const CropCalendarScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _buildAiToolCard(
                  title: l.translate('alertSettings'),
                  subtitle: 'Weather & price alert notifications',
                  icon: Icons.notifications_active_rounded,
                  color: Colors.amber.shade600,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const AlertSettingsScreen(),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ── Location Bar ──
  Widget _buildLocationBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.location_on_rounded, color: _accentGreen, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _locationName.isEmpty ? 'Detecting location...' : _locationName,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _accentGreen.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              _stateName,
              style: const TextStyle(
                color: _accentGreen,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Section Title ──
  Widget _buildSectionTitle(String emoji, String title) {
    return Row(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 20)),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  // ── Weather Card ──
  Widget _buildWeatherCard() {
    if (_loadingWeather) {
      return _shimmerCard(height: 140);
    }
    if (_weather == null || _weather!['current'] == null) {
      return _errorCard('Unable to load weather data');
    }

    final current = _weather!['current'] as Map<String, dynamic>;
    final temp = current['temperature'] ?? 0;
    final humidity = current['humidity'] ?? 0;
    final wind = current['wind_speed'] ?? 0;
    final desc = current['description'] ?? 'Unknown';
    final icon = current['icon'] ?? '☀️';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1A3A1E), Color(0xFF0F2912)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.2)),
        boxShadow: [
          BoxShadow(
            color: _accentGreen.withValues(alpha: 0.1),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          // Temperature & icon
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(icon, style: const TextStyle(fontSize: 48)),
                const SizedBox(height: 8),
                Text(
                  '${temp.toStringAsFixed(1)}°C',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  desc,
                  style: const TextStyle(
                    color: Colors.white60,
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          // Details
          Expanded(
            flex: 2,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                _weatherDetail(
                  Icons.water_drop_rounded,
                  '$humidity%',
                  'Humidity',
                ),
                const SizedBox(height: 12),
                _weatherDetail(
                  Icons.air_rounded,
                  '${wind.toStringAsFixed(1)} km/h',
                  'Wind',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _weatherDetail(IconData icon, String value, String label) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: _accentGreen, size: 16),
            const SizedBox(width: 4),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white38, fontSize: 11),
        ),
      ],
    );
  }

  // ── 5-Day Forecast ──
  Widget _buildForecastRow() {
    final days = (_weather?['daily'] as List?) ?? [];
    return SizedBox(
      height: 150,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: days.length,
        separatorBuilder: (_, __) => const SizedBox(width: 10),
        itemBuilder: (context, i) {
          final day = days[i] as Map<String, dynamic>;
          final date = day['date'] ?? '';
          final icon = day['icon'] ?? '☀️';
          final max = day['temp_max'] ?? 0;
          final min = day['temp_min'] ?? 0;
          final precip = day['precipitation'] ?? 0;

          // Format date to short day name
          String shortDay = 'Day ${i + 1}';
          try {
            final dt = DateTime.parse(date);
            shortDay = [
              'Mon',
              'Tue',
              'Wed',
              'Thu',
              'Fri',
              'Sat',
              'Sun',
            ][dt.weekday - 1];
          } catch (_) {}

          return Container(
            width: 80,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: i == 0
                    ? _accentGreen.withValues(alpha: 0.5)
                    : Colors.white12,
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  i == 0 ? 'Today' : shortDay,
                  style: TextStyle(
                    color: i == 0 ? _accentGreen : Colors.white54,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(icon, style: const TextStyle(fontSize: 24)),
                const SizedBox(height: 4),
                Text(
                  '${max.toStringAsFixed(0)}°',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${min.toStringAsFixed(0)}°',
                  style: const TextStyle(color: Colors.white38, fontSize: 12),
                ),
                if (precip > 0)
                  Text(
                    '${precip}mm',
                    style: const TextStyle(
                      color: Colors.lightBlueAccent,
                      fontSize: 10,
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  // ── Market Prices ──
  Widget _buildMarketPrices() {
    if (_loadingMarket) {
      return Column(
        children: List.generate(
          3,
          (_) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _shimmerCard(height: 72),
          ),
        ),
      );
    }
    if (_market == null || _market!['prices'] == null) {
      return _errorCard('Unable to load market prices');
    }

    final prices = _market!['prices'] as List;
    final updated = _market!['last_updated'] ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Last updated
        if (updated.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Text(
              'Last updated: $updated',
              style: const TextStyle(color: Colors.white30, fontSize: 11),
            ),
          ),

        // Price cards
        ...prices.map<Widget>(
          (p) => _buildPriceCard(p as Map<String, dynamic>),
        ),
      ],
    );
  }

  Widget _buildPriceCard(Map<String, dynamic> p) {
    final crop = p['crop'] ?? '';
    final price = p['price'] ?? 0;
    final unit = p['unit'] ?? '₹/quintal';
    final change = (p['change'] ?? 0).toDouble();
    final changePct = (p['change_pct'] ?? 0).toDouble();
    final trend = p['trend'] ?? 'stable';
    final mandi = p['mandi'] ?? '';

    Color trendColor;
    IconData trendIcon;
    if (trend == 'up') {
      trendColor = const Color(0xFF66BB6A);
      trendIcon = Icons.trending_up_rounded;
    } else if (trend == 'down') {
      trendColor = const Color(0xFFEF5350);
      trendIcon = Icons.trending_down_rounded;
    } else {
      trendColor = Colors.amber;
      trendIcon = Icons.trending_flat_rounded;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        children: [
          // Crop icon
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: _accentGreen.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Center(
              child: Text(
                _cropEmoji(crop),
                style: const TextStyle(fontSize: 20),
              ),
            ),
          ),
          const SizedBox(width: 12),

          // Crop name & mandi
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  crop,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  '$mandi · $unit',
                  style: const TextStyle(color: Colors.white38, fontSize: 11),
                ),
              ],
            ),
          ),

          // Price
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '₹${price.toStringAsFixed(0)}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(trendIcon, color: trendColor, size: 14),
                  const SizedBox(width: 2),
                  Text(
                    '${change >= 0 ? '+' : ''}${change.toStringAsFixed(0)} (${changePct.abs()}%)',
                    style: TextStyle(
                      color: trendColor,
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _cropEmoji(String crop) {
    const map = {
      'Rice': '🌾',
      'Wheat': '🌾',
      'Maize': '🌽',
      'Cotton': '🏵️',
      'Sugarcane': '🎋',
      'Soybean': '🫘',
      'Groundnut': '🥜',
      'Mustard': '🌻',
      'Coconut': '🥥',
      'Tea': '🍵',
      'Coffee': '☕',
      'Rubber': '🌳',
      'Jute': '🧵',
      'Tobacco': '🍂',
      'Spices': '🌶️',
      'Jowar': '🌾',
      'Bajra': '🌾',
      'Ragi': '🌾',
      'Tur': '🫘',
      'Moong': '🫘',
      'Urad': '🫘',
      'Millets': '🌾',
      'Pulses': '🫘',
      'Sunflower': '🌻',
    };
    return map[crop] ?? '🌱';
  }

  Widget _buildAiToolCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.2)),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: Icon(icon, color: color, size: 32),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          color: Colors.white54,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right_rounded, color: Colors.white24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ── Helper Widgets ──
  Widget _shimmerCard({required double height}) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(strokeWidth: 2, color: _accentGreen),
        ),
      ),
    );
  }

  Widget _errorCard(String msg) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              msg,
              style: const TextStyle(color: Colors.white54, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}
