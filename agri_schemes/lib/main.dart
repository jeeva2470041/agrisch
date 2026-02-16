import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'l10n/app_localizations.dart';
import 'services/language_service.dart';
import 'services/tts_service.dart';
import 'screens/landing_screen.dart';

/// Main entry point for the AgriSchemes application
/// This app helps farmers find eligible government schemes based on their input
void main() async {
  // Ensure Flutter bindings are initialized before async operations
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize services
  await Hive.initFlutter(); // Initialize Hive
  final languageService = LanguageService();
  final ttsService = TtsService();

  // Load saved language preference and initialize TTS
  await languageService.init();
  await ttsService.init();

  // Set TTS language to match saved preference
  await ttsService.setLanguage(languageService.ttsLanguageCode);

  runApp(
    // Wrap app with MultiProvider for dependency injection
    MultiProvider(
      providers: [
        // Language service for locale management
        ChangeNotifierProvider.value(value: languageService),
        // TTS service for voice output
        ChangeNotifierProvider.value(value: ttsService),
      ],
      child: const AgriSchemesApp(),
    ),
  );
}

/// Root widget for the AgriSchemes application
/// Handles theme, localization, and navigation setup
class AgriSchemesApp extends StatelessWidget {
  const AgriSchemesApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Watch language service for locale changes
    final languageService = Provider.of<LanguageService>(context);

    return MaterialApp(
      // App title (shown in app switcher)
      title: 'Agri Schemes',

      // Disable debug banner
      debugShowCheckedModeBanner: false,

      // Current locale from language service
      locale: languageService.currentLocale,

      // Supported locales (English and Tamil)
      supportedLocales: AppLocalizations.supportedLocales,

      // Localization delegates for Flutter widgets and custom translations
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      // App theme configuration
      theme: ThemeData(
        // Use Material 3 design
        useMaterial3: true,

        // Color scheme based on green (agriculture theme)
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32),
          brightness: Brightness.light,
        ),

        // App bar theme
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF2E7D32),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
        ),

        // Elevated button theme
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF2E7D32),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),

        // Input decoration theme
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.grey.shade50,
        ),

        // Card theme
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),

      // Start with landing screen
      home: const LandingScreen(),
    );
  }
}
