import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from utils import get_day_number, load_content, send_slack


def format_messages(content):
    day = content['day']
    phase = content['phase']
    today = date.today().strftime('%Y-%m-%d')
    messages = []

    # ── 헤더 ──────────────────────────────────────────────
    messages.append(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ *Day {day} | 정답 & 복습 | {today}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌆 퇴근길 복습 시간! 오늘 공부한 내용을 확인해봐요 💪"
    )

    # ── 지문 정답 & 해설 ──────────────────────────────────
    ans = content['answers']['passage']
    answer_text = "📖 *지문 정답 & 해설*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for a in ans:
        answer_text += f"\n*Q{a['number']} 정답: {a['answer']}*\n💬 {a['explanation']}\n"
    messages.append(answer_text)

    # ── 문법 퀴즈 ─────────────────────────────────────────
    grammar = content['grammar']
    quiz_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *문법 퀴즈* — {grammar['title']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    for q in grammar['quiz']:
        quiz_text += f"\n*Q{q['number']}.* {q['question']}\n"
        for opt in q['options']:
            quiz_text += f"   {opt}\n"
        quiz_text += f"   ✅ 정답: *{q['answer']}*\n   💬 {q['explanation']}\n"
    messages.append(quiz_text)

    # ── 단어 퀴즈 ─────────────────────────────────────────
    vocab_quiz = content['answers']['vocab_quiz']
    vocab_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📗 *단어 퀴즈* (오늘의 단어 20개 중 5문제)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    for q in vocab_quiz:
        vocab_text += f"\n*Q{q['number']}.* {q['question']}\n"
        for opt in q['options']:
            vocab_text += f"   {opt}\n"
        vocab_text += f"   ✅ 정답: *{q['answer']}*\n   💬 {q['explanation']}\n"
    messages.append(vocab_text)

    # ── 푸터 ──────────────────────────────────────────────
    messages.append(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 *Day {day} 완료!* 오늘도 수고했어요! 내일 아침 7시에 또 만나요 📚\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    return messages


def main():
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")

    day_number = get_day_number()
    print(f"[Evening] Day {day_number} 발송 시작...")

    try:
        content = load_content(day_number)
    except FileNotFoundError:
        print(f"Day {day_number} 콘텐츠 파일이 없습니다. 건너뜁니다.")
        return

    for msg in format_messages(content):
        send_slack(webhook_url, msg)
        print("메시지 전송 완료.")


if __name__ == "__main__":
    main()
