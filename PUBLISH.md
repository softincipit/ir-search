# 대시보드 공유하기 (GitHub Pages)

공유 주소는 아래 형태가 됩니다:

**https://djfksjd.github.io/ir-search/**

## 1) 최초 1회 설정

터미널(또는 Git Bash)에서 `ir-search` 폴더로 이동한 뒤:

```bash
git add .gitignore docs .github start.bat PUBLISH.md
git commit -m "feat: publish dashboard via GitHub Pages + daily auto-update"
git push
```

## 2) Pages 켜기

GitHub 저장소 → **Settings → Pages**

- Source: `Deploy from a branch`
- Branch: `main` / 폴더: **`/docs`** → Save

1~2분 뒤 위 주소로 접속되면 끝입니다. 링크만 보내면 누구나 열람 가능합니다.
(저장소가 Private이면 Pages도 안 열리니, Public으로 두거나 GitHub Pro가 필요합니다.)

## 3) Actions 권한 확인

Settings → **Actions → General → Workflow permissions**
→ **Read and write permissions** 선택 후 Save.
(봇이 갱신된 데이터를 커밋해야 하므로 필요합니다.)

## 4) 자동 갱신

`.github/workflows/update-data.yml` 이 **3시간마다** 크롤러를 돌려
`docs/all.jsonl` 을 갱신하고 자동 커밋합니다 → Pages가 자동 재배포됩니다.

- 즉시 한 번 돌려보려면: 저장소 → **Actions → Update K-Startup data → Run workflow**
- 주기 변경: yml 파일의 `cron: "0 0 * * *"` 수정 (UTC 기준)
- 안전장치: 수집 건수가 10건 미만이면(사이트 차단·장애 등) 기존 데이터를 덮어쓰지 않습니다.

> 참고: K-Startup이 GitHub 서버 IP를 차단할 가능성이 있습니다.
> Actions 첫 실행 로그에서 수집 건수를 꼭 확인하세요. 차단된다면 로컬 PC에서
> `start.bat` 실행 후 `git add -f docs/all.jsonl && git commit && git push` 로 갱신하면 됩니다.

## 로컬에서 보기

`start.bat` 더블클릭 → 크롤링 후 http://localhost:8080/ 자동 오픈.
(공유 페이지와 완전히 같은 파일 `docs/index.html` 을 띄웁니다.)
