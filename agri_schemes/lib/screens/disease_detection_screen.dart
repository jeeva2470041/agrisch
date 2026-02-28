import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

/// Disease Detection Screen — Capture/pick a plant image and
/// get AI-powered disease analysis with treatment recommendations.
class DiseaseDetectionScreen extends StatefulWidget {
  const DiseaseDetectionScreen({super.key});

  @override
  State<DiseaseDetectionScreen> createState() => _DiseaseDetectionScreenState();
}

class _DiseaseDetectionScreenState extends State<DiseaseDetectionScreen> {
  final _api = ApiService();
  final _picker = ImagePicker();

  Uint8List? _imageBytes;
  bool _isAnalyzing = false;
  Map<String, dynamic>? _result;

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? picked = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      if (picked == null) return;

      final bytes = await picked.readAsBytes();
      setState(() {
        _imageBytes = bytes;
        _result = null;
      });
    } catch (e) {
      debugPrint('Image pick error: $e');
    }
  }

  String? _errorMsg;

  Future<void> _analyzeImage() async {
    if (_imageBytes == null) return;

    setState(() {
      _isAnalyzing = true;
      _errorMsg = null;
      _result = null;
    });

    final l = AppLocalizations.of(context);
    final langCode = l.locale.languageCode;
    final base64Image = base64Encode(_imageBytes!);

    try {
      final result = await _api.detectDisease(
        imageBase64: base64Image,
        language: langCode,
      );

      if (mounted) {
        if (result.containsKey('error')) {
          setState(() {
            _isAnalyzing = false;
            _errorMsg = result['error']?.toString() ?? 'Analysis failed';
          });
        } else {
          setState(() {
            _isAnalyzing = false;
            _result = result;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isAnalyzing = false;
          _errorMsg = 'Failed to analyze image. Please try again.';
        });
      }
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
          l.translate('diseaseDetection'),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Image preview or placeholder
            _buildImageSection(l),
            const SizedBox(height: 16),

            // Action buttons
            _buildActionButtons(l),
            const SizedBox(height: 24),

            // Error message
            if (_errorMsg != null && !_isAnalyzing) _buildErrorCard(_errorMsg!),

            // Results
            if (_isAnalyzing) _buildLoadingCard(l),
            if (_result != null && !_isAnalyzing) _buildResultCard(l),
          ],
        ),
      ),
    );
  }

  Widget _buildImageSection(AppLocalizations l) {
    return Container(
      height: 280,
      width: double.infinity,
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: _accentGreen.withValues(alpha: 0.3),
          width: 2,
        ),
      ),
      child: _imageBytes != null
          ? ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: Image.memory(
                _imageBytes!,
                fit: BoxFit.cover,
                width: double.infinity,
              ),
            )
          : Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.local_florist_rounded,
                  size: 64,
                  color: _accentGreen.withValues(alpha: 0.5),
                ),
                const SizedBox(height: 16),
                Text(
                  l.translate('diseaseUploadHint'),
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.6),
                    fontSize: 15,
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildActionButtons(AppLocalizations l) {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () => _pickImage(ImageSource.camera),
            icon: const Icon(Icons.camera_alt_rounded),
            label: Text(l.translate('diseaseCamera')),
            style: ElevatedButton.styleFrom(
              backgroundColor: _accentGreen,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () => _pickImage(ImageSource.gallery),
            icon: const Icon(Icons.photo_library_rounded),
            label: Text(l.translate('diseaseGallery')),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2E7D32),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
        ),
        if (_imageBytes != null) ...[
          const SizedBox(width: 12),
          ElevatedButton(
            onPressed: _isAnalyzing ? null : _analyzeImage,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF7C4DFF),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: _isAnalyzing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : Text(l.translate('diseaseAnalyze')),
          ),
        ],
      ],
    );
  }

  Widget _buildErrorCard(String message) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.red.withValues(alpha: 0.5), width: 2),
      ),
      child: Column(
        children: [
          const Icon(Icons.error_outline_rounded, color: Colors.red, size: 40),
          const SizedBox(height: 12),
          Text(
            'Analysis Failed',
            style: const TextStyle(
              color: Colors.red,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.7),
              fontSize: 14,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _analyzeImage,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('Try Again'),
            style: ElevatedButton.styleFrom(
              backgroundColor: _accentGreen,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingCard(AppLocalizations l) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          const CircularProgressIndicator(color: _accentGreen),
          const SizedBox(height: 16),
          Text(
            l.translate('diseaseAnalyzing'),
            style: const TextStyle(color: Colors.white70, fontSize: 15),
          ),
        ],
      ),
    );
  }

  Widget _buildResultCard(AppLocalizations l) {
    final isHealthy = _result!['is_healthy'] == true;
    final diseaseName = _result!['disease_name'] ?? 'Unknown';
    final confidence = ((_result!['confidence'] ?? 0.0) * 100).toStringAsFixed(0);
    final description = _result!['description'] ?? '';
    final severity = _result!['severity'] ?? 'unknown';
    final symptoms = (_result!['symptoms'] as List?)?.cast<String>() ?? [];
    final treatment = (_result!['treatment'] as List?)?.cast<String>() ?? [];
    final prevention = (_result!['prevention'] as List?)?.cast<String>() ?? [];
    final cropIdentified = _result!['crop_identified'] ?? '';

    final severityColor = severity == 'severe'
        ? Colors.red
        : severity == 'moderate'
            ? Colors.orange
            : severity == 'mild'
                ? Colors.yellow.shade700
                : Colors.grey;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isHealthy
              ? _accentGreen.withValues(alpha: 0.5)
              : Colors.red.withValues(alpha: 0.5),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Disease name & status
          Row(
            children: [
              Icon(
                isHealthy ? Icons.check_circle_rounded : Icons.warning_rounded,
                color: isHealthy ? _accentGreen : Colors.red,
                size: 28,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      diseaseName,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (cropIdentified.isNotEmpty)
                      Text(
                        cropIdentified,
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.6),
                          fontSize: 13,
                        ),
                      ),
                  ],
                ),
              ),
              // Confidence badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _accentGreen.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '$confidence%',
                  style: const TextStyle(
                    color: _accentGreen,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),

          if (!isHealthy) ...[
            const SizedBox(height: 8),
            // Severity
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                  decoration: BoxDecoration(
                    color: severityColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    severity.toUpperCase(),
                    style: TextStyle(
                      color: severityColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ],

          if (description.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              description,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
                fontSize: 14,
                height: 1.5,
              ),
            ),
          ],

          if (symptoms.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildSection(
              l.translate('diseaseSymptoms'),
              Icons.visibility_rounded,
              symptoms,
              Colors.orange,
            ),
          ],

          if (treatment.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildSection(
              l.translate('diseaseTreatment'),
              Icons.healing_rounded,
              treatment,
              _accentGreen,
            ),
          ],

          if (prevention.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildSection(
              l.translate('diseasePrevention'),
              Icons.shield_rounded,
              prevention,
              Colors.blue,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSection(String title, IconData icon, List<String> items, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: color, size: 18),
            const SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                color: color,
                fontSize: 15,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...items.map(
          (item) => Padding(
            padding: const EdgeInsets.only(left: 26, bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('• ', style: TextStyle(color: color, fontSize: 14)),
                Expanded(
                  child: Text(
                    item,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.75),
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
