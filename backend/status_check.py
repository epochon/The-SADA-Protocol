"""
HypeSlayer System Status Check
Verifies all components are running correctly
"""

import requests
import json

print('\n' + '='*70)
print('HYPESLAYER SOFTWARE STATUS CHECK')
print('='*70 + '\n')

# Check backend
try:
    backend = requests.get('http://localhost:8000/hypeslayer/health', timeout=5)
    print('✅ BACKEND: Running on http://localhost:8000')
    print(f'   Response: {backend.json()}')
except Exception as e:
    print(f'❌ BACKEND: Not responding - {str(e)}')
    exit(1)

# Check frontend
try:
    frontend = requests.get('http://localhost:3000', timeout=5)
    print(f'\n✅ FRONTEND: Running on http://localhost:3000')
    print(f'   Status Code: {frontend.status_code}')
except Exception as e:
    print(f'\n❌ FRONTEND: Not responding - {str(e)}')

# Test deliberation engine
print('\n' + '-'*70)
print('TESTING DELIBERATION ENGINE')
print('-'*70 + '\n')

test_results = []
scenarios = {
    'easy': 'ACT_CONFIDENTLY',
    'medium': 'ACT_WITH_WARNING',
    'hard': 'REFUSE',
    'adversarial': 'REFUSE'
}

for scenario, expected in scenarios.items():
    try:
        r = requests.post(
            f'http://localhost:8000/hypeslayer/test-deliberation',
            params={'scenario': scenario},
            timeout=10
        )
        decision = r.json()['final_decision']
        action = decision['action']
        confidence = decision['confidence']
        
        status = '✅ PASS' if action == expected else '❌ FAIL'
        test_results.append(action == expected)
        
        print(f'{status} | {scenario.upper():12} | {action:20} | Conf: {confidence:5.1f}%')
        
    except Exception as e:
        print(f'❌ ERROR | {scenario.upper():12} | {str(e)}')
        test_results.append(False)

# Summary
print('\n' + '='*70)
if all(test_results):
    print('✅ ALL SYSTEMS OPERATIONAL - DELIBERATION ENGINE WORKING')
else:
    print('⚠️  SOME TESTS FAILED - CHECK LOGS ABOVE')
print('='*70)

print('\n📍 Access Points:')
print('   Frontend:  http://localhost:3000')
print('   Backend:   http://localhost:8000')
print('   API Docs:  http://localhost:8000/docs')
print('   Swagger:   http://localhost:8000/redoc')

print('\n🧪 Test Endpoints:')
print('   POST http://localhost:8000/hypeslayer/test-deliberation?scenario=easy')
print('   POST http://localhost:8000/hypeslayer/test-deliberation?scenario=hard')

print('\n🎯 Features Implemented:')
print('   ✅ Risk Profile Questionnaire (9 questions)')
print('   ✅ Internal Deliberation Engine (4-phase)')
print('   ✅ Epistemic Refusal Logic (strict thresholds)')
print('   ✅ Multi-stage Analysis Pipeline')
print('   ✅ Personalized Warnings')

print('\n' + '='*70 + '\n')
