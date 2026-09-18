import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../models/committee_member.dart';
import '../data/committee_repository.dart';

final committeeRepositoryProvider = Provider<CommitteeRepository>((ref) {
  return CommitteeRepository(dio: ref.watch(dioProvider));
});

final committeeYearsProvider = FutureProvider.autoDispose<List<String>>((ref) async {
  final repo = ref.watch(committeeRepositoryProvider);
  return repo.fetchYears();
});

final selectedCommitteeYearProvider = StateProvider<String?>((ref) => null);

final committeeMembersProvider = FutureProvider.autoDispose<List<CommitteeMember>>((ref) async {
  final year = ref.watch(selectedCommitteeYearProvider);
  final repo = ref.watch(committeeRepositoryProvider);
  return repo.fetchMembers(year: year);
});
