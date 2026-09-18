import 'package:dio/dio.dart';

import 'api_config.dart';

/// Builds a [Dio] instance pointed at the Media Club API.
Dio buildApiClient() {
  final dio = Dio(
    BaseOptions(
      baseUrl: kApiBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      contentType: 'application/json',
    ),
  );

  return dio;
}
