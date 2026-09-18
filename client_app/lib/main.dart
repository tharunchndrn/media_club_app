import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import 'core/router.dart';

void main() {
  runApp(const ProviderScope(child: MediaClubApp()));
}

class MediaClubApp extends ConsumerWidget {
  const MediaClubApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    // Media Club KIC brand colors (Rich Deep Navy #0F2744, Golden Amber #E5A93C, Crisp Slate #F8FAFC)
    final colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF0F2744),
      brightness: Brightness.light,
      primary: const Color(0xFF0F2744),
      onPrimary: Colors.white,
      primaryContainer: const Color(0xFF1E3A8A),
      onPrimaryContainer: Colors.white,
      secondary: const Color(0xFFE5A93C),
      onSecondary: const Color(0xFF0A0A0A),
      secondaryContainer: const Color(0xFFFEF3C7),
      onSecondaryContainer: const Color(0xFF92400E),
      surface: const Color(0xFFF8FAFC),
      onSurface: const Color(0xFF0F172A),
      surfaceContainerHighest: const Color(0xFFF1F5F9),
      outline: const Color(0xFFE2E8F0),
      outlineVariant: const Color(0xFFCBD5E1),
      error: const Color(0xFFEF4444),
    );

    return MaterialApp.router(
      title: 'Media Club KIC',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: GoogleFonts.plusJakartaSans().fontFamily,
        colorScheme: colorScheme,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),

        // AppBar - clean frosted white with subtle border
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: const Color(0xFF0F2744),
          elevation: 0,
          scrolledUnderElevation: 1,
          shadowColor: Colors.black12,
          centerTitle: false,
          titleTextStyle: GoogleFonts.plusJakartaSans(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: const Color(0xFF0F2744),
            letterSpacing: -0.3,
          ),
          systemOverlayStyle: SystemUiOverlayStyle(
            statusBarColor: Colors.transparent,
            statusBarIconBrightness: Brightness.dark,
          ),
        ),

        // Cards - glassmorphic white panels
        cardTheme: CardThemeData(
          elevation: 0,
          color: Colors.white,
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          margin: EdgeInsets.zero,
        ),

        // Chips for year selection
        chipTheme: ChipThemeData(
          backgroundColor: Colors.white,
          selectedColor: const Color(0xFF0F2744),
          labelStyle: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Color(0xFF64748B),
          ),
          secondaryLabelStyle: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          elevation: 0,
          pressElevation: 0,
        ),

        // Navigation bar (bottom nav)
        navigationBarTheme: NavigationBarThemeData(
          backgroundColor: Colors.white,
          elevation: 0,
          height: 68,
          indicatorColor: const Color(0xFF0F2744),
          labelTextStyle: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: Color(0xFF0F2744),
                letterSpacing: 0.3,
              );
            }
            return const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: Color(0xFF64748B),
              letterSpacing: 0.3,
            );
          }),
          iconTheme: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return const IconThemeData(color: Color(0xFFE5A93C), size: 22);
            }
            return const IconThemeData(color: Color(0xFF64748B), size: 22);
          }),
        ),

        // Filled buttons
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF0F2744),
            foregroundColor: Colors.white,
            textStyle: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.3,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 15),
            elevation: 2,
            shadowColor: const Color(0xFF0F2744).withValues(alpha: 0.25),
          ),
        ),

        // Elevated buttons
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.white,
            foregroundColor: const Color(0xFF0F2744),
            elevation: 0,
            textStyle: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
              side: const BorderSide(color: Color(0xFFE2E8F0)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),

        // Input fields
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFF0A0A0A), width: 1.5),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFB71C1C)),
          ),
          labelStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: Color(0xFF9E9E9E),
          ),
          hintStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: Color(0xFFBDBDBD),
          ),
        ),

        // Dropdown
        dropdownMenuTheme: DropdownMenuThemeData(
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
            ),
          ),
        ),

        // Snackbar
        snackBarTheme: SnackBarThemeData(
          backgroundColor: const Color(0xFF0A0A0A),
          contentTextStyle: const TextStyle(
            color: Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          behavior: SnackBarBehavior.floating,
          elevation: 8,
        ),

        // Divider
        dividerTheme: DividerThemeData(
          color: Colors.black.withValues(alpha: 0.04),
          thickness: 1,
        ),

        // Switch
        switchTheme: SwitchThemeData(
          thumbColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) return const Color(0xFF0A0A0A);
            return const Color(0xFFBDBDBD);
          }),
          trackColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) return const Color(0xFF424242);
            return const Color(0xFFEEEEEE);
          }),
        ),

        // Text theme with Plus Jakarta Sans
        textTheme: GoogleFonts.plusJakartaSansTextTheme(
          const TextTheme(
            headlineLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, letterSpacing: -0.5, color: Color(0xFF0F172A)),
            headlineMedium: TextStyle(fontSize: 24, fontWeight: FontWeight.w700, letterSpacing: -0.3, color: Color(0xFF0F172A)),
            headlineSmall: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, letterSpacing: -0.2, color: Color(0xFF0F172A)),
            titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
            titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, letterSpacing: 0.1, color: Color(0xFF1E293B)),
            titleSmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
            bodyLarge: TextStyle(fontSize: 15, fontWeight: FontWeight.w400, color: Color(0xFF334155)),
            bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w400, color: Color(0xFF475569)),
            bodySmall: TextStyle(fontSize: 12, fontWeight: FontWeight.w400, color: Color(0xFF64748B)),
            labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, letterSpacing: 0.3, color: Color(0xFF0F172A)),
            labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 0.3, color: Color(0xFF475569)),
            labelSmall: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, letterSpacing: 0.5, color: Color(0xFF64748B)),
          ),
        ),
      ),
      routerConfig: router,
    );
  }
}
