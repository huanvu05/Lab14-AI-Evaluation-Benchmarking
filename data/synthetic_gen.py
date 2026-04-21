import json
import random
import os

# ===== CONFIG =====
OUTPUT_PATH = "data/golden_set.jsonl"
TOTAL_CASES = 50

DISTRIBUTION = {
    "easy": 20,
    "hard": 20,
    "adversarial": 10
}

# ===== DATA POOLS (dynamic templates, not static cases) =====

loan_types = ["mua nhà", "mua xe", "tiêu dùng", "kinh doanh"]
interest_rates = [5.5, 6.0, 6.5, 7.0, 7.5]

banks = ["Vietcombank", "Techcombank", "BIDV", "ACB"]
durations = ["12 tháng", "24 tháng", "36 tháng", "60 tháng"]

ambiguous_terms = [
    "có cao không",
    "có ổn không",
    "tốt không",
    "có đáng vay không"
]

# ===== GENERATORS =====

def gen_easy_case(i):
    loan = random.choice(loan_types)
    rate = random.choice(interest_rates)

    return {
        "id": f"case_{i}",
        "query": f"Lãi suất vay {loan} là bao nhiêu?",
        "expected_answer": f"Khoảng {rate}%/năm",
        "ground_truth_doc_id": f"doc_vay_{loan.replace(' ', '_')}_{int(rate*10)}",
        "difficulty": "easy"
    }


def gen_hard_case(i):
    loan = random.choice(loan_types)
    bank = random.choice(banks)
    duration = random.choice(durations)
    rate = random.choice(interest_rates)

    doc1 = f"doc_{bank.lower()}_{loan.replace(' ', '_')}"
    doc2 = f"doc_lai_suat_{duration.replace(' ', '_')}"

    return {
        "id": f"case_{i}",
        "query": f"Vay {loan} tại {bank} trong {duration} thì lãi suất bao nhiêu?",
        "expected_answer": f"{bank} áp dụng khoảng {rate}%/năm cho kỳ hạn {duration}",
        "ground_truth_doc_id": f"{doc1}+{doc2}",
        "difficulty": "hard"
    }


def gen_adversarial_case(i):
    loan = random.choice(loan_types)
    term = random.choice(ambiguous_terms)
    rate = random.choice(interest_rates)

    return {
        "id": f"case_{i}",
        "query": f"Lãi suất vay {loan} {term}?",
        "expected_answer": f"Khoảng {rate}%/năm, tùy điều kiện cụ thể",
        "ground_truth_doc_id": f"doc_vay_{loan.replace(' ', '_')}_{int(rate*10)}",
        "difficulty": "adversarial"
    }


# ===== MAIN GENERATION =====

def generate_dataset():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    cases = []
    idx = 1

    # EASY
    for _ in range(DISTRIBUTION["easy"]):
        cases.append(gen_easy_case(idx))
        idx += 1

    # HARD (multi-hop)
    for _ in range(DISTRIBUTION["hard"]):
        cases.append(gen_hard_case(idx))
        idx += 1

    # ADVERSARIAL
    for _ in range(DISTRIBUTION["adversarial"]):
        cases.append(gen_adversarial_case(idx))
        idx += 1

    # Shuffle to avoid ordering bias
    random.shuffle(cases)

    # Write JSONL
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    print(f"✅ Generated {len(cases)} cases at {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_dataset()