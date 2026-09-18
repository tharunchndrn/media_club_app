class CommitteeMember {
  CommitteeMember({
    required this.id,
    required this.name,
    required this.position,
    required this.academicYear,
    required this.photoUrl,
    required this.linkedinUrl,
    required this.sortOrder,
  });

  final String id;
  final String name;
  final String position;
  final String academicYear;
  final String? photoUrl;
  final String? linkedinUrl;
  final int sortOrder;

  factory CommitteeMember.fromJson(Map<String, dynamic> json) {
    return CommitteeMember(
      id: json['id'] as String,
      name: json['name'] as String,
      position: json['position'] as String,
      academicYear: json['academic_year'] as String,
      photoUrl: json['photo_url'] as String?,
      linkedinUrl: json['linkedin_url'] as String?,
      sortOrder: json['sort_order'] as int,
    );
  }
}
