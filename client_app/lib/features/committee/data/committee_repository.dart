import 'package:dio/dio.dart';

import '../../../core/api_exception.dart';
import '../../../models/committee_member.dart';

class CommitteeRepository {
  CommitteeRepository({required Dio dio}) : _dio = dio;

  final Dio _dio;

  Future<List<CommitteeMember>> fetchMembers({String? year}) async {
    try {
      final response = await _dio.get(
        '/committee',
        queryParameters: {if (year != null && year.isNotEmpty) 'year': year},
      );
      return (response.data as List)
          .map((m) => CommitteeMember.fromJson(m as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  Future<List<String>> fetchYears() async {
    try {
      final response = await _dio.get('/committee/years');
      return (response.data as List).map((y) => y as String).toList();
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }
}
