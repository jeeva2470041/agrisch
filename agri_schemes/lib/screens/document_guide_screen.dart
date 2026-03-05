import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/document_guide_model.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

/// Screen that shows step-by-step guidance on how to apply for a
/// specific document that the farmer doesn't have.
class DocumentGuideScreen extends StatefulWidget {
  /// The name of the document the farmer needs help obtaining
  final String documentName;

  const DocumentGuideScreen({super.key, required this.documentName});

  @override
  State<DocumentGuideScreen> createState() => _DocumentGuideScreenState();
}

class _DocumentGuideScreenState extends State<DocumentGuideScreen> {
  static const _primary = Color(0xFF2E7D32);
  static const _primaryLight = Color(0xFFE8F5E9);

  final ApiService _api = ApiService();
  DocumentGuideModel? _guide;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchGuide();
  }

  Future<void> _fetchGuide() async {
    try {
      final guide = await _api.getDocumentGuide(widget.documentName);
      if (mounted) {
        setState(() {
          _guide = guide;
          _loading = false;
          if (guide == null) {
            _error = 'No guide available for this document.';
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = 'Failed to load guide. Please check your connection.';
        });
      }
    }
  }

  Future<void> _openUrl(String url) async {
    if (url.isEmpty) return;
    final uri = Uri.parse(url);
    try {
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Could not open link')),
          );
        }
      }
    } catch (_) {
      if (mounted) {
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
          // ── App Bar ──
          SliverAppBar(
            expandedHeight: 140,
            pinned: true,
            backgroundColor: _primary,
            foregroundColor: Colors.white,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                l.translate('docGuideTitle'),
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              titlePadding: const EdgeInsets.only(
                left: 56,
                bottom: 16,
                right: 16,
              ),
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
                      Icons.description_outlined,
                      size: 64,
                      color: Colors.white.withValues(alpha: 0.15),
                    ),
                  ),
                ),
              ),
            ),
          ),

          // ── Body ──
          SliverToBoxAdapter(
            child: _loading
                ? const Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: Center(child: CircularProgressIndicator(color: _primary)),
                  )
                : _error != null
                    ? _buildError()
                    : _buildGuideContent(l),
          ),
        ],
      ),
    );
  }

  Widget _buildError() {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          const SizedBox(height: 60),
          Icon(Icons.info_outline, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            _error!,
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              setState(() {
                _loading = true;
                _error = null;
              });
              _fetchGuide();
            },
            icon: const Icon(Icons.refresh),
            label: const Text('Retry'),
            style: ElevatedButton.styleFrom(
              backgroundColor: _primary,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGuideContent(AppLocalizations l) {
    final guide = _guide!;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Document Name Header ──
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.article_outlined, color: Colors.blue.shade700, size: 24),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        guide.documentName,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue.shade800,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  guide.description,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.blue.shade700,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Quick Info Row ──
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _infoRow(Icons.account_balance_outlined,
                      l.translate('docGuideIssuedBy'), guide.issuingAuthority),
                  const Divider(height: 20),
                  _infoRow(Icons.schedule_outlined,
                      l.translate('docGuideTime'), guide.estimatedTime),
                  const Divider(height: 20),
                  _infoRow(Icons.currency_rupee,
                      l.translate('docGuideFee'), guide.fee),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // ── Steps Section ──
          if (guide.steps.isNotEmpty) ...[
            _sectionHeader(
                Icons.format_list_numbered, l.translate('docGuideSteps')),
            const SizedBox(height: 8),
            Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: List.generate(guide.steps.length, (i) {
                    return Padding(
                      padding: EdgeInsets.only(
                          bottom: i < guide.steps.length - 1 ? 16 : 0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            width: 30,
                            height: 30,
                            decoration: const BoxDecoration(
                              color: _primaryLight,
                              shape: BoxShape.circle,
                            ),
                            child: Center(
                              child: Text(
                                '${i + 1}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: _primary,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.only(top: 4),
                              child: Text(
                                guide.steps[i],
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey.shade800,
                                  height: 1.4,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],

          // ── Documents Needed Section ──
          if (guide.documentsNeeded.isNotEmpty) ...[
            _sectionHeader(
                Icons.folder_outlined, l.translate('docGuideDocsNeeded')),
            const SizedBox(height: 8),
            Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: Column(
                children: List.generate(guide.documentsNeeded.length, (i) {
                  return Column(
                    children: [
                      ListTile(
                        leading: Icon(Icons.check_circle_outline,
                            color: _primary, size: 20),
                        title: Text(
                          guide.documentsNeeded[i],
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                      if (i < guide.documentsNeeded.length - 1)
                        const Divider(height: 1, indent: 56),
                    ],
                  );
                }),
              ),
            ),
            const SizedBox(height: 24),
          ],

          // ── Tips Section ──
          if (guide.tips.isNotEmpty) ...[
            _sectionHeader(Icons.lightbulb_outline, l.translate('docGuideTips')),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.amber.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.amber.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: guide.tips.map((tip) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.star, color: Colors.amber.shade700, size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            tip,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.amber.shade900,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 24),
          ],

          // ── Helpful Links Section ──
          if (guide.helpfulLinks.isNotEmpty) ...[
            _sectionHeader(
                Icons.link_outlined, l.translate('docGuideLinks')),
            const SizedBox(height: 8),
            Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: Column(
                children:
                    List.generate(guide.helpfulLinks.length, (i) {
                  final link = guide.helpfulLinks[i];
                  return Column(
                    children: [
                      ListTile(
                        leading: Icon(Icons.open_in_new,
                            color: Colors.blue.shade600, size: 20),
                        title: Text(
                          link.title,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.blue.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        subtitle: Text(
                          link.url,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade500,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        onTap: () => _openUrl(link.url),
                      ),
                      if (i < guide.helpfulLinks.length - 1)
                        const Divider(height: 1, indent: 56),
                    ],
                  );
                }),
              ),
            ),
            const SizedBox(height: 24),
          ],

          // ── Visit CSC note ──
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _primaryLight,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _primary.withValues(alpha: 0.3)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, color: _primary, size: 22),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    l.translate('docGuideCscNote'),
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.green.shade800,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),
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
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF333333),
          ),
        ),
      ],
    );
  }

  Widget _infoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: _primary),
        const SizedBox(width: 12),
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: TextStyle(fontSize: 13, color: Colors.grey.shade800),
          ),
        ),
      ],
    );
  }
}
