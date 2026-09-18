import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Bottom-nav shell wrapping the five main tabs of the student app.
class AppShell extends StatelessWidget {
  const AppShell({super.key, required this.child});

  final Widget child;

  static const _tabs = [
    ('/events', Icons.calendar_month_rounded, Icons.calendar_month_outlined, 'Events'),
    ('/committee', Icons.people_alt_rounded, Icons.people_alt_outlined, 'Committee'),
    ('/suggestions/new', Icons.lightbulb_rounded, Icons.lightbulb_outline_rounded, 'Suggest'),
    ('/suggestions/mine', Icons.mark_chat_read_rounded, Icons.mark_chat_read_outlined, 'My Ideas'),
  ];

  int _indexForLocation(String location) {
    for (var i = 0; i < _tabs.length; i++) {
      if (location.startsWith(_tabs[i].$1)) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    final currentIndex = _indexForLocation(location);
    final isDesktopWeb = MediaQuery.of(context).size.width > 700;

    final shellContent = Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          border: const Border(
            top: BorderSide(
              color: Color(0xFFE2E8F0),
              width: 1,
            ),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 16,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: NavigationBar(
          backgroundColor: Colors.white,
          elevation: 0,
          height: 68,
          indicatorColor: const Color(0xFF0F2744),
          selectedIndex: currentIndex,
          onDestinationSelected: (index) => context.go(_tabs[index].$1),
          destinations: [
            for (final tab in _tabs)
              NavigationDestination(
                icon: Icon(tab.$3, size: 22, color: const Color(0xFF64748B)),
                selectedIcon: Icon(tab.$2, size: 22, color: const Color(0xFFE5A93C)),
                label: tab.$4,
              ),
          ],
        ),
      ),
    );

    if (isDesktopWeb) {
      return Scaffold(
        backgroundColor: const Color(0xFFE8EEF5),
        body: Center(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 500),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF0F2744).withValues(alpha: 0.12),
                  blurRadius: 40,
                  spreadRadius: 2,
                  offset: const Offset(0, 12),
                ),
              ],
            ),
            clipBehavior: Clip.antiAlias,
            margin: const EdgeInsets.symmetric(vertical: 20),
            child: shellContent,
          ),
        ),
      );
    }

    return shellContent;
  }
}
