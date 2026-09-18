/// Fixed enum wire values, per CLAUDE.md section 5 / api-contract.md.
/// Fetched from `GET /suggestions/categories` at runtime rather than
/// hardcoded for display purposes, but kept here as the canonical Dart type.
class SuggestionStatus {
  static const nw = 'new';
  static const reviewing = 'reviewing';
  static const planned = 'planned';
  static const declined = 'declined';
}

class Suggestion {
  Suggestion({
    required this.id,
    required this.category,
    required this.body,
    required this.status,
    required this.themeId,
    required this.themeLabel,
    required this.sentiment,
    required this.isAnonymous,
    required this.createdAt,
  });

  final String id;
  final String category;
  final String body;
  final String status;

  /// Always null in v1 — the clustering engine is not yet built.
  final String? themeId;
  final String? themeLabel;
  final double? sentiment;

  final bool isAnonymous;
  final DateTime createdAt;

  factory Suggestion.fromJson(Map<String, dynamic> json) {
    return Suggestion(
      id: json['id'] as String,
      category: json['category'] as String,
      body: json['body'] as String,
      status: json['status'] as String,
      themeId: json['theme_id'] as String?,
      themeLabel: json['theme_label'] as String?,
      sentiment: (json['sentiment'] as num?)?.toDouble(),
      isAnonymous: json['is_anonymous'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
