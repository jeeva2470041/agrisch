// Models for smart alerts (weather + price).

class WeatherAlert {
  final String type;
  final String title;
  final String severity;
  final String description;
  final String action;
  final String timestamp;

  WeatherAlert({
    required this.type,
    required this.title,
    required this.severity,
    required this.description,
    required this.action,
    required this.timestamp,
  });

  factory WeatherAlert.fromJson(Map<String, dynamic> json) {
    return WeatherAlert(
      type: json['type'] ?? '',
      title: json['title'] ?? '',
      severity: json['severity'] ?? 'low',
      description: json['description'] ?? '',
      action: json['action'] ?? '',
      timestamp: json['timestamp'] ?? '',
    );
  }

  bool get isCritical => severity == 'critical';
  bool get isHigh => severity == 'high';
}

class AlertsResponse {
  final List<WeatherAlert> alerts;
  final String summary;
  final String checkedAt;

  AlertsResponse({
    required this.alerts,
    required this.summary,
    required this.checkedAt,
  });

  factory AlertsResponse.fromJson(Map<String, dynamic> json) {
    return AlertsResponse(
      alerts: (json['alerts'] as List? ?? [])
          .map((a) => WeatherAlert.fromJson(a))
          .toList(),
      summary: json['summary'] ?? '',
      checkedAt: json['checked_at'] ?? '',
    );
  }

  int get criticalCount => alerts.where((a) => a.isCritical).length;
  int get highCount => alerts.where((a) => a.isHigh).length;
  bool get hasAlerts => alerts.isNotEmpty;
}

class PriceTrigger {
  String crop;
  double thresholdPrice;
  String direction; // 'above' or 'below'

  PriceTrigger({
    required this.crop,
    required this.thresholdPrice,
    this.direction = 'above',
  });

  Map<String, dynamic> toJson() => {
        'crop': crop,
        'threshold_price': thresholdPrice,
        'direction': direction,
      };

  factory PriceTrigger.fromJson(Map<String, dynamic> json) {
    return PriceTrigger(
      crop: json['crop'] ?? '',
      thresholdPrice: (json['threshold_price'] ?? 0).toDouble(),
      direction: json['direction'] ?? 'above',
    );
  }
}
