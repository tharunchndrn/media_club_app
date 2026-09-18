import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../models/event.dart';
import '../data/events_repository.dart';

final eventsRepositoryProvider = Provider<EventsRepository>((ref) {
  return EventsRepository(dio: ref.watch(dioProvider));
});

/// The academic year currently selected in the events feed filter. `null`
/// means "all years".
final selectedEventYearProvider = StateProvider<String?>((ref) => null);

final eventsListProvider = FutureProvider.autoDispose<List<ClubEvent>>((ref) async {
  final year = ref.watch(selectedEventYearProvider);
  final repo = ref.watch(eventsRepositoryProvider);
  return repo.fetchEvents(year: year);
});

final eventDetailProvider = FutureProvider.autoDispose.family<ClubEvent, String>((ref, id) async {
  final repo = ref.watch(eventsRepositoryProvider);
  return repo.fetchEvent(id);
});
