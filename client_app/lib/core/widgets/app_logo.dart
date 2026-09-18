import 'package:flutter/material.dart';

class AppLogo extends StatelessWidget {
  const AppLogo({
    super.key,
    this.height = 36,
    this.showTagline = false,
  });

  final double height;
  final bool showTagline;

  @override
  Widget build(BuildContext context) {
    return Image.network(
      'http://localhost:8000/images/logo.png',
      height: height,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) {
        return Image.asset(
          'assets/images/logo.png',
          height: height,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) => _FallbackBrandLogo(height: height),
        );
      },
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Image.asset(
          'assets/images/logo.png',
          height: height,
          fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => _FallbackBrandLogo(height: height),
        );
      },
    );
  }
}

class _FallbackBrandLogo extends StatelessWidget {
  const _FallbackBrandLogo({required this.height});
  final double height;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: height * 0.85,
          height: height * 0.85,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFFE5A93C), Color(0xFF1D3557)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(height * 0.25),
          ),
          child: const Center(
            child: Icon(Icons.play_arrow_rounded, color: Colors.white, size: 18),
          ),
        ),
        const SizedBox(width: 8),
        Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'MEDIA CLUB - KIC',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w900,
                color: Color(0xFF1D3557),
                letterSpacing: 0.5,
              ),
            ),
            Text(
              '"The Innovative Community"',
              style: TextStyle(
                fontSize: 9,
                fontStyle: FontStyle.italic,
                fontWeight: FontWeight.w600,
                color: Colors.black.withValues(alpha: 0.7),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
