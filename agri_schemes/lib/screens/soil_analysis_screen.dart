import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../models/soil_analysis_model.dart';
import '../l10n/app_localizations.dart';
import 'crop_recommendation_screen.dart';

/// Soil Health Analysis Screen — photo or manual soil test input.
class SoilAnalysisScreen extends StatefulWidget {
  const SoilAnalysisScreen({super.key});

  @override
  State<SoilAnalysisScreen> createState() => _SoilAnalysisScreenState();
}

class _SoilAnalysisScreenState extends State<SoilAnalysisScreen>
    with SingleTickerProviderStateMixin {
  final _api = ApiService();
  late TabController _tabCtrl;

  // Photo mode
  Uint8List? _imageBytes;
  bool _analyzing = false;
  SoilAnalysisModel? _result;
  String? _error;

  // Manual mode
  final _phCtrl = TextEditingController(text: '7.0');
  final _nCtrl = TextEditingController();
  final _pCtrl = TextEditingController();
  final _kCtrl = TextEditingController();
  final _ocCtrl = TextEditingController();
  String _selectedSoilType = '';
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
    _phCtrl.dispose();
    _nCtrl.dispose();
    _pCtrl.dispose();
    _kCtrl.dispose();
    _ocCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picker = ImagePicker();
      final file = await picker.pickImage(source: source, maxWidth: 1024);
      if (file != null) {
        final bytes = await file.readAsBytes();
        setState(() {
          _imageBytes = bytes;
          _result = null;
          _error = null;
        });
      }
    } catch (e) {
      debugPrint('Image pick error: $e');
    }
  }

  Future<void> _analyzePhoto() async {
    if (_imageBytes == null) return;
    setState(() {
      _analyzing = true;
      _error = null;
    });

    final b64 = base64Encode(_imageBytes!);
    final langCode =
        AppLocalizations.of(context).locale.languageCode;
    final resp = await _api.analyzeSoilPhoto(imageBase64: b64, language: langCode);

    setState(() {
      _analyzing = false;
      if (resp.containsKey('error')) {
        _error = resp['error'];
      } else {
        _result = SoilAnalysisModel.fromJson(resp);
      }
    });
  }

  Future<void> _analyzeManual() async {
    setState(() {
      _analyzing = true;
      _error = null;
      _result = null;
    });

    final Map<String, dynamic> soilData = {};
    if (_phCtrl.text.isNotEmpty) soilData['ph'] = double.tryParse(_phCtrl.text);
    if (_nCtrl.text.isNotEmpty) soilData['nitrogen'] = double.tryParse(_nCtrl.text);
    if (_pCtrl.text.isNotEmpty) soilData['phosphorus'] = double.tryParse(_pCtrl.text);
    if (_kCtrl.text.isNotEmpty) soilData['potassium'] = double.tryParse(_kCtrl.text);
    if (_ocCtrl.text.isNotEmpty) {
      soilData['organic_carbon'] = double.tryParse(_ocCtrl.text);
    }
    if (_selectedSoilType.isNotEmpty) soilData['soil_type'] = _selectedSoilType;

    if (soilData.isEmpty) {
      setState(() {
        _analyzing = false;
        _error = 'Please enter at least one soil parameter.';
      });
      return;
    }

    final langCode =
        AppLocalizations.of(context).locale.languageCode;
    final resp =
        await _api.analyzeSoilManual(soilData: soilData, language: langCode);

    setState(() {
      _analyzing = false;
      if (resp.containsKey('error')) {
        _error = resp['error'];
      } else {
        _result = SoilAnalysisModel.fromJson(resp);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);
    return Scaffold(
      backgroundColor: _darkBg,
      appBar: AppBar(
        backgroundColor: _primaryGreen,
        title: Text(l.translate('soilAnalysis')),
        bottom: TabBar(
          controller: _tabCtrl,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          tabs: [
            Tab(icon: const Icon(Icons.camera_alt), text: l.translate('photoAnalysis')),
            Tab(icon: const Icon(Icons.edit_note), text: l.translate('manualEntry')),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabCtrl,
        children: [
          _buildPhotoTab(l),
          _buildManualTab(l),
        ],
      ),
    );
  }

  Widget _buildPhotoTab(AppLocalizations l) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Image picker area
        GestureDetector(
          onTap: () => _showImageSourceDialog(),
          child: Container(
            height: 200,
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _accentGreen.withValues(alpha: 0.3)),
            ),
            child: _imageBytes != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Image.memory(_imageBytes!, fit: BoxFit.cover,
                        width: double.infinity),
                  )
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.add_a_photo_rounded,
                          size: 48, color: Colors.white38),
                      const SizedBox(height: 12),
                      Text(l.translate('tapToUploadSoilPhoto'),
                          style: const TextStyle(color: Colors.white54)),
                    ],
                  ),
          ),
        ),
        const SizedBox(height: 16),
        // Analyze button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed:
                _imageBytes != null && !_analyzing ? _analyzePhoto : null,
            icon: _analyzing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2))
                : const Icon(Icons.science_rounded),
            label: Text(_analyzing
                ? l.translate('analyzing')
                : l.translate('analyzeSoil')),
            style: ElevatedButton.styleFrom(
              backgroundColor: _accentGreen,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 16),
          _buildErrorCard(_error!),
        ],
        if (_result != null) ...[
          const SizedBox(height: 24),
          _buildResultsSection(_result!),
        ],
      ],
    );
  }

  Widget _buildManualTab(AppLocalizations l) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildInputCard(
          title: l.translate('soilTestValues'),
          children: [
            _buildDropdown(l.translate('soilType'), _soilTypes, _selectedSoilType,
                (v) => setState(() => _selectedSoilType = v ?? '')),
            const SizedBox(height: 12),
            _buildNumberField(l.translate('phValue'), _phCtrl, '0-14'),
            const SizedBox(height: 12),
            _buildNumberField('${l.translate('nitrogen')} (kg/ha)', _nCtrl, '0-500'),
            const SizedBox(height: 12),
            _buildNumberField(
                '${l.translate('phosphorus')} (kg/ha)', _pCtrl, '0-200'),
            const SizedBox(height: 12),
            _buildNumberField(
                '${l.translate('potassium')} (kg/ha)', _kCtrl, '0-500'),
            const SizedBox(height: 12),
            _buildNumberField(
                '${l.translate('organicCarbon')} (%)', _ocCtrl, '0-5'),
          ],
        ),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: !_analyzing ? _analyzeManual : null,
            icon: _analyzing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2))
                : const Icon(Icons.science_rounded),
            label: Text(_analyzing
                ? l.translate('analyzing')
                : l.translate('analyzeSoil')),
            style: ElevatedButton.styleFrom(
              backgroundColor: _accentGreen,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 16),
          _buildErrorCard(_error!),
        ],
        if (_result != null) ...[
          const SizedBox(height: 24),
          _buildResultsSection(_result!),
        ],
      ],
    );
  }

  Widget _buildResultsSection(SoilAnalysisModel result) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Health score gauge
        _buildHealthScoreCard(result),
        const SizedBox(height: 16),
        // Soil details
        _buildInfoCard('Soil Type', result.soilType, Icons.terrain_rounded),
        const SizedBox(height: 8),
        _buildInfoCard('pH Level', result.phEstimate.toStringAsFixed(1),
            Icons.water_drop_rounded),
        const SizedBox(height: 8),
        _buildInfoCard(
            'Organic Matter', result.organicMatter, Icons.eco_rounded),
        const SizedBox(height: 8),
        _buildInfoCard('Drainage', result.drainage, Icons.waves_rounded),
        // Deficiencies
        if (result.deficiencies.isNotEmpty) ...[
          const SizedBox(height: 16),
          _buildSectionTitle('Deficiencies Detected'),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: result.deficiencies.map((d) {
              return Chip(
                label: Text(d, style: const TextStyle(color: Colors.white)),
                backgroundColor: Colors.red.shade700,
                avatar:
                    const Icon(Icons.warning_rounded, color: Colors.amber, size: 18),
              );
            }).toList(),
          ),
        ],
        // Recommendations
        if (result.recommendations.isNotEmpty) ...[
          const SizedBox(height: 16),
          _buildSectionTitle('Recommendations'),
          const SizedBox(height: 8),
          ...result.recommendations
              .map((r) => _buildRecommendationTile(r)),
        ],
        // Suitable crops
        if (result.suitableCrops.isNotEmpty) ...[
          const SizedBox(height: 16),
          _buildSectionTitle('Suitable Crops'),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: result.suitableCrops.map((c) {
              return Chip(
                label: Text(c, style: const TextStyle(color: Colors.white)),
                backgroundColor: _primaryGreen,
                avatar: const Icon(Icons.grass_rounded,
                    color: Colors.lightGreenAccent, size: 18),
              );
            }).toList(),
          ),
        ],
        const SizedBox(height: 20),
        // CTA: Recommend Crops
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => CropRecommendationScreen(
                    soilType: result.soilType,
                    soilPh: result.phEstimate,
                  ),
                ),
              );
            },
            icon: const Icon(Icons.auto_awesome),
            label: const Text('Get Crop Recommendations'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepPurple,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildHealthScoreCard(SoilAnalysisModel result) {
    final score = result.healthScore.clamp(0, 10);
    final color = score >= 8
        ? Colors.green
        : score >= 6
            ? Colors.lightGreen
            : score >= 4
                ? Colors.orange
                : Colors.red;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Column(
        children: [
          Text('Soil Health Score',
              style: TextStyle(color: Colors.white70, fontSize: 14)),
          const SizedBox(height: 12),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 100,
                height: 100,
                child: CircularProgressIndicator(
                  value: score / 10,
                  strokeWidth: 10,
                  backgroundColor: Colors.white12,
                  valueColor: AlwaysStoppedAnimation(color),
                ),
              ),
              Column(
                children: [
                  Text(
                    '$score/10',
                    style: TextStyle(
                        color: color,
                        fontSize: 28,
                        fontWeight: FontWeight.bold),
                  ),
                  Text(result.healthLabel,
                      style: TextStyle(color: color, fontSize: 12)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Confidence: ${(result.confidence * 100).toStringAsFixed(0)}%',
            style: const TextStyle(color: Colors.white38, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(String title, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: _accentGreen, size: 24),
          const SizedBox(width: 12),
          Text(title, style: const TextStyle(color: Colors.white54, fontSize: 14)),
          const Spacer(),
          Text(value,
              style: const TextStyle(
                  color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildRecommendationTile(String text) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.eco_rounded, color: _accentGreen, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(text,
                style: const TextStyle(color: Colors.white70, fontSize: 13)),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(title,
        style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold));
  }

  Widget _buildErrorCard(String message) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade900.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade700),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.red),
          const SizedBox(width: 12),
          Expanded(
            child: Text(message, style: const TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  Widget _buildInputCard(
      {required String title, required List<Widget> children}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }

  Widget _buildNumberField(
      String label, TextEditingController ctrl, String hint) {
    return TextField(
      controller: ctrl,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white54),
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white24),
        filled: true,
        fillColor: _darkBg,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: Colors.white24),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: _accentGreen),
        ),
      ),
    );
  }

  Widget _buildDropdown(String label, List<String> items, String value,
      ValueChanged<String?> onChanged) {
    return DropdownButtonFormField<String>(
      initialValue: value.isEmpty ? null : value,
      dropdownColor: _cardBg,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white54),
        filled: true,
        fillColor: _darkBg,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Colors.white24),
        ),
      ),
      items: items
          .map((s) => DropdownMenuItem(value: s, child: Text(s)))
          .toList(),
      onChanged: onChanged,
    );
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      backgroundColor: _cardBg,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt, color: _accentGreen),
              title: const Text('Camera',
                  style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library, color: _accentGreen),
              title: const Text('Gallery',
                  style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }
}
