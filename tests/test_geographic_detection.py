#!/usr/bin/env python3
"""
Geographic Detection Testing Script
Tests the enhanced geographic detection capabilities for Africa, Latin America, and MENA regions.
Validates that articles are properly tagged with correct continents and regions.
"""

import json
import re
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeographicDetectionTester:
    def __init__(self):
        self.results = []
        
        # Enhanced geographic mapping for testing
        self.geographic_mapping = {
            # Africa - Major cities and countries
            'africa': 'Africa',
            'african': 'Africa',
            'nigeria': 'Africa', 'lagos': 'Africa', 'abuja': 'Africa', 'kano': 'Africa',
            'south africa': 'Africa', 'johannesburg': 'Africa', 'cape town': 'Africa', 'durban': 'Africa',
            'kenya': 'Africa', 'nairobi': 'Africa', 'mombasa': 'Africa',
            'egypt': 'Africa', 'cairo': 'Africa', 'alexandria': 'Africa',
            'morocco': 'Africa', 'casablanca': 'Africa', 'rabat': 'Africa',
            'ghana': 'Africa', 'accra': 'Africa', 'kumasi': 'Africa',
            'ethiopia': 'Africa', 'addis ababa': 'Africa',
            'tanzania': 'Africa', 'dar es salaam': 'Africa',
            'uganda': 'Africa', 'kampala': 'Africa',
            'zimbabwe': 'Africa', 'harare': 'Africa',
            'zambia': 'Africa', 'lusaka': 'Africa',
            'botswana': 'Africa', 'gaborone': 'Africa',
            'namibia': 'Africa', 'windhoek': 'Africa',
            'senegal': 'Africa', 'dakar': 'Africa',
            'ivory coast': 'Africa', 'abidjan': 'Africa',
            'mali': 'Africa', 'bamako': 'Africa',
            'burkina faso': 'Africa', 'ouagadougou': 'Africa',
            'niger': 'Africa', 'niamey': 'Africa',
            'chad': 'Africa', 'ndjamena': 'Africa',
            'cameroon': 'Africa', 'yaounde': 'Africa',
            'central african republic': 'Africa', 'bangui': 'Africa',
            'democratic republic of congo': 'Africa', 'kinshasa': 'Africa',
            'republic of congo': 'Africa', 'brazzaville': 'Africa',
            'gabon': 'Africa', 'libreville': 'Africa',
            'equatorial guinea': 'Africa', 'malabo': 'Africa',
            'sao tome and principe': 'Africa', 'sao tome': 'Africa',
            'angola': 'Africa', 'luanda': 'Africa',
            'mozambique': 'Africa', 'maputo': 'Africa',
            'madagascar': 'Africa', 'antananarivo': 'Africa',
            'mauritius': 'Africa', 'port louis': 'Africa',
            'seychelles': 'Africa', 'victoria': 'Africa',
            'comoros': 'Africa', 'moroni': 'Africa',
            'djibouti': 'Africa', 'djibouti city': 'Africa',
            'somalia': 'Africa', 'mogadishu': 'Africa',
            'eritrea': 'Africa', 'asmara': 'Africa',
            'sudan': 'Africa', 'khartoum': 'Africa',
            'south sudan': 'Africa', 'juba': 'Africa',
            'libya': 'Africa', 'tripoli': 'Africa',
            'tunisia': 'Africa', 'tunis': 'Africa',
            'algeria': 'Africa', 'algiers': 'Africa',
            'mauritania': 'Africa', 'nouakchott': 'Africa',
            'western sahara': 'Africa', 'laayoune': 'Africa',
            'lesotho': 'Africa', 'maseru': 'Africa',
            'eswatini': 'Africa', 'mbabane': 'Africa',
            'malawi': 'Africa', 'lilongwe': 'Africa',
            'rwanda': 'Africa', 'kigali': 'Africa',
            'burundi': 'Africa', 'bujumbura': 'Africa',
            'sierra leone': 'Africa', 'freetown': 'Africa',
            'liberia': 'Africa', 'monrovia': 'Africa',
            'guinea': 'Africa', 'conakry': 'Africa',
            'guinea-bissau': 'Africa', 'bissau': 'Africa',
            'gambia': 'Africa', 'banjul': 'Africa',
            'cape verde': 'Africa', 'praia': 'Africa',
            'sao tome': 'Africa', 'sao tome and principe': 'Africa',
            
            # Latin America - Major cities and countries
            'latin america': 'Latin America',
            'south america': 'Latin America',
            'central america': 'Latin America',
            'brazil': 'Latin America', 'brasil': 'Latin America',
            'sao paulo': 'Latin America', 'rio de janeiro': 'Latin America',
            'brasilia': 'Latin America', 'belo horizonte': 'Latin America',
            'salvador': 'Latin America', 'fortaleza': 'Latin America',
            'recife': 'Latin America', 'porto alegre': 'Latin America',
            'curitiba': 'Latin America', 'manaus': 'Latin America',
            'mexico': 'Latin America', 'mexico city': 'Latin America',
            'guadalajara': 'Latin America', 'monterrey': 'Latin America',
            'puebla': 'Latin America', 'tijuana': 'Latin America',
            'argentina': 'Latin America', 'buenos aires': 'Latin America',
            'cordoba': 'Latin America', 'rosario': 'Latin America',
            'mendoza': 'Latin America', 'la plata': 'Latin America',
            'chile': 'Latin America', 'santiago': 'Latin America',
            'valparaiso': 'Latin America', 'concepcion': 'Latin America',
            'colombia': 'Latin America', 'bogota': 'Latin America',
            'medellin': 'Latin America', 'cali': 'Latin America',
            'barranquilla': 'Latin America', 'cartagena': 'Latin America',
            'peru': 'Latin America', 'lima': 'Latin America',
            'arequipa': 'Latin America', 'trujillo': 'Latin America',
            'venezuela': 'Latin America', 'caracas': 'Latin America',
            'maracaibo': 'Latin America', 'valencia': 'Latin America',
            'ecuador': 'Latin America', 'quito': 'Latin America',
            'guayaquil': 'Latin America', 'cuenca': 'Latin America',
            'bolivia': 'Latin America', 'la paz': 'Latin America',
            'santa cruz': 'Latin America', 'cochabamba': 'Latin America',
            'paraguay': 'Latin America', 'asuncion': 'Latin America',
            'uruguay': 'Latin America', 'montevideo': 'Latin America',
            'guyana': 'Latin America', 'georgetown': 'Latin America',
            'suriname': 'Latin America', 'paramaribo': 'Latin America',
            'french guiana': 'Latin America', 'cayenne': 'Latin America',
            'guatemala': 'Latin America', 'guatemala city': 'Latin America',
            'honduras': 'Latin America', 'tegucigalpa': 'Latin America',
            'el salvador': 'Latin America', 'san salvador': 'Latin America',
            'nicaragua': 'Latin America', 'managua': 'Latin America',
            'costa rica': 'Latin America', 'san jose': 'Latin America',
            'panama': 'Latin America', 'panama city': 'Latin America',
            'belize': 'Latin America', 'belmopan': 'Latin America',
            'cuba': 'Latin America', 'havana': 'Latin America',
            'jamaica': 'Latin America', 'kingston': 'Latin America',
            'haiti': 'Latin America', 'port-au-prince': 'Latin America',
            'dominican republic': 'Latin America', 'santo domingo': 'Latin America',
            'puerto rico': 'Latin America', 'san juan': 'Latin America',
            'trinidad and tobago': 'Latin America', 'port of spain': 'Latin America',
            'barbados': 'Latin America', 'bridgetown': 'Latin America',
            'bahamas': 'Latin America', 'nassau': 'Latin America',
            'dominica': 'Latin America', 'roseau': 'Latin America',
            'grenada': 'Latin America', 'saint georges': 'Latin America',
            'saint lucia': 'Latin America', 'castries': 'Latin America',
            'saint vincent and the grenadines': 'Latin America', 'kingstown': 'Latin America',
            'antigua and barbuda': 'Latin America', 'saint johns': 'Latin America',
            'saint kitts and nevis': 'Latin America', 'basseterre': 'Latin America',
            
            # MENA - Major cities and countries
            'mena': 'MENA',
            'middle east': 'MENA',
            'gulf': 'MENA',
            'saudi arabia': 'MENA', 'saudi': 'MENA',
            'riyadh': 'MENA', 'jeddah': 'MENA', 'mecca': 'MENA', 'medina': 'MENA',
            'dammam': 'MENA', 'taif': 'MENA', 'tabuk': 'MENA',
            'united arab emirates': 'MENA', 'uae': 'MENA',
            'dubai': 'MENA', 'abu dhabi': 'MENA', 'sharjah': 'MENA',
            'ajman': 'MENA', 'ras al khaimah': 'MENA', 'fujairah': 'MENA',
            'qatar': 'MENA', 'doha': 'MENA', 'al rayyan': 'MENA',
            'kuwait': 'MENA', 'kuwait city': 'MENA', 'al ahmadi': 'MENA',
            'bahrain': 'MENA', 'manama': 'MENA', 'muharraq': 'MENA',
            'oman': 'MENA', 'muscat': 'MENA', 'salalah': 'MENA',
            'yemen': 'MENA', 'sanaa': 'MENA', 'aden': 'MENA',
            'iraq': 'MENA', 'baghdad': 'MENA', 'basra': 'MENA', 'mosul': 'MENA',
            'iran': 'MENA', 'tehran': 'MENA', 'mashhad': 'MENA', 'isfahan': 'MENA',
            'syria': 'MENA', 'damascus': 'MENA', 'aleppo': 'MENA',
            'lebanon': 'MENA', 'beirut': 'MENA', 'tripoli': 'MENA',
            'jordan': 'MENA', 'amman': 'MENA', 'zarqa': 'MENA',
            'israel': 'MENA', 'jerusalem': 'MENA', 'tel aviv': 'MENA',
            'haifa': 'MENA', 'beersheba': 'MENA', 'netanya': 'MENA',
            'palestine': 'MENA', 'gaza': 'MENA', 'ramallah': 'MENA',
            'west bank': 'MENA', 'east jerusalem': 'MENA',
            'turkey': 'MENA', 'ankara': 'MENA', 'istanbul': 'MENA',
            'izmir': 'MENA', 'bursa': 'MENA', 'antalya': 'MENA',
            'cyprus': 'MENA', 'nicosia': 'MENA', 'limassol': 'MENA',
            'egypt': 'MENA', 'cairo': 'MENA', 'alexandria': 'MENA',
            'giza': 'MENA', 'luxor': 'MENA', 'aswan': 'MENA',
            'libya': 'MENA', 'tripoli': 'MENA', 'benghazi': 'MENA',
            'tunisia': 'MENA', 'tunis': 'MENA', 'sfax': 'MENA',
            'algeria': 'MENA', 'algiers': 'MENA', 'oran': 'MENA',
            'morocco': 'MENA', 'casablanca': 'MENA', 'rabat': 'MENA',
            'fes': 'MENA', 'marrakech': 'MENA', 'agadir': 'MENA',
            'mauritania': 'MENA', 'nouakchott': 'MENA', 'nouadhibou': 'MENA',
            'western sahara': 'MENA', 'laayoune': 'MENA', 'dakhla': 'MENA',
            'sudan': 'MENA', 'khartoum': 'MENA', 'port sudan': 'MENA',
            'south sudan': 'MENA', 'juba': 'MENA', 'wau': 'MENA',
            'ethiopia': 'MENA', 'addis ababa': 'MENA', 'dire dawa': 'MENA',
            'eritrea': 'MENA', 'asmara': 'MENA', 'massawa': 'MENA',
            'djibouti': 'MENA', 'djibouti city': 'MENA', 'ali sabieh': 'MENA',
            'somalia': 'MENA', 'mogadishu': 'MENA', 'hargeisa': 'MENA',
            'somaliland': 'MENA', 'berbera': 'MENA',
        }
        
    def detect_continents(self, text):
        """Detect continents from text using enhanced mapping"""
        if not text:
            return []
            
        text_lower = text.lower()
        detected_continents = set()
        
        for location, continent in self.geographic_mapping.items():
            if re.search(r'\b' + re.escape(location) + r'\b', text_lower):
                detected_continents.add(continent)
                
        return list(detected_continents)
        
    def test_geographic_detection(self, test_case):
        """Test geographic detection on a single test case"""
        result = {
            'test_name': test_case['name'],
            'text': test_case['text'],
            'expected_continents': test_case['expected_continents'],
            'detected_continents': [],
            'status': 'FAILED',
            'errors': []
        }
        
        try:
            detected = self.detect_continents(test_case['text'])
            result['detected_continents'] = detected
            
            # Check if all expected continents are detected
            expected_set = set(test_case['expected_continents'])
            detected_set = set(detected)
            
            if expected_set.issubset(detected_set):
                result['status'] = 'PASSED'
            else:
                missing = expected_set - detected_set
                result['errors'].append(f"Missing continents: {list(missing)}")
                
            # Check for false positives
            false_positives = detected_set - expected_set
            if false_positives:
                result['errors'].append(f"False positives: {list(false_positives)}")
                
        except Exception as e:
            result['errors'].append(f"Detection error: {str(e)}")
            
        return result
        
    def run_all_tests(self):
        """Run comprehensive geographic detection tests"""
        test_cases = [
            # Africa tests
            {
                'name': 'Nigeria Energy News',
                'text': 'Lagos announces new solar energy initiative in Nigeria. The project will provide renewable energy to over 100,000 homes in the African country.',
                'expected_continents': ['Africa']
            },
            {
                'name': 'South Africa Mining',
                'text': 'Johannesburg mining company reports record profits. The South African firm operates across the continent.',
                'expected_continents': ['Africa']
            },
            {
                'name': 'Kenya Technology',
                'text': 'Nairobi startup raises $50M for AI technology. The Kenyan company plans to expand across Africa.',
                'expected_continents': ['Africa']
            },
            {
                'name': 'Egypt Oil',
                'text': 'Cairo announces new oil discovery in the Red Sea. The Egyptian government expects significant economic impact.',
                'expected_continents': ['Africa']
            },
            {
                'name': 'Morocco Renewable',
                'text': 'Casablanca hosts renewable energy conference. Moroccan officials discuss solar power expansion.',
                'expected_continents': ['Africa']
            },
            {
                'name': 'Ghana Business',
                'text': 'Accra business district sees record growth. Ghanaian economy shows strong performance.',
                'expected_continents': ['Africa']
            },
            
            # Latin America tests
            {
                'name': 'Brazil Energy',
                'text': 'São Paulo announces new wind energy project. The Brazilian government invests in renewable energy.',
                'expected_continents': ['Latin America']
            },
            {
                'name': 'Mexico Oil',
                'text': 'Mexico City reports oil production increase. The Mexican state oil company sees growth.',
                'expected_continents': ['Latin America']
            },
            {
                'name': 'Argentina Gas',
                'text': 'Buenos Aires natural gas exports reach record high. Argentine energy sector shows strong performance.',
                'expected_continents': ['Latin America']
            },
            {
                'name': 'Chile Mining',
                'text': 'Santiago copper mining company reports profits. Chilean mining sector continues to grow.',
                'expected_continents': ['Latin America']
            },
            {
                'name': 'Colombia Oil',
                'text': 'Bogotá oil production increases. Colombian energy sector shows positive trends.',
                'expected_continents': ['Latin America']
            },
            {
                'name': 'Peru Mining',
                'text': 'Lima mining conference attracts international investors. Peruvian mining sector shows growth.',
                'expected_continents': ['Latin America']
            },
            
            # MENA tests
            {
                'name': 'Saudi Arabia Oil',
                'text': 'Riyadh announces new oil production targets. Saudi Arabia continues to lead OPEC.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'UAE Energy',
                'text': 'Dubai launches new solar energy initiative. The UAE continues to invest in renewable energy.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Qatar Gas',
                'text': 'Doha natural gas exports reach record levels. Qatari energy sector shows strong performance.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Kuwait Oil',
                'text': 'Kuwait City oil production increases. Kuwaiti energy sector shows positive trends.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Bahrain Energy',
                'text': 'Manama energy conference attracts international investors. Bahraini energy sector shows growth.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Oman Gas',
                'text': 'Muscat natural gas production increases. Omani energy sector shows positive trends.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Israel Technology',
                'text': 'Tel Aviv startup raises $100M for AI technology. Israeli tech sector continues to grow.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Jordan Energy',
                'text': 'Amman announces new renewable energy project. Jordanian government invests in solar power.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Lebanon Business',
                'text': 'Beirut business district sees record growth. Lebanese economy shows strong performance.',
                'expected_continents': ['MENA']
            },
            {
                'name': 'Turkey Energy',
                'text': 'Istanbul energy conference attracts international investors. Turkish energy sector shows growth.',
                'expected_continents': ['MENA']
            },
            
            # Multi-continent tests
            {
                'name': 'Global Energy Summit',
                'text': 'Energy summit brings together leaders from Saudi Arabia, Brazil, and South Africa. The conference focuses on renewable energy across the Middle East, Latin America, and Africa.',
                'expected_continents': ['MENA', 'Latin America', 'Africa']
            },
            {
                'name': 'International Oil Trade',
                'text': 'Oil trade between Nigeria, Mexico, and Kuwait reaches record levels. The three countries represent Africa, Latin America, and the Middle East.',
                'expected_continents': ['Africa', 'Latin America', 'MENA']
            },
            
            # Edge cases
            {
                'name': 'No Geographic References',
                'text': 'Technology company announces new AI product. The innovation will revolutionize the industry.',
                'expected_continents': []
            },
            {
                'name': 'Ambiguous References',
                'text': 'The company operates in the middle of the country. The business is located in the center of the region.',
                'expected_continents': []
            },
            {
                'name': 'Partial Matches',
                'text': 'The company is based in New York, not New York City. The business operates in the United States.',
                'expected_continents': []
            }
        ]
        
        logger.info(f"Running {len(test_cases)} geographic detection tests...")
        
        for test_case in test_cases:
            result = self.test_geographic_detection(test_case)
            self.results.append(result)
            
        return self.results
        
    def generate_report(self):
        """Generate comprehensive test report"""
        passed = [r for r in self.results if r['status'] == 'PASSED']
        failed = [r for r in self.results if r['status'] == 'FAILED']
        
        # Calculate accuracy metrics
        total_tests = len(self.results)
        accuracy = len(passed) / total_tests * 100 if total_tests > 0 else 0
        
        # Analyze by region
        region_analysis = {
            'Africa': {'passed': 0, 'failed': 0, 'total': 0},
            'Latin America': {'passed': 0, 'failed': 0, 'total': 0},
            'MENA': {'passed': 0, 'failed': 0, 'total': 0},
            'Multi-continent': {'passed': 0, 'failed': 0, 'total': 0},
            'Edge cases': {'passed': 0, 'failed': 0, 'total': 0}
        }
        
        for result in self.results:
            if 'Africa' in result['test_name']:
                region = 'Africa'
            elif 'Latin America' in result['test_name'] or 'Brazil' in result['test_name'] or 'Mexico' in result['test_name']:
                region = 'Latin America'
            elif 'MENA' in result['test_name'] or 'Saudi' in result['test_name'] or 'UAE' in result['test_name']:
                region = 'MENA'
            elif 'Global' in result['test_name'] or 'International' in result['test_name']:
                region = 'Multi-continent'
            else:
                region = 'Edge cases'
                
            region_analysis[region]['total'] += 1
            if result['status'] == 'PASSED':
                region_analysis[region]['passed'] += 1
            else:
                region_analysis[region]['failed'] += 1
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': len(passed),
                'failed': len(failed),
                'accuracy': accuracy
            },
            'region_analysis': region_analysis,
            'passed_tests': passed,
            'failed_tests': failed,
            'recommendations': self.get_recommendations()
        }
        
        return report
        
    def get_recommendations(self):
        """Get recommendations for improving geographic detection"""
        failed_tests = [r for r in self.results if r['status'] == 'FAILED']
        
        recommendations = {
            'immediate_fixes': [],
            'enhancements': [],
            'monitoring': []
        }
        
        # Analyze common failure patterns
        missing_continents = {}
        false_positives = {}
        
        for result in failed_tests:
            for error in result['errors']:
                if 'Missing continents' in error:
                    missing = error.split(': ')[1].strip('[]').replace("'", '')
                    if missing not in missing_continents:
                        missing_continents[missing] = 0
                    missing_continents[missing] += 1
                elif 'False positives' in error:
                    false_pos = error.split(': ')[1].strip('[]').replace("'", '')
                    if false_pos not in false_positives:
                        false_positives[false_pos] = 0
                    false_positives[false_pos] += 1
        
        # Generate recommendations based on failure patterns
        if missing_continents:
            recommendations['immediate_fixes'].append(f"Add missing continent mappings: {list(missing_continents.keys())}")
            
        if false_positives:
            recommendations['immediate_fixes'].append(f"Fix false positive detections: {list(false_positives.keys())}")
            
        if len(failed_tests) > 0:
            recommendations['enhancements'].append("Improve geographic keyword matching with better regex patterns")
            recommendations['enhancements'].append("Add more specific location mappings for edge cases")
            
        recommendations['monitoring'].append("Monitor geographic detection accuracy in production")
        recommendations['monitoring'].append("Track false positive and false negative rates")
        
        return recommendations

def main():
    """Main testing function"""
    tester = GeographicDetectionTester()
    
    print("🔍 Starting Geographic Detection Testing...")
    print("=" * 50)
    
    results = tester.run_all_tests()
    report = tester.generate_report()
    
    # Save detailed results
    os.makedirs('results', exist_ok=True)
    with open('results/geographic_detection_test_results.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Accuracy: {report['summary']['accuracy']:.1f}%")
    
    print(f"\n📈 REGION ANALYSIS")
    for region, stats in report['region_analysis'].items():
        if stats['total'] > 0:
            accuracy = stats['passed'] / stats['total'] * 100
            print(f"{region}: {stats['passed']}/{stats['total']} ({accuracy:.1f}%)")
    
    print(f"\n✅ PASSED TESTS:")
    for test in report['passed_tests']:
        print(f"  - {test['test_name']}")
        
    print(f"\n❌ FAILED TESTS:")
    for test in report['failed_tests']:
        print(f"  - {test['test_name']}: {', '.join(test['errors'])}")
    
    print(f"\n🔧 RECOMMENDATIONS:")
    for category, recs in report['recommendations'].items():
        if recs:
            print(f"\n{category.upper()}:")
            for rec in recs:
                print(f"  - {rec}")
    
    print(f"\n📄 Detailed results saved to: results/geographic_detection_test_results.json")
    
    return report

if __name__ == "__main__":
    main()