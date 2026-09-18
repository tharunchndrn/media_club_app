import 'photo.dart';

class EventStatus {
  static const draft = 'draft';
  static const published = 'published';
}

class ClubEvent {
  ClubEvent({
    required this.id,
    required this.title,
    required this.slug,
    required this.description,
    required this.venue,
    required this.eventDate,
    required this.coverImageUrl,
    required this.status,
    required this.academicYear,
    required this.createdAt,
    this.photos,
  });

  final String id;
  final String title;
  final String slug;
  final String description;
  final String venue;
  final DateTime eventDate;
  final String? coverImageUrl;
  final String status;
  final String academicYear;
  final DateTime createdAt;

  /// Only present on `GET /events/{id}`, ordered by `sort_order`.
  final List<EventPhoto>? photos;

  bool get isPast => eventDate.isBefore(DateTime.now());

  factory ClubEvent.fromJson(Map<String, dynamic> json) {
    return ClubEvent(
      id: json['id'] as String,
      title: json['title'] as String,
      slug: json['slug'] as String,
      description: json['description'] as String,
      venue: json['venue'] as String,
      eventDate: DateTime.parse(json['event_date'] as String),
      coverImageUrl: json['cover_image_url'] as String?,
      status: json['status'] as String,
      academicYear: json['academic_year'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      photos: json['photos'] == null
          ? null
          : (json['photos'] as List)
              .map((p) => EventPhoto.fromJson(p as Map<String, dynamic>))
              .toList(),
    );
  }
}
