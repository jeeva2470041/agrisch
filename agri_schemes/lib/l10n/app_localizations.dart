import 'package:flutter/material.dart';
import 'l10n_en.dart';
import 'l10n_ta.dart';
import 'l10n_hi.dart';
import 'l10n_ml.dart';

/// Main localization class that provides translations for the app
/// Supports English (en), Tamil (ta), Hindi (hi), and Malayalam (ml)
class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  /// Helper method to get the localization instance from context
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  /// Delegate for Flutter's localization system
  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// Supported locales for this app
  static const List<Locale> supportedLocales = [
    Locale('en', 'IN'), // English (India)
    Locale('ta', 'IN'), // Tamil (India)
    Locale('hi', 'IN'), // Hindi (India)
    Locale('ml', 'IN'), // Malayalam (India)
  ];

  /// Returns the translation map based on current locale
  Map<String, String> get _localizedStrings {
    switch (locale.languageCode) {
      case 'ta':
        return tamilTranslations;
      case 'hi':
        return hindiTranslations;
      case 'ml':
        return malayalamTranslations;
      case 'en':
      default:
        return englishTranslations;
    }
  }

  /// Get translated string by key
  String translate(String key) {
    return _localizedStrings[key] ?? key;
  }

  // ========== App Title ==========
  String get appTitle => translate('appTitle');

  // ========== Language Selection Screen ==========
  String get selectLanguage => translate('selectLanguage');
  String get english => translate('english');
  String get tamil => translate('tamil');
  String get hindi => translate('hindi');
  String get malayalam => translate('malayalam');
  String get continueButton => translate('continueButton');

  // ========== Farmer Input Screen ==========
  String get farmerDetails => translate('farmerDetails');
  String get cropType => translate('cropType');
  String get selectCrop => translate('selectCrop');
  String get landSize => translate('landSize');
  String get landSizeHint => translate('landSizeHint');
  String get season => translate('season');
  String get selectSeason => translate('selectSeason');
  String get kharif => translate('kharif');
  String get rabi => translate('rabi');
  String get zaid => translate('zaid');
  String get state => translate('state');
  String get selectState => translate('selectState');
  String get searchState => translate('searchState');
  String get findSchemes => translate('findSchemes');
  String get pleaseEnterLandSize => translate('pleaseEnterLandSize');
  String get pleaseSelectAllFields => translate('pleaseSelectAllFields');

  // ========== Crop Types ==========
  String get rice => translate('rice');
  String get wheat => translate('wheat');
  String get cotton => translate('cotton');
  String get sugarcane => translate('sugarcane');
  String get pulses => translate('pulses');
  String get vegetables => translate('vegetables');
  String get coconut => translate('coconut');
  String get maize => translate('maize');
  String get groundnut => translate('groundnut');
  String get soybean => translate('soybean');
  String get jute => translate('jute');
  String get tea => translate('tea');
  String get coffee => translate('coffee');
  String get spices => translate('spices');
  String get fruits => translate('fruits');
  String get millets => translate('millets');
  String get oilseeds => translate('oilseeds');
  String get tobacco => translate('tobacco');

  // ========== States (28) ==========
  String get tamilNadu => translate('tamilNadu');
  String get andhraPradesh => translate('andhraPradesh');
  String get karnataka => translate('karnataka');
  String get maharashtra => translate('maharashtra');
  String get punjab => translate('punjab');
  String get uttarPradesh => translate('uttarPradesh');
  String get arunachalPradesh => translate('arunachalPradesh');
  String get assam => translate('assam');
  String get bihar => translate('bihar');
  String get chhattisgarh => translate('chhattisgarh');
  String get goa => translate('goa');
  String get gujarat => translate('gujarat');
  String get haryana => translate('haryana');
  String get himachalPradesh => translate('himachalPradesh');
  String get jharkhand => translate('jharkhand');
  String get kerala => translate('kerala');
  String get madhyaPradesh => translate('madhyaPradesh');
  String get manipur => translate('manipur');
  String get meghalaya => translate('meghalaya');
  String get mizoram => translate('mizoram');
  String get nagaland => translate('nagaland');
  String get odisha => translate('odisha');
  String get rajasthan => translate('rajasthan');
  String get sikkim => translate('sikkim');
  String get telangana => translate('telangana');
  String get tripura => translate('tripura');
  String get uttarakhand => translate('uttarakhand');
  String get westBengal => translate('westBengal');

  // ========== Union Territories (8) ==========
  String get andamanNicobar => translate('andamanNicobar');
  String get chandigarh => translate('chandigarh');
  String get dadraGarHaveli => translate('dadraGarHaveli');
  String get delhi => translate('delhi');
  String get jammuKashmir => translate('jammuKashmir');
  String get ladakh => translate('ladakh');
  String get lakshadweep => translate('lakshadweep');
  String get puducherry => translate('puducherry');

  // ========== Section Headers ==========
  String get statesHeader => translate('statesHeader');
  String get unionTerritoriesHeader => translate('unionTerritoriesHeader');

  // ========== Scheme Recommendation Screen ==========
  String get eligibleSchemes => translate('eligibleSchemes');
  String get noSchemesFound => translate('noSchemesFound');
  String get benefitAmount => translate('benefitAmount');
  String get listenExplanation => translate('listenExplanation');
  String get stopSpeaking => translate('stopSpeaking');
  String get backToInput => translate('backToInput');
  String get perYear => translate('perYear');
  String get perHectare => translate('perHectare');

  // ========== Scheme Names ==========
  String get pmKisan => translate('pmKisan');
  String get pmfby => translate('pmfby');
  String get kisanCreditCard => translate('kisanCreditCard');
  String get soilHealthCard => translate('soilHealthCard');
  String get nmsa => translate('nmsa');
  String get pkvy => translate('pkvy');
  String get rkvy => translate('rkvy');
  String get microIrrigation => translate('microIrrigation');

  // ========== Scheme Descriptions (Short) ==========
  String get pmKisanDesc => translate('pmKisanDesc');
  String get pmfbyDesc => translate('pmfbyDesc');
  String get kccDesc => translate('kccDesc');
  String get shcDesc => translate('shcDesc');
  String get nmsaDesc => translate('nmsaDesc');
  String get pkvyDesc => translate('pkvyDesc');
  String get rkvyDesc => translate('rkvyDesc');
  String get microIrrigationDesc => translate('microIrrigationDesc');

  // ========== Voice Explanations (Detailed) ==========
  String get pmKisanVoice => translate('pmKisanVoice');
  String get pmfbyVoice => translate('pmfbyVoice');
  String get kccVoice => translate('kccVoice');
  String get shcVoice => translate('shcVoice');
  String get nmsaVoice => translate('nmsaVoice');
  String get pkvyVoice => translate('pkvyVoice');
  String get rkvyVoice => translate('rkvyVoice');
  String get microIrrigationVoice => translate('microIrrigationVoice');
}

/// Private delegate class for localization
class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ta', 'hi', 'ml'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
