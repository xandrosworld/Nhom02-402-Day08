"""
run_grading.py — HNK: Grading Script
======================================
Mục tiêu:
  Chạy pipeline RAG với grading_questions.json (BTC public lúc 17:00)
  và xuất kết quả vào logs/grading_run.json để nộp trước 18:00.

Cách chạy:
  python -X utf8 run_grading.py

Lưu ý:
  - BTC public grading_questions.json lúc 17:00
  - Download file đó → đặt vào data/grading_questions.json
  - Chạy script này NGAY để có đủ thời gian
  - Deadline commit: 18:00
"""

import json
from pathlib import Path
from datetime import datetime
from rag_answer import rag_answer

# HNK: Cấu hình đường dẫn
GRADING_QUESTIONS_PATH = Path(__file__).parent / "data" / "grading_questions.json"
LOG_OUTPUT_PATH = Path(__file__).parent / "logs" / "grading_run.json"

# HNK: Dùng cấu hình tốt nhất của nhóm (hybrid sau khi Tùng Anh xong Sprint 3)
# Nếu hybrid chưa xong → dùng "dense"
RETRIEVAL_MODE = "hybrid"


def run_grading():
    """
    HNK: Chạy toàn bộ grading questions qua pipeline và lưu log.
    """
    # Kiểm tra file grading_questions.json
    if not GRADING_QUESTIONS_PATH.exists():
        print(f"❌ Chưa có file: {GRADING_QUESTIONS_PATH}")
        print("→ Chờ BTC public lúc 17:00, download và đặt vào data/grading_questions.json")
        return

    # Load câu hỏi
    with open(GRADING_QUESTIONS_PATH, encoding="utf-8") as f:
        questions = json.load(f)

    print(f"✅ Tìm thấy {len(questions)} câu hỏi grading")
    print(f"📋 Retrieval mode: {RETRIEVAL_MODE}")
    print(f"⏰ Bắt đầu: {datetime.now().strftime('%H:%M:%S')}\n")

    log = []
    errors = []

    for i, q in enumerate(questions, 1):
        qid = q.get("id", f"q{i:02d}")
        question = q["question"]
        print(f"[{i}/{len(questions)}] {qid}: {question[:60]}...")

        try:
            result = rag_answer(
                query=question,
                retrieval_mode=RETRIEVAL_MODE,
                verbose=False,
            )
            entry = {
                "id": qid,
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"],
                "chunks_retrieved": len(result["chunks_used"]),
                "retrieval_mode": result["config"]["retrieval_mode"],
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  ✅ Answer: {result['answer'][:80]}...")

        except Exception as e:
            # HNK: Không crash toàn bộ script nếu 1 câu lỗi
            print(f"  ❌ Lỗi: {e}")
            entry = {
                "id": qid,
                "question": question,
                "answer": f"PIPELINE_ERROR: {str(e)}",
                "sources": [],
                "chunks_retrieved": 0,
                "retrieval_mode": RETRIEVAL_MODE,
                "timestamp": datetime.now().isoformat(),
            }
            errors.append(qid)

        log.append(entry)

    # Lưu log
    LOG_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"✅ Hoàn thành! {len(log)} câu đã chạy")
    if errors:
        print(f"⚠️  Lỗi ở: {errors}")
    print(f"📁 Log đã lưu: {LOG_OUTPUT_PATH}")
    print(f"⏰ Kết thúc: {datetime.now().strftime('%H:%M:%S')}")
    print(f"\n🚨 COMMIT NGAY trước 18:00:")
    print(f"   git add logs/grading_run.json")
    print(f"   git commit -m \"feat(HNK): add grading run log\"")
    print(f"   git push origin main")


if __name__ == "__main__":
    run_grading()
