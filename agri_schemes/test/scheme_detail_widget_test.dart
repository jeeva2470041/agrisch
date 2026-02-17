import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:agri_schemes/screens/scheme_detail_screen.dart';
import 'package:agri_schemes/models/scheme_model.dart';
import 'package:agri_schemes/l10n/app_localizations.dart';

void main() {
  testWidgets('SchemeDetailScreen shows documents and apply button', (WidgetTester tester) async {
    final scheme = SchemeModel.fromJson({
      'scheme_name': 'PM-KISAN',
      'type': 'Income Support',
      'benefit': '₹6,000 per year',
      'description': {'en': 'Direct income support'},
      'documents_required': ['Aadhaar Card', 'Bank Account'],
      'official_link': 'https://pmkisan.gov.in',
      'states': ['All'],
      'crops': ['All'],
      'min_land': 0,
      'max_land': 100,
      'season': 'All',
      'benefit_amount': 6000,
    });

    await tester.pumpWidget(MaterialApp(
      localizationsDelegates: [AppLocalizations.delegate],
      supportedLocales: AppLocalizations.supportedLocales,
      home: SchemeDetailScreen(scheme: scheme),
    ));

    await tester.pumpAndSettle();

    // Section headers
    expect(find.text('Documents checklist'), findsOneWidget);
    expect(find.text('Eligibility'), findsOneWidget);
    expect(find.text('How to apply'), findsOneWidget);

    // Documents are listed
    expect(find.text('Aadhaar Card'), findsOneWidget);
    expect(find.text('Bank Account'), findsOneWidget);

    // Single apply button (no duplicate)
    expect(find.text('Apply online'), findsOneWidget);

    // URL hint shown
    expect(find.text('https://pmkisan.gov.in'), findsOneWidget);
  });
}
