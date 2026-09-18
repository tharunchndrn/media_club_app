import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api_exception.dart';
import '../../../core/widgets/app_logo.dart';
import '../application/suggestions_providers.dart';

class SubmitSuggestionScreen extends ConsumerStatefulWidget {
  const SubmitSuggestionScreen({super.key});

  @override
  ConsumerState<SubmitSuggestionScreen> createState() => _SubmitSuggestionScreenState();
}

class _SubmitSuggestionScreenState extends ConsumerState<SubmitSuggestionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _batchController = TextEditingController();
  final _bodyController = TextEditingController();
  String? _selectedCategory;
  bool _isAnonymous = false;
  bool _submitting = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _nameController.dispose();
    _batchController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
    });
    if (_selectedCategory == null) {
      setState(() => _errorMessage = 'Please select a category.');
      return;
    }
    if (!_formKey.currentState!.validate()) return;

    setState(() => _submitting = true);
    try {
      await ref
          .read(suggestionsRepositoryProvider)
          .submit(
            category: _selectedCategory!,
            body: _bodyController.text.trim(),
            isAnonymous: _isAnonymous,
            name: _nameController.text.trim(),
            batch: _batchController.text.trim(),
          );
      if (!mounted) return;
      _bodyController.clear();
      setState(() {
        _selectedCategory = null;
        _isAnonymous = false;
        _successMessage = 'Thanks! Your suggestion has been submitted.';
      });
      ref.invalidate(mySuggestionsProvider);
    } on ApiException catch (e) {
      setState(() => _errorMessage = e.message);
    } catch (e) {
      setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final categoriesAsync = ref.watch(suggestionCategoriesProvider);

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 16,
        title: const AppLogo(height: 38),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Branded Header banner
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF0F2744), Color(0xFF1D3557)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(18),
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
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          color: const Color(0xFFE5A93C).withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.lightbulb_rounded, color: Color(0xFFE5A93C), size: 24),
                      ),
                      const SizedBox(width: 14),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Shape Media Club KIC',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 15,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              '"The Innovative Community" • Propose workshops, gear, or events',
                              style: TextStyle(
                                color: Color(0xFF94A3B8),
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                                height: 1.3,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Name
                TextFormField(
                  key: const Key('suggestion_name_field'),
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Your name',
                    prefixIcon: Icon(Icons.person_outline_rounded, size: 20),
                  ),
                  validator: (value) {
                    if ((value ?? '').trim().isEmpty) return 'Please enter your name.';
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Batch
                TextFormField(
                  key: const Key('suggestion_batch_field'),
                  controller: _batchController,
                  decoration: const InputDecoration(
                    labelText: 'Your batch',
                    prefixIcon: Icon(Icons.school_outlined, size: 20),
                  ),
                  validator: (value) {
                    if ((value ?? '').trim().isEmpty) return 'Please enter your batch.';
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Category
                categoriesAsync.when(
                  loading: () => const Center(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: CircularProgressIndicator(color: Color(0xFF0A0A0A)),
                    ),
                  ),
                  error: (err, _) => Text(
                    err is ApiException ? err.message : 'Failed to load categories',
                    style: const TextStyle(color: Color(0xFFB71C1C)),
                  ),
                  data: (categories) {
                    return DropdownButtonFormField<String>(
                      key: const Key('suggestion_category_dropdown'),
                      initialValue: _selectedCategory,
                      decoration: const InputDecoration(
                        labelText: 'Category',
                        prefixIcon: Icon(Icons.category_outlined, size: 20),
                      ),
                      items: [
                        for (final c in categories) DropdownMenuItem(value: c, child: Text(c)),
                      ],
                      onChanged: (value) => setState(() => _selectedCategory = value),
                    );
                  },
                ),
                const SizedBox(height: 16),

                // Body
                TextFormField(
                  key: const Key('suggestion_body_field'),
                  controller: _bodyController,
                  maxLines: 6,
                  maxLength: 2000,
                  decoration: const InputDecoration(
                    labelText: 'Tell us more',
                    hintText: 'Minimum 10 characters',
                    alignLabelWithHint: true,
                    prefixIcon: Padding(
                      padding: EdgeInsets.only(bottom: 100),
                      child: Icon(Icons.edit_note_rounded, size: 20),
                    ),
                  ),
                  validator: (value) {
                    final v = value?.trim() ?? '';
                    if (v.length < 10) return 'Please write at least 10 characters.';
                    if (v.length > 2000) return 'Please keep it under 2000 characters.';
                    return null;
                  },
                ),
                const SizedBox(height: 8),

                // Anonymous switch
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: Colors.black.withValues(alpha: 0.04)),
                  ),
                  child: SwitchListTile(
                    key: const Key('suggestion_anonymous_switch'),
                    contentPadding: EdgeInsets.zero,
                    title: const Text(
                      'Submit anonymously',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                    ),
                    subtitle: const Text(
                      'Your name won\'t be visible to the committee',
                      style: TextStyle(fontSize: 12, color: Color(0xFF9E9E9E)),
                    ),
                    value: _isAnonymous,
                    onChanged: (value) => setState(() => _isAnonymous = value),
                  ),
                ),

                // Error
                if (_errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFF5F5),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFFFCDD2)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline_rounded, size: 18, color: Color(0xFFB71C1C)),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            key: const Key('suggestion_error_text'),
                            style: const TextStyle(color: Color(0xFFB71C1C), fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],

                // Success
                if (_successMessage != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF1F8E9),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFC5E1A5)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.check_circle_outline_rounded, size: 18, color: Color(0xFF33691E)),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _successMessage!,
                            key: const Key('suggestion_success_text'),
                            style: const TextStyle(color: Color(0xFF33691E), fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 20),

                // Submit button
                FilledButton(
                  key: const Key('suggestion_submit_button'),
                  onPressed: _submitting ? null : _submit,
                  child: _submitting
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Submit Suggestion'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
