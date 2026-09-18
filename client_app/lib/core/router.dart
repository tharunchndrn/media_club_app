import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/committee/presentation/committee_screen.dart';
import '../features/events/presentation/event_detail_screen.dart';
import '../features/events/presentation/events_list_screen.dart';
import '../features/suggestions/presentation/my_suggestions_screen.dart';
import '../features/suggestions/presentation/submit_suggestion_screen.dart';
import 'app_shell.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/events',
    routes: [
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(path: '/events', builder: (context, state) => const EventsListScreen()),
          GoRoute(
            path: '/events/:id',
            builder: (context, state) => EventDetailScreen(eventId: state.pathParameters['id']!),
          ),
          GoRoute(path: '/committee', builder: (context, state) => const CommitteeScreen()),
          GoRoute(
            path: '/suggestions/new',
            builder: (context, state) => const SubmitSuggestionScreen(),
          ),
          GoRoute(
            path: '/suggestions/mine',
            builder: (context, state) => const MySuggestionsScreen(),
          ),
        ],
      ),
    ],
  );
});
