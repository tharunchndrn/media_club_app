import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api_exception.dart';
import '../../../core/widgets/app_logo.dart';
import '../../../core/widgets/app_network_image.dart';
import '../../../models/committee_member.dart';
import '../application/committee_providers.dart';

class CommitteeScreen extends ConsumerWidget {
  const CommitteeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final yearsAsync = ref.watch(committeeYearsProvider);
    final membersAsync = ref.watch(committeeMembersProvider);
    final selectedYear = ref.watch(selectedCommitteeYearProvider);

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 16,
        title: const AppLogo(height: 38),
      ),
      body: Column(
        children: [
          // Executive Header Card
          Container(
            margin: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0F2744), Color(0xFF1D3557)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF1D3557).withValues(alpha: 0.15),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE5A93C).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.stars_rounded, color: Color(0xFFE5A93C), size: 24),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Executive Board & Leadership',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(height: 2),
                      Text(
                        '"The Innovative Community" • Guiding Media Arts',
                        style: TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Year filter chips
          yearsAsync.when(
            loading: () => const SizedBox.shrink(),
            error: (error, stackTrace) => const SizedBox.shrink(),
            data: (years) {
              if (years.isEmpty) return const SizedBox.shrink();
              return Container(
                height: 52,
                padding: const EdgeInsets.only(top: 8),
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  children: [
                    ChoiceChip(
                      label: const Text('All terms'),
                      selected: selectedYear == null,
                      selectedColor: const Color(0xFF1D3557),
                      labelStyle: TextStyle(
                        color: selectedYear == null ? Colors.white : const Color(0xFF475569),
                        fontWeight: FontWeight.w600,
                        fontSize: 12,
                      ),
                      onSelected: (_) =>
                          ref.read(selectedCommitteeYearProvider.notifier).state = null,
                    ),
                    const SizedBox(width: 8),
                    for (final year in years) ...[
                      ChoiceChip(
                        label: Text(year),
                        selected: selectedYear == year,
                        selectedColor: const Color(0xFF1D3557),
                        labelStyle: TextStyle(
                          color: selectedYear == year ? Colors.white : const Color(0xFF475569),
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                        onSelected: (_) =>
                            ref.read(selectedCommitteeYearProvider.notifier).state = year,
                      ),
                      const SizedBox(width: 8),
                    ],
                  ],
                ),
              );
            },
          ),
          // Members list
          Expanded(
            child: membersAsync.when(
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
                      err is ApiException ? err.message : 'Failed to load committee',
                      style: const TextStyle(color: Color(0xFF9E9E9E)),
                    ),
                  ],
                ),
              ),
              data: (members) {
                if (members.isEmpty) {
                  return const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.people_outline_rounded, size: 48, color: Color(0xFFBDBDBD)),
                        SizedBox(height: 12),
                        Text(
                          'No committee members found.',
                          style: TextStyle(color: Color(0xFF9E9E9E)),
                        ),
                      ],
                    ),
                  );
                }
                final byYear = <String, List<CommitteeMember>>{};
                for (final m in members) {
                  byYear.putIfAbsent(m.academicYear, () => []).add(m);
                }
                final sortedYears = byYear.keys.toList()..sort((a, b) => b.compareTo(a));

                return ListView(
                  key: const Key('committee_list'),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  children: [
                    for (final year in sortedYears) ...[
                      // Year header
                      Padding(
                        padding: const EdgeInsets.only(bottom: 10, top: 6),
                        child: Row(
                          children: [
                            Text(
                              year,
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF1D3557),
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
                                '${byYear[year]!.length}',
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0A0A0A),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      for (final member in byYear[year]!) _MemberCard(member: member),
                      const SizedBox(height: 12),
                    ],
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _MemberCard extends StatelessWidget {
  const _MemberCard({required this.member});

  final CommitteeMember member;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        padding: const EdgeInsets.all(14),
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
        child: Row(
          children: [
            // Avatar
            Container(
              width: 58,
              height: 58,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                color: const Color(0xFFF1F5F9),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: member.photoUrl != null
                  ? AppNetworkImage(
                      imageUrl: member.photoUrl!,
                      fit: BoxFit.cover,
                      placeholderIcon: Icons.person_rounded,
                    )
                  : const Icon(Icons.person_rounded, color: Color(0xFF94A3B8), size: 28),
            ),
            const SizedBox(width: 14),
            // Name & position
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    member.name,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0A0A0A),
                      letterSpacing: -0.2,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF3C7),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      member.position,
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF92400E),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // LinkedIn URL copy action
            if (member.linkedinUrl != null)
              Material(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(12),
                child: InkWell(
                  borderRadius: BorderRadius.circular(12),
                  onTap: () async {
                    await Clipboard.setData(ClipboardData(text: member.linkedinUrl!));
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('LinkedIn link copied to clipboard')),
                      );
                    }
                  },
                  child: const Padding(
                    padding: EdgeInsets.all(10),
                    child: Icon(Icons.link_rounded, size: 18, color: Color(0xFF1D3557)),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
