import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../l10n/app_localizations.dart';
import '../data/constants.dart';
import '../models/farmer_input_model.dart';
import 'scheme_recommendation_screen.dart';

/// Farmer Input Screen — Premium UI with searchable state picker
/// Collects: Crop type, Land size, Season, State/UT
class FarmerInputScreen extends StatefulWidget {
  const FarmerInputScreen({super.key});

  @override
  State<FarmerInputScreen> createState() => _FarmerInputScreenState();
}

class _FarmerInputScreenState extends State<FarmerInputScreen>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _landSizeController = TextEditingController();

  String? _selectedCrop;
  String? _selectedSeason;
  String? _selectedState;
  bool _isGettingLocation = false;

  late AnimationController _animController;
  late Animation<double> _fadeAnim;

  // Theme colors
  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _lightGreen = Color(0xFFE8F5E9);
  static const _darkBg = Color(0xFF0D2818);
  static const _cardBg = Color(0xFFFAFDFA);

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnim = CurvedAnimation(parent: _animController, curve: Curves.easeOut);
    _animController.forward();
  }

  @override
  void dispose() {
    _landSizeController.dispose();
    _animController.dispose();
    super.dispose();
  }

  void _onFindSchemes() {
    if (_formKey.currentState!.validate()) {
      if (_selectedCrop == null ||
          _selectedSeason == null ||
          _selectedState == null) {
        _showSnackbar(
          AppLocalizations.of(context).pleaseSelectAllFields,
          isError: true,
        );
        return;
      }

      final farmerInput = FarmerInputModel(
        cropType: _selectedCrop!,
        landSize: double.parse(_landSizeController.text),
        season: _selectedSeason!,
        state: _selectedState!,
      );

      Navigator.push(
        context,
        PageRouteBuilder(
          pageBuilder: (_, __, ___) =>
              SchemeRecommendationScreen(farmerInput: farmerInput),
          transitionsBuilder: (_, anim, __, child) {
            return SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(1, 0),
                end: Offset.zero,
              ).animate(CurvedAnimation(parent: anim, curve: Curves.easeOut)),
              child: child,
            );
          },
        ),
      );
    }
  }

  void _showSnackbar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: isError ? Colors.red.shade700 : _accentGreen,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  Future<void> _getCurrentLocation() async {
    setState(() => _isGettingLocation = true);

    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          _showSnackbar('Location permissions are denied', isError: true);
          setState(() => _isGettingLocation = false);
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        _showSnackbar(
          'Location permissions are permanently denied',
          isError: true,
        );
        setState(() => _isGettingLocation = false);
        return;
      }

      final position = await Geolocator.getCurrentPosition();
      final placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );

      if (placemarks.isNotEmpty) {
        final state = placemarks.first.administrativeArea;
        if (state != null && States.all.contains(state)) {
          setState(() => _selectedState = state);
          _showSnackbar('Detected state: $state');
        } else {
          _showSnackbar(
            'Detected state "$state" is not in the list.',
            isError: true,
          );
        }
      }
    } catch (e) {
      if (e.toString().contains('Not supported') ||
          e.toString().contains('UnimplementedError')) {
        _showSnackbar(
          'Location detection not supported on this platform.',
          isError: true,
        );
      } else {
        _showSnackbar('Error getting location: $e', isError: true);
      }
    } finally {
      setState(() => _isGettingLocation = false);
    }
  }

  /// Open a bottom sheet with searchable list for state selection
  void _openStatePicker() {
    final localizations = AppLocalizations.of(context);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _StatePickerSheet(
        selectedState: _selectedState,
        localizations: localizations,
        onStateSelected: (state) {
          setState(() => _selectedState = state);
          Navigator.pop(ctx);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [_darkBg, Color(0xFF1A3A2A), Color(0xFF0D2818)],
          ),
        ),
        child: SafeArea(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: CustomScrollView(
              slivers: [
                // ─── App Bar ───
                SliverAppBar(
                  expandedHeight: 140,
                  floating: false,
                  pinned: true,
                  backgroundColor: Colors.transparent,
                  elevation: 0,
                  flexibleSpace: FlexibleSpaceBar(
                    centerTitle: true,
                    title: Text(
                      l.farmerDetails,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                        letterSpacing: 0.5,
                      ),
                    ),
                    background: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            _primaryGreen.withValues(alpha: 0.8),
                            Colors.transparent,
                          ],
                        ),
                      ),
                      child: const Center(
                        child: Padding(
                          padding: EdgeInsets.only(bottom: 30),
                          child: Icon(
                            Icons.agriculture_rounded,
                            size: 50,
                            color: Colors.white38,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),

                // ─── Form Content ───
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          // ── Header banner ──
                          _buildInfoBanner(l),
                          const SizedBox(height: 24),

                          // ── Input Form Card ──
                          Container(
                            decoration: BoxDecoration(
                              color: _cardBg,
                              borderRadius: BorderRadius.circular(24),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.15),
                                  blurRadius: 30,
                                  offset: const Offset(0, 10),
                                ),
                              ],
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(24),
                              child: Column(
                                children: [
                                  // Green accent strip
                                  Container(
                                    height: 4,
                                    decoration: const BoxDecoration(
                                      gradient: LinearGradient(
                                        colors: [
                                          _primaryGreen,
                                          _accentGreen,
                                          Color(0xFF66BB6A),
                                        ],
                                      ),
                                    ),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.all(24),
                                    child: Column(
                                      children: [
                                        // 1. Crop Type
                                        _buildSectionLabel(
                                          Icons.grass_rounded,
                                          l.cropType,
                                        ),
                                        const SizedBox(height: 10),
                                        _buildDropdown(
                                          hint: l.selectCrop,
                                          value: _selectedCrop,
                                          items: _getCropItems(l),
                                          onChanged: (v) =>
                                              setState(() => _selectedCrop = v),
                                        ),
                                        const SizedBox(height: 28),

                                        // 2. Land Size
                                        _buildSectionLabel(
                                          Icons.square_foot_rounded,
                                          l.landSize,
                                        ),
                                        const SizedBox(height: 10),
                                        _buildLandSizeField(l),
                                        const SizedBox(height: 28),

                                        // 3. Season
                                        _buildSectionLabel(
                                          Icons.wb_sunny_rounded,
                                          l.season,
                                        ),
                                        const SizedBox(height: 10),
                                        _buildSeasonChips(l),
                                        const SizedBox(height: 28),

                                        // 4. State — Searchable Picker
                                        _buildSectionLabel(
                                          Icons.location_on_rounded,
                                          l.state,
                                        ),
                                        const SizedBox(height: 10),
                                        _buildStatePicker(l),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(height: 32),

                          // ── Find Schemes Button ──
                          _buildFindButton(l),
                          const SizedBox(height: 16),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════
  //  UI BUILDERS
  // ═══════════════════════════════════════════════════

  Widget _buildInfoBanner(AppLocalizations l) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            _accentGreen.withValues(alpha: 0.15),
            _primaryGreen.withValues(alpha: 0.08),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accentGreen.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: _accentGreen.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.search_rounded,
              color: Colors.white70,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l.findSchemes,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  l.farmerDetails,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withValues(alpha: 0.6),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionLabel(IconData icon, String label) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: _lightGreen,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 18, color: _primaryGreen),
        ),
        const SizedBox(width: 10),
        Text(
          label,
          style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: Color(0xFF2D3436),
            letterSpacing: 0.3,
          ),
        ),
      ],
    );
  }

  Widget _buildDropdown({
    required String hint,
    required String? value,
    required List<DropdownMenuItem<String>> items,
    required ValueChanged<String?> onChanged,
  }) {
    return DropdownButtonFormField<String>(
      value: value,
      hint: Text(hint, style: TextStyle(color: Colors.grey.shade500)),
      items: items,
      onChanged: onChanged,
      decoration: _inputDecoration(),
      dropdownColor: Colors.white,
      borderRadius: BorderRadius.circular(16),
      icon: const Icon(Icons.keyboard_arrow_down_rounded, color: _accentGreen),
      style: const TextStyle(fontSize: 15, color: Color(0xFF2D3436)),
    );
  }

  Widget _buildLandSizeField(AppLocalizations l) {
    return TextFormField(
      controller: _landSizeController,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      inputFormatters: [
        FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*')),
      ],
      validator: (value) {
        if (value == null || value.isEmpty) return l.pleaseEnterLandSize;
        if (double.tryParse(value) == null) return l.pleaseEnterLandSize;
        return null;
      },
      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500),
      decoration: _inputDecoration().copyWith(
        hintText: l.landSizeHint,
        suffixText: 'ha',
        suffixStyle: TextStyle(
          color: _accentGreen,
          fontWeight: FontWeight.w600,
          fontSize: 14,
        ),
      ),
    );
  }

  /// Season selector — modern chip-based design
  Widget _buildSeasonChips(AppLocalizations l) {
    final seasons = [
      (Seasons.kharif, l.kharif, Icons.water_drop_rounded),
      (Seasons.rabi, l.rabi, Icons.ac_unit_rounded),
      (Seasons.zaid, l.zaid, Icons.wb_twilight_rounded),
    ];

    return Row(
      children: seasons.map((s) {
        final isSelected = _selectedSeason == s.$1;
        return Expanded(
          child: Padding(
            padding: EdgeInsets.only(right: s.$1 != Seasons.zaid ? 10 : 0),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () => setState(() => _selectedSeason = s.$1),
                  borderRadius: BorderRadius.circular(14),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    decoration: BoxDecoration(
                      color: isSelected ? _primaryGreen : Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: isSelected
                            ? _primaryGreen
                            : Colors.grey.shade300,
                        width: isSelected ? 2 : 1,
                      ),
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: _primaryGreen.withValues(alpha: 0.3),
                                blurRadius: 8,
                                offset: const Offset(0, 3),
                              ),
                            ]
                          : null,
                    ),
                    child: Column(
                      children: [
                        Icon(
                          s.$3,
                          size: 22,
                          color: isSelected
                              ? Colors.white
                              : Colors.grey.shade600,
                        ),
                        const SizedBox(height: 6),
                        Text(
                          s.$2,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: isSelected
                                ? FontWeight.w700
                                : FontWeight.w500,
                            color: isSelected
                                ? Colors.white
                                : Colors.grey.shade700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  /// State picker — tap to open searchable bottom sheet
  Widget _buildStatePicker(AppLocalizations l) {
    return Row(
      children: [
        Expanded(
          child: InkWell(
            onTap: _openStatePicker,
            borderRadius: BorderRadius.circular(14),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: _selectedState != null
                      ? _accentGreen
                      : Colors.grey.shade300,
                  width: _selectedState != null ? 2 : 1,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      _selectedState ?? l.selectState,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: _selectedState != null
                            ? FontWeight.w500
                            : FontWeight.w400,
                        color: _selectedState != null
                            ? const Color(0xFF2D3436)
                            : Colors.grey.shade500,
                      ),
                    ),
                  ),
                  Icon(
                    Icons.arrow_drop_down_rounded,
                    color: _selectedState != null
                        ? _accentGreen
                        : Colors.grey.shade400,
                    size: 28,
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
        // GPS Button
        SizedBox(
          height: 52,
          width: 52,
          child: Material(
            color: _primaryGreen,
            borderRadius: BorderRadius.circular(14),
            elevation: 2,
            child: InkWell(
              onTap: _isGettingLocation ? null : _getCurrentLocation,
              borderRadius: BorderRadius.circular(14),
              child: Center(
                child: _isGettingLocation
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2.5,
                        ),
                      )
                    : const Icon(
                        Icons.my_location_rounded,
                        color: Colors.white,
                        size: 22,
                      ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFindButton(AppLocalizations l) {
    return SizedBox(
      width: double.infinity,
      height: 58,
      child: ElevatedButton(
        onPressed: _onFindSchemes,
        style: ElevatedButton.styleFrom(
          backgroundColor: _accentGreen,
          foregroundColor: Colors.white,
          elevation: 6,
          shadowColor: _accentGreen.withValues(alpha: 0.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.search_rounded, size: 24),
            const SizedBox(width: 12),
            Text(
              l.findSchemes,
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  InputDecoration _inputDecoration() {
    return InputDecoration(
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: _accentGreen, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: Colors.redAccent),
      ),
      filled: true,
      fillColor: Colors.grey.shade50,
    );
  }

  // ═══════════════════════════════════════════════════
  //  DROPDOWN DATA
  // ═══════════════════════════════════════════════════

  List<DropdownMenuItem<String>> _getCropItems(AppLocalizations l) {
    return [
      DropdownMenuItem(value: CropTypes.rice, child: Text(l.rice)),
      DropdownMenuItem(value: CropTypes.wheat, child: Text(l.wheat)),
      DropdownMenuItem(value: CropTypes.cotton, child: Text(l.cotton)),
      DropdownMenuItem(value: CropTypes.sugarcane, child: Text(l.sugarcane)),
      DropdownMenuItem(value: CropTypes.maize, child: Text(l.maize)),
      DropdownMenuItem(value: CropTypes.pulses, child: Text(l.pulses)),
      DropdownMenuItem(value: CropTypes.millets, child: Text(l.millets)),
      DropdownMenuItem(value: CropTypes.groundnut, child: Text(l.groundnut)),
      DropdownMenuItem(value: CropTypes.soybean, child: Text(l.soybean)),
      DropdownMenuItem(value: CropTypes.coconut, child: Text(l.coconut)),
      DropdownMenuItem(value: CropTypes.vegetables, child: Text(l.vegetables)),
      DropdownMenuItem(value: CropTypes.fruits, child: Text(l.fruits)),
      DropdownMenuItem(value: CropTypes.tea, child: Text(l.tea)),
      DropdownMenuItem(value: CropTypes.coffee, child: Text(l.coffee)),
      DropdownMenuItem(value: CropTypes.spices, child: Text(l.spices)),
      DropdownMenuItem(value: CropTypes.oilseeds, child: Text(l.oilseeds)),
      DropdownMenuItem(value: CropTypes.jute, child: Text(l.jute)),
      DropdownMenuItem(value: CropTypes.tobacco, child: Text(l.tobacco)),
    ];
  }
}

// ═══════════════════════════════════════════════════════════════
// SEARCHABLE STATE PICKER — Bottom Sheet
// ═══════════════════════════════════════════════════════════════

class _StatePickerSheet extends StatefulWidget {
  final String? selectedState;
  final AppLocalizations localizations;
  final ValueChanged<String> onStateSelected;

  const _StatePickerSheet({
    required this.selectedState,
    required this.localizations,
    required this.onStateSelected,
  });

  @override
  State<_StatePickerSheet> createState() => _StatePickerSheetState();
}

class _StatePickerSheetState extends State<_StatePickerSheet> {
  final _searchController = TextEditingController();
  String _query = '';

  // 28 States
  static const _stateKeys = [
    'andhraPradesh',
    'arunachalPradesh',
    'assam',
    'bihar',
    'chhattisgarh',
    'goa',
    'gujarat',
    'haryana',
    'himachalPradesh',
    'jharkhand',
    'karnataka',
    'kerala',
    'madhyaPradesh',
    'maharashtra',
    'manipur',
    'meghalaya',
    'mizoram',
    'nagaland',
    'odisha',
    'punjab',
    'rajasthan',
    'sikkim',
    'tamilNadu',
    'telangana',
    'tripura',
    'uttarPradesh',
    'uttarakhand',
    'westBengal',
  ];

  // 8 Union Territories
  static const _utKeys = [
    'andamanNicobar',
    'chandigarh',
    'dadraGarHaveli',
    'delhi',
    'jammuKashmir',
    'ladakh',
    'lakshadweep',
    'puducherry',
  ];

  /// Map translation key to actual constant value
  String _keyToValue(String key) {
    final map = {
      'andhraPradesh': States.andhraPradesh,
      'arunachalPradesh': States.arunachalPradesh,
      'assam': States.assam,
      'bihar': States.bihar,
      'chhattisgarh': States.chhattisgarh,
      'goa': States.goa,
      'gujarat': States.gujarat,
      'haryana': States.haryana,
      'himachalPradesh': States.himachalPradesh,
      'jharkhand': States.jharkhand,
      'karnataka': States.karnataka,
      'kerala': States.kerala,
      'madhyaPradesh': States.madhyaPradesh,
      'maharashtra': States.maharashtra,
      'manipur': States.manipur,
      'meghalaya': States.meghalaya,
      'mizoram': States.mizoram,
      'nagaland': States.nagaland,
      'odisha': States.odisha,
      'punjab': States.punjab,
      'rajasthan': States.rajasthan,
      'sikkim': States.sikkim,
      'tamilNadu': States.tamilNadu,
      'telangana': States.telangana,
      'tripura': States.tripura,
      'uttarPradesh': States.uttarPradesh,
      'uttarakhand': States.uttarakhand,
      'westBengal': States.westBengal,
      'andamanNicobar': States.andamanNicobar,
      'chandigarh': States.chandigarh,
      'dadraGarHaveli': States.dadraGarHaveli,
      'delhi': States.delhi,
      'jammuKashmir': States.jammuKashmir,
      'ladakh': States.ladakh,
      'lakshadweep': States.lakshadweep,
      'puducherry': States.puducherry,
    };
    return map[key] ?? key;
  }

  String _localizedName(String key) {
    return widget.localizations.translate(key);
  }

  List<String> _filterKeys(List<String> keys) {
    if (_query.isEmpty) return keys;
    return keys.where((k) {
      final localName = _localizedName(k).toLowerCase();
      final engName = _keyToValue(k).toLowerCase();
      return localName.contains(_query) || engName.contains(_query);
    }).toList();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l = widget.localizations;
    final filteredStates = _filterKeys(_stateKeys);
    final filteredUTs = _filterKeys(_utKeys);

    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Drag handle
          Container(
            margin: const EdgeInsets.only(top: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(4),
            ),
          ),

          // Title
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
            child: Text(
              l.selectState,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: Color(0xFF1B5E20),
              ),
            ),
          ),

          // Search bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: TextField(
              controller: _searchController,
              onChanged: (v) => setState(() => _query = v.toLowerCase()),
              decoration: InputDecoration(
                hintText: l.searchState,
                prefixIcon: const Icon(Icons.search_rounded, size: 22),
                suffixIcon: _query.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear_rounded, size: 20),
                        onPressed: () {
                          _searchController.clear();
                          setState(() => _query = '');
                        },
                      )
                    : null,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: const BorderSide(
                    color: Color(0xFF43A047),
                    width: 2,
                  ),
                ),
                filled: true,
                fillColor: Colors.grey.shade50,
              ),
            ),
          ),

          // Scrollable list
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                // States section
                if (filteredStates.isNotEmpty) ...[
                  _sectionHeader(l.statesHeader, '${filteredStates.length}'),
                  ...filteredStates.map((k) => _stateTile(k)),
                ],
                // UTs section
                if (filteredUTs.isNotEmpty) ...[
                  _sectionHeader(
                    l.unionTerritoriesHeader,
                    '${filteredUTs.length}',
                  ),
                  ...filteredUTs.map((k) => _stateTile(k)),
                ],
                // No results
                if (filteredStates.isEmpty && filteredUTs.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(40),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(
                            Icons.search_off_rounded,
                            size: 48,
                            color: Colors.grey.shade400,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'No states found',
                            style: TextStyle(color: Colors.grey.shade500),
                          ),
                        ],
                      ),
                    ),
                  ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionHeader(String title, String count) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 16, 8, 8),
      child: Row(
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: Colors.grey.shade600,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              count,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Color(0xFF1B5E20),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _stateTile(String key) {
    final value = _keyToValue(key);
    final isSelected = widget.selectedState == value;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Material(
        color: isSelected ? const Color(0xFFE8F5E9) : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: () => widget.onStateSelected(value),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    _localizedName(key),
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: isSelected
                          ? FontWeight.w600
                          : FontWeight.w400,
                      color: isSelected
                          ? const Color(0xFF1B5E20)
                          : const Color(0xFF2D3436),
                    ),
                  ),
                ),
                if (isSelected)
                  const Icon(
                    Icons.check_circle_rounded,
                    color: Color(0xFF43A047),
                    size: 22,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
