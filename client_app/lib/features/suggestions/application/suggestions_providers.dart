import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../models/suggestion.dart';
import '../data/suggestions_repository.dart';

final suggestionsRepositoryProvider = Provider<SuggestionsRepository>((ref) {
  return SuggestionsRepository(dio: ref.watch(dioProvider));
});

final suggestionCategoriesProvider = FutureProvider.autoDispose<List<String>>((ref) async {
  final repo = ref.watch(suggestionsRepositoryProvider);
  return repo.fetchCategories();
});

final mySuggestionsProvider =
    FutureProvider.autoDispose<List<Suggestion>>((ref) async {
  final repo = ref.watch(suggestionsRepositoryProvider);
  return repo.fetchMine();
});
