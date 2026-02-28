// Models for crop calendar with growth phases and tasks.

class CropCalendarModel {
  final String crop;
  final String state;
  final String season;
  final String sowingDate;
  final String expectedHarvest;
  final String displayHarvest;
  final int totalWeeks;
  final String currentPhase;
  final int progressPercent;
  final int daysIntoCycle;
  final int totalDays;
  final List<GrowthPhase> phases;
  final List<CalendarTask> upcomingTasks;
  final int totalTasks;

  CropCalendarModel({
    required this.crop,
    required this.state,
    required this.season,
    required this.sowingDate,
    required this.expectedHarvest,
    required this.displayHarvest,
    required this.totalWeeks,
    required this.currentPhase,
    required this.progressPercent,
    required this.daysIntoCycle,
    required this.totalDays,
    required this.phases,
    required this.upcomingTasks,
    required this.totalTasks,
  });

  factory CropCalendarModel.fromJson(Map<String, dynamic> json) {
    return CropCalendarModel(
      crop: json['crop'] ?? '',
      state: json['state'] ?? '',
      season: json['season'] ?? '',
      sowingDate: json['sowing_date'] ?? '',
      expectedHarvest: json['expected_harvest'] ?? '',
      displayHarvest: json['display_harvest'] ?? '',
      totalWeeks: json['total_weeks'] ?? 0,
      currentPhase: json['current_phase'] ?? '',
      progressPercent: json['progress_percent'] ?? 0,
      daysIntoCycle: json['days_into_cycle'] ?? 0,
      totalDays: json['total_days'] ?? 0,
      phases: (json['phases'] as List? ?? [])
          .map((p) => GrowthPhase.fromJson(p))
          .toList(),
      upcomingTasks: (json['upcoming_tasks'] as List? ?? [])
          .map((t) => CalendarTask.fromJson(t))
          .toList(),
      totalTasks: json['total_tasks'] ?? 0,
    );
  }
}

class GrowthPhase {
  final String name;
  final String startDate;
  final String endDate;
  final String displayStart;
  final String displayEnd;
  final String color;
  final bool isCurrent;
  final List<CalendarTask> tasks;

  GrowthPhase({
    required this.name,
    required this.startDate,
    required this.endDate,
    required this.displayStart,
    required this.displayEnd,
    required this.color,
    required this.isCurrent,
    required this.tasks,
  });

  factory GrowthPhase.fromJson(Map<String, dynamic> json) {
    return GrowthPhase(
      name: json['name'] ?? '',
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'] ?? '',
      displayStart: json['display_start'] ?? '',
      displayEnd: json['display_end'] ?? '',
      color: json['color'] ?? '#4CAF50',
      isCurrent: json['is_current'] ?? false,
      tasks: (json['tasks'] as List? ?? [])
          .map((t) => CalendarTask.fromJson(t))
          .toList(),
    );
  }
}

class CalendarTask {
  final String title;
  final String description;
  final String date;
  final String displayDate;
  final bool isPast;
  final bool isToday;
  final String phase;
  bool isCompleted;

  CalendarTask({
    required this.title,
    required this.description,
    required this.date,
    required this.displayDate,
    required this.isPast,
    required this.isToday,
    required this.phase,
    this.isCompleted = false,
  });

  factory CalendarTask.fromJson(Map<String, dynamic> json) {
    return CalendarTask(
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      date: json['date'] ?? '',
      displayDate: json['display_date'] ?? '',
      isPast: json['is_past'] ?? false,
      isToday: json['is_today'] ?? false,
      phase: json['phase'] ?? '',
    );
  }

  /// Unique key for tracking completion in local storage.
  String get taskKey => '${phase}_${title}_$date';
}
