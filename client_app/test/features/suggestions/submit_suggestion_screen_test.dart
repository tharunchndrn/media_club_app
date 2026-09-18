import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:client_app/features/suggestions/application/suggestions_providers.dart';
import 'package:client_app/features/suggestions/presentation/submit_suggestion_screen.dart';

import '../../support/fakes.dart';

void main() {
  Widget wrap(FakeSuggestionsRepository repo) {
    return ProviderScope(
      overrides: [suggestionsRepositoryProvider.overrideWithValue(repo)],
      child: const MaterialApp(home: SubmitSuggestionScreen()),
    );
  }

  testWidgets('fetches categories from the API and populates the dropdown', (tester) async {
    final repo = FakeSuggestionsRepository(categories: const ['event-idea', 'feedback']);
    await tester.pumpWidget(wrap(repo));
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('suggestion_category_dropdown')));
    await tester.pumpAndSettle();

    expect(find.text('event-idea').hitTestable(), findsOneWidget);
    expect(find.text('feedback').hitTestable(), findsOneWidget);
  });

  testWidgets('blocks submission when body is shorter than 10 characters', (tester) async {
    final repo = FakeSuggestionsRepository(categories: const ['event-idea']);
    await tester.pumpWidget(wrap(repo));
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('suggestion_name_field')), 'Jane Doe');
    await tester.enterText(find.byKey(const Key('suggestion_batch_field')), '2025/2026');

    await tester.tap(find.byKey(const Key('suggestion_category_dropdown')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('event-idea').last);
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('suggestion_body_field')), 'too short');
    await tester.tap(find.byKey(const Key('suggestion_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Please write at least 10 characters.'), findsOneWidget);
    expect(repo.submitCalled, isFalse);
  });

  testWidgets('submits successfully with a valid category and body', (tester) async {
    final repo = FakeSuggestionsRepository(categories: const ['event-idea']);
    await tester.pumpWidget(wrap(repo));
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('suggestion_name_field')), 'Jane Doe');
    await tester.enterText(find.byKey(const Key('suggestion_batch_field')), '2025/2026');

    await tester.tap(find.byKey(const Key('suggestion_category_dropdown')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('event-idea').last);
    await tester.pumpAndSettle();

    await tester.enterText(
      find.byKey(const Key('suggestion_body_field')),
      'Host an inter-batch photography quiz next month.',
    );
    await tester.tap(find.byKey(const Key('suggestion_submit_button')));
    await tester.pumpAndSettle();

    expect(repo.submitCalled, isTrue);
    expect(find.byKey(const Key('suggestion_success_text')), findsOneWidget);
  });
}
