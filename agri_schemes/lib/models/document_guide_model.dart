/// Model class representing a document application guide.
/// Contains step-by-step instructions on how a farmer can obtain
/// a required document (e.g., Aadhaar Card, Land Records, etc.)
class DocumentGuideModel {
  /// Display name of the document
  final String documentName;

  /// Brief description of what the document is
  final String description;

  /// Government authority that issues this document
  final String issuingAuthority;

  /// Estimated time to obtain the document
  final String estimatedTime;

  /// Fee / cost involved
  final String fee;

  /// Step-by-step application process
  final List<String> steps;

  /// Documents needed to apply for this document
  final List<String> documentsNeeded;

  /// Helpful links (title + URL)
  final List<HelpfulLink> helpfulLinks;

  /// Practical tips for the farmer
  final List<String> tips;

  const DocumentGuideModel({
    required this.documentName,
    required this.description,
    required this.issuingAuthority,
    required this.estimatedTime,
    required this.fee,
    this.steps = const [],
    this.documentsNeeded = const [],
    this.helpfulLinks = const [],
    this.tips = const [],
  });

  /// Factory constructor to create from API JSON response
  factory DocumentGuideModel.fromJson(Map<String, dynamic> json) {
    return DocumentGuideModel(
      documentName: json['document_name'] ?? '',
      description: json['description'] ?? '',
      issuingAuthority: json['issuing_authority'] ?? '',
      estimatedTime: json['estimated_time'] ?? '',
      fee: json['fee'] ?? '',
      steps: json['steps'] is List ? List<String>.from(json['steps']) : const [],
      documentsNeeded: json['documents_needed'] is List
          ? List<String>.from(json['documents_needed'])
          : const [],
      helpfulLinks: json['helpful_links'] is List
          ? (json['helpful_links'] as List)
              .map((e) => HelpfulLink.fromJson(e as Map<String, dynamic>))
              .toList()
          : const [],
      tips: json['tips'] is List ? List<String>.from(json['tips']) : const [],
    );
  }
}

/// A helpful link with a display title and URL
class HelpfulLink {
  final String title;
  final String url;

  const HelpfulLink({required this.title, required this.url});

  factory HelpfulLink.fromJson(Map<String, dynamic> json) {
    return HelpfulLink(
      title: json['title'] ?? '',
      url: json['url'] ?? '',
    );
  }
}
