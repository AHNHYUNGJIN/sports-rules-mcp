#!/usr/bin/env python3
"""체육 수업용 스포츠 규칙 검색 MCP 서버 (HTTP 모드)"""

import os
import json
from mcp.server.fastmcp import FastMCP
from sports_rules_mcp.server import SPORTS_DATABASE, LESSON_PLAN_DATA, find_sport

mcp = FastMCP("sports-rules-mcp")


@mcp.tool()
def list_sports() -> str:
    """지원하는 스포츠 종목 목록을 반환합니다"""
    lines = ["## 지원 스포츠 종목 목록\n"]
    for sport in SPORTS_DATABASE.values():
        p = sport["players"]["official"]
        lines.append(f"- **{sport['name']}** ({sport['english']}) | 선수: {p}명 | 경기장: {sport['field']}")
    return "\n".join(lines)


@mcp.tool()
def get_sport_rules(sport_name: str) -> str:
    """특정 스포츠 종목의 기본 규칙과 반칙 정보를 조회합니다

    Args:
        sport_name: 종목명 (예: 축구, 농구, 배구, 야구, 피클볼, 탁구, 배드민턴, 티볼, 테니스)
    """
    sport = find_sport(sport_name)
    if not sport:
        return f"'{sport_name}' 종목을 찾을 수 없습니다. list_sports 도구로 지원 종목을 확인하세요."
    lines = [f"## {sport['name']} ({sport['english']}) 기본 규칙\n"]
    lines.append(f"**선수 수:** {sport['players']['official']}명")
    lines.append(f"**경기 시간:** {sport['duration']}")
    lines.append(f"**경기장:** {sport['field']}\n")
    lines.append("### 기본 규칙")
    for i, rule in enumerate(sport["basic_rules"], 1):
        lines.append(f"{i}. {rule}")
    lines.append("\n### 반칙 (파울)")
    for foul in sport["fouls"]:
        lines.append(f"- {foul}")
    return "\n".join(lines)


@mcp.tool()
def get_modified_rules(sport_name: str, grade: str) -> str:
    """학교 체육 수업에 맞게 변형된 규칙을 조회합니다

    Args:
        sport_name: 종목명
        grade: 학교급 (초등, 중등, 고등)
    """
    sport = find_sport(sport_name)
    if not sport:
        return f"'{sport_name}' 종목을 찾을 수 없습니다."
    modified = sport["modified_for_class"].get(grade)
    if not modified:
        return f"{grade} 변형 규칙 정보가 없습니다."
    lines = [f"## {sport['name']} — {grade} 수업용 변형 규칙\n"]
    lines.append(f"**인원:** {modified['players']}")
    lines.append(f"**시간:** {modified['duration']}\n")
    lines.append("### 변형 사항")
    for mod in modified["modifications"]:
        lines.append(f"- {mod}")
    return "\n".join(lines)


@mcp.tool()
def get_referee_guide(sport_name: str) -> str:
    """특정 스포츠의 심판 방법과 신호 동작을 조회합니다

    Args:
        sport_name: 종목명
    """
    sport = find_sport(sport_name)
    if not sport:
        return f"'{sport_name}' 종목을 찾을 수 없습니다."
    lines = [f"## {sport['name']} 심판 방법\n"]
    for guide in sport["referee_guide"]:
        lines.append(f"- {guide}")
    return "\n".join(lines)


@mcp.tool()
def search_sports(keyword: str) -> str:
    """키워드로 스포츠 종목을 검색합니다

    Args:
        keyword: 검색 키워드 (예: 네트, 라켓, 이닝)
    """
    results = []
    for sport in SPORTS_DATABASE.values():
        if keyword.lower() in json.dumps(sport, ensure_ascii=False).lower():
            results.append(f"- **{sport['name']}** ({sport['english']})")
    if results:
        return f"## '{keyword}' 검색 결과\n\n" + "\n".join(results)
    return f"'{keyword}'에 해당하는 종목을 찾을 수 없습니다."


@mcp.tool()
def generate_lesson_plan(sport_name: str, grade: str, total_sessions: int = 8, students_count: int = 30) -> str:
    """특정 종목과 학교급에 맞는 체육 수업 계획서를 생성합니다

    Args:
        sport_name: 종목명
        grade: 학교급 (초등, 중등, 고등)
        total_sessions: 총 차시 수 (기본값: 8)
        students_count: 학생 수 (기본값: 30)
    """
    sport = find_sport(sport_name)
    if not sport:
        return f"'{sport_name}' 종목을 찾을 수 없습니다."
    plan = LESSON_PLAN_DATA.get(sport["name"])
    if not plan:
        return f"'{sport_name}' 수업 계획 데이터가 없습니다."
    modified = sport["modified_for_class"].get(grade, {})
    sessions = plan["sessions"].get(grade, [])
    assessment = plan["assessment"].get(grade, [])

    lines = [f"# {sport['name']} 체육 수업 계획서 ({grade})\n"]
    lines.append("## 기본 정보\n")
    lines.append("| 항목 | 내용 |")
    lines.append("|------|------|")
    lines.append(f"| 대상 | {grade} |")
    lines.append(f"| 총 차시 | {total_sessions}차시 |")
    lines.append(f"| 학생 수 | {students_count}명 |")
    lines.append(f"| 경기 인원 | {modified.get('players', '-')} |")
    lines.append(f"| 경기장 | {sport['field']} |\n")
    lines.append("## 학습 목표\n")
    for i, skill in enumerate(plan["key_skills"], 1):
        lines.append(f"{i}. {skill}의 기본 기술을 익히고 경기에 적용할 수 있다.")
    lines.append("\n## 준비물\n")
    for item in plan["equipment"]:
        lines.append(f"- {item}")
    lines.append("\n## ⚠️ 안전 지도 사항\n")
    for safety in plan["safety"]:
        lines.append(f"- {safety}")
    lines.append("\n## 차시별 수업 계획\n")
    lines.append("| 차시 | 주제 | 주요 내용 |")
    lines.append("|------|------|-----------|")
    for s in sessions:
        lines.append(f"| {s['range']} | {s['topic']} | {s['content']} |")
    lines.append("\n## 기본 수업 흐름 (매 차시 50분 기준)\n")
    lines.append("### 도입 (10분)")
    lines.append("- 출석 확인 및 용구 배부")
    lines.append("- 준비운동 (스트레칭 5분 + 동적 워밍업 5분)")
    lines.append("- 전 차시 복습 및 오늘 학습 목표 제시\n")
    lines.append("### 전개 (30분)")
    lines.append(f"- 기능 연습 (15분): {', '.join(plan['key_skills'][:3])} 기술 집중 연습")
    lines.append(f"- 게임 적용 (15분): {modified.get('players', '팀')} {modified.get('duration', '변형 경기')}\n")
    lines.append("### 정리 (10분)")
    lines.append("- 정리운동 (스트레칭 5분)")
    lines.append("- 학습 내용 정리 및 질의응답")
    lines.append("- 다음 차시 예고 및 용구 정리")
    lines.append("\n## 평가 기준\n")
    lines.append("| 평가 항목 | 내용 |")
    lines.append("|-----------|------|")
    for i, item in enumerate(assessment, 1):
        lines.append(f"| 평가 {i} | {item} |")
    lines.append("\n## 변형 규칙 요약\n")
    for mod in modified.get("modifications", []):
        lines.append(f"- {mod}")
    return "\n".join(lines)


# uvicorn이 직접 참조할 ASGI 앱
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
