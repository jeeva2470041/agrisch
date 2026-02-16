// Basic Flutter widget test for AgriSchemes app
// Tests landing screen rendering

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:agri_schemes/services/language_service.dart';
import 'package:agri_schemes/services/tts_service.dart';
import 'package:agri_schemes/screens/landing_screen.dart';
import 'package:agri_schemes/l10n/app_localizations.dart';

void main() {
  testWidgets('Landing screen renders correctly', (WidgetTester tester) async {
    // Create mock services for testing
    final languageService = LanguageService();
    final ttsService = TtsService();

    // Build the widget tree with providers
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider.value(value: languageService),
          ChangeNotifierProvider.value(value: ttsService),
        ],
        child: MaterialApp(
          locale: const Locale('en', 'IN'),
          supportedLocales: AppLocalizations.supportedLocales,
          localizationsDelegates: const [AppLocalizations.delegate],
          home: const LandingScreen(),
        ),
      ),
    );

    // Wait for the widget to build
    await tester.pumpAndSettle();

    // Verify landing screen is displayed
    expect(find.byType(LandingScreen), findsOneWidget);

    // Verify agriculture icon is present
    expect(find.byIcon(Icons.agriculture_rounded), findsOneWidget);
  });
}
