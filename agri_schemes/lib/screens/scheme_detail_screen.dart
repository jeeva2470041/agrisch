import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/scheme_model.dart';
import '../l10n/app_localizations.dart';

class SchemeDetailScreen extends StatelessWidget {
  final SchemeModel scheme;
  const SchemeDetailScreen({super.key, required this.scheme});

  static const _primary = Color(0xFF2E7D32);
  static const _primaryLight = Color(0xFFE8F5E9);

  Future<void> _openUrl(BuildContext context, String url) async {
    if (url.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No link available for this scheme')),
      );
      return;
    }
    final uri = Uri.parse(url);
    try {
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Could not open link')),
          );
        }
      }
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open link')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: CustomScrollView(
        slivers: [
          // ── Collapsing App Bar ──
          SliverAppBar(
            expandedHeight: 160,
            pinned: true,
            backgroundColor: _primary,
            foregroundColor: Colors.white,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                scheme.name,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              titlePadding: const EdgeInsets.only(left: 56, bottom: 16, right: 16),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF1B5E20), Color(0xFF43A047)],
                  ),
                ),
                child: Align(
                  alignment: Alignment.bottomRight,
                  child: Padding(
                    padding: const EdgeInsets.only(right: 20, bottom: 48),
                    child: Icon(
                      _iconForType(scheme.type),
                      size: 64,
                      color: Colors.white.withValues(alpha: 0.15),
                    ),
                  ),
                ),
              ),
            ),
          ),

          // ── Body Content ──
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Benefit chip ──
                  if (scheme.benefit.isNotEmpty)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.currency_rupee, color: Colors.orange.shade700, size: 22),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              scheme.benefit,
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                                color: Colors.orange.shade800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                  const SizedBox(height: 20),

                  // ── Section: How to apply ──
                  _sectionHeader(Icons.assignment_outlined, l.howToApply),
                  const SizedBox(height: 8),
                  Text(
                    'Visit the official portal, fill the application form, and upload the required documents listed below.',
                    style: TextStyle(fontSize: 14, color: Colors.grey.shade700, height: 1.5),
                  ),

                  const SizedBox(height: 24),

                  // ── Section: Eligibility ──
                  _sectionHeader(Icons.verified_user_outlined, l.eligibilitySummary),
                  const SizedBox(height: 8),
                  Card(
                    elevation: 0,
                    color: _primaryLight,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          _eligibilityRow(Icons.location_on_outlined, 'States', scheme.states.join(', ')),
                          const Divider(height: 20),
                          _eligibilityRow(Icons.grass_outlined, 'Crops', scheme.crops.join(', ')),
                          const Divider(height: 20),
                          _eligibilityRow(Icons.square_foot_outlined, 'Land',
                              '${scheme.minLand} – ${scheme.maxLand} hectares'),
                          const Divider(height: 20),
                          _eligibilityRow(Icons.wb_sunny_outlined, 'Season', scheme.season),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // ── Section: Documents checklist ──
                  _sectionHeader(Icons.checklist_outlined, l.documentsChecklist),
                  const SizedBox(height: 8),
                  if (scheme.documentsRequired.isEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(l.noDocumentsRequired,
                          style: TextStyle(color: Colors.grey.shade600)),
                    )
                  else
                    Card(
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Column(
                        children: List.generate(scheme.documentsRequired.length, (i) {
                          final doc = scheme.documentsRequired[i];
                          return Column(
                            children: [
                              ListTile(
                                leading: Container(
                                  width: 32,
                                  height: 32,
                                  decoration: BoxDecoration(
                                    color: _primaryLight,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Center(
                                    child: Text(
                                      '${i + 1}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: _primary,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ),
                                ),
                                title: Text(doc, style: const TextStyle(fontSize: 14)),
                                trailing: const Icon(Icons.check_circle, color: _primary, size: 20),
                              ),
                              if (i < scheme.documentsRequired.length - 1)
                                const Divider(height: 1, indent: 56),
                            ],
                          );
                        }),
                      ),
                    ),

                  const SizedBox(height: 32),

                  // ── Apply / Official Link button (single) ──
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton.icon(
                      onPressed: () => _openUrl(context, scheme.officialLink),
                      icon: const Icon(Icons.open_in_new, size: 20),
                      label: Text(
                        scheme.officialLink.isNotEmpty ? l.applyOnline : l.applyOnline,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _primary,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        elevation: 2,
                      ),
                    ),
                  ),

                  // ── Show URL hint ──
                  if (scheme.officialLink.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Center(
                      child: Text(
                        scheme.officialLink,
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Helpers ──

  Widget _sectionHeader(IconData icon, String title) {
    return Row(
      children: [
        Icon(icon, color: _primary, size: 22),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF333333)),
        ),
      ],
    );
  }

  Widget _eligibilityRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: _primary),
        const SizedBox(width: 12),
        SizedBox(
          width: 60,
          child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(value, style: TextStyle(fontSize: 13, color: Colors.grey.shade800)),
        ),
      ],
    );
  }

  IconData _iconForType(String type) {
    switch (type.toLowerCase()) {
      case 'insurance':
        return Icons.shield_outlined;
      case 'loan':
        return Icons.account_balance_outlined;
      case 'subsidy':
        return Icons.savings_outlined;
      case 'income support':
        return Icons.payments_outlined;
      case 'marketing':
        return Icons.store_outlined;
      case 'service':
        return Icons.miscellaneous_services_outlined;
      default:
        return Icons.policy_outlined;
    }
  }
}
