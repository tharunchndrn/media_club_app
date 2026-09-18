import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/api_exception.dart';
import '../../../core/widgets/app_logo.dart';
import '../../../models/suggestion.dart';
import '../application/suggestions_providers.dart';

class MySuggestionsScreen extends ConsumerWidget {
  const MySuggestionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final suggestionsAsync = ref.watch(mySuggestionsProvider);

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 16,
        title: const AppLogo(height: 38),
      ),
      body: RefreshIndicator(
        color: const Color(0xFF1D3557),
        onRefresh: () async => ref.refresh(mySuggestionsProvider.future),
        child: suggestionsAsync.when(
          loading: () => const Center(
            child: CircularProgressIndicator(color: Color(0xFF1D3557)),
          ),
          error: (err, _) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline_rounded, size: 48, color: Color(0xFFBDBDBD)),
                const SizedBox(height: 12),
                Text(
                  err is ApiException ? err.message : 'Failed to load suggestions',
                  style: const TextStyle(color: Color(0xFF9E9E9E)),
                ),
              ],
            ),
          ),
          data: (suggestions) {
            if (suggestions.isEmpty) {
              return ListView(
                children: const [
                  Padding(
                    padding: EdgeInsets.only(top: 64),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(Icons.inbox_rounded, size: 48, color: Color(0xFFBDBDBD)),
                          SizedBox(height: 12),
                          Text(
                            "You haven't submitted any suggestions yet.",
                            style: TextStyle(color: Color(0xFF9E9E9E)),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            }
            return ListView.builder(
              key: const Key('my_suggestions_list'),
              padding: const EdgeInsets.all(20),
              itemCount: suggestions.length,
              itemBuilder: (context, index) => _SuggestionCard(suggestion: suggestions[index]),
            );
          },
        ),
      ),
    );
  }
}

class _SuggestionCard extends StatelessWidget {
  const _SuggestionCard({required this.suggestion});

  final Suggestion suggestion;

  Color _statusColor() {
    switch (suggestion.status) {
      case SuggestionStatus.planned:
        return const Color(0xFF33691E);
      case SuggestionStatus.declined:
        return const Color(0xFFB71C1C);
      case SuggestionStatus.reviewing:
        return const Color(0xFFE65100);
      default:
        return const Color(0xFF0A0A0A);
    }
  }

  Color _statusBgColor() {
    switch (suggestion.status) {
      case SuggestionStatus.planned:
        return const Color(0xFFF1F8E9);
      case SuggestionStatus.declined:
        return const Color(0xFFFFF5F5);
      case SuggestionStatus.reviewing:
        return const Color(0xFFFFF3E0);
      default:
        return const Color(0xFFF5F5F5);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateStr = DateFormat.yMMMd().format(suggestion.createdAt.toLocal());
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.black.withValues(alpha: 0.04)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header row
            Row(
              children: [
                // Category badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF5F5F5),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    suggestion.category,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF616161),
                      letterSpacing: 0.3,
                    ),
                  ),
                ),
                const Spacer(),
                // Status badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _statusBgColor(),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    suggestion.status,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _statusColor(),
                      letterSpacing: 0.3,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Body
            Text(
              suggestion.body,
              style: const TextStyle(
                fontSize: 14,
                height: 1.5,
                color: Color(0xFF424242),
              ),
            ),
            const SizedBox(height: 10),
            // Date
            Text(
              dateStr,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Color(0xFFBDBDBD),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
