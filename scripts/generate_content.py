#!/usr/bin/env python3
"""Generate all 200 days of TOEIC/TOEFL study content using Claude API."""

import anthropic
import json
import os
import sys
import time
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"

# ── 200일 커리큘럼 ────────────────────────────────────────────
# (day, phase, grammar_topic, vocab_theme, passage_type)
CURRICULUM_RAW = [
    # ── TOEIC Phase: Day 1~100 ─────────────────────────────────
    (1,  "TOEIC", "문장의 기본 구조 1 — 주어(S) + 동사(V)", "기본 비즈니스", "business memo"),
    (2,  "TOEIC", "문장의 기본 구조 2 — 목적어(O): S+V+O", "회의와 일정", "business email"),
    (3,  "TOEIC", "문장의 기본 구조 3 — 보어(C): S+V+C", "회사와 부서", "company notice"),
    (4,  "TOEIC", "문장의 기본 구조 4 — 4형식: S+V+IO+DO", "출장과 여행", "travel notice"),
    (5,  "TOEIC", "문장의 기본 구조 5 — 5형식: S+V+O+OC", "프로젝트와 업무", "business report"),
    (6,  "TOEIC", "명사 1 — 셀 수 있는 명사 (단수/복수)", "채용과 인사", "job advertisement"),
    (7,  "TOEIC", "명사 2 — 셀 수 없는 명사", "재무와 회계", "financial report"),
    (8,  "TOEIC", "명사 3 — 복수형 만들기 (-s, -es, 불규칙)", "마케팅과 광고", "advertisement"),
    (9,  "TOEIC", "관사 1 — 부정관사 a/an 사용법", "제품과 서비스", "product brochure"),
    (10, "TOEIC", "관사 2 — 정관사 the 사용법", "고객 서비스", "customer service letter"),
    (11, "TOEIC", "대명사 1 — 인칭대명사 주격 (I/you/he/she/it/we/they)", "사무실 환경", "office memo"),
    (12, "TOEIC", "대명사 2 — 인칭대명사 목적격 (me/you/him/her/it/us/them)", "이메일과 서신", "business email"),
    (13, "TOEIC", "대명사 3 — 소유격과 소유대명사 (my/mine/your/yours)", "회의실과 시설", "facility notice"),
    (14, "TOEIC", "대명사 4 — 재귀대명사 (myself/yourself/himself)", "교육과 훈련", "training announcement"),
    (15, "TOEIC", "대명사 5 — 지시대명사 this/that/these/those", "이벤트와 행사", "event announcement"),
    (16, "TOEIC", "be동사 1 — am/is/are 현재형", "회사 소개", "company profile"),
    (17, "TOEIC", "be동사 2 — was/were 과거형", "프로젝트 결과", "project report"),
    (18, "TOEIC", "be동사 3 — 부정문(isn't/aren't)과 의문문(Is/Are?)", "제품 소개", "product notice"),
    (19, "TOEIC", "일반동사 1 — 현재형 기본", "업무 지시", "office email"),
    (20, "TOEIC", "일반동사 2 — 3인칭 단수 현재 (-s/-es)", "일정 조율", "schedule email"),
    (21, "TOEIC", "일반동사 3 — 부정문: don't/doesn't", "정책과 규정", "policy notice"),
    (22, "TOEIC", "일반동사 4 — 의문문: Do/Does + 주어?", "고객 문의", "customer inquiry"),
    (23, "TOEIC", "현재시제 — 습관, 사실, 반복되는 일", "배송과 물류", "shipping notice"),
    (24, "TOEIC", "과거시제 1 — 규칙 동사 (-ed)", "회의 결과", "meeting minutes"),
    (25, "TOEIC", "과거시제 2 — 불규칙 동사 (go-went, see-saw)", "프레젠테이션", "presentation memo"),
    (26, "TOEIC", "과거시제 3 — 부정문(didn't)과 의문문(Did?)", "문제 해결", "problem report"),
    (27, "TOEIC", "미래시제 1 — will: 의지/예측", "신제품 출시", "product launch notice"),
    (28, "TOEIC", "미래시제 2 — be going to: 계획/예정", "회사 계획", "business plan"),
    (29, "TOEIC", "미래시제 3 — will vs be going to 차이", "협력과 파트너십", "partnership email"),
    (30, "TOEIC", "현재진행형 1 — am/is/are + -ing 형태와 의미", "공사와 리모델링", "renovation notice"),
    (31, "TOEIC", "현재진행형 2 — 진행형으로 쓸 수 없는 동사", "계약과 협상", "contract notice"),
    (32, "TOEIC", "과거진행형 — was/were + -ing", "사고와 보고", "incident report"),
    (33, "TOEIC", "현재완료 1 — have/has + p.p. 기본 개념", "업무 성과", "performance report"),
    (34, "TOEIC", "현재완료 2 — 경험 표현 (ever/never)", "출장 경험", "travel email"),
    (35, "TOEIC", "현재완료 3 — 완료 표현 (just/already/yet)", "작업 완료", "completion notice"),
    (36, "TOEIC", "현재완료 4 — 계속 표현 (for/since)", "장기 프로젝트", "project update"),
    (37, "TOEIC", "현재완료 5 — 현재완료 vs 과거시제 차이", "회사 역사", "company history"),
    (38, "TOEIC", "과거완료 — had + p.p.: 과거보다 더 이전", "문제 경위", "situation report"),
    (39, "TOEIC", "미래완료 — will have + p.p.", "목표와 마감", "deadline memo"),
    (40, "TOEIC", "형용사 1 — 한정적 용법 (명사 수식)", "제품 특징", "product catalog"),
    (41, "TOEIC", "형용사 2 — 서술적 용법 (be동사 + 형용사)", "직원 평가", "evaluation form"),
    (42, "TOEIC", "형용사 3 — 수량형용사 (many/much/few/little)", "재고 관리", "inventory report"),
    (43, "TOEIC", "부사 1 — 형태(-ly)와 역할 (동사/형용사/다른부사 수식)", "영업과 판매", "sales report"),
    (44, "TOEIC", "부사 2 — 빈도부사 (always/usually/often/never)", "업무 루틴", "office newsletter"),
    (45, "TOEIC", "부사 3 — 정도부사 (very/quite/rather/too)", "고객 만족", "customer survey"),
    (46, "TOEIC", "전치사 1 — 시간 전치사: at/on/in", "행사 일정", "event schedule"),
    (47, "TOEIC", "전치사 2 — 장소 전치사: at/on/in", "사무실 위치", "location notice"),
    (48, "TOEIC", "전치사 3 — 방향 전치사: to/from/into/out of", "출퇴근과 이동", "commute email"),
    (49, "TOEIC", "전치사 4 — 기타 전치사: for/with/by/about", "보고서 작성", "business report"),
    (50, "TOEIC", "조동사 1 — can/could: 능력과 가능", "기술과 역량", "job posting"),
    (51, "TOEIC", "조동사 2 — may/might: 허가와 추측", "허가와 승인", "approval email"),
    (52, "TOEIC", "조동사 3 — will/would: 의지와 정중한 요청", "서비스 요청", "service request"),
    (53, "TOEIC", "조동사 4 — must: 의무와 강한 추측", "규정 준수", "compliance notice"),
    (54, "TOEIC", "조동사 5 — should/ought to: 충고와 권고", "업무 가이드", "guidelines memo"),
    (55, "TOEIC", "조동사 6 — had better/would rather: 강한 권고와 선호", "리스크 관리", "risk notice"),
    (56, "TOEIC", "접속사 1 — 등위접속사: and/but/or/so", "협업과 팀워크", "team email"),
    (57, "TOEIC", "접속사 2 — 이유 접속사: because/since/as", "지연과 사유", "delay notice"),
    (58, "TOEIC", "접속사 3 — 시간 접속사: when/while/before/after", "업무 순서", "procedure notice"),
    (59, "TOEIC", "접속사 4 — 조건 접속사: if/unless", "조건부 제안", "conditional email"),
    (60, "TOEIC", "접속사 5 — 양보 접속사: although/though/even though", "문제점과 대안", "alternative proposal"),
    (61, "TOEIC", "수동태 1 — 현재/과거 수동태: be + p.p.", "제품 생산", "manufacturing report"),
    (62, "TOEIC", "수동태 2 — 조동사 수동태: must/should be + p.p.", "의무와 지시", "instruction manual"),
    (63, "TOEIC", "수동태 3 — 완료 수동태: have been + p.p.", "완료된 업무", "completion report"),
    (64, "TOEIC", "수동태 4 — 4형식 수동태", "정보 전달", "information memo"),
    (65, "TOEIC", "수동태 5 — by + 행위자 생략", "공지와 발표", "official announcement"),
    (66, "TOEIC", "관계대명사 1 — who: 사람을 수식", "인물 소개", "staff profile"),
    (67, "TOEIC", "관계대명사 2 — which: 사물을 수식", "제품 설명", "product description"),
    (68, "TOEIC", "관계대명사 3 — that: 사람/사물 모두", "서비스 조건", "terms of service"),
    (69, "TOEIC", "관계대명사 4 — what: '~하는 것'", "요구 사항", "requirement notice"),
    (70, "TOEIC", "관계대명사 5 — whose: 소유격 관계대명사", "파트너사 소개", "partner introduction"),
    (71, "TOEIC", "관계부사 1 — where: 장소", "지점과 위치", "branch notice"),
    (72, "TOEIC", "관계부사 2 — when: 시간", "일정과 기한", "timeline email"),
    (73, "TOEIC", "관계부사 3 — why/how", "이유와 방법", "process explanation"),
    (74, "TOEIC", "관계사절 — 계속적 용법: , which / , who", "뉴스레터", "company newsletter"),
    (75, "TOEIC", "비교급 1 — 원급 비교: as ~ as", "제품 비교", "comparison article"),
    (76, "TOEIC", "비교급 2 — 비교급 형태: -er/more ~", "성과 비교", "performance comparison"),
    (77, "TOEIC", "비교급 3 — 비교급 강조: much/far/even + 비교급", "시장 분석", "market analysis"),
    (78, "TOEIC", "최상급 1 — 최상급 형태: the -est/most ~", "최고 실적", "achievement report"),
    (79, "TOEIC", "최상급 2 — 최상급 표현 패턴", "순위와 평가", "ranking report"),
    (80, "TOEIC", "최상급 3 — 원급/비교급으로 최상급 표현", "업계 동향", "industry newsletter"),
    (81, "TOEIC", "부정사 1 — to부정사 명사적 용법 (주어/목적어/보어)", "목표 설정", "goal-setting email"),
    (82, "TOEIC", "부정사 2 — to부정사 형용사적 용법 (명사 수식)", "기회와 제안", "business proposal"),
    (83, "TOEIC", "부정사 3 — to부정사 부사적 용법 (목적/결과)", "방문 목적", "visit schedule"),
    (84, "TOEIC", "부정사 4 — 원형부정사: 사역동사(make/let/have) + 목적어 + 동사원형", "업무 위임", "delegation memo"),
    (85, "TOEIC", "동명사 1 — 동명사 주어와 목적어 역할", "취미와 관심사", "employee profile"),
    (86, "TOEIC", "동명사 2 — 전치사 + 동명사", "절차와 방법", "procedure guide"),
    (87, "TOEIC", "동명사 3 — 동명사 vs to부정사 (의미 차이)", "계획과 실행", "action plan"),
    (88, "TOEIC", "분사 1 — 현재분사: ~하는/~하고 있는 (능동/진행)", "진행 중인 업무", "status update"),
    (89, "TOEIC", "분사 2 — 과거분사: ~된/~해진 (수동/완료)", "완료 보고", "completion memo"),
    (90, "TOEIC", "분사 3 — 분사구문 기초: 부사절 → 분사구문 변환", "복합 업무", "complex email"),
    (91, "TOEIC", "가정법 1 — 가정법 현재: If + 현재동사, will + 동사원형", "조건과 결과", "conditional proposal"),
    (92, "TOEIC", "가정법 2 — 가정법 과거: If + 과거동사, would + 동사원형", "가상 시나리오", "scenario analysis"),
    (93, "TOEIC", "가정법 3 — 가정법 과거완료: If + had p.p., would have p.p.", "과거 회고", "retrospective report"),
    (94, "TOEIC", "가정법 4 — I wish 가정법: 현재/과거 소망", "피드백과 개선", "feedback email"),
    (95, "TOEIC", "가정법 5 — as if/as though 가정법", "비유와 표현", "descriptive email"),
    (96, "TOEIC", "명사절 1 — that절: I think that / It is ~ that", "의견과 제안", "suggestion email"),
    (97, "TOEIC", "명사절 2 — 의문사절: what/who/how/when + 완전한 문장", "정보 요청", "inquiry email"),
    (98, "TOEIC", "명사절 3 — whether/if절: ~인지 아닌지", "확인 요청", "confirmation email"),
    (99, "TOEIC", "TOEIC 핵심 문법 총정리 1 — 문장 구조, 시제, 조동사", "종합 비즈니스 1", "mixed business email"),
    (100,"TOEIC", "TOEIC 핵심 문법 총정리 2 — 관계사, 수동태, 가정법", "종합 비즈니스 2", "mixed business report"),
    # ── TOEFL Phase: Day 101~200 ────────────────────────────────
    (101,"TOEFL", "부사절 1 — 시간: when/while/before/after/until/as soon as", "생태학과 환경", "environmental science"),
    (102,"TOEFL", "부사절 2 — 이유/원인: because/since/as/now that", "심리학 기초", "psychology article"),
    (103,"TOEFL", "부사절 3 — 양보: although/even though/while/whereas", "사회학과 문화", "social science"),
    (104,"TOEFL", "부사절 4 — 조건: if/unless/provided that/as long as", "경제학 기초", "economics article"),
    (105,"TOEFL", "부사절 5 — 결과: so ~ that / such ~ that", "물리학과 에너지", "physics article"),
    (106,"TOEFL", "분사구문 1 — 시간 분사구문: When/While ~ → -ing", "생물학", "biology article"),
    (107,"TOEFL", "분사구문 2 — 이유/원인 분사구문: Because ~ → -ing", "화학 기초", "chemistry article"),
    (108,"TOEFL", "분사구문 3 — 조건/양보 분사구문", "지질학", "geology article"),
    (109,"TOEFL", "분사구문 4 — 독립분사구문: 주어가 다른 경우", "천문학", "astronomy article"),
    (110,"TOEFL", "분사구문 5 — with + 명사 + 분사 구문", "해양학", "marine science"),
    (111,"TOEFL", "도치 1 — 부정어 도치: Never/Hardly/Seldom + 조동사 + 주어", "역사 — 고대 문명", "ancient history"),
    (112,"TOEFL", "도치 2 — Only + 부사구/절 도치", "역사 — 중세 유럽", "medieval history"),
    (113,"TOEFL", "도치 3 — So/Neither/Nor 도치: 동의 표현", "역사 — 근대", "modern history"),
    (114,"TOEFL", "도치 4 — 장소/방향 부사구 도치", "역사 — 현대", "contemporary history"),
    (115,"TOEFL", "강조 1 — It is ~ that 강조구문", "고고학", "archaeology article"),
    (116,"TOEFL", "강조 2 — do/does/did 강조: 동사 강조", "인류학", "anthropology article"),
    (117,"TOEFL", "강조 3 — 재귀대명사 강조: himself/herself/itself", "언어학 기초", "linguistics article"),
    (118,"TOEFL", "생략 1 — 접속사절에서의 생략 (반복 주어/동사)", "예술사", "art history"),
    (119,"TOEFL", "생략 2 — to부정사에서의 생략: to 남기기", "음악사", "music history"),
    (120,"TOEFL", "대용 — so/not/do so: 앞 내용 대신 받기", "건축사", "architecture article"),
    (121,"TOEFL", "병렬구조 1 — 등위접속사와 병렬: A and/but/or B", "철학 기초", "philosophy article"),
    (122,"TOEFL", "병렬구조 2 — 상관접속사: both A and B / either A or B", "논리학", "logic article"),
    (123,"TOEFL", "병렬구조 3 — not only A but also B / neither A nor B", "윤리학", "ethics article"),
    (124,"TOEFL", "동격 1 — 명사의 동격: N, N / N called N", "과학사", "science history"),
    (125,"TOEFL", "동격 2 — that절 동격: the fact that / the idea that", "기술 발전", "technology history"),
    (126,"TOEFL", "명사구 수식 1 — 전치 수식: 형용사/분사 + 명사", "뇌과학", "neuroscience article"),
    (127,"TOEFL", "명사구 수식 2 — 후치 수식: 명사 + 전치사구/분사/관계절", "유전학", "genetics article"),
    (128,"TOEFL", "복합명사와 명사구 패턴", "진화론", "evolution article"),
    (129,"TOEFL", "추상명사와 구체명사의 학술적 활용", "생태계", "ecology article"),
    (130,"TOEFL", "학술 글쓰기 1 — 주장(claim)과 근거(evidence) 구조", "기후변화", "climate science"),
    (131,"TOEFL", "학술 글쓰기 2 — 정의(definition)와 설명(explanation)", "물의 순환", "earth science"),
    (132,"TOEFL", "학술 글쓰기 3 — 비교(comparison)와 대조(contrast)", "동물 행동", "zoology article"),
    (133,"TOEFL", "학술 글쓰기 4 — 원인(cause)과 결과(effect)", "인구 변화", "demography article"),
    (134,"TOEFL", "학술 글쓰기 5 — 문제(problem)와 해결(solution)", "환경 오염", "environmental policy"),
    (135,"TOEFL", "논리 접속어 1 — 추가: furthermore/moreover/in addition/besides", "사회 변화", "social science"),
    (136,"TOEFL", "논리 접속어 2 — 대조: however/nevertheless/on the other hand", "경제 이론", "economics theory"),
    (137,"TOEFL", "논리 접속어 3 — 원인결과: therefore/thus/consequently/as a result", "산업 혁명", "industrial history"),
    (138,"TOEFL", "논리 접속어 4 — 예시: for example/for instance/such as/namely", "과학적 방법", "scientific method"),
    (139,"TOEFL", "논리 접속어 5 — 요약: in conclusion/in summary/overall/to sum up", "연구 방법론", "research methodology"),
    (140,"TOEFL", "학술 어휘 1 — 연구/분석 관련 핵심 동사", "통계학 기초", "statistics article"),
    (141,"TOEFL", "학술 어휘 2 — 주장/논거 관련 표현", "인지과학", "cognitive science"),
    (142,"TOEFL", "학술 어휘 3 — 변화/발전 관련 어휘", "기술 혁신", "technology innovation"),
    (143,"TOEFL", "학술 어휘 4 — 비교/평가 관련 어휘", "교육학", "education science"),
    (144,"TOEFL", "학술 어휘 5 — 과학/기술 분야 필수 어휘", "컴퓨터 과학", "computer science"),
    (145,"TOEFL", "복잡한 문장 1 — 중문: 독립절 + 독립절", "의학 발전", "medical history"),
    (146,"TOEFL", "복잡한 문장 2 — 복문: 주절 + 종속절", "공중 보건", "public health"),
    (147,"TOEFL", "복잡한 문장 3 — 중복문: 중문 + 복문 결합", "약학과 치료", "pharmacology article"),
    (148,"TOEFL", "긴 주어 처리 — 명사구/명사절이 주어인 경우", "신경과학", "neurology article"),
    (149,"TOEFL", "삽입구와 삽입절 — 문장 중간의 부가 정보", "면역학", "immunology article"),
    (150,"TOEFL", "동사구 패턴 1 — 자주 쓰이는 동사구 (phrasal verbs)", "영양학", "nutrition science"),
    (151,"TOEFL", "동사구 패턴 2 — 학술 텍스트의 동사구 패턴", "스포츠 과학", "sports science"),
    (152,"TOEFL", "전치사구 패턴 — 학술 텍스트의 전치사구 활용", "물리치료학", "physical science"),
    (153,"TOEFL", "형용사절 심화 — 제한적/비제한적 관계사절 비교", "도시 계획", "urban planning"),
    (154,"TOEFL", "명사절 심화 — 복잡한 명사절 패턴 분석", "지리학", "geography article"),
    (155,"TOEFL", "수일치 1 — 기본 원칙: 단수 주어 → 단수 동사", "인구지리학", "population geography"),
    (156,"TOEFL", "수일치 2 — 주의할 경우: 수식어구/접속사/집합명사", "경제지리학", "economic geography"),
    (157,"TOEFL", "시제 일치 — 주절 과거 → 종속절 시제 변화", "문화 지리학", "cultural geography"),
    (158,"TOEFL", "화법 1 — 직접화법: 인용부호 사용", "사회 심리학", "social psychology"),
    (159,"TOEFL", "화법 2 — 간접화법: that절로 전환", "발달 심리학", "developmental psychology"),
    (160,"TOEFL", "화법 3 — 간접화법 전환 규칙 (시제/대명사 변화)", "행동 심리학", "behavioral psychology"),
    (161,"TOEFL", "TOEFL RC 문제 유형 1 — 사실 확인 문제 (Factual Information)", "자연과학 종합", "natural science"),
    (162,"TOEFL", "TOEFL RC 문제 유형 2 — 추론 문제 (Inference)", "사회과학 종합", "social science"),
    (163,"TOEFL", "TOEFL RC 문제 유형 3 — 어휘 문제 (Vocabulary)", "인문학 종합", "humanities article"),
    (164,"TOEFL", "TOEFL RC 문제 유형 4 — 주제/목적 문제 (Main Idea)", "역사 종합", "history article"),
    (165,"TOEFL", "TOEFL RC 문제 유형 5 — 문장 삽입 문제 (Sentence Insertion)", "기술 종합", "technology article"),
    (166,"TOEFL", "TOEFL 지문 유형 1 — 자연과학: 실전 지문 분석", "천문학 심화", "astronomy research"),
    (167,"TOEFL", "TOEFL 지문 유형 2 — 사회과학: 실전 지문 분석", "경제학 심화", "economics research"),
    (168,"TOEFL", "TOEFL 지문 유형 3 — 역사/문화: 실전 지문 분석", "문화사 심화", "cultural history"),
    (169,"TOEFL", "TOEFL 지문 유형 4 — 예술/인문학: 실전 지문 분석", "예술 이론", "art theory"),
    (170,"TOEFL", "TOEFL 지문 유형 5 — 기술/공학: 실전 지문 분석", "공학 기초", "engineering article"),
    (171,"TOEFL", "복잡한 수동태 구조 심화", "의학 연구", "medical research"),
    (172,"TOEFL", "복잡한 관계사절 심화", "사회 연구", "social research"),
    (173,"TOEFL", "복합 가정법 — 혼합 가정법과 특수 가정법", "과학 실험", "science experiment"),
    (174,"TOEFL", "학술적 표현 심화 1 — 논문에서 자주 쓰는 표현", "연구 방법 1", "research methods"),
    (175,"TOEFL", "학술적 표현 심화 2 — 인용과 출처 표현", "연구 방법 2", "academic writing"),
    (176,"TOEFL", "오답 패턴 1 — 품사 혼동 (명사/형용사/부사 혼동)", "언어학 심화", "linguistics research"),
    (177,"TOEFL", "오답 패턴 2 — 시제 혼동 (현재완료 vs 과거 등)", "역사 언어학", "historical linguistics"),
    (178,"TOEFL", "오답 패턴 3 — 수일치 오류 (주어-동사 불일치)", "사회언어학", "sociolinguistics"),
    (179,"TOEFL", "오답 패턴 4 — 관계사 혼동 (who/which/that/whose)", "심리언어학", "psycholinguistics"),
    (180,"TOEFL", "오답 패턴 5 — 전치사 혼동 (in/on/at/for/by)", "응용 언어학", "applied linguistics"),
    (181,"TOEFL", "TOEFL 고급 어휘 1 — 학술 명사 필수 50개", "철학 심화", "philosophy research"),
    (182,"TOEFL", "TOEFL 고급 어휘 2 — 학술 동사 필수 50개", "윤리학 심화", "ethics research"),
    (183,"TOEFL", "TOEFL 고급 어휘 3 — 학술 형용사/부사 필수 50개", "정치학", "political science"),
    (184,"TOEFL", "TOEFL 고급 어휘 4 — 과학/기술 분야 전문 어휘", "국제 관계", "international relations"),
    (185,"TOEFL", "TOEFL 고급 어휘 5 — 인문/사회 분야 전문 어휘", "문화 연구", "cultural studies"),
    (186,"TOEFL", "실전 TOEFL RC 연습 1 — 자연과학 지문 + 전략", "자연과학 실전", "natural science practice"),
    (187,"TOEFL", "실전 TOEFL RC 연습 2 — 사회과학 지문 + 전략", "사회과학 실전", "social science practice"),
    (188,"TOEFL", "실전 TOEFL RC 연습 3 — 역사 지문 + 전략", "역사 실전", "history practice"),
    (189,"TOEFL", "실전 TOEFL RC 연습 4 — 예술/인문 지문 + 전략", "인문 실전", "humanities practice"),
    (190,"TOEFL", "실전 TOEFL RC 연습 5 — 기술/공학 지문 + 전략", "기술 실전", "technology practice"),
    (191,"TOEFL", "종합 복습 1 — 문장 구조와 5형식", "종합 복습 어휘 1", "comprehensive review"),
    (192,"TOEFL", "종합 복습 2 — 시제 완전 정복", "종합 복습 어휘 2", "comprehensive review"),
    (193,"TOEFL", "종합 복습 3 — 조동사와 가정법", "종합 복습 어휘 3", "comprehensive review"),
    (194,"TOEFL", "종합 복습 4 — 관계사 완전 정복", "종합 복습 어휘 4", "comprehensive review"),
    (195,"TOEFL", "종합 복습 5 — 수동태와 분사 완전 정복", "종합 복습 어휘 5", "comprehensive review"),
    (196,"TOEFL", "종합 복습 6 — 접속사와 전치사 완전 정복", "종합 복습 어휘 6", "comprehensive review"),
    (197,"TOEFL", "종합 복습 7 — 비교 구문 완전 정복", "종합 복습 어휘 7", "comprehensive review"),
    (198,"TOEFL", "종합 복습 8 — 도치와 강조 완전 정복", "종합 복습 어휘 8", "comprehensive review"),
    (199,"TOEFL", "최종 정리 1 — TOEIC 핵심 문법 & 전략 총정리", "TOEIC 핵심 어휘", "toeic final review"),
    (200,"TOEFL", "최종 정리 2 — TOEFL 핵심 문법 & 전략 총정리", "TOEFL 핵심 어휘", "toefl final review"),
]

CURRICULUM = {row[0]: {"phase": row[1], "grammar": row[2], "vocab_theme": row[3], "passage_type": row[4]}
              for row in CURRICULUM_RAW}

JSON_SCHEMA = """{
  "day": <integer>,
  "phase": "<TOEIC or TOEFL>",
  "passage": {
    "title": "<title string>",
    "text": "<passage text 150-250 words>",
    "questions": [
      {"number": 1, "question": "<Q1>", "options": ["A) ...", "B) ...", "C) ...", "D) ..."]},
      {"number": 2, "question": "<Q2>", "options": ["A) ...", "B) ...", "C) ...", "D) ..."]},
      {"number": 3, "question": "<Q3>", "options": ["A) ...", "B) ...", "C) ...", "D) ..."]}
    ]
  },
  "grammar": {
    "title": "<grammar topic title>",
    "korean_explanation": "<detailed Korean explanation>",
    "english_explanation": "<English explanation>",
    "examples": ["<example 1>", "<example 2>", "<example 3>"],
    "quiz": [
      {"number": 1, "question": "<Q>", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "<A/B/C/D>", "explanation": "<Korean explanation>"},
      {"number": 2, "question": "<Q>", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "<A/B/C/D>", "explanation": "<Korean explanation>"},
      {"number": 3, "question": "<Q>", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "<A/B/C/D>", "explanation": "<Korean explanation>"}
    ]
  },
  "vocabulary": [
    <exactly 20 objects: first 10 with category "TOEIC", then 10 with category "TOEFL">,
    each object: {"word": "...", "part_of_speech": "...", "korean_meaning": "...", "english_meaning": "...", "example": "...", "synonyms": [...], "antonyms": [...], "category": "TOEIC or TOEFL"}
  ],
  "answers": {
    "passage": [
      {"number": 1, "answer": "<A/B/C/D>", "explanation": "<Korean>"},
      {"number": 2, "answer": "<A/B/C/D>", "explanation": "<Korean>"},
      {"number": 3, "answer": "<A/B/C/D>", "explanation": "<Korean>"}
    ],
    "vocab_quiz": [
      <exactly 5 quiz items, each: {"number": 1-5, "question": "...", "options": ["A)..","B)..","C)..","D).."], "answer": "<A/B/C/D>", "explanation": "<Korean>"}>
    ]
  }
}"""


def build_prompt(day: int, info: dict) -> str:
    return f"""You are an expert Korean English teacher creating TOEIC/TOEFL study content.

Generate complete study content for Day {day}.

Specifications:
- Day: {day}
- Phase: {info['phase']}
- Grammar Topic: {info['grammar']}
- Vocabulary Theme: {info['vocab_theme']}
- Passage Type: {info['passage_type']}

REQUIREMENTS:

1. PASSAGE ({info['phase']} style, {info['passage_type']}, 150-250 words):
   - {'Business/professional context' if info['phase'] == 'TOEIC' else 'Academic/scholarly context'}
   - 3 comprehension questions with 4 answer choices (A, B, C, D)
   - Questions should test: main purpose/topic, specific detail, and inference

2. GRAMMAR: "{info['grammar']}"
   - Korean explanation: VERY BEGINNER-FRIENDLY. Assume zero grammar knowledge. Use simple Korean. Include ❌ wrong and ✅ correct examples. Explain WHY.
   - English explanation: Clear and concise
   - 3 annotated examples showing structure (e.g., "The manager(주어) works(동사) hard(부사).")
   - 3 quiz questions testing this specific grammar point

3. VOCABULARY (exactly 20 words):
   - First 10: TOEIC words related to "{info['vocab_theme']}" theme
   - Next 10: TOEFL academic vocabulary related to "{info['vocab_theme'] if info['phase'] == 'TOEFL' else 'academic concepts'}"
   - Each word needs: word, part_of_speech, korean_meaning, english_meaning, example sentence, synonyms (2-3), antonyms (0-2, use [] if none), category

4. ANSWERS:
   - Correct answers for all 3 passage questions with Korean explanations (cite the passage text)
   - 5 vocabulary quiz questions (mix of: Korean↔English, fill-in-blank, synonym/antonym matching)

Return ONLY valid JSON. No markdown. No explanation. Just the JSON object matching this schema exactly:
{JSON_SCHEMA}"""


def generate_day(client: anthropic.Anthropic, day: int) -> dict:
    info = CURRICULUM[day]
    prompt = build_prompt(day, info)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    data = json.loads(raw)
    data["day"] = day  # ensure correct day number
    return data


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY 환경변수가 없습니다.")
        return 1

    client = anthropic.Anthropic(api_key=api_key)
    CONTENT_DIR.mkdir(exist_ok=True)

    start_day = int(os.environ.get("START_DAY", "2"))
    end_day   = int(os.environ.get("END_DAY",   "200"))

    print(f"Day {start_day} ~ {end_day} 콘텐츠 생성 시작...")

    success, failed = 0, []

    for day in range(start_day, end_day + 1):
        output_path = CONTENT_DIR / f"day_{day:03d}.json"

        if output_path.exists():
            print(f"Day {day:3d}: 이미 존재 — 건너뜀")
            continue

        if day not in CURRICULUM:
            print(f"Day {day:3d}: 커리큘럼 없음 — 건너뜀")
            continue

        print(f"Day {day:3d}: 생성 중...", end=" ", flush=True)

        for attempt in range(3):
            try:
                data = generate_day(client, day)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("✓")
                success += 1
                break
            except json.JSONDecodeError as e:
                if attempt < 2:
                    print(f"JSON 오류, 재시도 {attempt + 1}...", end=" ", flush=True)
                    time.sleep(3)
                else:
                    print(f"✗ JSON 파싱 실패: {e}")
                    failed.append(day)
            except Exception as e:
                if attempt < 2:
                    print(f"오류, 재시도 {attempt + 1}...", end=" ", flush=True)
                    time.sleep(5)
                else:
                    print(f"✗ 실패: {e}")
                    failed.append(day)

        time.sleep(1.5)  # rate limit 방지

    print(f"\n완료! 성공: {success}개, 실패: {len(failed)}개")
    if failed:
        print(f"실패한 날: {failed}")
        print("다시 실행하려면: START_DAY=<day> END_DAY=<day> python generate_content.py")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
