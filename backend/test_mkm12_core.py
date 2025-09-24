#!/usr/bin/env python3
"""
MKM12 Core Library Test Script

This script tests the functionality of the MKM12 core library
including model creation, simulation, visualization, and utilities.
"""

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mkm12_model():
    """Test MKM12 model creation and basic functionality."""
    print("🧪 Testing MKM12 Model...")
    
    try:
        from mkm12_core.model import MKM12Model, MKM12Params
        
        # Test default model creation
        model = MKM12Model.default()
        print("✅ Default model created successfully")
        
        # Test force names
        force_names = model.get_force_names()
        print(f"✅ Force names: {force_names}")
        
        # Test mode names
        mode_names = model.get_mode_names()
        print(f"✅ Mode names: {mode_names}")
        
        # Test persona activation
        test_forces = [0.5, 0.6, 0.3, 0.2]
        personas = model.persona_activation(test_forces)
        print(f"✅ Persona activation: {personas}")
        
        # Test stability analysis
        is_stable, stability_score = model.analyze_stability(test_forces)
        print(f"✅ Stability: {is_stable}, Score: {stability_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        traceback.print_exc()
        return False


def test_mkm12_simulation():
    """Test MKM12 simulation functionality."""
    print("\n🧪 Testing MKM12 Simulation...")
    
    try:
        from mkm12_core.model import MKM12Model
        from mkm12_core.simulation import MKM12Simulator, SimulationConfig
        
        # Create model and simulator
        model = MKM12Model.default()
        simulator = MKM12Simulator(model)
        print("✅ Simulator created successfully")
        
        # Test basic simulation
        test_forces = [0.5, 0.6, 0.3, 0.2]
        result = simulator.simulate(test_forces, cfg=SimulationConfig(t1=10.0, dt=0.1))
        print(f"✅ Simulation completed: {len(result['t'])} time steps")
        
        # Test trajectory analysis
        analysis = simulator.analyze_trajectory(result)
        print(f"✅ Trajectory analysis: {analysis['overall_state']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        traceback.print_exc()
        return False


def test_mkm12_visualization():
    """Test MKM12 visualization functionality."""
    print("\n🧪 Testing MKM12 Visualization...")
    
    try:
        from mkm12_core.model import MKM12Model
        from mkm12_core.visualization import MKM12Visualizer
        
        # Create model and visualizer
        model = MKM12Model.default()
        visualizer = MKM12Visualizer(model)
        print("✅ Visualizer created successfully")
        
        # Test force gauge creation
        test_forces = [0.5, 0.6, 0.3, 0.2]
        force_viz = visualizer.create_force_gauge(test_forces)
        print("✅ Force gauge visualization created")
        
        # Test persona chart creation
        test_personas = [0.4, 0.35, 0.25]
        persona_viz = visualizer.create_persona_chart(test_personas)
        print("✅ Persona chart visualization created")
        
        # Test digital fingerprint visualization
        fingerprint_viz = visualizer.create_digital_fingerprint_visualization(
            test_forces, test_personas
        )
        print("✅ Digital fingerprint visualization created")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        traceback.print_exc()
        return False


def test_mkm12_utilities():
    """Test MKM12 utility functions."""
    print("\n🧪 Testing MKM12 Utilities...")
    
    try:
        from mkm12_core.utils import (
            analyze_persona, generate_digital_fingerprint,
            create_mkm12_narrative, validate_mkm12_data,
            export_analysis_report
        )
        
        # Test persona analysis
        test_forces = [0.5, 0.6, 0.3, 0.2]
        analysis = analyze_persona(test_forces)
        print(f"✅ Persona analysis: {analysis['analysis']['dominant_persona']}")
        
        # Test digital fingerprint generation
        test_personas = [0.4, 0.35, 0.25]
        fingerprint = generate_digital_fingerprint(test_forces, test_personas)
        print(f"✅ Digital fingerprint: {fingerprint['pattern_hash'][:16]}...")
        
        # Test narrative creation (Korean)
        korean_narrative = create_mkm12_narrative(analysis, "ko")
        print(f"✅ Korean narrative: {korean_narrative['title']}")
        
        # Test narrative creation (English)
        english_narrative = create_mkm12_narrative(analysis, "en")
        print(f"✅ English narrative: {english_narrative['title']}")
        
        # Test data validation
        is_valid, errors = validate_mkm12_data(test_forces, test_personas)
        print(f"✅ Data validation: {is_valid}")
        
        # Test report export
        report_path = export_analysis_report(analysis, "json")
        print(f"✅ Report exported: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        traceback.print_exc()
        return False


def test_mkm12_integration():
    """Test MKM12 library integration."""
    print("\n🧪 Testing MKM12 Integration...")
    
    try:
        from mkm12_core import (
            MKM12Model, MKM12Simulator, MKM12Visualizer,
            analyze_persona, generate_digital_fingerprint
        )
        
        # Test complete workflow
        model = MKM12Model.default()
        simulator = MKM12Simulator(model)
        visualizer = MKM12Visualizer(model)
        
        # Simulate
        test_forces = [0.5, 0.6, 0.3, 0.2]
        result = simulator.simulate(test_forces, cfg=SimulationConfig(t1=5.0, dt=0.1))
        
        # Analyze
        analysis = analyze_persona(test_forces)
        
        # Visualize
        force_viz = visualizer.create_force_gauge(test_forces)
        
        # Generate fingerprint
        fingerprint = generate_digital_fingerprint(test_forces, analysis['personas'].values())
        
        print("✅ Complete MKM12 workflow executed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 MKM12 Core Library Test Suite")
    print("=" * 50)
    
    tests = [
        test_mkm12_model,
        test_mkm12_simulation,
        test_mkm12_visualization,
        test_mkm12_utilities,
        test_mkm12_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MKM12 Core Library is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
