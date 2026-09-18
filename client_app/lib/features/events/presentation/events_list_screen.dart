import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/api_exception.dart';
import '../../../core/widgets/app_logo.dart';
import '../../../core/widgets/app_network_image.dart';
import '../../../models/event.dart';
import '../application/events_providers.dart';

class EventsListScreen extends ConsumerWidget {
  const EventsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(eventsListProvider);
    final selectedYear = ref.watch(selectedEventYearProvider);

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 16,
        title: const AppLogo(height: 38),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF1D3557)),
            tooltip: 'Refresh events',
            onPressed: () => ref.invalidate(eventsListProvider),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: RefreshIndicator(
        color: const Color(0xFF1D3557),
        onRefresh: () async => ref.refresh(eventsListProvider.future),
        child: eventsAsync.when(
          loading: () => const Center(
            child: CircularProgressIndicator(color: Color(0xFF1D3557)),
          ),
          error: (err, _) => _ErrorView(
            message: err is ApiException ? err.message : 'Failed to load events',
            onRetry: () => ref.invalidate(eventsListProvider),
          ),
          data: (events) {
            final years = {for (final e in events) e.academicYear}.toList()
              ..sort((a, b) => b.compareTo(a));
            final now = DateTime.now();
            final upcoming = events.where((e) => e.eventDate.isAfter(now)).toList()
              ..sort((a, b) => a.eventDate.compareTo(b.eventDate));
            final past = events.where((e) => !e.eventDate.isAfter(now)).toList()
              ..sort((a, b) => b.eventDate.compareTo(a.eventDate));

            return ListView(
              key: const Key('events_list'),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              children: [
                // Hero Banner
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF0F2744), Color(0xFF1E3A8A)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF0F2744).withValues(alpha: 0.2),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFFE5A93C).withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: const Color(0xFFE5A93C).withValues(alpha: 0.4)),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.stars_rounded, size: 13, color: Color(0xFFE5A93C)),
                                  SizedBox(width: 4),
                                  Text(
                                    'MEDIA CLUB KIC',
                                    style: TextStyle(
                                      color: Color(0xFFE5A93C),
                                      fontSize: 10,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: 0.8,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'Capturing Moments,\nCreating Legacies',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                height: 1.25,
                              ),
                            ),
                            const SizedBox(height: 6),
                            const Text(
                              'Explore club events, galas, and photography productions.',
                              style: TextStyle(
                                color: Color(0xFF94A3B8),
                                fontSize: 12,
                                fontWeight: FontWeight.w400,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Container(
                        width: 52,
                        height: 52,
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: Colors.white24),
                        ),
                        child: const Icon(Icons.camera_alt_rounded, color: Color(0xFFE5A93C), size: 28),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),

                // Year filter chips
                if (years.isNotEmpty)
                  SizedBox(
                    height: 44,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        ChoiceChip(
                          label: const Text('All years'),
                          selected: selectedYear == null,
                          selectedColor: const Color(0xFF0F2744),
                          labelStyle: TextStyle(
                            color: selectedYear == null ? Colors.white : const Color(0xFF475569),
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                          ),
                          onSelected: (_) =>
                              ref.read(selectedEventYearProvider.notifier).state = null,
                        ),
                        const SizedBox(width: 8),
                        for (final year in years) ...[
                          ChoiceChip(
                            label: Text(year),
                            selected: selectedYear == year,
                            selectedColor: const Color(0xFF0F2744),
                            labelStyle: TextStyle(
                              color: selectedYear == year ? Colors.white : const Color(0xFF475569),
                              fontWeight: FontWeight.w700,
                              fontSize: 13,
                            ),
                            onSelected: (_) =>
                                ref.read(selectedEventYearProvider.notifier).state = year,
                          ),
                          const SizedBox(width: 8),
                        ],
                      ],
                    ),
                  ),
                const SizedBox(height: 16),
                if (events.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 48),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(Icons.calendar_today_rounded, size: 48, color: Color(0xFFBDBDBD)),
                          SizedBox(height: 12),
                          Text('No events yet.', style: TextStyle(color: Color(0xFF9E9E9E))),
                        ],
                      ),
                    ),
                  ),
                // Upcoming section
                if (upcoming.isNotEmpty) ...[
                  _SectionHeader(title: 'Upcoming Events', count: upcoming.length),
                  const SizedBox(height: 12),
                  for (final event in upcoming) _EventCard(event: event),
                  const SizedBox(height: 28),
                ],
                // Past section
                if (past.isNotEmpty) ...[
                  _SectionHeader(title: 'Past Productions', count: past.length),
                  const SizedBox(height: 12),
                  for (final event in past) _EventCard(event: event),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, required this.count});
  final String title;
  final int count;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w800,
            color: Color(0xFF1D3557),
            letterSpacing: -0.3,
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: const Color(0xFFE5A93C),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            '$count',
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0A0A0A),
            ),
          ),
        ),
      ],
    );
  }
}

class _EventCard extends StatelessWidget {
  const _EventCard({required this.event});

  final ClubEvent event;

  @override
  Widget build(BuildContext context) {
    final dateStr = DateFormat.yMMMd().add_jm().format(event.eventDate.toLocal());
    final isPast = event.eventDate.isBefore(DateTime.now());

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        clipBehavior: Clip.antiAlias,
        elevation: 0,
        child: InkWell(
          onTap: () => context.push('/events/${event.id}'),
          borderRadius: BorderRadius.circular(18),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.03),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Cover image banner
                if (event.coverImageUrl != null)
                  Stack(
                    children: [
                      AppNetworkImage(
                        imageUrl: event.coverImageUrl!,
                        height: 155,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                      // Gradient scrim
                      Positioned.fill(
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: [
                                Colors.black.withValues(alpha: 0.35),
                                Colors.transparent,
                                Colors.black.withValues(alpha: 0.7),
                              ],
                            ),
                          ),
                        ),
                      ),
                      // Academic Year Badge
                      Positioned(
                        top: 12,
                        left: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFF0F2744).withValues(alpha: 0.85),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: Colors.white24),
                          ),
                          child: Text(
                            event.academicYear,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.3,
                            ),
                          ),
                        ),
                      ),
                      // Status badge
                      Positioned(
                        top: 12,
                        right: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: event.status == EventStatus.published
                                ? const Color(0xFF10B981)
                                : const Color(0xFF64748B),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            event.status.toUpperCase(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ),
                      // Date on cover
                      Positioned(
                        bottom: 12,
                        left: 12,
                        right: 12,
                        child: Row(
                          children: [
                            const Icon(Icons.calendar_today_rounded, size: 13, color: Color(0xFFE5A93C)),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                dateStr,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  )
                else
                  _imagePlaceholder(),

                // Card details
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        event.title,
                        style: const TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 17,
                          color: Color(0xFF0A0A0A),
                          letterSpacing: -0.3,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          const Icon(Icons.location_on_outlined, size: 14, color: Color(0xFFE5A93C)),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              event.venue,
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                                color: isPast ? const Color(0xFF94A3B8) : const Color(0xFF475569),
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Explore Event & Gallery',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF1D3557),
                            ),
                          ),
                          Icon(
                            Icons.arrow_forward_rounded,
                            size: 16,
                            color: const Color(0xFF1D3557).withValues(alpha: 0.8),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _imagePlaceholder() {
    return Container(
      width: double.infinity,
      height: 120,
      color: const Color(0xFFE2E8F0),
      child: const Center(
        child: Icon(Icons.camera_alt_outlined, color: Color(0xFF94A3B8), size: 36),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(24),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 20,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: const Color(0xFFEF4444).withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.wifi_off_rounded, size: 30, color: Color(0xFFEF4444)),
            ),
            const SizedBox(height: 18),
            const Text(
              'Connection Unavailable',
              style: TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F2744),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF64748B),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: const Text('Retry Connection'),
            ),
          ],
        ),
      ),
    );
  }
}
