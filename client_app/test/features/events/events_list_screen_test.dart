import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:client_app/features/events/application/events_providers.dart';
import 'package:client_app/features/events/presentation/events_list_screen.dart';

import '../../support/fakes.dart';

void main() {
  testWidgets('splits events into upcoming and past sections', (tester) async {
    final now = DateTime.now();
    final repo = FakeEventsRepository(
      events: [
        buildEvent(id: '1', title: 'Future Photowalk', eventDate: now.add(const Duration(days: 5))),
        buildEvent(id: '2', title: 'Past Quiz Night', eventDate: now.subtract(const Duration(days: 5))),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [eventsRepositoryProvider.overrideWithValue(repo)],
        child: const MaterialApp(home: EventsListScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Upcoming'), findsOneWidget);
    expect(find.text('Past'), findsOneWidget);
    expect(find.text('Future Photowalk'), findsOneWidget);
    expect(find.text('Past Quiz Night'), findsOneWidget);
  });

  testWidgets('shows an empty state when there are no events', (tester) async {
    final repo = FakeEventsRepository(events: []);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [eventsRepositoryProvider.overrideWithValue(repo)],
        child: const MaterialApp(home: EventsListScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('No events yet.'), findsOneWidget);
  });
}
