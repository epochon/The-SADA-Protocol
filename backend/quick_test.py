import requests

scenarios = ['easy', 'medium', 'hard', 'adversarial']
expected = {
    'easy': 'ACT_CONFIDENTLY',
    'medium': 'ACT_WITH_WARNING', 
    'hard': 'REFUSE',
    'adversarial': 'REFUSE'
}

print('\n' + '='*70)
print('DELIBERATION ENGINE TEST RESULTS')
print('='*70 + '\n')

for scenario in scenarios:
    r = requests.post(f'http://localhost:8000/hypeslayer/test-deliberation?scenario={scenario}')
    data = r.json()
    decision = data['final_decision']
    
    action = decision['action']
    confidence = decision['confidence']
    risk = decision['risk']
    
    status = 'PASS' if action == expected[scenario] else 'FAIL'
    
    print(f'{status:4} | {scenario.upper():12} | {action:20} | Conf: {confidence:5.1f}% | Risk: {risk:5.1f}%')
    
    if decision.get('refusal_reason'):
        reason = decision['refusal_reason'].replace('\n', ' ')[:80]
        print(f'      Refusal: {reason}...')

print('\n' + '='*70)
print('ALL TESTS PASSED!' if all(
    requests.post(f'http://localhost:8000/hypeslayer/test-deliberation?scenario={s}').json()['final_decision']['action'] == expected[s]
    for s in scenarios
) else 'SOME TESTS FAILED')
print('='*70)
