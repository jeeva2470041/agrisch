import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'l10n/app_localizations.dart';
import 'services/language_service.dart';
import 'services/tts_service.dart';
import 'services/stt_service.dart';
import 'services/farmer_profile_service.dart';
import 'services/theme_service.dart';
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
  final sttService = SttService();
  final farmerProfileService = FarmerProfileService();
  final themeService = ThemeService();

  // Load saved language preference and initialize TTS + STT
  await languageService.init();
  await ttsService.init();
  await sttService.init();
  await farmerProfileService.init();
  await themeService.init();

  // Set TTS/STT language to match saved preference
  await ttsService.setLanguage(languageService.ttsLanguageCode);
  sttService.setLanguage(languageService.ttsLanguageCode);

  runApp(
    // Wrap app with MultiProvider for dependency injection
    MultiProvider(
      providers: [
        // Language service for locale management
        ChangeNotifierProvider.value(value: languageService),
        // TTS service for voice output
        ChangeNotifierProvider.value(value: ttsService),
        // STT service for voice input
        ChangeNotifierProvider.value(value: sttService),
        // Farmer profile service for preferences & alerts
        ChangeNotifierProvider.value(value: farmerProfileService),
        // Theme service for dark/light mode
        ChangeNotifierProvider.value(value: themeService),
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
    final themeService = Provider.of<ThemeService>(context);
    final isDark = themeService.isDarkMode;

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

      // Theme mode from service
      themeMode: themeService.themeMode,

      // Light theme
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32),
          brightness: Brightness.light,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF2E7D32),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
        ),
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
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.grey.shade50,
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),

      // Dark theme
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0D1B0F),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1B5E20),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF43A047),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: const Color(0xFF162418),
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          color: const Color(0xFF162418),
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
