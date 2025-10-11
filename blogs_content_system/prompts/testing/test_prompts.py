#!/usr/bin/env python3
"""
Prompt Testing Framework

Test and compare different prompt versions to see which performs better.

Usage:
    # Test a single mode
    python test_prompts.py --mode quick

    # Test specific topic
    python test_prompts.py --mode quick --topic productivity_remote

    # Compare two prompt versions
    python test_prompts.py --compare quick_v1 quick_v2

    # Compare quick vs thoughtout mode
    python test_prompts.py --compare quick thoughtout

    # Run all tests and generate report
    python test_prompts.py --full-suite
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import importlib.util

# Add parent directory to path to import prompt modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.agents import Agent

# Directories
RESULTS_DIR = Path(__file__).parent / "results"
ARCHIVE_DIR = Path(__file__).parent.parent / "archive"
MODES_DIR = Path(__file__).parent.parent / "modes"
TEST_CASES_FILE = Path(__file__).parent / "test_cases.json"

RESULTS_DIR.mkdir(exist_ok=True)


def load_test_cases():
    """Load test cases from JSON"""
    with open(TEST_CASES_FILE, 'r') as f:
        return json.load(f)


def load_prompt_module(mode_or_version):
    """
    Load a prompt module dynamically

    Args:
        mode_or_version: Can be:
            - "quick" or "thoughtout" (loads from modes/)
            - "quick_v1", "thoughtout_v2" (loads from archive/)
            - Path to a .py file

    Returns:
        The PROMPT string from the module
    """
    # Handle direct file path
    if mode_or_version.endswith('.py'):
        path = Path(mode_or_version)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {mode_or_version}")

        spec = importlib.util.spec_from_file_location("prompt_module", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.PROMPT if hasattr(module, 'PROMPT') else module.BLOG_WRITER_INSTRUCTIONS

    # Handle version strings (e.g., "quick_v1")
    if '_v' in mode_or_version:
        # Look in archive
        files = list(ARCHIVE_DIR.glob(f"{mode_or_version}*.py"))
        if not files:
            raise FileNotFoundError(f"Archive version not found: {mode_or_version}")

        spec = importlib.util.spec_from_file_location("prompt_module", files[0])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.PROMPT if hasattr(module, 'PROMPT') else module.BLOG_WRITER_INSTRUCTIONS

    # Handle current modes (e.g., "quick", "thoughtout")
    mode_file = MODES_DIR / f"{mode_or_version}_mode.py"
    if not mode_file.exists():
        raise FileNotFoundError(f"Mode not found: {mode_or_version}")

    spec = importlib.util.spec_from_file_location("prompt_module", mode_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PROMPT


def generate_blog(prompt, topic, model="gemini-2.0-flash-exp"):
    """
    Generate a blog using the given prompt and topic

    Args:
        prompt: The instruction prompt
        topic: The blog topic
        model: The model to use

    Returns:
        dict with blog content and metadata
    """
    agent = Agent(
        name="test_blog_writer",
        model=model,
        instruction=prompt
    )

    start_time = datetime.now()

    try:
        # For thoughtout mode, we need to handle the conversation
        # For quick mode, just send the topic
        response = agent.send_message(topic)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "content": response.content,
            "duration_seconds": duration,
            "timestamp": start_time.isoformat(),
            "model": model,
            "success": True
        }

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "content": None,
            "duration_seconds": duration,
            "timestamp": start_time.isoformat(),
            "model": model,
            "success": False,
            "error": str(e)
        }


def evaluate_blog(blog_content, test_case, evaluation_criteria):
    """
    Evaluate a blog against criteria using AI

    Returns:
        dict with scores and feedback
    """
    # Use AI to evaluate the blog
    evaluator = Agent(
        name="blog_evaluator",
        model="gemini-2.0-flash-exp",
        instruction=f"""You are an expert blog evaluator.

        Evaluate the blog based on these criteria:
        {json.dumps(evaluation_criteria, indent=2)}

        For each criterion, provide:
        - score (0-100)
        - feedback (what's good, what's missing)

        Return JSON format:
        {{
            "scores": {{
                "structure": {{"score": 85, "feedback": "..."}},
                "depth": {{"score": 90, "feedback": "..."}},
                ...
            }},
            "overall_score": 87,
            "summary": "Overall assessment..."
        }}
        """
    )

    prompt = f"""Evaluate this blog written for the topic: "{test_case['topic']}"

Expected qualities:
{json.dumps(test_case['expected_qualities'], indent=2)}

BLOG CONTENT:
{blog_content}

Provide detailed evaluation."""

    try:
        response = evaluator.send_message(prompt)
        # Parse JSON from response
        # This is simplified - in reality you'd want more robust parsing
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Could not parse evaluation"}
    except Exception as e:
        return {"error": str(e)}


def compare_blogs(blog1, blog2, topic, comparison_prompts):
    """
    Compare two blogs using AI

    Returns:
        dict with comparison results
    """
    comparator = Agent(
        name="blog_comparator",
        model="gemini-2.0-flash-exp",
        instruction="""You are an expert content analyst comparing two blog posts.

        For each comparison dimension, choose which blog is better and explain why.
        Be specific about what makes one better than the other.

        Return JSON format:
        {
            "comparisons": [
                {
                    "dimension": "engagement",
                    "winner": "blog_a" or "blog_b",
                    "reasoning": "..."
                }
            ],
            "overall_winner": "blog_a" or "blog_b",
            "summary": "..."
        }
        """
    )

    prompt = f"""Compare these two blogs written for topic: "{topic}"

BLOG A:
{blog1}

BLOG B:
{blog2}

Compare on these dimensions:
{json.dumps(comparison_prompts, indent=2)}

Which is better overall and why?"""

    try:
        response = comparator.send_message(prompt)
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Could not parse comparison"}
    except Exception as e:
        return {"error": str(e)}


def test_single_mode(mode, topic_id=None, save_results=True):
    """Test a single prompt mode on one or all topics"""
    print(f"\n{'='*60}")
    print(f"Testing mode: {mode}")
    print(f"{'='*60}\n")

    data = load_test_cases()
    prompt = load_prompt_module(mode)

    # Filter to specific topic if requested
    topics = data['test_topics']
    if topic_id:
        topics = [t for t in topics if t['id'] == topic_id]
        if not topics:
            print(f"Error: Topic '{topic_id}' not found")
            return

    results = {
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "test_results": []
    }

    for test_case in topics:
        print(f"\nTesting topic: {test_case['topic']}")
        print(f"Category: {test_case['category']} | Difficulty: {test_case['difficulty']}")

        # Generate blog
        blog = generate_blog(prompt, test_case['topic'])

        if not blog['success']:
            print(f"❌ Generation failed: {blog['error']}")
            results['test_results'].append({
                "test_case": test_case,
                "blog": blog,
                "evaluation": None
            })
            continue

        print(f"✅ Generated in {blog['duration_seconds']:.1f}s")
        print(f"Length: {len(blog['content'])} characters")

        # Evaluate blog
        print("Evaluating...")
        evaluation = evaluate_blog(blog['content'], test_case, data['evaluation_criteria'])

        if 'error' not in evaluation:
            print(f"📊 Overall Score: {evaluation.get('overall_score', 'N/A')}/100")
        else:
            print(f"⚠️  Evaluation error: {evaluation['error']}")

        results['test_results'].append({
            "test_case": test_case,
            "blog": blog,
            "evaluation": evaluation
        })

    # Save results
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = RESULTS_DIR / f"{mode}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")

    return results


def compare_modes(mode1, mode2, topic_id=None, save_results=True):
    """Compare two prompt versions"""
    print(f"\n{'='*60}")
    print(f"Comparing: {mode1} vs {mode2}")
    print(f"{'='*60}\n")

    data = load_test_cases()
    prompt1 = load_prompt_module(mode1)
    prompt2 = load_prompt_module(mode2)

    # Filter to specific topic if requested
    topics = data['test_topics']
    if topic_id:
        topics = [t for t in topics if t['id'] == topic_id]

    results = {
        "mode1": mode1,
        "mode2": mode2,
        "timestamp": datetime.now().isoformat(),
        "comparisons": []
    }

    for test_case in topics:
        print(f"\n{'='*50}")
        print(f"Topic: {test_case['topic']}")
        print(f"{'='*50}")

        # Generate both blogs
        print(f"Generating with {mode1}...")
        blog1 = generate_blog(prompt1, test_case['topic'])

        print(f"Generating with {mode2}...")
        blog2 = generate_blog(prompt2, test_case['topic'])

        if not blog1['success'] or not blog2['success']:
            print("❌ One or both generations failed")
            continue

        print(f"✅ Both generated successfully")
        print(f"   {mode1}: {len(blog1['content'])} chars in {blog1['duration_seconds']:.1f}s")
        print(f"   {mode2}: {len(blog2['content'])} chars in {blog2['duration_seconds']:.1f}s")

        # Compare
        print("Comparing blogs...")
        comparison = compare_blogs(
            blog1['content'],
            blog2['content'],
            test_case['topic'],
            data['comparison_prompts']
        )

        if 'error' not in comparison:
            winner = comparison.get('overall_winner', 'unknown')
            print(f"🏆 Winner: {winner}")
            print(f"   {comparison.get('summary', '')[:100]}...")
        else:
            print(f"⚠️  Comparison error: {comparison['error']}")

        results['comparisons'].append({
            "test_case": test_case,
            "blog1": blog1,
            "blog2": blog2,
            "comparison": comparison
        })

    # Save results
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = RESULTS_DIR / f"compare_{mode1}_vs_{mode2}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Comparison saved to: {filename}")

    # Print summary
    if results['comparisons']:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")

        mode1_wins = sum(1 for c in results['comparisons']
                        if c.get('comparison', {}).get('overall_winner') == 'blog_a')
        mode2_wins = sum(1 for c in results['comparisons']
                        if c.get('comparison', {}).get('overall_winner') == 'blog_b')

        print(f"{mode1}: {mode1_wins} wins")
        print(f"{mode2}: {mode2_wins} wins")

    return results


def main():
    parser = argparse.ArgumentParser(description='Test and compare blog prompts')
    parser.add_argument('--mode', help='Test a single mode (e.g., quick, thoughtout)')
    parser.add_argument('--compare', nargs=2, help='Compare two modes (e.g., quick thoughtout)')
    parser.add_argument('--topic', help='Test specific topic ID')
    parser.add_argument('--full-suite', action='store_true', help='Run all tests')

    args = parser.parse_args()

    if args.full_suite:
        # Test all modes on all topics
        print("Running full test suite...")
        test_single_mode('quick')
        test_single_mode('thoughtout')
        compare_modes('quick', 'thoughtout')

    elif args.compare:
        compare_modes(args.compare[0], args.compare[1], args.topic)

    elif args.mode:
        test_single_mode(args.mode, args.topic)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
