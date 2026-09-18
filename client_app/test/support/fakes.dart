import 'package:dio/dio.dart';

import 'package:client_app/features/events/data/events_repository.dart';
import 'package:client_app/features/suggestions/data/suggestions_repository.dart';
import 'package:client_app/models/event.dart';
import 'package:client_app/models/suggestion.dart';

/// A never-invoked [Dio] used purely to satisfy constructors whose real HTTP
/// methods are overridden away in these fakes.
Dio unusedDio() => Dio();

class FakeEventsRepository extends EventsRepository {
  FakeEventsRepository({required this.events}) : super(dio: unusedDio());

  final List<ClubEvent> events;

  @override
  Future<List<ClubEvent>> fetchEvents({String? year}) async {
    if (year == null) return events;
    return events.where((e) => e.academicYear == year).toList();
  }

  @override
  Future<ClubEvent> fetchEvent(String id) async {
    return events.firstWhere((e) => e.id == id);
  }
}

class FakeSuggestionsRepository extends SuggestionsRepository {
  FakeSuggestionsRepository({this.categories = const [], this.mine = const []})
    : super(dio: unusedDio());

  final List<String> categories;
  final List<Suggestion> mine;
  bool submitCalled = false;

  @override
  Future<List<String>> fetchCategories() async => categories;

  @override
  Future<List<Suggestion>> fetchMine() async => mine;

  @override
  Future<Suggestion> submit({
    required String category,
    required String body,
    required bool isAnonymous,
    required String name,
    required String batch,
  }) async {
    submitCalled = true;
    return Suggestion(
      id: 'new-id',
      category: category,
      body: body,
      status: 'new',
      themeId: null,
      themeLabel: null,
      sentiment: null,
      isAnonymous: isAnonymous,
      createdAt: DateTime.now(),
    );
  }
}

ClubEvent buildEvent({
  required String id,
  required String title,
  required DateTime eventDate,
  String academicYear = '2025/2026',
}) {
  return ClubEvent(
    id: id,
    title: title,
    slug: title.toLowerCase().replaceAll(' ', '-'),
    description: 'A test event',
    venue: 'Test Venue',
    eventDate: eventDate,
    coverImageUrl: null,
    status: 'published',
    academicYear: academicYear,
    createdAt: DateTime.now(),
  );
}
