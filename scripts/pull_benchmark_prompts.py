"""
Pull real user prompts from published HuggingFace datasets for benchmarking.

Sources:
  - WildBench (allenai/WildBench v2) — CC-BY-4.0
  - LMSYS Chatbot Arena (lmsys/chatbot_arena_conversations) — CC-BY-4.0 (prompts)
  - LMSYS-Chat-1M (lmsys/lmsys-chat-1m) — CC-BY-NC-4.0

Outputs: data/benchmarks/prompts.json (55 prompts mapped to our evaluation schema)
"""

import warnings
warnings.filterwarnings('ignore')

import json
import random
import hashlib
from pathlib import Path
from datasets import load_dataset

from backend.evaluation.benchmark_registry import annotate_prompt_records

random.seed(42)

# ---------------------------------------------------------------------------
# Category mapping helpers
# ---------------------------------------------------------------------------

WILDBENCH_TAG_MAP = {
    "Coding & Debugging": "code_generation",
    "Math":               "reasoning",
    "Reasoning":          "reasoning",
    "Planning":           "reasoning",
    "Information seeking": "question_answering",
    "Data Analysis":      "reasoning",
    "Creative Writing":   "creative_writing",
    "Editing":            "creative_writing",
    "Role playing":       "creative_writing",
    "Brainstorming":      "general",
    "Advice seeking":     "general",
    "Others":             "general",
}

def classify_prompt(text):
    """Heuristic classifier for LMSYS/Chat-1M prompts."""
    t = text.lower()

    # Summarization first (distinctive keywords)
    summary_kw = ["summarize", "summary", "tldr", "condense", "key points",
                  "brief this", "shorten", "main point", "recap", "sum up"]
    if any(k in t for k in summary_kw):
        return "summarization"

    # Code generation — must explicitly ask for code/implementation
    # Be careful not to match "zip code", "area code", "error code", etc.
    code_strong = ["write a function", "write code", "write a script",
                   "write a program", "implement a", "create a function",
                   "write python", "write javascript", "write java ",
                   "write c++", "write sql", "write html",
                   "python code", "javascript code", "java code",
                   "code to ", "code that ", "debug this",
                   "fix this code", "write me a function", "generate code",
                   "write a class", "create a script", "write a query",
                   "write a regex", "refactor this", "write unit test",
                   "design a database", "create an api", "build an api",
                   "function(", "```", "generate a function",
                   "numba function", "write me code", "code comment",
                   "write a decorator", "create a component",
                   "snake game", "write me a script"]
    # Exclude false positives
    code_false = ["zip code", "area code", "error code", "code of conduct",
                  "dress code", "code name", "country code", "qr code"]
    if any(k in t for k in code_strong) and not any(k in t for k in code_false):
        return "code_generation"

    # Creative writing
    creative_kw = ["write a story", "write a poem", "write an essay",
                   "write a song", "write a letter", "write a speech",
                   "write a dialogue", "write a review", "compose a",
                   "write me a story", "write me a poem", "write me a song",
                   "marketing copy", "slogan", "tagline", "cover letter",
                   "blog post", "creative writ", "make me a song",
                   "write a couplet", "write a haiku", "write a limerick"]
    if any(k in t for k in creative_kw):
        return "creative_writing"

    # Reasoning — analytical / logical / mathematical
    reason_kw = ["explain why", "analyze ", "what would happen",
                 "prove that", "solve this", "calculate", "probability",
                 "logic", "argument", "ethical", "implications",
                 "reasoning", "solve ", "what if ", "evaluate the",
                 "compare and contrast", "critically", "pros and cons"]
    if any(k in t for k in reason_kw):
        return "reasoning"

    # Question answering
    qa_kw = ["what is ", "what are ", "how does ", "how do ",
             "explain ", "tell me about", "describe ", "define ",
             "who is ", "who was ", "can you explain", "difference between",
             "what does ", "how can i", "how to "]
    if any(k in t for k in qa_kw):
        return "question_answering"

    return "general"


DOMAIN_MAP = {
    "code_generation":   "software_engineering",
    "reasoning":         "general",
    "creative_writing":  "creative",
    "summarization":     "general",
    "question_answering":"general",
    "general":           "general",
}

TASK_TYPE_MAP = {
    "code_generation":   "code_generation",
    "reasoning":         "reasoning",
    "creative_writing":  "creative_writing",
    "summarization":     "summarization",
    "question_answering":"question_answering",
    "general":           "general",
}


def estimate_difficulty(prompt_text):
    """Estimate difficulty from prompt length and specificity."""
    length = len(prompt_text)
    if length < 50:
        return "easy"
    elif length < 200:
        return "medium"
    else:
        return "hard"


def estimate_human_score(prompt_text):
    """Estimate a human quality score based on prompt characteristics."""
    length = len(prompt_text)
    has_constraints = any(w in prompt_text.lower() for w in [
        "must", "should", "format", "include", "maximum", "minimum",
        "step by step", "example", "specific", "output"])
    has_context = any(w in prompt_text.lower() for w in [
        "i have", "i need", "i want", "given", "consider", "assume",
        "the following", "below", "provided"])
    has_role = any(w in prompt_text.lower() for w in [
        "you are", "act as", "pretend", "role", "expert"])

    score = 3.0
    if length > 30:  score += 1.0
    if length > 100: score += 1.0
    if length > 200: score += 1.0
    if has_constraints: score += 1.0
    if has_context: score += 0.5
    if has_role: score += 0.5
    return min(score, 9.5)


def estimate_defects(prompt_text):
    """Estimate expected defects using Tian et al. taxonomy heuristics."""
    defects = []
    t = prompt_text.lower()
    length = len(prompt_text)

    # D001 - Ambiguity
    if length < 40 or any(w in t for w in ["something", "stuff", "things", "good", "nice", "better"]):
        defects.append("D001")
    # D002 - Incomplete specification
    if length < 80:
        defects.append("D002")
    # D004 - Missing context/input
    if any(w in t for w in ["this code", "this article", "this text", "the following",
                            "we discussed", "my resume", "this riddle"]) and length < 60:
        defects.append("D004")
    # D005 - Poor structure
    if length < 30:
        defects.append("D005")
    # D008 - Missing output constraints
    if not any(w in t for w in ["format", "words", "length", "maximum", "json",
                                "table", "list", "bullet", "output", "return"]):
        if length < 150:
            defects.append("D008")
    # D011 - Missing input reference
    if any(w in t for w in ["this", "the following", "below", "provided", "above"]):
        if "here" not in t and length < 100:
            defects.append("D011")
    # D015 - Missing audience specification
    if not any(w in t for w in ["audience", "reader", "for a", "for an", "explain like",
                                "beginner", "expert", "child", "student"]):
        if length < 100:
            defects.append("D015")
    # D023 - Injection vulnerability
    if any(w in t for w in ["scrape", "hack", "bypass", "ignore previous"]):
        defects.append("D023")

    return defects


def is_good_prompt(text, category_hint=None):
    """Filter: English, reasonable length, no junk, meaningful content."""
    if not text or len(text) < 15 or len(text) > 2000:
        return False
    t = text.lower().strip()
    # Skip jailbreak / system prompt injection attempts
    bad = ["ignore previous", "DAN", "jailbreak", "pretend you have no",
           "you are now", "ignore all", "disregard"]
    if any(b.lower() in t for b in bad):
        return False
    # Skip NSFW / problematic / dangerous content
    if any(w in t for w in ["nsfw", "erotic", "sexual", "unconscious", "naked",
                            "kill ", "murder", "torture", "molotov", "bomb",
                            "weapon", "hack into", "exploit", "her body",
                            "his body", "anatomy", "nude", "rob a bank",
                            "steal ", "illegal", "drug ", "drugs "]):
        return False
    # Skip NAME_1 / NAME_2 anonymization placeholders
    if "NAME_1" in text or "NAME_2" in text:
        return False
    # Skip meaningless single-word / greeting prompts
    trivial = ["hi", "hello", "hey", "continue", "ok", "yes", "no", "thanks",
               "thank you", "an apple", "error_code", "hi there", "test",
               "help", "help me", "go on", "sure", "okay"]
    if t.rstrip(".,!? ") in trivial:
        return False
    # Must have at least 4 words to be a meaningful prompt
    if len(t.split()) < 4:
        return False
    # Stricter English check: must be >95% ASCII
    ascii_ratio = sum(1 for c in text if ord(c) < 128) / len(text)
    if ascii_ratio < 0.95:
        return False
    # Skip prompts in other languages
    non_eng = ["peux tu", "traduire", "en francais", "por favor", "auf deutsch",
               "en espanol", "schreibe", "escribe", "ecrivez", "s'il vous"]
    if any(w in t for w in non_eng):
        return False
    # Skip prompts containing CJK characters (Chinese/Japanese/Korean)
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or
                    '\u3040' <= c <= '\u30ff' or '\uac00' <= c <= '\ud7af')
    if cjk_count > 0:
        return False
    # Skip trivial non-task prompts
    trivial_phrases = ["what a wonderful", "good morning", "how are you",
                       "nice to meet", "thank you for", "reply in english",
                       "respond in english", "what can you do", "who are you",
                       "are you a", "can you help me"]
    if any(w in t for w in trivial_phrases):
        return False
    return True


# ---------------------------------------------------------------------------
# Pull from each dataset
# ---------------------------------------------------------------------------

print("=" * 60)
print("Pulling prompts from published datasets...")
print("=" * 60)

all_prompts = []

# --- 1. WildBench (allenai/WildBench v2) ---
print("\n[1/3] WildBench (allenai/WildBench v2)...")
wb_prompts = []
ds = load_dataset("allenai/WildBench", "v2", split="test", streaming=True)
for ex in ds:
    conv = ex.get("conversation_input", [])
    if not conv:
        continue
    text = conv[0].get("content", "")
    if not is_good_prompt(text):
        continue
    tag = ex.get("primary_tag", "Others")
    category = WILDBENCH_TAG_MAP.get(tag, "general")
    wb_prompts.append({
        "text": text.strip(),
        "category": category,
        "source": "WildBench",
        "source_id": ex.get("id", ""),
    })

print(f"  Collected {len(wb_prompts)} valid WildBench prompts")

# --- 2. LMSYS Chatbot Arena ---
print("\n[2/3] LMSYS Chatbot Arena (lmsys/chatbot_arena_conversations)...")
arena_prompts = []
ds = load_dataset("lmsys/chatbot_arena_conversations", split="train", streaming=True)
count = 0
for ex in ds:
    if ex.get("language") != "English":
        continue
    if ex.get("turn", 0) != 1:  # single-turn only
        continue
    conv = ex.get("conversation_a", [])
    if not conv:
        continue
    text = conv[0].get("content", "")
    if not is_good_prompt(text):
        continue
    arena_prompts.append({
        "text": text.strip(),
        "category": classify_prompt(text),
        "source": "LMSYS-Chatbot-Arena",
        "source_id": ex.get("question_id", ""),
    })
    count += 1
    if count >= 5000:  # sample from first 5000 valid
        break

print(f"  Collected {len(arena_prompts)} valid Arena prompts")

# --- 3. LMSYS-Chat-1M ---
print("\n[3/3] LMSYS-Chat-1M (lmsys/lmsys-chat-1m)...")
chat1m_prompts = []
ds = load_dataset("lmsys/lmsys-chat-1m", split="train", streaming=True)
count = 0
for ex in ds:
    if ex.get("language") != "English":
        continue
    if ex.get("turn", 0) != 1:  # single-turn only
        continue
    conv = ex.get("conversation", [])
    if not conv:
        continue
    text = conv[0].get("content", "")
    if not is_good_prompt(text):
        continue
    chat1m_prompts.append({
        "text": text.strip(),
        "category": classify_prompt(text),
        "source": "LMSYS-Chat-1M",
        "source_id": ex.get("conversation_id", ""),
    })
    count += 1
    if count >= 5000:  # sample from first 5000 valid
        break

print(f"  Collected {len(chat1m_prompts)} valid Chat-1M prompts")


# ---------------------------------------------------------------------------
# Curate final 55 prompts with balanced distribution
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("Curating final benchmark set (55 prompts)...")
print("=" * 60)

TARGET_DISTRIBUTION = {
    "code_generation":    11,
    "reasoning":          11,
    "creative_writing":    9,
    "question_answering":  7,
    "summarization":       8,
    "general":             9,
}

# Pool all prompts by category
pools = {cat: [] for cat in TARGET_DISTRIBUTION}
for p in wb_prompts:
    if p["category"] in pools:
        pools[p["category"]].append(p)
for p in arena_prompts:
    if p["category"] in pools:
        pools[p["category"]].append(p)
for p in chat1m_prompts:
    if p["category"] in pools:
        pools[p["category"]].append(p)

print("\nPool sizes per category:")
for cat, items in pools.items():
    print(f"  {cat}: {len(items)}")

# For each category, select a diverse mix:
# - Mix of short (terse/bad) and long (detailed/good) prompts
# - Mix of sources
final_prompts = []
prompt_id = 1

for category, target_count in TARGET_DISTRIBUTION.items():
    pool = pools[category]
    random.shuffle(pool)

    # Sort by length to pick from both ends (short=bad, long=good)
    pool.sort(key=lambda p: len(p["text"]))

    selected = []

    # Pick ~30% short (easy/underspecified), ~35% medium, ~35% long (hard/detailed)
    n_short = max(1, int(target_count * 0.3))
    n_long = max(1, int(target_count * 0.35))
    n_mid = target_count - n_short - n_long

    # Short: 20-80 chars (enough to be meaningful but still underspecified)
    short_pool = [p for p in pool if 20 <= len(p["text"]) < 80]
    mid_pool = [p for p in pool if 80 <= len(p["text"]) < 300]
    long_pool = [p for p in pool if len(p["text"]) >= 300]

    # Deduplicate by content hash + fuzzy similarity check
    seen = set()
    seen_texts = []

    def is_near_duplicate(text):
        """Check if text is too similar to any already-selected prompt."""
        words = set(text.lower().split())
        for prev in seen_texts:
            prev_words = set(prev.lower().split())
            if not words or not prev_words:
                continue
            overlap = len(words & prev_words) / max(len(words), len(prev_words))
            if overlap >= 0.5:
                return True
        return False

    def pick_unique(src, n):
        picks = []
        for p in src:
            h = hashlib.md5(p["text"].lower().encode()).hexdigest()
            if h in seen:
                continue
            if is_near_duplicate(p["text"]):
                continue
            seen.add(h)
            seen_texts.append(p["text"])
            picks.append(p)
            if len(picks) >= n:
                break
        return picks

    selected.extend(pick_unique(short_pool, n_short))
    selected.extend(pick_unique(mid_pool, n_mid))
    selected.extend(pick_unique(long_pool, n_long))

    # Fill remaining if needed
    remaining = target_count - len(selected)
    if remaining > 0:
        all_remaining = [p for p in pool
                        if hashlib.md5(p["text"].lower().encode()).hexdigest() not in seen]
        selected.extend(pick_unique(all_remaining, remaining))

    for p in selected[:target_count]:
        text = p["text"]
        cat = p["category"]
        final_prompts.append({
            "id": f"B{prompt_id:03d}",
            "prompt": text,
            "task_type": TASK_TYPE_MAP.get(cat, "general"),
            "domain": DOMAIN_MAP.get(cat, "general"),
            "expected_defects": estimate_defects(text),
            "human_score": estimate_human_score(text),
            "category": cat,
            "difficulty": estimate_difficulty(text),
            "source": p["source"],
            "source_id": p["source_id"],
            "benchmark_split": "public_test",
            "benchmark_bucket": "defect_taxonomy" if estimate_defects(text) else "real_user",
            "benchmark_tags": [cat, p["source"]],
        })
        prompt_id += 1

final_prompts = annotate_prompt_records(final_prompts)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

out_path = Path(__file__).parent.parent / "data" / "benchmarks" / "prompts.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(final_prompts, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(final_prompts)} prompts to {out_path}")

# Print summary
from collections import Counter
print("\n--- Distribution ---")
print("\nBy category:")
for cat, n in Counter(p["category"] for p in final_prompts).most_common():
    print(f"  {cat}: {n}")
print("\nBy source:")
for src, n in Counter(p["source"] for p in final_prompts).most_common():
    print(f"  {src}: {n}")
print("\nBy difficulty:")
for d, n in Counter(p["difficulty"] for p in final_prompts).most_common():
    print(f"  {d}: {n}")
scores = [p["human_score"] for p in final_prompts]
print(f"\nScore range: {min(scores):.1f} - {max(scores):.1f} (mean {sum(scores)/len(scores):.1f})")
