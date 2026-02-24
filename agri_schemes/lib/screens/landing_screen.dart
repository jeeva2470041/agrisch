import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../services/language_service.dart';
import '../services/tts_service.dart';
import '../services/stt_service.dart';
import '../services/api_service.dart';
import 'farmer_input_screen.dart';

/// Landing Screen
/// First screen shown to the user with AgriTrust branding
class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> {
  final _apiService = ApiService();
  bool? _isConnected;
  String? _currentIp = '10.57.27.73'; // Default from code

  @override
  void initState() {
    super.initState();
    _checkConnection();
  }

  Future<void> _checkConnection() async {
    setState(() => _isConnected = null); // Loading
    final result = await _apiService.checkHealth();
    if (mounted) {
      setState(() => _isConnected = result);
    }
  }

  void _showIpDialog() {
    final controller = TextEditingController(text: _currentIp);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Configure Backend IP'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Enter the IP address of your computer running the backend server.',
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'IP Address',
                hintText: 'e.g. 192.168.1.5',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final newIp = controller.text.trim();
              if (newIp.isNotEmpty) {
                _apiService.updateBaseUrl(newIp);
                setState(() => _currentIp = newIp);
                Navigator.pop(context);
                _checkConnection();
              }
            },
            child: const Text('Save & Test'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<LanguageService>(context);
    final localizations = AppLocalizations.of(context);
    final ttsService = Provider.of<TtsService>(context, listen: false);

    return Scaffold(
      // Gradient background
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF2E7D32), // Dark green
              Color(0xFF43A047), // Lighter green
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // ─── Header: Language + Connection Status ───
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Connection Status Indicator
                    GestureDetector(
                      onTap: _showIpDialog,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: _isConnected == true
                              ? Colors.green.shade800
                              : (_isConnected == false
                                    ? Colors.red.shade900
                                    : Colors.black26),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _isConnected == true
                                  ? Icons.check_circle_rounded
                                  : (_isConnected == false
                                        ? Icons.error_rounded
                                        : Icons.sync_rounded),
                              color: Colors.white,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _isConnected == true
                                  ? 'Connected'
                                  : (_isConnected == false
                                        ? 'Server Offline'
                                        : 'Checking...'),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    // Language Dropdown
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: languageService.languageCode,
                          icon: const Icon(Icons.language, color: Colors.white),
                          dropdownColor: const Color(0xFF2E7D32),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                          onChanged: (String? newValue) async {
                            if (newValue != null) {
                              await languageService.setLanguage(newValue);
                              // Sync TTS & STT
                              await ttsService.setLanguage(
                                languageService.ttsLanguageCode,
                              );
                              if (!context.mounted) return;
                              Provider.of<SttService>(
                                context,
                                listen: false,
                              ).setLanguage(languageService.ttsLanguageCode);
                            }
                          },
                          items: const [
                            DropdownMenuItem(
                              value: 'en',
                              child: Text('English'),
                            ),
                            DropdownMenuItem(value: 'ta', child: Text('தமிழ்')),
                            DropdownMenuItem(value: 'hi', child: Text('हिंदी')),
                            DropdownMenuItem(
                              value: 'ml',
                              child: Text('മലയാളം'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(),

              // Branding Section
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.15),
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Colors.white.withValues(alpha: 0.25),
                        width: 2,
                      ),
                    ),
                    child: const Text('🌾', style: TextStyle(fontSize: 72)),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'AgriTrust',
                    style: TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      localizations
                          .appTitle, // "Agri Schemes" or localized tagline if changed
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 18,
                        color: Colors.white70,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),

              const Spacer(),

              // Get Started Button
              Padding(
                padding: const EdgeInsets.all(32.0),
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const FarmerInputScreen(),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: const Color(0xFF2E7D32),
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          localizations.continueButton,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Icon(Icons.arrow_forward_rounded, size: 24),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
