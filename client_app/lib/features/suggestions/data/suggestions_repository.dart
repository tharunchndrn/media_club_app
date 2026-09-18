import 'package:dio/dio.dart';

import '../../../core/api_exception.dart';
import '../../../models/suggestion.dart';

class SuggestionsRepository {
  SuggestionsRepository({required Dio dio}) : _dio = dio;

  final Dio _dio;

  Future<List<String>> fetchCategories() async {
    try {
      final response = await _dio.get('/suggestions/categories');
      return (response.data as List).map((c) => c as String).toList();
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  /// There is no authenticated profile to pull name/batch from, so the
  /// submitter provides them directly on the form.
  Future<Suggestion> submit({
    required String category,
    required String body,
    required bool isAnonymous,
    required String name,
    required String batch,
  }) async {
    try {
      final response = await _dio.post(
        '/suggestions',
        data: {
          'category': category,
          'body': body,
          'is_anonymous': isAnonymous,
          'name': name,
          'batch': batch,
        },
      );
      return Suggestion.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  Future<List<Suggestion>> fetchMine() async {
    try {
      final response = await _dio.get('/suggestions/mine');
      return (response.data as List)
          .map((s) => Suggestion.fromJson(s as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }
}
