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
        f"📚 *Day {day} | {phase} RC 학습 | {today}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"☀️ 좋은 아침이에요! 오늘도 30분 영어 공부 시작합니다 🚀"
    )

    # ── 지문 ──────────────────────────────────────────────
    p = content['passage']
    messages.append(
        f"📖 *오늘의 지문*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"*{p['title']}*\n\n"
        f"{p['text']}"
    )

    # ── 문제 ──────────────────────────────────────────────
    q_text = "❓ *문제* _(정답은 저녁 6시에 공개됩니다)_\n"
    for q in p['questions']:
        q_text += f"\n*Q{q['number']}.* {q['question']}\n"
        for opt in q['options']:
            q_text += f"   {opt}\n"
    messages.append(q_text)

    # ── 문법 ──────────────────────────────────────────────
    g = content['grammar']
    grammar_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *문법 Day {day}: {g['title']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🇰🇷 *한국어 설명*\n{g['korean_explanation']}\n\n"
        f"🇺🇸 *English Explanation*\n{g['english_explanation']}\n\n"
        f"💡 *예문*\n"
    )
    for i, ex in enumerate(g['examples'], 1):
        grammar_text += f"   {i}. {ex}\n"
    messages.append(grammar_text)

    # ── 단어 (5개씩 나눠서 전송) ──────────────────────────
    vocab = content['vocabulary']
    messages.append(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📗 *오늘의 단어 20개* (TOEIC 10 + TOEFL 10)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    for i in range(0, len(vocab), 5):
        chunk = vocab[i:i + 5]
        chunk_text = ""
        for j, w in enumerate(chunk, i + 1):
            synonyms = ", ".join(w['synonyms']) if w['synonyms'] else "—"
            antonyms = ", ".join(w['antonyms']) if w['antonyms'] else "—"
            chunk_text += (
                f"\n*{j}. {w['word']}* [{w['part_of_speech']}] `{w['category']}`\n"
                f"   🔹 뜻: {w['korean_meaning']}\n"
                f"   🔹 Meaning: {w['english_meaning']}\n"
                f"   🔹 예문: _{w['example']}_\n"
                f"   🔹 동의어: {synonyms}\n"
                f"   🔹 반의어: {antonyms}\n"
            )
        messages.append(chunk_text)

    # ── 푸터 ──────────────────────────────────────────────
    messages.append(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ *저녁 6시에 정답 해설 + 단어 퀴즈 + 문법 퀴즈가 발송됩니다!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    return messages


def main():
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")

    day_number = get_day_number()
    print(f"[Morning] Day {day_number} 발송 시작...")

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
