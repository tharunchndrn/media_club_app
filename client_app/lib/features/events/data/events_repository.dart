import 'package:dio/dio.dart';

import '../../../core/api_exception.dart';
import '../../../models/event.dart';

class EventsRepository {
  EventsRepository({required Dio dio}) : _dio = dio;

  final Dio _dio;

  /// Fetches events for the student app. Deliberately never sends `status`
  /// - the backend defaults to published-only when it's omitted, which is
  /// the correct behaviour for students (they should never see drafts).
  Future<List<ClubEvent>> fetchEvents({String? year}) async {
    try {
      final response = await _dio.get(
        '/events',
        queryParameters: {if (year != null && year.isNotEmpty) 'year': year},
      );
      return (response.data as List)
          .map((e) => ClubEvent.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  Future<ClubEvent> fetchEvent(String id) async {
    try {
      final response = await _dio.get('/events/$id');
      return ClubEvent.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }
}
