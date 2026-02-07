"""
Test script for Internal Deliberation Engine
Tests all 4 scenarios: Easy, Medium, Hard, Adversarial
"""

import requests
import json

BASE_URL = "http://localhost:8000/hypeslayer"

def test_scenario(scenario_name):
    """Test a specific deliberation scenario"""
    print(f"\n{'='*80}")
    print(f"TESTING SCENARIO: {scenario_name.upper()}")
    print(f"{'='*80}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/test-deliberation",
            params={"scenario": scenario_name}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Print final decision
            decision = data["final_decision"]
            print(f"✅ ACTION: {decision['action']}")
            print(f"📊 CONFIDENCE: {decision['confidence']:.1f}%")
            print(f"⚠️  RISK: {decision['risk']:.1f}%")
            print(f"💭 REASONING: {decision['reasoning']}")
            
            if decision['refusal_reason']:
                print(f"\n🚫 REFUSAL REASON:\n{decision['refusal_reason']}")
            
            if decision['warnings']:
                print(f"\n⚠️  WARNINGS:")
                for warning in decision['warnings']:
                    print(f"   - {warning}")
            
            # Print deliberation process
            print(f"\n📋 DELIBERATION PROCESS:")
            for phase in data["deliberation_process"]:
                print(f"\n   {phase['phase']}:")
                print(f"   └─ {phase['output']}")
            
            return decision['action']
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return None


def main():
    """Run all test scenarios"""
    print("\n" + "="*80)
    print("HYPESLAYER INTERNAL DELIBERATION ENGINE - TEST SUITE")
    print("="*80)
    
    scenarios = ["easy", "medium", "hard", "adversarial"]
    expected_actions = {
        "easy": "ACT_CONFIDENTLY",
        "medium": "ACT_WITH_WARNING",
        "hard": "REFUSE",
        "adversarial": "REFUSE"
    }
    
    results = {}
    
    for scenario in scenarios:
        action = test_scenario(scenario)
        results[scenario] = action
        
        # Validate
        expected = expected_actions[scenario]
        if action == expected:
            print(f"\n✅ PASS: {scenario} → {action} (expected {expected})")
        else:
            print(f"\n❌ FAIL: {scenario} → {action} (expected {expected})")
    
    # Summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for s in scenarios if results[s] == expected_actions[s])
    total = len(scenarios)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Deliberation engine is working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED. Review the output above.")


if __name__ == "__main__":
    main()
