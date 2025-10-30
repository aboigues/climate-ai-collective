#!/usr/bin/env python3
"""
CLI wrapper for the validator service.

This script provides a command-line interface to the validator,
compatible with the GitHub Actions workflow.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate a climate proposal"
    )
    parser.add_argument(
        "--proposal",
        required=True,
        help="Input JSON file with the proposal"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file for validation results"
    )
    return parser.parse_args()


def load_proposal(proposal_path: str) -> Dict[str, Any]:
    """Load the proposal from JSON file."""
    with open(proposal_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def adapt_proposal_format(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt the proposal format to match what the validator expects.

    The validator expects certain fields that may not be in the generated proposal,
    so we need to map or create them.
    """
    # Extract values from the content structure
    content = proposal.get("content", {})

    adapted = {
        "id": proposal.get("id", "unknown"),
        "title": proposal.get("title", ""),
        "domain": proposal.get("domain", "unknown"),
        "description": proposal.get("description", ""),
        "co2_reduction_estimate": content.get("impact", {}).get("co2_reduction_tonnes_yearly", 0),
        "implementation_cost": content.get("budget", {}).get("total_chf", 0),
        "timeline": content.get("implementation", {}).get("total_duration_years", 1) * 12,  # Convert to months
        "stakeholders": content.get("stakeholders", []),
        "prerequisites": ["Budget approved", "Stakeholder consultation"],  # Default values
        "risks": [risk.get("description", "") for risk in content.get("risks", [])],
        "scientific_references": ["IPCC AR6", "Local emission factors"]  # Default values
    }

    return adapted


def simple_validation(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a simple validation without async/LLM dependencies.

    This is a synchronous version that can run in the CI environment.
    """
    issues = []
    recommendations = []
    score = 10.0

    # Check required fields
    required_fields = [
        "id", "title", "domain", "description",
        "co2_reduction_estimate", "implementation_cost", "timeline"
    ]

    for field in required_fields:
        if not proposal.get(field):
            issues.append(f"Missing or empty field: {field}")
            score -= 1.0

    # Check CO2 reduction is positive
    if proposal.get("co2_reduction_estimate", 0) <= 0:
        issues.append("CO2 reduction estimate must be positive")
        score -= 2.0

    # Check implementation cost is reasonable
    cost = proposal.get("implementation_cost", 0)
    if cost <= 0:
        issues.append("Implementation cost must be positive")
        score -= 2.0
    elif cost > 1_000_000_000:  # 1 billion CHF
        recommendations.append("Very high implementation cost - consider splitting into phases")

    # Check timeline is reasonable
    timeline = proposal.get("timeline", 0)
    if timeline <= 0:
        issues.append("Timeline must be positive")
        score -= 1.0
    elif timeline > 120:  # 10 years
        recommendations.append("Very long timeline - consider shorter milestones")

    # Calculate cost per tonne CO2
    co2_10y = proposal.get("co2_reduction_estimate", 1) * 10  # 10 years
    cost_per_tonne = cost / co2_10y if co2_10y > 0 else float('inf')

    if cost_per_tonne > 500:
        recommendations.append(f"High cost per tonne CO2: {cost_per_tonne:.2f} CHF/tonne")

    # Check stakeholders
    if not proposal.get("stakeholders"):
        recommendations.append("No stakeholders identified - consider adding key actors")

    # Check risks
    if not proposal.get("risks"):
        recommendations.append("No risks identified - consider potential obstacles")

    # Ensure score is in [0, 10]
    score = max(0.0, min(10.0, score))

    # Proposal is valid if score >= 7 and no critical issues
    is_valid = score >= 7.0 and len(issues) < 3

    return {
        "valid": is_valid,
        "score": round(score, 1),
        "issues": issues,
        "recommendations": recommendations,
        "metadata": {
            "validation_method": "simple",
            "validated_at": datetime.utcnow().isoformat() + "Z",
            "validator_version": "1.0"
        },
        "details": {
            "cost_per_tonne_co2": round(cost_per_tonne, 2) if cost_per_tonne != float('inf') else "N/A",
            "timeline_months": timeline,
            "annual_co2_reduction": proposal.get("co2_reduction_estimate", 0)
        }
    }


def export_validation(validation: Dict[str, Any], output_path: str):
    """Export validation results to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation, f, indent=2, ensure_ascii=False)

    print(f"💾 Validation results exported to: {output_path}")


def print_summary(validation: Dict[str, Any]):
    """Print a summary of the validation results."""
    print("\n" + "="*60)
    print("✅ VALIDATION SUMMARY")
    print("="*60)

    status = "✅ VALID" if validation["valid"] else "❌ INVALID"
    print(f"\nStatus: {status}")
    print(f"Score: {validation['score']}/10")

    if validation["issues"]:
        print(f"\n⚠️  Issues ({len(validation['issues'])}):")
        for issue in validation["issues"]:
            print(f"   - {issue}")

    if validation["recommendations"]:
        print(f"\n💡 Recommendations ({len(validation['recommendations'])}):")
        for rec in validation["recommendations"]:
            print(f"   - {rec}")

    print("\n" + "="*60)


def main():
    """Main entry point."""
    args = parse_args()

    try:
        print(f"🔍 Validating proposal from: {args.proposal}")

        # Load the proposal
        proposal = load_proposal(args.proposal)

        # Adapt format if needed
        adapted_proposal = adapt_proposal_format(proposal)

        # Perform validation
        validation = simple_validation(adapted_proposal)

        # Export results
        export_validation(validation, args.output)

        # Print summary
        print_summary(validation)

        # Exit with appropriate code
        if validation["valid"]:
            print("\n✨ Validation passed!")
            return 0
        else:
            print("\n❌ Validation failed!")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
