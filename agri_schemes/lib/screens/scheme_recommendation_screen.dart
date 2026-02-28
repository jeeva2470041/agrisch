import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../models/farmer_input_model.dart';
import '../models/scheme_model.dart';
import 'scheme_detail_screen.dart';
import 'ask_ai_screen.dart';
import '../services/scheme_matching_service.dart';
import '../services/tts_service.dart';
import 'dashboard_screen.dart';
import 'settings_screen.dart';

/// Scheme Recommendation Screen
/// Displays eligible schemes based on farmer input with visual type differentiation
class SchemeRecommendationScreen extends StatefulWidget {
  final FarmerInputModel farmerInput;

  const SchemeRecommendationScreen({super.key, required this.farmerInput});

  @override
  State<SchemeRecommendationScreen> createState() =>
      _SchemeRecommendationScreenState();
}

class _SchemeRecommendationScreenState
    extends State<SchemeRecommendationScreen> {
  final _schemeService = SchemeMatchingService();
  late Future<List<SchemeModel>> _eligibleSchemesFuture;
  String? _speakingSchemeId;
  String _selectedFilter = 'filterAll';
  TtsService? _ttsService;

  // ── Type-based theming ───────────────────────────────────────
  // Type themes use localization keys for labels
  static const _typeThemeData = <String, _SchemeTypeThemeData>{
    'Income Support': _SchemeTypeThemeData(
      color: Color(0xFF2E7D32),
      icon: Icons.account_balance_wallet_rounded,
      labelKey: 'filterIncomeSupport',
    ),
    'Investment Support': _SchemeTypeThemeData(
      color: Color(0xFF2E7D32),
      icon: Icons.account_balance_wallet_rounded,
      labelKey: 'filterIncomeSupport',
    ),
    'Income & Livelihood Support': _SchemeTypeThemeData(
      color: Color(0xFF2E7D32),
      icon: Icons.account_balance_wallet_rounded,
      labelKey: 'filterIncomeSupport',
    ),
    'Direct Income Support': _SchemeTypeThemeData(
      color: Color(0xFF2E7D32),
      icon: Icons.account_balance_wallet_rounded,
      labelKey: 'filterIncomeSupport',
    ),
    'Loan': _SchemeTypeThemeData(
      color: Color(0xFF1565C0),
      icon: Icons.credit_card_rounded,
      labelKey: 'filterLoan',
    ),
    'Interest Subvention': _SchemeTypeThemeData(
      color: Color(0xFF1565C0),
      icon: Icons.credit_card_rounded,
      labelKey: 'filterLoan',
    ),
    'Insurance': _SchemeTypeThemeData(
      color: Color(0xFF6A1B9A),
      icon: Icons.shield_rounded,
      labelKey: 'filterInsurance',
    ),
    'Crop Insurance': _SchemeTypeThemeData(
      color: Color(0xFF6A1B9A),
      icon: Icons.shield_rounded,
      labelKey: 'filterInsurance',
    ),
    'Weather Index Insurance': _SchemeTypeThemeData(
      color: Color(0xFF6A1B9A),
      icon: Icons.shield_rounded,
      labelKey: 'filterInsurance',
    ),
    'Subsidy': _SchemeTypeThemeData(
      color: Color(0xFFE65100),
      icon: Icons.redeem_rounded,
      labelKey: 'filterSubsidy',
    ),
    'Irrigation Subsidy': _SchemeTypeThemeData(
      color: Color(0xFF00838F),
      icon: Icons.water_drop_rounded,
      labelKey: 'filterIrrigation',
    ),
    'Crop Compensation': _SchemeTypeThemeData(
      color: Color(0xFFE65100),
      icon: Icons.redeem_rounded,
      labelKey: 'filterCompensation',
    ),
    'Service': _SchemeTypeThemeData(
      color: Color(0xFF00695C),
      icon: Icons.miscellaneous_services_rounded,
      labelKey: 'filterService',
    ),
    'Digital Infrastructure': _SchemeTypeThemeData(
      color: Color(0xFF00695C),
      icon: Icons.phone_android_rounded,
      labelKey: 'filterDigital',
    ),
    'Marketing': _SchemeTypeThemeData(
      color: Color(0xFF4527A0),
      icon: Icons.storefront_rounded,
      labelKey: 'filterMarketing',
    ),
    'MSP Procurement': _SchemeTypeThemeData(
      color: Color(0xFF4527A0),
      icon: Icons.storefront_rounded,
      labelKey: 'filterMSP',
    ),
    'Price Compensation': _SchemeTypeThemeData(
      color: Color(0xFF4527A0),
      icon: Icons.storefront_rounded,
      labelKey: 'filterPriceSupport',
    ),
    'Price Deficit': _SchemeTypeThemeData(
      color: Color(0xFF4527A0),
      icon: Icons.storefront_rounded,
      labelKey: 'filterPriceSupport',
    ),
    'Fisheries Support': _SchemeTypeThemeData(
      color: Color(0xFF0277BD),
      icon: Icons.water_rounded,
      labelKey: 'filterService',
    ),
    'Animal Husbandry': _SchemeTypeThemeData(
      color: Color(0xFF795548),
      icon: Icons.pets_rounded,
      labelKey: 'filterService',
    ),
  };

  static const _defaultThemeData = _SchemeTypeThemeData(
    color: Color(0xFF546E7A),
    icon: Icons.policy_rounded,
    labelKey: 'filterService',
  );

  _SchemeTypeThemeData _getThemeData(String type) {
    return _typeThemeData[type] ?? _defaultThemeData;
  }

  /// Get localized label for scheme type
  String _getLocalizedLabel(String type, AppLocalizations l) {
    final data = _getThemeData(type);
    return l.translate(data.labelKey);
  }

  /// Get simplified category key for filtering
  String _getCategoryKey(String type) {
    return _getThemeData(type).labelKey;
  }

  @override
  void initState() {
    super.initState();
    _eligibleSchemesFuture = _schemeService.getEligibleSchemes(
      widget.farmerInput,
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _ttsService = Provider.of<TtsService>(context, listen: false);
  }

  @override
  void dispose() {
    _ttsService?.stop();
    super.dispose();
  }

  void _speakSchemeExplanation(
    SchemeModel scheme,
    String explanationText,
  ) async {
    final ttsService = Provider.of<TtsService>(context, listen: false);

    if (_speakingSchemeId == scheme.name && ttsService.isSpeaking) {
      await ttsService.stop();
      setState(() => _speakingSchemeId = null);
      return;
    }

    setState(() => _speakingSchemeId = scheme.name);
    await ttsService.speak(explanationText);

    ttsService.addListener(() {
      if (!ttsService.isSpeaking && mounted) {
        setState(() => _speakingSchemeId = null);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    final ttsService = Provider.of<TtsService>(context);
    final localeCode = Localizations.localeOf(context).languageCode;

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.eligibleSchemes),
        backgroundColor: const Color(0xFF1B5E20),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (ttsService.isSpeaking)
            IconButton(
              onPressed: () async {
                await ttsService.stop();
                setState(() => _speakingSchemeId = null);
              },
              icon: const Icon(Icons.stop_circle),
              tooltip: localizations.stopSpeaking,
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
          currentIndex: 0, // Home/Schemes section
          onTap: (index) {
            if (index == 4) {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            } else if (index != 0) {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => DashboardScreen(initialTab: index - 1),
                ),
              );
            }
          },
          backgroundColor: const Color(0xFF122214),
          selectedItemColor: const Color(0xFF43A047),
          unselectedItemColor: Colors.white54,
          type: BottomNavigationBarType.fixed,
          selectedFontSize: 11,
          unselectedFontSize: 10,
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.search_rounded),
              label: localizations.translate('schemesNav'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.cloud_outlined),
              label: localizations.translate('weatherNav'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.storefront_outlined),
              label: localizations.translate('marketNav'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.auto_awesome_outlined),
              label: localizations.translate('aiToolsNav'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.settings_outlined),
              activeIcon: const Icon(Icons.settings),
              label: localizations.translate('settingsNav'),
            ),
          ],
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B5E20), Color(0xFFF1F5F1)],
            stops: [0.0, 0.18],
          ),
        ),
        child: FutureBuilder<List<SchemeModel>>(
          future: _eligibleSchemesFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(
                child: CircularProgressIndicator(color: Colors.white),
              );
            } else if (snapshot.hasError) {
              return Center(child: Text("Error: ${snapshot.error}"));
            } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return _buildNoSchemesFound(localizations);
            } else {
              return _buildSchemesList(
                localizations,
                snapshot.data!,
                localeCode,
              );
            }
          },
        ),
      ),
    );
  }

  Widget _buildNoSchemesFound(AppLocalizations localizations) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.search_off, size: 80, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            localizations.noSchemesFound,
            style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2E7D32),
              foregroundColor: Colors.white,
            ),
            icon: const Icon(Icons.arrow_back),
            label: Text(localizations.backToInput),
          ),
        ],
      ),
    );
  }

  Widget _buildSchemesList(
    AppLocalizations localizations,
    List<SchemeModel> schemes,
    String localeCode,
  ) {
    // Build category list for filter chips
    final categories = <String>{'filterAll'};
    for (final s in schemes) {
      categories.add(_getCategoryKey(s.type));
    }
    final categoryList = categories.toList();

    // Filter schemes
    final filtered = _selectedFilter == 'filterAll'
        ? schemes
        : schemes
              .where((s) => _getCategoryKey(s.type) == _selectedFilter)
              .toList();

    return Column(
      children: [
        // Summary card
        _buildSummaryCard(localizations, schemes.length, categoryList),

        // Filter chips
        _buildFilterChips(categoryList, filtered.length),

        // Scheme cards
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
            itemCount: filtered.length,
            itemBuilder: (context, index) {
              return _buildSchemeCard(
                filtered[index],
                localizations,
                localeCode,
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(
    AppLocalizations localizations,
    int count,
    List<String> categories,
  ) {
    // Count by category (excluding 'All')
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2E7D32), Color(0xFF43A047)],
              ),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Column(
              children: [
                Text(
                  '$count',
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                  ),
                ),
                Text(
                  localizations.schemesCount,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          // Brief text
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  localizations.eligibleSchemes,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF1B5E20),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${localizations.foundForCropState} ${widget.farmerInput.cropType} - ${widget.farmerInput.state}',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Filter chips row showing available categories
  Widget _buildFilterChips(List<String> categories, int filteredCount) {
    return SizedBox(
      height: 44,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final cat = categories[index];
          final isSelected = _selectedFilter == cat;
          final l = AppLocalizations.of(context);
          final chipLabel = l.translate(cat);
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              selected: isSelected,
              label: Text(
                chipLabel,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isSelected ? Colors.white : Colors.grey.shade700,
                ),
              ),
              backgroundColor: Colors.white,
              selectedColor: const Color(0xFF1B5E20),
              checkmarkColor: Colors.white,
              side: BorderSide(
                color: isSelected
                    ? const Color(0xFF1B5E20)
                    : Colors.grey.shade300,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              onSelected: (_) {
                setState(() => _selectedFilter = cat);
              },
            ),
          );
        },
      ),
    );
  }

  /// Build individual scheme card with type-based theming
  Widget _buildSchemeCard(
    SchemeModel scheme,
    AppLocalizations localizations,
    String localeCode,
  ) {
    final isSpeaking = _speakingSchemeId == scheme.name;
    final description = scheme.getDescription(localeCode);
    final theme = _getThemeData(scheme.type);
    final typeLabel = _getLocalizedLabel(scheme.type, localizations);

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isSpeaking ? theme.color : Colors.grey.shade200,
          width: isSpeaking ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: isSpeaking
                ? theme.color.withValues(alpha: 0.15)
                : Colors.black.withValues(alpha: 0.04),
            blurRadius: isSpeaking ? 12 : 6,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Color-coded type bar at top ──
          Container(
            height: 4,
            decoration: BoxDecoration(
              color: theme.color,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(15),
              ),
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Type badge + icon row ──
                Row(
                  children: [
                    // Type badge (pill-shaped with color)
                    Flexible(
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 5,
                        ),
                        decoration: BoxDecoration(
                          color: theme.color.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: theme.color.withValues(alpha: 0.3),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(theme.icon, size: 14, color: theme.color),
                            const SizedBox(width: 5),
                            Flexible(
                              child: Text(
                                typeLabel,
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w700,
                                  color: theme.color,
                                  letterSpacing: 0.3,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Benefit amount badge
                    if (scheme.benefit.isNotEmpty)
                      Flexible(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.amber.shade50,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: Colors.amber.shade200),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.currency_rupee,
                                size: 12,
                                color: Colors.amber.shade800,
                              ),
                              const SizedBox(width: 2),
                              Flexible(
                                child: Text(
                                  scheme.benefit,
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: Colors.amber.shade900,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 12),

                // ── Scheme name ──
                Text(
                  scheme.name,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF1A1A2E),
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 8),

                // ── Description ──
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade600,
                    height: 1.5,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 12),

                // ── Quick info chips (states, season) ──
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: [
                    if (scheme.states.isNotEmpty &&
                        !scheme.states.contains('All'))
                      _infoChip(
                        Icons.location_on_outlined,
                        scheme.states.join(', '),
                        Colors.blue,
                      ),
                    if (scheme.season != 'All')
                      _infoChip(
                        Icons.wb_sunny_outlined,
                        scheme.season,
                        Colors.orange,
                      ),
                    if (scheme.maxLand < 100)
                      _infoChip(
                        Icons.square_foot_outlined,
                        'Max ${scheme.maxLand.toStringAsFixed(0)} ha',
                        Colors.teal,
                      ),
                  ],
                ),
                const SizedBox(height: 14),

                // ── Action buttons ──
                Row(
                  children: [
                    // Listen button
                    Expanded(
                      child: SizedBox(
                        height: 40,
                        child: OutlinedButton.icon(
                          onPressed: () =>
                              _speakSchemeExplanation(scheme, description),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: isSpeaking
                                ? Colors.red.shade600
                                : theme.color,
                            side: BorderSide(
                              color: isSpeaking
                                  ? Colors.red.shade300
                                  : theme.color.withValues(alpha: 0.4),
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            padding: EdgeInsets.zero,
                          ),
                          icon: Icon(
                            isSpeaking ? Icons.stop : Icons.volume_up_rounded,
                            size: 18,
                          ),
                          label: Text(
                            isSpeaking
                                ? localizations.stopSpeaking
                                : localizations.listenExplanation,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    // View Details button
                    Expanded(
                      child: SizedBox(
                        height: 40,
                        child: ElevatedButton.icon(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) =>
                                    SchemeDetailScreen(scheme: scheme),
                              ),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.color,
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            padding: EdgeInsets.zero,
                          ),
                          icon: const Icon(
                            Icons.arrow_forward_rounded,
                            size: 18,
                          ),
                          label: Text(
                            localizations.howToApply,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // ── Ask Gemini button ──
                SizedBox(
                  width: double.infinity,
                  height: 38,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => AskAiScreen(scheme: scheme),
                        ),
                      );
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF7C4DFF),
                      side: BorderSide(
                        color: const Color(0xFF7C4DFF).withValues(alpha: 0.4),
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      padding: EdgeInsets.zero,
                    ),
                    icon: const Icon(Icons.auto_awesome, size: 16),
                    label: Text(
                      localizations.translate('askGemini'),
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Small info chip for states, season, land size
  Widget _infoChip(IconData icon, String text, Color color) {
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.7),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 12, color: color),
            const SizedBox(width: 4),
            Flexible(
              child: Text(
                text,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: color.shade700,
                ),
                overflow: TextOverflow.ellipsis,
                maxLines: 2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Theme data class for scheme types ─────────────────────────
class _SchemeTypeThemeData {
  final Color color;
  final IconData icon;
  final String labelKey;

  const _SchemeTypeThemeData({
    required this.color,
    required this.icon,
    required this.labelKey,
  });
}

/// Extension to get shade variants from Color
extension _ColorShade on Color {
  Color get shade700 {
    final hsl = HSLColor.fromColor(this);
    return hsl.withLightness((hsl.lightness * 0.7).clamp(0.0, 1.0)).toColor();
  }
}
