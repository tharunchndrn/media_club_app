import 'package:dio/dio.dart';

/// A normalised, user-displayable error extracted from an API failure.
///
/// The backend returns errors as `{"detail": "..."}` (a string) or
/// `{"detail": [...]}` (FastAPI's 422 validation-error array shape). This
/// class collapses both into a single readable message, and optionally a
/// per-field map for validation errors so forms can show inline messages.
class ApiException implements Exception {
  ApiException(this.message, {this.statusCode, this.fieldErrors});

  final String message;
  final int? statusCode;

  /// Field name -> error message, populated only for 422 validation errors
  /// where the field could be determined from FastAPI's `loc` array.
  final Map<String, String>? fieldErrors;

  factory ApiException.fromDioException(DioException e) {
    final statusCode = e.response?.statusCode;
    final data = e.response?.data;

    if (data is Map && data.containsKey('detail')) {
      final detail = data['detail'];
      if (detail is String) {
        return ApiException(detail, statusCode: statusCode);
      }
      if (detail is List) {
        final messages = <String>[];
        final fieldErrors = <String, String>{};
        for (final item in detail) {
          if (item is Map) {
            final msg = item['msg']?.toString() ?? 'Invalid value';
            messages.add(msg);
            final loc = item['loc'];
            if (loc is List && loc.isNotEmpty) {
              final field = loc.last.toString();
              fieldErrors[field] = msg;
            }
          }
        }
        return ApiException(
          messages.isNotEmpty ? messages.join('\n') : 'Validation failed',
          statusCode: statusCode,
          fieldErrors: fieldErrors.isNotEmpty ? fieldErrors : null,
        );
      }
    }

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException('Connection timed out. Please try again.', statusCode: statusCode);
      case DioExceptionType.connectionError:
        return ApiException('Could not reach the server. Check your connection.', statusCode: statusCode);
      default:
        return ApiException(e.message ?? 'Something went wrong.', statusCode: statusCode);
    }
  }

  @override
  String toString() => message;
}
