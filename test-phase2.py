#!/usr/bin/env python3
"""
Phase 2 AI Agents - Test Script

Tests all AI components:
1. AI Memory Layer
2. Recommendation Engine
3. Proactive Guidance
4. Predictive Analytics
5. Smart Profile Assistant

Run: python test-phase2.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Test imports
def test_imports():
    """Test that all AI modules import successfully"""
    print("\n🧪 Testing AI Package Imports...")
    
    try:
        from app.services.foundation.ai import (
            ai_memory,
            recommendation_engine,
            proactive_guidance,
            predictive_analytics,
            profile_assistant
        )
        print("   ✅ AI memory module imported")
        print("   ✅ Recommendation engine imported")
        print("   ✅ Proactive guidance imported")
        print("   ✅ Predictive analytics imported")
        print("   ✅ Profile assistant imported")
        return True, {
            "memory": ai_memory,
            "recommendations": recommendation_engine,
            "guidance": proactive_guidance,
            "predictions": predictive_analytics,
            "profile": profile_assistant
        }
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False, None


async def test_memory_layer(ai_memory):
    """Test AI memory formation"""
    print("\n🧪 Testing AI Memory Layer...")
    
    try:
        # Test memory formation (will work without Gemini API)
        user_id = "test-user-123"
        
        # Try to form memory
        memory = await ai_memory.form_memory_from_events(
            user_id=user_id,
            event_category="JOB",
            days=7
        )
        
        if memory:
            print(f"   ✅ Memory formed: {memory.memory_type}")
            print(f"   ✅ Content: {memory.content[:100]}...")
        else:
            print("   ⚠️ No memory formed (expected if insufficient events)")
        
        # Test context retrieval
        context = await ai_memory.get_user_context(user_id)
        print(f"   ✅ Context retrieved: {context['memory_count']} memories")
        print(f"   ✅ AI Ready: {context['ai_ready']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_recommendations(recommendation_engine):
    """Test recommendation engine"""
    print("\n🧪 Testing Recommendation Engine...")
    
    try:
        user_id = "test-user-123"
        
        # Test cold-start recommendations
        recs = await recommendation_engine.get_recommendations(
            user_id=user_id,
            limit=5,
            include_stretch=True
        )
        
        print(f"   ✅ Generated {len(recs)} recommendations")
        
        if recs:
            first_rec = recs[0]
            print(f"   ✅ Top recommendation score: {first_rec.recommendation_score:.1f}")
            print(f"   ✅ Match reasons: {', '.join(first_rec.match_reasons)}")
            print(f"   ✅ Confidence: {first_rec.confidence:.2f}")
        else:
            print("   ⚠️ No recommendations (expected if no jobs in database)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Recommendation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_guidance(proactive_guidance):
    """Test proactive guidance system"""
    print("\n🧪 Testing Proactive Guidance System...")
    
    try:
        user_id = "test-user-123"
        
        # Get guidance messages
        guidance_messages = await proactive_guidance.get_guidance_for_user(user_id)
        
        print(f"   ✅ Generated {len(guidance_messages)} guidance messages")
        
        for msg in guidance_messages[:3]:  # Show first 3
            print(f"   ✅ {msg.guidance_type.value}: {msg.title}")
            print(f"      Priority: {msg.priority}, Action: {msg.action_text}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Guidance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_predictions(predictive_analytics):
    """Test predictive analytics"""
    print("\n🧪 Testing Predictive Analytics...")
    
    try:
        user_id = "test-user-123"
        
        # Test churn prediction
        churn = await predictive_analytics.predict_churn(user_id)
        print(f"   ✅ Churn prediction: {churn.risk_level.value}")
        print(f"   ✅ Probability: {churn.churn_probability:.2%}")
        print(f"   ✅ Risk factors: {len(churn.risk_factors)}")
        
        # Test success prediction
        success = await predictive_analytics.predict_success(user_id)
        print(f"   ✅ Success probability: {success.success_probability:.2%}")
        if success.estimated_days_to_hire:
            print(f"   ✅ Est. days to hire: {success.estimated_days_to_hire}")
        
        # Test engagement forecast
        forecast = await predictive_analytics.forecast_engagement(user_id)
        print(f"   ✅ Engagement forecast: {forecast.predicted_weekly_events} events/week")
        print(f"   ✅ Trend: {forecast.engagement_trend}")
        
        # Test intervention timing
        timing = await predictive_analytics.optimal_intervention_time(user_id)
        print(f"   ✅ Best time: {timing['best_day']} at {timing['best_hour']}:00")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Prediction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test full AI agent workflow"""
    print("\n🧪 Testing Full AI Agent Workflow...")
    
    try:
        from app.services.foundation.ai import (
            ai_memory,
            recommendation_engine,
            proactive_guidance,
            predictive_analytics
        )
        
        user_id = "test-user-123"
        
        # Simulate AI agent decision-making workflow
        print("\n   📊 Building user intelligence profile...")
        
        # 1. Get user context from memory
        context = await ai_memory.get_user_context(user_id)
        print(f"   ✅ Context: {context['memory_count']} memories")
        
        # 2. Predict churn risk
        churn = await predictive_analytics.predict_churn(user_id)
        print(f"   ✅ Churn risk: {churn.risk_level.value}")
        
        # 3. If at risk, get guidance
        if churn.risk_level.value in ["high", "critical"]:
            guidance = await proactive_guidance.get_guidance_for_user(user_id)
            print(f"   ✅ Guidance needed: {len(guidance)} messages")
        
        # 4. Generate recommendations
        recs = await recommendation_engine.get_recommendations(user_id, limit=3)
        print(f"   ✅ Recommendations: {len(recs)} jobs")
        
        # 5. Predict success
        success = await predictive_analytics.predict_success(user_id)
        print(f"   ✅ Success probability: {success.success_probability:.2%}")
        
        print("\n   ✨ AI agent workflow complete!")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_profile_assistant(profile_assistant):
    """Test profile assistant"""
    print("\n🧪 Testing Smart Profile Assistant...")
    
    try:
        user_id = "test-user-123"
        
        # Test profile analysis
        analysis = await profile_assistant.analyze_profile(user_id)
        print(f"   ✅ Profile analyzed: {analysis.completeness_level.value}")
        print(f"   ✅ Completeness: {analysis.completeness_score:.2%}")
        print(f"   ✅ Missing fields: {len(analysis.missing_fields)}")
        print(f"   ✅ Suggestions: {len(analysis.suggestions)}")
        
        # Test data inference
        inferred = await profile_assistant.infer_missing_data(user_id)
        print(f"   ✅ Inferred {len(inferred)} fields")
        
        # Test summary generation (may fail without API key)
        summary = await profile_assistant.generate_summary(user_id)
        if summary:
            print(f"   ✅ Summary generated: {len(summary)} chars")
        else:
            print("   ⚠️ Summary generation skipped (no API key)")
        
        # Test next steps
        next_steps = await profile_assistant.suggest_next_steps(user_id)
        print(f"   ✅ Next steps: {len(next_steps)} suggestions")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Profile assistant test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all Phase 2 tests"""
    print("=" * 60)
    print("Phase 2 AI Agents - Test Suite")
    print("=" * 60)
    
    # Track results
    results = {
        "imports": False,
        "memory": False,
        "recommendations": False,
        "guidance": False,
        "predictions": False,
        "profile": False,
        "integration": False
    }
    
    # Test imports
    results["imports"], modules = test_imports()
    
    if not results["imports"]:
        print("\n❌ Import tests failed. Cannot proceed.")
        return
    
    # Test individual components
    results["memory"] = await test_memory_layer(modules["memory"])
    results["recommendations"] = await test_recommendations(modules["recommendations"])
    results["guidance"] = await test_guidance(modules["guidance"])
    results["predictions"] = await test_predictions(modules["predictions"])
    results["profile"] = await test_profile_assistant(modules["profile"])
    
    # Test integration
    results["integration"] = await test_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 2 AI agent tests passed!")
        print("\nYour AI agents are ready to:")
        print("  • Learn from user behavior")
        print("  • Generate personalized recommendations")
        print("  • Provide proactive guidance")
        print("  • Predict future outcomes")
        print("  • Optimize user profiles intelligently")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
        print("\nNote: Some failures are expected without:")
        print("  • GEMINI_API_KEY in .env")
        print("  • Supabase credentials configured")
        print("  • Test event data in database")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
