import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../models/farmer_input_model.dart';
import '../models/scheme_model.dart';
import 'ask_ai_screen.dart';
import 'scheme_detail_screen.dart';
import '../services/scheme_matching_service.dart';
import '../services/tts_service.dart';

/// Scheme Recommendation Screen
/// Displays eligible schemes based on farmer input
/// Features:
/// - List of eligible schemes with details
/// - Voice explanation button for each scheme
/// - Total benefit calculation
class SchemeRecommendationScreen extends StatefulWidget {
  final FarmerInputModel farmerInput;

  const SchemeRecommendationScreen({super.key, required this.farmerInput});

  @override
  State<SchemeRecommendationScreen> createState() =>
      _SchemeRecommendationScreenState();
}

class _SchemeRecommendationScreenState
    extends State<SchemeRecommendationScreen> {
  // Scheme matching service
  final _schemeService = SchemeMatchingService();

  // Future for eligible schemes
  late Future<List<SchemeModel>> _eligibleSchemesFuture;

  // Currently speaking scheme ID (to highlight which one is being spoken)
  String? _speakingSchemeId;

  @override
  void initState() {
    super.initState();
    // Get eligible schemes based on farmer input
    _eligibleSchemesFuture = _schemeService.getEligibleSchemes(
      widget.farmerInput,
    );
  }

  @override
  void dispose() {
    // Stop TTS when leaving the screen
    final ttsService = Provider.of<TtsService>(context, listen: false);
    ttsService.stop();
    super.dispose();
  }

  /// Speak scheme explanation using TTS
  void _speakSchemeExplanation(
    SchemeModel scheme,
    String explanationText,
  ) async {
    final ttsService = Provider.of<TtsService>(context, listen: false);

    // If already speaking this scheme, stop
    if (_speakingSchemeId == scheme.name && ttsService.isSpeaking) {
      await ttsService.stop();
      setState(() => _speakingSchemeId = null);
      return;
    }

    setState(() => _speakingSchemeId = scheme.name);

    await ttsService.speak(explanationText);

    // Listen for completion
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
        backgroundColor: const Color(0xFF2E7D32),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          // Stop all TTS button
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
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF2E7D32), Color(0xFFF5F5F5)],
            stops: [0.0, 0.15],
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

  /// Build empty state when no schemes found
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

  /// Build the list of eligible schemes
  Widget _buildSchemesList(
    AppLocalizations localizations,
    List<SchemeModel> schemes,
    String localeCode,
  ) {
    // Total benefit calculation might need adjustment as benefit is now string
    // Simplified to just showing count for now or parsing if needed.
    // Assuming backend returns benefit string not float.

    return Column(
      children: [
        // Summary card
        _buildSummaryCard(localizations, schemes.length),

        // Schemes list
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: schemes.length,
            itemBuilder: (context, index) {
              final scheme = schemes[index];
              return _buildSchemeCard(scheme, localizations, localeCode);
            },
          ),
        ),
      ],
    );
  }

  /// Build summary card showing number of schemes
  Widget _buildSummaryCard(AppLocalizations localizations, int count) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Schemes count
          Column(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF2E7D32).withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.assignment_turned_in,
                  color: Color(0xFF2E7D32),
                  size: 28,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '$count',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2E7D32),
                ),
              ),
              Text(
                localizations.eligibleSchemes,
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build individual scheme card
  Widget _buildSchemeCard(
    SchemeModel scheme,
    AppLocalizations localizations,
    String localeCode,
  ) {
    // Use scheme name as ID for speaking tracking since ID is optional/missing
    final isSpeaking = _speakingSchemeId == scheme.name;
    final description = scheme.getDescription(localeCode);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: isSpeaking ? 8 : 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: isSpeaking
            ? const BorderSide(color: Color(0xFF2E7D32), width: 2)
            : BorderSide.none,
      ),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          color: isSpeaking
              ? const Color(0xFF2E7D32).withValues(alpha: 0.05)
              : Colors.white,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Scheme header
            Row(
              children: [
                // Scheme icon
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2E7D32).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.policy,
                    color: Color(0xFF2E7D32),
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),

                // Scheme name
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        scheme.name,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF333333),
                        ),
                      ),
                      if (scheme.benefit.isNotEmpty)
                        Row(
                          children: [
                            const Icon(
                              Icons.currency_rupee,
                              size: 14,
                              color: Colors.orange,
                            ),
                            Expanded(
                              child: Text(
                                scheme.benefit,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.orange,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Scheme description
            Text(
              description,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade700,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 16),

            // Voice explanation button + "How to apply" CTA
            SizedBox(
              width: double.infinity,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ElevatedButton.icon(
                    onPressed: () => _speakSchemeExplanation(scheme, description),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isSpeaking
                          ? Colors.red.shade600
                          : const Color(0xFF2E7D32),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    icon: Icon(isSpeaking ? Icons.stop : Icons.volume_up),
                    label: Text(
                      isSpeaking ? localizations.stopSpeaking : localizations.listenExplanation,
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                    ),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => SchemeDetailScreen(scheme: scheme)),
                      );
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF2E7D32),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      side: const BorderSide(color: Color(0xFF2E7D32)),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    icon: const Icon(Icons.info_outline, color: Color(0xFF2E7D32)),
                    label: Text(localizations.howToApply, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => AskAiScreen(scheme: scheme)),
                      );
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.deepPurple,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      side: const BorderSide(color: Colors.deepPurple),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    icon: const Icon(Icons.auto_awesome, color: Colors.deepPurple),
                    label: Text(localizations.askAi, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
