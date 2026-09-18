import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/api_exception.dart';
import '../../../core/widgets/app_network_image.dart';
import '../../../models/photo.dart';
import '../application/events_providers.dart';

class EventDetailScreen extends ConsumerWidget {
  const EventDetailScreen({super.key, required this.eventId});

  final String eventId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventAsync = ref.watch(eventDetailProvider(eventId));

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Event Details',
          style: TextStyle(
            fontWeight: FontWeight.w800,
            color: Color(0xFF1D3557),
          ),
        ),
      ),
      body: eventAsync.when(
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
                err is ApiException ? err.message : 'Failed to load event',
                style: const TextStyle(color: Color(0xFF9E9E9E)),
              ),
            ],
          ),
        ),
        data: (event) {
          final photos = event.photos ?? const <EventPhoto>[];
          final dateStr = DateFormat.yMMMMd().add_jm().format(event.eventDate.toLocal());
          return ListView(
            padding: EdgeInsets.zero,
            children: [
              // Hero cover image
              if (event.coverImageUrl != null)
                Stack(
                  children: [
                    AppNetworkImage(
                      imageUrl: event.coverImageUrl!,
                      height: 240,
                      width: double.infinity,
                      fit: BoxFit.cover,
                    ),
                    Positioned.fill(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              Colors.black.withValues(alpha: 0.2),
                              Colors.transparent,
                              Colors.black.withValues(alpha: 0.8),
                            ],
                          ),
                        ),
                      ),
                    ),
                    // Academic Year & Status Badge
                    Positioned(
                      top: 16,
                      left: 16,
                      right: 16,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0F2744).withValues(alpha: 0.9),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(color: Colors.white30),
                            ),
                            child: Text(
                              event.academicYear,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: event.status == 'published'
                                  ? const Color(0xFF10B981)
                                  : const Color(0xFF64748B),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              event.status.toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

              Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(
                      event.title,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: Color(0xFF0A0A0A),
                        letterSpacing: -0.5,
                        height: 1.25,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Info card
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.02),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          _InfoRow(
                            icon: Icons.calendar_today_rounded,
                            text: dateStr,
                            iconColor: const Color(0xFFE5A93C),
                          ),
                          const Divider(color: Color(0xFFF1F5F9), height: 20),
                          _InfoRow(
                            icon: Icons.location_on_outlined,
                            text: event.venue,
                            iconColor: const Color(0xFF1D3557),
                          ),
                          const Divider(color: Color(0xFFF1F5F9), height: 20),
                          _InfoRow(
                            icon: Icons.school_outlined,
                            text: 'Academic Term: ${event.academicYear}',
                            iconColor: const Color(0xFF64748B),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Section Heading
                    const Text(
                      'About This Production',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF1D3557),
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 10),

                    // Description
                    Text(
                      event.description,
                      style: const TextStyle(
                        fontSize: 15,
                        height: 1.65,
                        color: Color(0xFF334155),
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Gallery
                    if (photos.isNotEmpty) ...[
                      Row(
                        children: [
                          const Text(
                            'Production Gallery',
                            style: TextStyle(
                              fontSize: 18,
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
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              '${photos.length} captures',
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0A0A0A),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      GridView.builder(
                        key: const Key('event_gallery_grid'),
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: 10,
                          mainAxisSpacing: 10,
                          childAspectRatio: 1.3,
                        ),
                        itemCount: photos.length,
                        itemBuilder: (context, index) {
                          final photo = photos[index];
                          return GestureDetector(
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => _FullScreenGallery(photos: photos, initialIndex: index),
                              ),
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(14),
                              child: Stack(
                                fit: StackFit.expand,
                                children: [
                                  AppNetworkImage(
                                    imageUrl: photo.thumbUrl ?? photo.imageUrl,
                                    fit: BoxFit.cover,
                                  ),
                                  if (photo.caption != null && photo.caption!.isNotEmpty)
                                    Positioned(
                                      bottom: 0,
                                      left: 0,
                                      right: 0,
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        color: Colors.black.withValues(alpha: 0.6),
                                        child: Text(
                                          photo.caption!,
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 10,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ] else
                      Container(
                        padding: const EdgeInsets.all(28),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: const Center(
                          child: Column(
                            children: [
                              Icon(Icons.photo_library_outlined, size: 36, color: Color(0xFF94A3B8)),
                              SizedBox(height: 8),
                              Text(
                                'Gallery captures being curated.',
                                style: TextStyle(color: Color(0xFF64748B), fontSize: 13, fontWeight: FontWeight.w500),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.icon, required this.text, this.iconColor});
  final IconData icon;
  final String text;
  final Color? iconColor;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: (iconColor ?? const Color(0xFF1D3557)).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, size: 18, color: iconColor ?? const Color(0xFF1D3557)),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: Color(0xFF424242),
            ),
          ),
        ),
      ],
    );
  }
}

class _FullScreenGallery extends StatefulWidget {
  const _FullScreenGallery({required this.photos, required this.initialIndex});

  final List<EventPhoto> photos;
  final int initialIndex;

  @override
  State<_FullScreenGallery> createState() => _FullScreenGalleryState();
}

class _FullScreenGalleryState extends State<_FullScreenGallery> {
  late final PageController _controller = PageController(initialPage: widget.initialIndex);
  late int _currentPage = widget.initialIndex;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A0A0A),
        foregroundColor: Colors.white,
        title: Text(
          '${_currentPage + 1} / ${widget.photos.length}',
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: Colors.white54),
        ),
        centerTitle: true,
      ),
      body: PageView.builder(
        key: const Key('fullscreen_gallery_pageview'),
        controller: _controller,
        itemCount: widget.photos.length,
        onPageChanged: (index) => setState(() => _currentPage = index),
        itemBuilder: (context, index) {
          final photo = widget.photos[index];
          return InteractiveViewer(
            child: Center(
              child: AppNetworkImage(
                imageUrl: photo.imageUrl,
                fit: BoxFit.contain,
              ),
            ),
          );
        },
      ),
    );
  }
}
