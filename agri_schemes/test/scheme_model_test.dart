import 'package:flutter_test/flutter_test.dart';
import 'package:agri_schemes/models/scheme_model.dart';

void main() {
  test('SchemeModel.fromJson parses fields', () {
    final json = {
      'scheme_name': 'Test Scheme',
      'type': 'Subsidy',
      'benefit': '₹10,000 per year',
      'description': {'en': 'English description'},
      'documents_required': ['Aadhaar Card', 'Land Records'],
      'official_link': 'https://example.gov.in/apply',
      'states': ['All'],
      'crops': ['All'],
      'min_land': 0,
      'max_land': 5,
      'season': 'All',
      'benefit_amount': 10000,
    };

    final s = SchemeModel.fromJson(json);

    expect(s.name, 'Test Scheme');
    expect(s.type, 'Subsidy');
    expect(s.benefit, '₹10,000 per year');
    expect(s.getDescription('en'), 'English description');
    expect(s.documentsRequired.length, 2);
    expect(s.officialLink, 'https://example.gov.in/apply');
    expect(s.states, contains('All'));
    expect(s.minLand, 0);
    expect(s.maxLand, 5);
    expect(s.benefitAmount, 10000);
  });
}
