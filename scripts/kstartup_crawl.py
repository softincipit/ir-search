#!/usr/bin/env python3
"""K-Startup 사업공고 크롤러 — ir-search 스킬 동봉 스크립트.

공개 공고 페이지(모집중)만 접근한다. 로그인·비공개 영역 접근 없음.

사용법:
  # 모집중 공고 전수 수집 (JSONL)
  python3 kstartup_crawl.py list -o kstartup_all.jsonl

  # 상세공고 텍스트 저장 (자격요건 검증용)
  python3 kstartup_crawl.py detail 178481 178215 -o details/

의존성: curl_cffi>=0.15 (권장, TLS 지문 통과용).
미설치 시 표준 urllib로 시도하며, 차단되면 설치 안내를 출력한다.
"""
import argparse
import html as htmllib
import json
import os
import re
import sys
import time

BASE = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
DETAIL_URL = BASE + "?schM=view&pbancSn={sn}"
DELAY = 0.3  # 요청 간 최소 지연 (서버 예의)


def make_fetcher():
    """curl_cffi 우선, 없으면 urllib 폴백."""
    try:
        from curl_cffi import requests as cr

        sess = cr.Session(impersonate="safari")

        def fetch(url):
            r = sess.get(url, timeout=30)
            return r.status_code, r.text

        return fetch, "curl_cffi"
    except ImportError:
        import urllib.request

        def fetch(url):
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
                    )
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")

        return fetch, "urllib"


def parse_list(html):
    """목록 페이지에서 공고 레코드 추출.

    본목록(id=bizPbancList)만 파싱한다 — 상단 캐러셀에 추천 공고가
    중복 노출되므로 캐러셀은 버린다. 실제 목록은 페이지당 15건.
    """
    items = []
    parts = html.split('id="bizPbancList"', 1)
    if len(parts) < 2:
        return items
    body = parts[1]
    for blk in re.split(r'<li class="notice">|<li >|<li>', body)[1:]:
        m = re.search(r"go_view\((\d+)\)", blk)
        if not m:
            continue

        def g(pat):
            mm = re.search(pat, blk)
            return re.sub(r"\s+", " ", mm.group(1)).strip() if mm else ""

        lists = [
            re.sub(r"\s+", " ", x).strip()
            for x in re.findall(r'<span class="list"><i[^>]*></i>([^<]+)</span>', blk)
        ]

        def pick(prefix):
            for x in lists:
                if x.startswith(prefix):
                    return x.replace(prefix, "").strip()
            return ""

        items.append(
            {
                "pbancSn": m.group(1),
                "category": htmllib.unescape(
                    g(r'<span class="flag type\d+">\s*([^<]+)</span>')
                ),
                "dday": g(r'<span class="flag day">\s*([^<]+)</span>'),
                "title": htmllib.unescape(g(r'<p class="tit">\s*([^<]+)')),
                "program": htmllib.unescape(lists[0]) if lists else "",
                "org": htmllib.unescape(lists[1]) if len(lists) > 1 else "",
                "start": pick("시작일자"),
                "deadline": pick("마감일자"),
                "agency_type": g(r'<span class="flag_agency">\s*([^<]+)</span>'),
                "url": DETAIL_URL.format(sn=m.group(1)),
            }
        )
    return items


def cmd_list(args):
    fetch, backend = make_fetcher()
    print(f"[ir-search] fetch backend: {backend}", file=sys.stderr)
    if backend == "urllib":
        print(
            "[ir-search] 권장: pip install 'curl_cffi>=0.15' (TLS 지문 차단 회피)",
            file=sys.stderr,
        )
    seen = {}
    page = 1
    while page <= args.max_pages:
        status, html = fetch(f"{BASE}?page={page}&schStr=&pbancEndYn=N")
        if status != 200:
            print(f"[ir-search] page {page}: HTTP {status} — 중단", file=sys.stderr)
            if backend == "urllib" and status in (403, 412):
                print(
                    "[ir-search] 차단으로 보임. pip install 'curl_cffi>=0.15' 후 재시도하세요.",
                    file=sys.stderr,
                )
            break
        items = parse_list(html)
        new = [i for i in items if i["pbancSn"] not in seen]
        for i in items:
            seen[i["pbancSn"]] = i
        print(
            f"[ir-search] page {page}: {len(items)}건 파싱, 신규 {len(new)}건, 누적 {len(seen)}건",
            file=sys.stderr,
        )
        if not items or not new:
            break  # 마지막 페이지 다음은 캐러셀만 남음 → 신규 0건으로 종료
        page += 1
        time.sleep(DELAY)
    with open(args.output, "w", encoding="utf-8") as f:
        for i in seen.values():
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    print(f"[ir-search] 저장: {args.output} ({len(seen)}건)", file=sys.stderr)


def strip_html(text):
    text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", text)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = htmllib.unescape(text)
    return re.sub(r"\n\s*\n+", "\n", text)


def cmd_detail(args):
    fetch, backend = make_fetcher()
    os.makedirs(args.output, exist_ok=True)
    for sn in args.pbancSn:
        if not sn.isdigit():
            print(f"[ir-search] 잘못된 공고번호 무시: {sn}", file=sys.stderr)
            continue
        try:
            status, html = fetch(DETAIL_URL.format(sn=sn))
            if status != 200:
                print(f"[ir-search] {sn}: HTTP {status}", file=sys.stderr)
                continue
            path = os.path.join(args.output, f"{sn}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(strip_html(html))
            print(f"[ir-search] {sn}: 저장 → {path}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 — 개별 실패는 건너뛰고 계속
            print(f"[ir-search] {sn}: 오류 {e}", file=sys.stderr)
        time.sleep(DELAY)


def main():
    ap = argparse.ArgumentParser(description="K-Startup 공고 크롤러 (ir-search)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="모집중 공고 전수 수집")
    p_list.add_argument("-o", "--output", default="kstartup_all.jsonl")
    p_list.add_argument("--max-pages", type=int, default=40)
    p_list.set_defaults(func=cmd_list)

    p_det = sub.add_parser("detail", help="상세공고 텍스트 저장")
    p_det.add_argument("pbancSn", nargs="+", help="공고번호(들)")
    p_det.add_argument("-o", "--output", default="details")
    p_det.set_defaults(func=cmd_detail)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
