class EventPhoto {
  EventPhoto({
    required this.id,
    required this.eventId,
    required this.imageUrl,
    required this.thumbUrl,
    required this.caption,
    required this.altText,
    required this.sortOrder,
  });

  final String id;
  final String eventId;
  final String imageUrl;
  final String? thumbUrl;
  final String? caption;
  final String? altText;
  final int sortOrder;

  factory EventPhoto.fromJson(Map<String, dynamic> json) {
    return EventPhoto(
      id: json['id'] as String,
      eventId: json['event_id'] as String,
      imageUrl: json['image_url'] as String,
      thumbUrl: json['thumb_url'] as String?,
      caption: json['caption'] as String?,
      altText: json['alt_text'] as String?,
      sortOrder: json['sort_order'] as int,
    );
  }
}
