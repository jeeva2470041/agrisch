import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/farmer_profile_service.dart';
import '../models/crop_calendar_model.dart';
import '../l10n/app_localizations.dart';

/// Crop Calendar & Planner — shows growth phases, tasks, progress.
class CropCalendarScreen extends StatefulWidget {
  final String? crop;
  final String? state;
  final String? season;
  final String? sowingDate;

  const CropCalendarScreen({
    super.key,
    this.crop,
    this.state,
    this.season,
    this.sowingDate,
  });

  @override
  State<CropCalendarScreen> createState() => _CropCalendarScreenState();
}

class _CropCalendarScreenState extends State<CropCalendarScreen> {
  final _api = ApiService();

  bool _loading = false;
  CropCalendarModel? _calendar;
  String? _error;

  String _crop = '';
  String _state = '';
  String _season = '';
  DateTime _sowingDate = DateTime.now();

  final _crops = [
    'Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Groundnut',
    'Soybean', 'Mustard', 'Chickpea', 'Pigeon Pea', 'Jowar', 'Bajra',
    'Ragi', 'Sunflower', 'Sesame', 'Turmeric', 'Onion', 'Tomato',
    'Potato', 'Brinjal',
  ];

  final _states = [
    'Tamil Nadu', 'Andhra Pradesh', 'Karnataka', 'Kerala', 'Maharashtra',
    'Madhya Pradesh', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Rajasthan',
    'Gujarat', 'Bihar', 'West Bengal', 'Odisha', 'Telangana',
  ];

  final _seasons = ['Kharif', 'Rabi', 'Zaid', 'Whole Year'];

  static const _primaryGreen = Color(0xFF1B5E20);
  static const _accentGreen = Color(0xFF43A047);
  static const _darkBg = Color(0xFF0D1B0F);
  static const _cardBg = Color(0xFF162418);

  @override
  void initState() {
    super.initState();
    if (widget.crop != null) _crop = widget.crop!;
    if (widget.state != null) _state = widget.state!;
    if (widget.season != null) _season = widget.season!;
    if (widget.sowingDate != null) {
      _sowingDate = DateTime.tryParse(widget.sowingDate!) ?? DateTime.now();
    }

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final profile =
          Provider.of<FarmerProfileService>(context, listen: false);
      setState(() {
        if (_crop.isEmpty && profile.crop.isNotEmpty && _crops.contains(profile.crop)) {
          _crop = profile.crop;
        }
        if (_state.isEmpty && profile.state.isNotEmpty && _states.contains(profile.state)) {
          _state = profile.state;
        }
        if (_season.isEmpty && profile.season.isNotEmpty && _seasons.contains(profile.season)) {
          _season = profile.season;
        }
        if (widget.sowingDate == null && profile.sowingDate.isNotEmpty) {
          _sowingDate =
              DateTime.tryParse(profile.sowingDate) ?? DateTime.now();
        }
      });
    });
  }

  Future<void> _fetchCalendar() async {
    if (_crop.isEmpty || _state.isEmpty) {
      setState(() => _error = 'Please select Crop and State.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    final dateStr =
        '${_sowingDate.year}-${_sowingDate.month.toString().padLeft(2, '0')}-${_sowingDate.day.toString().padLeft(2, '0')}';

    final resp = await _api.getCropCalendar(
      crop: _crop,
      state: _state,
      season: _season.isEmpty ? 'Kharif' : _season,
      sowingDate: dateStr,
    );

    setState(() {
      _loading = false;
      if (resp == null) {
        _error = 'Could not load crop calendar. Please try again.';
      } else if (resp.containsKey('error')) {
        _error = resp['error'];
      } else {
        _calendar = CropCalendarModel.fromJson(resp);
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
        title: Text(l.translate('cropCalendar')),
        actions: [
          if (_calendar != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => setState(() => _calendar = null),
              tooltip: 'Change inputs',
            ),
        ],
      ),
      body: _calendar != null ? _buildCalendarView(l) : _buildInputForm(l),
    );
  }

  Widget _buildInputForm(AppLocalizations l) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.teal.shade800, _primaryGreen],
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              const Icon(Icons.calendar_month, color: Colors.white, size: 40),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l.translate('cropCalendar'),
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(l.translate('cropCalendarDesc'),
                        style: const TextStyle(
                            color: Colors.white70, fontSize: 12)),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        _buildDropdown(l.translate('crop'), _crops, _crop,
            (v) => setState(() => _crop = v ?? '')),
        const SizedBox(height: 12),
        _buildDropdown(l.translate('state'), _states, _state,
            (v) => setState(() => _state = v ?? '')),
        const SizedBox(height: 12),
        _buildDropdown(l.translate('season'), _seasons, _season,
            (v) => setState(() => _season = v ?? '')),
        const SizedBox(height: 12),
        // Sowing date picker
        InkWell(
          onTap: () async {
            final picked = await showDatePicker(
              context: context,
              initialDate: _sowingDate,
              firstDate: DateTime(2020),
              lastDate: DateTime(2030),
              builder: (ctx, child) => Theme(
                data: ThemeData.dark().copyWith(
                  colorScheme: const ColorScheme.dark(
                    primary: _accentGreen,
                    surface: _cardBg,
                  ),
                ),
                child: child!,
              ),
            );
            if (picked != null) setState(() => _sowingDate = picked);
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(12),
              border:
                  Border.all(color: _accentGreen.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.calendar_today, color: _accentGreen, size: 20),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l.translate('sowingDate'),
                        style: const TextStyle(
                            color: Colors.white54, fontSize: 12)),
                    const SizedBox(height: 4),
                    Text(
                      '${_sowingDate.day}/${_sowingDate.month}/${_sowingDate.year}',
                      style: const TextStyle(
                          color: Colors.white, fontSize: 16),
                    ),
                  ],
                ),
                const Spacer(),
                const Icon(Icons.edit_calendar, color: Colors.white38),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),
        if (_error != null) ...[
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red.shade900.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(_error!, style: const TextStyle(color: Colors.red)),
          ),
          const SizedBox(height: 12),
        ],
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: !_loading ? _fetchCalendar : null,
            icon: _loading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2))
                : const Icon(Icons.calendar_month),
            label: Text(_loading
                ? l.translate('loading')
                : l.translate('generateCalendar')),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal.shade700,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14)),
              textStyle:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCalendarView(AppLocalizations l) {
    final cal = _calendar!;
    final profile =
        Provider.of<FarmerProfileService>(context);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Progress header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _cardBg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: _accentGreen.withValues(alpha: 0.3)),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('$_crop ${l.translate('calendar')}',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold)),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _accentGreen.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text('${cal.totalWeeks} weeks',
                        style: const TextStyle(color: _accentGreen)),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Text(l.translate('overallProgress'),
                      style: const TextStyle(color: Colors.white54)),
                  const Spacer(),
                  Text('${cal.progressPercent.toStringAsFixed(0)}%',
                      style: const TextStyle(
                          color: _accentGreen, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: cal.progressPercent / 100,
                  backgroundColor: Colors.white12,
                  valueColor: const AlwaysStoppedAnimation(_accentGreen),
                  minHeight: 8,
                ),
              ),
              if (cal.currentPhase.isNotEmpty) ...[
                const SizedBox(height: 10),
                Row(
                  children: [
                    const Icon(Icons.location_on, color: Colors.amber, size: 16),
                    const SizedBox(width: 4),
                    Text('Current: ${cal.currentPhase}',
                        style: const TextStyle(color: Colors.amber, fontSize: 13)),
                  ],
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Phase timeline
        ...cal.phases.asMap().entries.map((e) {
          final idx = e.key;
          final phase = e.value;
          return _buildPhaseCard(phase, idx, cal.phases.length, profile);
        }),

        // Upcoming tasks section
        if (cal.upcomingTasks.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text(l.translate('upcomingTasks'),
              style: const TextStyle(
                  color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ...cal.upcomingTasks.map((t) => _buildTaskTile(t, profile)),
        ],
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildPhaseCard(
      GrowthPhase phase, int index, int total, FarmerProfileService profile) {
    final phaseColor = _parseColor(phase.color);
    final isActive = phase.isCurrent;

    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline column
          SizedBox(
            width: 40,
            child: Column(
              children: [
                Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: isActive ? phaseColor : phaseColor.withValues(alpha: 0.5),
                    shape: BoxShape.circle,
                    border: isActive
                        ? Border.all(color: Colors.white, width: 2)
                        : null,
                  ),
                  child: isActive
                      ? const Icon(Icons.play_arrow, color: Colors.white, size: 12)
                      : null,
                ),
                if (index < total - 1)
                  Container(
                    width: 2,
                    height: 60,
                    color: phaseColor.withValues(alpha: 0.3),
                  ),
              ],
            ),
          ),
          // Phase content
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: isActive
                    ? phaseColor.withValues(alpha: 0.15)
                    : _cardBg,
                borderRadius: BorderRadius.circular(12),
                border: isActive
                    ? Border.all(color: phaseColor.withValues(alpha: 0.5))
                    : null,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 10,
                        height: 10,
                        decoration: BoxDecoration(
                          color: phaseColor,
                          borderRadius: BorderRadius.circular(3),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(phase.name,
                            style: TextStyle(
                                color: isActive ? phaseColor : Colors.white,
                                fontSize: 15,
                                fontWeight: FontWeight.bold)),
                      ),
                      Text('${phase.displayStart} - ${phase.displayEnd}',
                          style: const TextStyle(
                              color: Colors.white38, fontSize: 11)),
                    ],
                  ),
                  if (phase.tasks.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    ...phase.tasks.take(3).map((t) => _buildTaskTile(t, profile)),
                    if (phase.tasks.length > 3)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          '+${phase.tasks.length - 3} more tasks',
                          style: const TextStyle(
                              color: Colors.white38, fontSize: 12),
                        ),
                      ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTaskTile(CalendarTask task, FarmerProfileService profile) {
    final isCompleted = profile.completedTasks.contains(task.taskKey);
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      child: InkWell(
        onTap: () => profile.toggleTaskCompletion(task.taskKey),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: _darkBg,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(
                isCompleted
                    ? Icons.check_circle_rounded
                    : task.isPast
                        ? Icons.radio_button_unchecked
                        : task.isToday
                            ? Icons.pending_rounded
                            : Icons.circle_outlined,
                color: isCompleted
                    ? _accentGreen
                    : task.isToday
                        ? Colors.amber
                        : Colors.white24,
                size: 20,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      task.title,
                      style: TextStyle(
                        color:
                            isCompleted ? Colors.white38 : Colors.white,
                        fontSize: 13,
                        decoration:
                            isCompleted ? TextDecoration.lineThrough : null,
                      ),
                    ),
                    if (task.description.isNotEmpty)
                      Text(task.description,
                          style: const TextStyle(
                              color: Colors.white30, fontSize: 11),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis),
                  ],
                ),
              ),
              if (task.date.isNotEmpty)
                Text(task.date,
                    style: const TextStyle(color: Colors.white24, fontSize: 10)),
            ],
          ),
        ),
      ),
    );
  }

  Color _parseColor(String hexColor) {
    try {
      final hex = hexColor.replaceAll('#', '');
      return Color(int.parse('FF$hex', radix: 16));
    } catch (_) {
      return _accentGreen;
    }
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
        fillColor: _cardBg,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: _accentGreen.withValues(alpha: 0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _accentGreen),
        ),
      ),
      items: items
          .map((s) => DropdownMenuItem(value: s, child: Text(s)))
          .toList(),
      onChanged: onChanged,
    );
  }
}
