#!/usr/bin/env python3
"""
PromptOptimizer Pro - Interactive CLI Tool

Enhanced command-line interface with safe multi-line input handling.
"""

import asyncio
import sys
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

from backend.services.agent_orchestrator import get_orchestrator
from backend.services.optimizer_service import get_optimizer
from backend.models.technique_registry import TECHNIQUE_REGISTRY
from backend.models.defect_taxonomy import DEFECT_TAXONOMY
from backend.config import Config


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_section(text: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*40}{Colors.END}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def check_api_keys() -> bool:
    """Check if API keys are configured"""
    has_anthropic = bool(Config.ANTHROPIC_API_KEY)
    has_groq = bool(Config.GROQ_API_KEY)

    if has_anthropic:
        print_success("Anthropic API key configured")
        return True
    elif has_groq:
        print_success("Groq API key configured (fallback)")
        return True
    else:
        print_error("No API keys configured!")
        print_info("Please set ANTHROPIC_API_KEY or GROQ_API_KEY in your .env file")
        return False


def show_system_info():
    """Display system information"""
    print_header("PromptOptimizer Pro - System Info")

    print_section("Configuration")
    print(f"  Environment: {Config.FLASK_ENV}")
    print(f"  Debug Mode: {Config.FLASK_DEBUG}")
    print(f"  Default Provider: {Config.DEFAULT_PROVIDER}")

    print_section("Statistics")
    print(f"  Total Defects: {len(DEFECT_TAXONOMY)}")
    print(f"  Total Techniques: {len(TECHNIQUE_REGISTRY)}")
    print(f"  Total Agents: 4")
    print(f"  Consensus Threshold: {Config.CONSENSUS_THRESHOLD}")

    print_section("API Keys")
    check_api_keys()


def get_prompt_input() -> Optional[str]:
    """
    Get prompt input from user with multiple safe methods.
    Returns the prompt text or None if cancelled.
    """
    print(f"\n{Colors.BOLD}How would you like to enter your prompt?{Colors.END}\n")
    print("  1. Type directly (multi-line, end with '###' on new line)")
    print("  2. Open Notepad to edit (recommended for Windows)")
    print("  3. Load from file")
    print("  4. Cancel")

    choice = input(f"\n{Colors.BOLD}Choose method (1-4):{Colors.END} ").strip()

    if choice == "1":
        return get_prompt_multiline()
    elif choice == "2":
        return get_prompt_notepad()
    elif choice == "3":
        return get_prompt_from_file()
    elif choice == "4":
        return None
    else:
        print_error("Invalid choice")
        return get_prompt_input()


def get_prompt_multiline() -> Optional[str]:
    """
    Get multi-line prompt input with clear termination marker.
    """
    print(f"\n{Colors.BOLD}Enter your prompt (type '###' on a new line when done):{Colors.END}")
    print(f"{Colors.YELLOW}Tip: You can safely paste long text here!{Colors.END}\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "###":
                break
            lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print_warning("\nInput cancelled")
            return None

    prompt = "\n".join(lines).strip()

    if not prompt:
        print_error("Prompt cannot be empty!")
        return None

    print_success(f"Received {len(prompt)} characters")
    return prompt


def get_prompt_notepad() -> Optional[str]:
    """
    Open Notepad (or default text editor) for prompt input.
    This is the safest method for Windows users.
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("# Enter your prompt below this line\n")
            f.write("# Save and close this file when done\n")
            f.write("# Lines starting with # will be ignored\n\n")
            temp_path = f.name

        print_info(f"Opening text editor...")
        print_info("Save and close the file when you're done editing")

        # Open in Notepad (Windows) or default editor
        if sys.platform == "win32":
            subprocess.run(['notepad.exe', temp_path], check=True)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(['open', '-t', temp_path], check=True)
        else:  # Linux
            editor = os.environ.get('EDITOR', 'nano')
            subprocess.run([editor, temp_path], check=True)

        # Read the file
        with open(temp_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f.readlines() if not line.strip().startswith('#')]
            prompt = '\n'.join(lines).strip()

        # Clean up
        os.unlink(temp_path)

        if not prompt:
            print_error("No prompt entered!")
            return None

        print_success(f"Loaded {len(prompt)} characters from editor")
        return prompt

    except subprocess.CalledProcessError:
        print_error("Failed to open text editor")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def get_prompt_from_file() -> Optional[str]:
    """Load prompt from a file"""
    print(f"\n{Colors.BOLD}Enter file path:{Colors.END}")
    file_path = input("> ").strip().strip('"').strip("'")

    if not file_path:
        print_error("No file path provided")
        return None

    try:
        path = Path(file_path)
        if not path.exists():
            print_error(f"File not found: {file_path}")
            return None

        with open(path, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()

        if not prompt:
            print_error("File is empty!")
            return None

        print_success(f"Loaded {len(prompt)} characters from {path.name}")
        return prompt

    except Exception as e:
        print_error(f"Error reading file: {str(e)}")
        return None


async def analyze_prompt_interactive():
    """Interactive prompt analysis"""
    print_header("Analyze Prompt")

    if not check_api_keys():
        return

    # Get prompt from user using safe input method
    prompt = get_prompt_input()
    if not prompt:
        return

    # Get optional context
    print(f"\n{Colors.BOLD}Task type (press Enter for 'general'):{Colors.END}")
    print("Options: code_generation, reasoning, creative_writing, general")
    task_type = input("> ").strip() or "general"

    print(f"\n{Colors.BOLD}Domain (press Enter for 'general'):{Colors.END}")
    print("Options: software_engineering, mathematics, science, general")
    domain = input("> ").strip() or "general"

    # Analyze
    print_section("Analyzing...")
    print_info(f"Prompt length: {len(prompt)} characters")
    print_info("Running 4 agents in parallel...")

    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.analyze_with_agents(
            prompt=prompt,
            context={"task_type": task_type, "domain": domain}
        )

        # Display results
        print_section("Analysis Results")

        # Overall score
        score = result["overall_score"]
        score_color = Colors.GREEN if score >= 7 else Colors.YELLOW if score >= 5 else Colors.RED
        print(f"\n  {Colors.BOLD}Overall Score:{Colors.END} {score_color}{score:.1f}/10{Colors.END}")
        print(f"  {Colors.BOLD}Consensus:{Colors.END} {result['consensus']:.0%}")
        print(f"  {Colors.BOLD}Defects Found:{Colors.END} {len(result['defects'])}")

        # Defects
        if result['defects']:
            print_section("Detected Defects")
            for i, defect in enumerate(result['defects'], 1):
                severity_color = {
                    "critical": Colors.RED,
                    "high": Colors.YELLOW,
                    "medium": Colors.BLUE,
                    "low": Colors.CYAN
                }.get(defect['severity'], Colors.END)

                print(f"\n  {Colors.BOLD}{i}. {defect['name']} ({defect['id']}){Colors.END}")
                print(f"     {severity_color}Severity: {defect['severity'].upper()}{Colors.END}")
                print(f"     Confidence: {defect['confidence']:.0%}")
                print(f"     Detected by: {', '.join(defect['detected_by'])}")
                print(f"     Evidence: {defect['evidence'][:100]}...")
                print(f"     Fix: {defect['remediation'][:150]}...")
        else:
            print_success("\nNo defects found! Your prompt looks good.")

        # Agent breakdown
        print_section("Agent Breakdown")
        for agent_name, agent_result in result['agent_results'].items():
            agent_score = agent_result['score']
            agent_defects = len(agent_result['defects'])
            print(f"  {agent_name}: {agent_score:.1f}/10 ({agent_defects} defects)")

        return result

    except Exception as e:
        print_error(f"Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def optimize_prompt_interactive(analysis_result: Optional[dict] = None):
    """Interactive prompt optimization"""
    print_header("Optimize Prompt")

    if not check_api_keys():
        return

    # Get prompt from user using safe input method
    prompt = get_prompt_input()
    if not prompt:
        return

    # Get optimization settings
    print(f"\n{Colors.BOLD}Optimization level (press Enter for 'balanced'):{Colors.END}")
    print("Options: minimal (≤3 techniques), balanced (5 techniques), aggressive (7 techniques)")
    level = input("> ").strip() or "balanced"

    print(f"\n{Colors.BOLD}Max techniques to apply (press Enter for 5):{Colors.END}")
    max_tech = input("> ").strip()
    max_techniques = int(max_tech) if max_tech else 5

    # Optimize
    print_section("Optimizing...")
    print_info(f"Optimization level: {level}")
    print_info(f"Max techniques: {max_techniques}")
    print_info("Step 1: Analyzing original prompt...")

    try:
        optimizer = get_optimizer()
        result = await optimizer.optimize(
            prompt=prompt,
            context={"task_type": "general", "domain": "general"},
            optimization_level=level,
            max_techniques=max_techniques,
            analysis=analysis_result
        )

        # Display results
        print_section("Optimization Results")

        # Scores
        before_score = result['before_analysis']['overall_score']
        after_score = result['after_analysis']['overall_score']
        improvement = result['improvement_score']

        print(f"\n  {Colors.BOLD}Before Score:{Colors.END} {before_score:.1f}/10")
        print(f"  {Colors.BOLD}After Score:{Colors.END} {after_score:.1f}/10")

        improvement_color = Colors.GREEN if improvement > 0 else Colors.RED if improvement < 0 else Colors.YELLOW
        print(f"  {improvement_color}{Colors.BOLD}Improvement:{Colors.END} {improvement_color}{improvement:+.1f}{Colors.END}")

        # Techniques applied
        print_section(f"Techniques Applied ({len(result['techniques_applied'])})")
        for i, tech in enumerate(result['techniques_applied'], 1):
            print(f"\n  {Colors.BOLD}{i}. {tech['technique_name']} ({tech['technique_id']}){Colors.END}")
            print(f"     Target Defects: {', '.join(tech['target_defects'])}")
            print(f"     Change: {tech['modification'][:100]}...")

        # Prompts comparison
        print_section("Original Prompt")
        print(f"{Colors.YELLOW}{result['original_prompt'][:300]}...{Colors.END}")

        print_section("Optimized Prompt")
        print(f"{Colors.GREEN}{result['optimized_prompt'][:300]}...{Colors.END}")

        # Save option
        print(f"\n{Colors.BOLD}Save optimized prompt to file? (y/n):{Colors.END}")
        save = input("> ").strip().lower()
        if save == 'y':
            filename = f"optimized_prompt_{int(asyncio.get_event_loop().time())}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== ORIGINAL PROMPT ===\n\n")
                f.write(result['original_prompt'])
                f.write("\n\n=== OPTIMIZED PROMPT ===\n\n")
                f.write(result['optimized_prompt'])
                f.write("\n\n=== TECHNIQUES APPLIED ===\n\n")
                for tech in result['techniques_applied']:
                    f.write(f"- {tech['technique_name']}: {tech['modification']}\n")
            print_success(f"Saved to {filename}")

        return result

    except Exception as e:
        print_error(f"Optimization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def list_techniques():
    """List all available techniques"""
    print_header("Available Techniques")

    # Group by category
    from backend.models.technique_registry import TechniqueCategory

    categories = {}
    for tech_id, technique in TECHNIQUE_REGISTRY.items():
        cat = technique.category.value
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(technique)

    for category, techniques in categories.items():
        print_section(category.replace("_", " ").title())
        for tech in sorted(techniques, key=lambda t: t.effectiveness_score, reverse=True):
            print(f"\n  {Colors.BOLD}{tech.id}: {tech.name}{Colors.END}")
            print(f"     Effectiveness: {tech.effectiveness_score:.0%}")
            print(f"     Fixes: {', '.join(tech.fixes_defects[:5])}")
            print(f"     {tech.description[:100]}...")


async def show_menu():
    """Display main menu"""
    while True:
        print_header("PromptOptimizer Pro - Enhanced CLI")

        print(f"{Colors.BOLD}What would you like to do?{Colors.END}\n")
        print("  1. Analyze a prompt")
        print("  2. Optimize a prompt")
        print("  3. Analyze + Optimize (recommended)")
        print("  4. List all techniques")
        print("  5. System information")
        print("  6. Exit")

        choice = input(f"\n{Colors.BOLD}Enter choice (1-6):{Colors.END} ").strip()

        if choice == "1":
            await analyze_prompt_interactive()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")

        elif choice == "2":
            await optimize_prompt_interactive()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")

        elif choice == "3":
            print_info("First analyzing, then optimizing...")
            analysis_result = await analyze_prompt_interactive()
            if analysis_result:
                print_info("\nNow optimizing based on analysis...")
                await optimize_prompt_interactive(analysis_result)
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")

        elif choice == "4":
            await list_techniques()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")

        elif choice == "5":
            show_system_info()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")

        elif choice == "6":
            print_success("\nGoodbye! 👋")
            sys.exit(0)

        else:
            print_error("Invalid choice. Please enter 1-6.")


async def main():
    """Main entry point"""
    try:
        await show_menu()
    except KeyboardInterrupt:
        print_success("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
