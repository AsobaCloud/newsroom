#!/usr/bin/env python3
"""
Master Testing Script
Runs all testing scripts in sequence and generates a comprehensive report.
Only sources that pass ALL tests will be recommended for production.
"""

import subprocess
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MasterTester:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    def run_script(self, script_name, description):
        """Run a testing script and capture results"""
        logger.info(f"Running {description}...")
        
        try:
            result = subprocess.run(
                ['python3', script_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per script
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {description} completed successfully")
                return {
                    'status': 'SUCCESS',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                logger.error(f"❌ {description} failed with return code {result.returncode}")
                return {
                    'status': 'FAILED',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {description} timed out")
            return {
                'status': 'TIMEOUT',
                'stdout': '',
                'stderr': 'Script timed out after 5 minutes'
            }
        except Exception as e:
            logger.error(f"💥 {description} crashed: {str(e)}")
            return {
                'status': 'CRASHED',
                'stdout': '',
                'stderr': str(e)
            }
    
    def load_test_results(self, filename):
        """Load test results from JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Results file {filename} not found")
                return None
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            return None
    
    def run_all_tests(self):
        """Run all testing scripts in sequence"""
        logger.info("🚀 Starting comprehensive testing suite...")
        
        # Test scripts to run
        test_scripts = [
            ('test_rss_feeds.py', 'RSS Feed Testing'),
            ('test_direct_scraping.py', 'Direct Scraping Testing'),
            ('test_geographic_detection.py', 'Geographic Detection Testing')
        ]
        
        # Run each test script
        for script, description in test_scripts:
            self.results[script] = self.run_script(script, description)
        
        # Load detailed results
        self.results['rss_results'] = self.load_test_results('rss_test_results.json')
        self.results['direct_scraping_results'] = self.load_test_results('direct_scraping_test_results.json')
        self.results['geographic_results'] = self.load_test_results('geographic_detection_test_results.json')
        
        return self.results
    
    def generate_master_report(self):
        """Generate comprehensive master report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Calculate overall statistics
        total_sources_tested = 0
        total_sources_passed = 0
        total_sources_failed = 0
        
        if self.results.get('rss_results'):
            rss_summary = self.results['rss_results'].get('summary', {})
            total_sources_tested += rss_summary.get('total_tested', 0)
            total_sources_passed += rss_summary.get('passed', 0)
            total_sources_failed += rss_summary.get('failed', 0)
        
        if self.results.get('direct_scraping_results'):
            direct_summary = self.results['direct_scraping_results'].get('summary', {})
            total_sources_tested += direct_summary.get('total_tested', 0)
            total_sources_passed += direct_summary.get('passed', 0)
            total_sources_failed += direct_summary.get('failed', 0)
        
        # Geographic detection accuracy
        geographic_accuracy = 0
        if self.results.get('geographic_results'):
            geo_summary = self.results['geographic_results'].get('summary', {})
            geographic_accuracy = geo_summary.get('accuracy', 0)
        
        # Overall success rate
        overall_success_rate = (total_sources_passed / total_sources_tested * 100) if total_sources_tested > 0 else 0
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        master_report = {
            'test_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'total_sources_tested': total_sources_tested,
                'total_sources_passed': total_sources_passed,
                'total_sources_failed': total_sources_failed,
                'overall_success_rate': overall_success_rate,
                'geographic_detection_accuracy': geographic_accuracy
            },
            'script_results': {
                'rss_testing': self.results.get('test_rss_feeds.py', {}),
                'direct_scraping_testing': self.results.get('test_direct_scraping.py', {}),
                'geographic_detection_testing': self.results.get('test_geographic_detection.py', {})
            },
            'detailed_results': {
                'rss_feeds': self.results.get('rss_results'),
                'direct_scraping': self.results.get('direct_scraping_results'),
                'geographic_detection': self.results.get('geographic_results')
            },
            'recommendations': recommendations,
            'production_ready_sources': self.get_production_ready_sources()
        }
        
        return master_report
    
    def generate_recommendations(self):
        """Generate comprehensive recommendations"""
        recommendations = {
            'immediate_actions': [],
            'deployment_strategy': [],
            'monitoring_plan': [],
            'risk_mitigation': []
        }
        
        # Analyze RSS feed results
        if self.results.get('rss_results'):
            rss_recs = self.results['rss_results'].get('recommendations', {})
            if rss_recs.get('deploy_immediately'):
                recommendations['immediate_actions'].append(f"Deploy {len(rss_recs['deploy_immediately'])} RSS feeds immediately")
            if rss_recs.get('deploy_with_monitoring'):
                recommendations['immediate_actions'].append(f"Deploy {len(rss_recs['deploy_with_monitoring'])} RSS feeds with monitoring")
        
        # Analyze direct scraping results
        if self.results.get('direct_scraping_results'):
            direct_recs = self.results['direct_scraping_results'].get('recommendations', {})
            if direct_recs.get('deploy_immediately'):
                recommendations['immediate_actions'].append(f"Deploy {len(direct_recs['deploy_immediately'])} direct scraping sources immediately")
            if direct_recs.get('deploy_with_monitoring'):
                recommendations['immediate_actions'].append(f"Deploy {len(direct_recs['deploy_with_monitoring'])} direct scraping sources with monitoring")
        
        # Geographic detection recommendations
        if self.results.get('geographic_results'):
            geo_recs = self.results['geographic_results'].get('recommendations', {})
            if geo_recs.get('immediate_fixes'):
                recommendations['immediate_actions'].extend(geo_recs['immediate_fixes'])
            if geo_recs.get('enhancements'):
                recommendations['deployment_strategy'].extend(geo_recs['enhancements'])
        
        # General recommendations
        recommendations['deployment_strategy'].append("Deploy sources in phases: RSS feeds first, then direct scraping")
        recommendations['deployment_strategy'].append("Monitor performance and remove any sources that start failing")
        recommendations['deployment_strategy'].append("Implement rate limiting and respectful scraping practices")
        
        recommendations['monitoring_plan'].append("Set up alerts for source failures")
        recommendations['monitoring_plan'].append("Monitor geographic distribution of articles")
        recommendations['monitoring_plan'].append("Track article relevance and quality metrics")
        
        recommendations['risk_mitigation'].append("Test sources in staging environment before production")
        recommendations['risk_mitigation'].append("Implement fallback mechanisms for critical sources")
        recommendations['risk_mitigation'].append("Regular source health checks and maintenance")
        
        return recommendations
    
    def get_production_ready_sources(self):
        """Get list of sources ready for production deployment"""
        production_sources = {
            'rss_feeds': [],
            'direct_scraping': []
        }
        
        # RSS feeds ready for production
        if self.results.get('rss_results'):
            rss_recs = self.results['rss_results'].get('recommendations', {})
            production_sources['rss_feeds'].extend(rss_recs.get('deploy_immediately', []))
            production_sources['rss_feeds'].extend(rss_recs.get('deploy_with_monitoring', []))
        
        # Direct scraping sources ready for production
        if self.results.get('direct_scraping_results'):
            direct_recs = self.results['direct_scraping_results'].get('recommendations', {})
            production_sources['direct_scraping'].extend(direct_recs.get('deploy_immediately', []))
            production_sources['direct_scraping'].extend(direct_recs.get('deploy_with_monitoring', []))
        
        return production_sources
    
    def print_summary(self, report):
        """Print a summary of the master report"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TESTING SUITE RESULTS")
        print("="*80)
        
        summary = report['test_summary']
        print(f"\n📊 OVERALL STATISTICS")
        print(f"Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"Total Sources Tested: {summary['total_sources_tested']}")
        print(f"Sources Passed: {summary['total_sources_passed']}")
        print(f"Sources Failed: {summary['total_sources_failed']}")
        print(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"Geographic Detection Accuracy: {summary['geographic_detection_accuracy']:.1f}%")
        
        print(f"\n✅ PRODUCTION READY SOURCES")
        prod_sources = report['production_ready_sources']
        print(f"RSS Feeds: {len(prod_sources['rss_feeds'])}")
        for source in prod_sources['rss_feeds']:
            print(f"  - {source}")
        print(f"Direct Scraping: {len(prod_sources['direct_scraping'])}")
        for source in prod_sources['direct_scraping']:
            print(f"  - {source}")
        
        print(f"\n🔧 RECOMMENDATIONS")
        for category, recs in report['recommendations'].items():
            if recs:
                print(f"\n{category.upper()}:")
                for rec in recs:
                    print(f"  - {rec}")
        
        print(f"\n📄 Detailed results saved to: master_test_results.json")
        print("="*80)

def main():
    """Main function"""
    tester = MasterTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Generate master report
    report = tester.generate_master_report()
    
    # Save master report
    with open('master_test_results.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    tester.print_summary(report)
    
    return report

if __name__ == "__main__":
    main()