# 기술 퀴즈

## 프로젝트 개요

- 터미널에서 네 개의 선택지 중 정답을 고르는 Python 게임
- 한 판에 풀 문제 수를 정하고, 모르는 문제에서는 힌트를 열 수 있음
- 직접 등록한 문제와 플레이 기록은 다음 실행에서도 이어짐

## 퀴즈 주제 선정 이유

- AI 에이전트, AI 기반 소프트웨어 개발, 로봇 시뮬레이션, 프로그래머블 머니, 양자 컴퓨팅을 한 문제씩 다룸
- 낯선 기술 용어를 실제 쓰임과 연결해 익힐 수 있도록 작동 원리나 적용 사례를 고르는 문제로 구성

## 실행 방법

- Python 3.10 이상과 표준 라이브러리 사용
- 프로젝트 폴더에서 Python 버전을 확인한 뒤 게임 실행

```sh
python --version
python quiz_game.py
```

- 같은 폴더에서 `python -m unittest -v`로 테스트 실행
- 테스트용 게임 데이터는 임시 폴더에 생성

## 기능 목록

- **1. 퀴즈 풀기**

  - 원하는 문제 수를 고르면 한 판에서 중복 없이 무작위로 출제
  - `1`~`4` 중 하나로 답하면 정답을 바로 확인할 수 있음

- **2. 퀴즈 추가**

  - 문제, 선택지 네 개, 정답 번호, 힌트를 차례로 입력
  - 힌트는 `Enter`로 건너뛸 수 있으며 등록을 마치면 즉시 저장

- **3. 퀴즈 목록**

  - 등록 순서대로 문제 번호와 내용 확인
  - 문제를 모두 삭제하면 다음 실행에서도 빈 목록 유지

- **4. 최고 점수와 플레이 기록**

  - 최고 점수와 모든 완주 기록 확인
  - 회차별 완료 시각, 문제 수, 정답 수, 힌트 사용 수, 점수를 최근 순으로 조회
  - 첫 완주 전에는 플레이 기록이 없다는 안내 표시

- **5. 종료**

  - 저장하지 못한 변경이 있으면 저장을 다시 시도한 뒤 종료

- **6. 퀴즈 삭제**

  - 목록에서 문제 번호를 고르면 해당 문제를 삭제하고 즉시 저장
  - `0`을 입력하면 삭제 취소

### 힌트와 점수

- 정답 하나당 2점
- `h` 또는 `힌트`로 힌트를 열면 해당 문제에서 한 번만 1점 차감
- 등록된 힌트가 없는 문제는 힌트를 요청해도 점수 차감 없음
- 합계의 최솟값은 0점이며, 합계를 만점으로 나눠 100을 곱한 뒤 Python의 `round`로 반올림
- 두 문제를 모두 맞히고 한 문제에서 힌트를 쓰면 4점 만점에 3점, 최종 75점

### 입력과 중단 처리

- 숫자 입력은 앞뒤 공백을 제거한 뒤 검사
- 빈 입력, 문자, 범위 밖 번호는 같은 단계에서 다시 입력 가능
- `Ctrl+C`나 입력 종료(EOF)로 중단하면 작성 중인 문제와 미완주 회차는 기록에서 제외

## 파일 구조

```text
Python_Git/
├── quiz_game.py       # 실행 진입점과 QuizGame 클래스, 메뉴 및 게임 진행
├── quiz.py            # Quiz 클래스, 선택지 출력과 정답 판정
├── quiz_storage.py    # JSON 검증, 동시 변경 병합과 파일 저장
├── quiz_list.json     # 첫 실행과 복구에 쓰는 기본 문제 5개
├── state.json         # 실행하면 생성되는 개인 퀴즈와 점수
├── test_quiz_game.py  # 콘솔과 저장 동작을 검증하는 unittest 테스트
├── docs/screenshots/  # 실행 환경과 게임 화면
├── .gitignore         # 개인 상태, 잠금·임시 파일과 Python 캐시 제외
└── README.md
```

## 데이터 파일

- `state.json`은 `quiz_game.py`와 같은 폴더에 UTF-8로 저장
- 첫 실행이나 JSON 손상 시 `quiz_list.json`에서 기본 문제를 불러오고 최고 점수와 플레이 기록 초기화
- 저장 파일을 읽을 권한이 없으면 안내 후 메모리에서 플레이 가능

| 필드 | 형식과 의미 |
| --- | --- |
| `quizzes` | 등록 순서대로 저장한 문제 배열(빈 배열 `[]` 허용) |
| `quizzes[].question`, `choices` | 문제 문자열과 비어 있지 않은 선택지 문자열 네 개 |
| `quizzes[].answer`, `hint` | 1~4 사이의 정답 번호와 힌트 문자열(힌트가 없으면 `""`) |
| `best_score` | 첫 완주 전에는 `null`, 이후에는 완주한 게임의 최고 점수(0~100점) |
| `history[].played_at` | 완료 시각을 현지 시각과 UTC 오프셋으로 기록한 ISO 8601 문자열 |
| `history[].total`, `correct`, `hints_used`, `score` | 해당 회차의 문제 수, 정답 수, 힌트를 연 문제 수, 100점 환산 점수 |

- 완주한 순서대로 `history` 배열 끝에 회차 기록 추가
- 같은 폴더의 임시 파일에 쓰기를 마친 뒤 `state.json` 교체
- 여러 터미널에서 동시에 저장할 때는 `.state.lock`으로 쓰기 순서를 조정해 각 실행에서 추가한 문제와 점수 보존

## 실행 화면

### 개발 환경 및 시작

[Python·Git 설정](docs/screenshots/environment.png)

```text
Python_Git $ python --version
Python 3.10.20
Python_Git $ git --version
git version 2.25.1
Python_Git $ git rev-parse --show-toplevel
/root/Python_Git
Python_Git $ git branch --show-current
main
Python_Git $ git config --get user.name
eunhye0323
Python_Git $
```

[첫 실행 메뉴](docs/screenshots/menu.png)

```text
Python_Git $ python quiz_game.py
첫 실행입니다. 기본 퀴즈를 불러옵니다.

기술 퀴즈 | 메뉴
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 최고 점수와 플레이 기록
5. 종료
6. 퀴즈 삭제
메뉴 선택 (1~6):
```

### 문제 등록 및 조회

[퀴즈 추가](docs/screenshots/add_quiz.png)

```text
메뉴 선택 (1~6): 2

새 퀴즈 등록
문제: Git에서 두 브랜치의 변경을 합치는 명령은?
선택지 1: git clone
선택지 2: git status
선택지 3: git merge
선택지 4: git log
정답 번호 (1~4): 3
힌트 (없으면 Enter): 각 브랜치의 커밋을 하나의 이력으로 모읍니다.
퀴즈를 추가했습니다. 현재 6개입니다.
```

[추가 후 목록](docs/screenshots/list.png)

```text
메뉴 선택 (1~6): 3

등록된 퀴즈 목록 (총 6개)
  1. Agentic AI의 핵심 특징으로 가장 적절한 것은?
  2. 기존 AIDD(AI-Driven Development)와 비교한 AI-Native Software Engineering의 차이로 옳은 것은?
  3. Sim2Real에서 시뮬레이션과 현실 사이의 물리적 차이를 줄이기 위해 마찰·질량·조명 등 환경 조건을 무작위로 바꾸는 기법은?
  4. AI Agent 시대에 스테이블코인이 구현하는 핵심 금융 인프라로 기대되는 'Programmable money'의 정의로 옳은 것은?
  5. 양자 컴퓨팅 본격 상용화의 분기점이 될 것으로 전망되는 것은?
  6. Git에서 두 브랜치의 변경을 합치는 명령은?
```

### 힌트 사용 및 점수 유지

[힌트를 사용한 풀이](docs/screenshots/play.png)

```text
메뉴 선택 (1~6): 1
풀 문제 수 (1~6): 1
정답은 2점, 힌트를 열면 문제당 한 번 1점 차감합니다. 결과는 100점으로 환산합니다.

[문제 1/1]
기존 AIDD(AI-Driven Development)와 비교한 AI-Native Software Engineering의 차이로 옳은 것은?
  1. 테스트 자동화 단계에만 AI를 적용한다
  2. 요구사항 정의부터 배포·운영까지 SDLC(Software Development Life Cycle) 전 과정을 포괄한다
  3. 개발자를 완전히 대체하는 것을 목표로 한다
  4. 설계 단계에서만 AI를 보조 도구로 사용한다
정답 번호 (1~4, h=힌트): h
힌트: 요구사항을 정하는 시점과 서비스를 운영하는 시점에 공통으로 적용할 수 있는지 살펴보세요.
정답 번호 (1~4, h=힌트): 2
정답입니다!

결과: 1문제 중 1문제 정답 · 힌트 1회 · 50점
새로운 최고 점수입니다!
```

[재실행 후 최고 점수와 기록](docs/screenshots/score.png)

```text
메뉴 선택 (1~6): 4

최고 점수: 50점
플레이 기록 2회 (최근 순)
  2026-11-22 12:12:15+00:00 | 1문제 중 0문제 정답 | 힌트 0회 | 0점
  2026-11-22 12:12:15+00:00 | 1문제 중 1문제 정답 | 힌트 1회 | 50점
```

## Git 저장소

- `feature/quiz-play` 브랜치에서 무작위 출제와 힌트 채점 구현 후 `main`에 병합
- 프로젝트의 GitHub 저장소 [eunhye0323/Python_Git](https://github.com/eunhye0323/Python_Git)
- 별도 로컬 저장소를 복제한 뒤 복제본에서 브랜치 병합 그래프를 추가해 커밋

[기능별 커밋과 브랜치 병합 그래프](docs/screenshots/git_graph.png)

```text
Python_Git $ git log --oneline --graph --decorate --all
* d94fdec (HEAD -> main, origin/main, origin/HEAD) Docs: 실행 방법과 점수·파일 구조를 설명하고 실제 터미널 화면 첨부
* 9b6a025 Fix: 여러 실행에서 추가한 문제와 점수 기록을 저장할 때 함께 보존
* 634ec50 Test: 콘솔 재실행, 빈 목록, 힌트 점수와 저장 실패 복구 검증
* abd9b4f Feat: 최고 점수와 모든 완주 기록을 시간·문제 수·힌트와 함께 저장 및 조회
* 0a98d0e Feat: 목록에서 퀴즈를 선택해 삭제하고 빈 목록도 그대로 저장
* 5ca0865 Feat: 문제와 선택지 네 개, 선택 힌트를 입력받아 즉시 저장
*   16239ed Merge: 무작위 퀴즈 풀이와 힌트 기능 통합
|\
| * 02452cb (origin/feature/quiz-play) Feat: 문제별 힌트를 열고 최초 사용 한 번만 점수에서 차감
| * 0a52d10 Feat: 원하는 수만큼 중복 없이 무작위로 출제하고 채점 결과 표시
|/
* ab417ed Feat: 프로젝트 루트의 UTF-8 상태 파일을 저장하고 누락·손상 시 복구
* 77b5ddc Feat: 반복 메뉴와 숫자 재입력, 저장된 문제 목록 화면 구현
* ec245ad Data: 기술 퀴즈 5개의 선택지 수를 맞추고 정답 번호와 힌트 추가
* dfae016 Feat: 문제와 네 선택지의 검증·출력·정답 판정을 Quiz로 분리
* 9ca07fa Chore: 기존 퀴즈 초안과 문제 원본을 보존하고 실행 상태 파일 제외
* 7fdcc26 Initial commit
Python_Git $
```

- 복제본에서 실습용 로컬 저장소로 커밋을 `push`
- 원래 폴더에서 `git pull --ff-only`로 해당 커밋을 가져옴
- 동기화 직후 두 폴더의 커밋이 모두 `31ca264`임을 확인

[clone부터 pull까지의 터미널 기록](docs/screenshots/git_workflow.png)

```text
$ git clone --branch main practice.git Python_Git
Cloning into 'Python_Git'...
done.
$ git -C Python_Git add README.md docs/screenshots/git_graph.png
$ git -C Python_Git commit -m "Docs: 복제본에 브랜치 병합 그래프 추가"
[main 31ca264] Docs: 복제본에 브랜치 병합 그래프 추가
 2 files changed, 2 insertions(+)
 create mode 100644 docs/screenshots/git_graph.png
$ git -C Python_Git push origin main
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 64 threads
Compressing objects: 100% (5/5), done.
Writing objects: 100% (6/6), 165.94 KiB | 9.22 MiB/s, done.
Total 6 (delta 3), reused 0 (delta 0)
To /tmp/python-git-mission.b5iE4l/practice.git
   d94fdec..31ca264  main -> main
$ git -C /root/Python_Git pull --ff-only "$PWD/practice.git" main
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 6 (delta 3), reused 0 (delta 0)
Unpacking objects: 100% (6/6), 165.92 KiB | 13.83 MiB/s, done.
From /tmp/python-git-mission.b5iE4l/practice
 * branch            main       -> FETCH_HEAD
Updating d94fdec..31ca264
Fast-forward
 README.md                      |   2 ++
 docs/screenshots/git_graph.png | Bin 0 -> 173783 bytes
 2 files changed, 2 insertions(+)
 create mode 100644 docs/screenshots/git_graph.png
$ git -C Python_Git rev-parse --short HEAD
31ca264
$ git -C /root/Python_Git rev-parse --short HEAD
31ca264
$
```
