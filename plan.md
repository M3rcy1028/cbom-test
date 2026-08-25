# cbom-test 게시 계획과 현재 상태

이 문서는 사용자가 요청한 `plan.md` 진입점이다. 실험의 전체 단계, 실행 명령, 관측값, 차단 사유는 단일 상세 원장인 [CBOM_LAB_PLAN.md](CBOM_LAB_PLAN.md)에 계속 누적한다. 대화 내용이 축약되더라도 두 문서와 `results/`, `evidence/`만으로 작업을 재개할 수 있다.

## 게시 대상

- 원격 저장소: `https://github.com/M3rcy1028/cbom-test.git`
- 기본 브랜치: `main`
- 사용자 지정 최초 커밋 메시지: `first commit`
- 최초 커밋: `066b89efca6623f15f380478752e7c1e188047e2`
- 최초 push: 완료
- GitHub-hosted Action: [run 32826680204](https://github.com/M3rcy1028/cbom-test/actions/runs/32826680204), `success`
- 원격 증거 결과 커밋: `fe54298394571ca90da14a674059e0e753fe309f`
- 최종 산출물 후속 push: 완료, 당시 local `HEAD`와 `origin/main` 일치 확인
- 결과 요약 커밋: `4ea726de3346a2d7292db2b1ef02c64d0fcc9b8d`, 사용자 승인 후 push 완료
- Quantum-safe 코드 커밋: `b018a5c3c82d51edc049047238554c78698bee5b`, push 완료
- Quantum-safe 원격 1차 run: [32837919108](https://github.com/M3rcy1028/cbom-test/actions/runs/32837919108), 다중 Go module index 오염으로 ML-KEM assertion 실패

## 사용자 요청 명령과 적용 방식

사용자가 지정한 게시 흐름은 다음과 같다.

```bash
echo "# cbom-test" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/M3rcy1028/cbom-test.git
git push -u origin main
```

실제 적용 시에는 이미 작성된 README와 전체 실험 산출물을 보존하기 위해 제목을 중복 추가하지 않고 `# cbom-test`로 정리했다. Markdown 링크 표기인 `[https://...](https://...)`가 아니라 Git이 인식하는 실제 HTTPS URL을 remote로 등록했다. 최초 커밋에는 README만이 아니라 민감정보·대용량 파일 검사를 통과한 보고서, fixture, 결과, 캡처와 재현 스크립트를 함께 포함했다.

## 완료 기준

- [x] `cbom-lab/` 안에서 IBM CBOM 및 관련 도구 실험
- [x] 통합 기능 명세서와 실행 원장 작성
- [x] 실제 결과 JSON·로그·화면 캡처 생성
- [x] 테스트 개인키, credential, 대용량 upstream 소스 제외
- [x] 최초 `first commit` 생성 및 `origin/main` push
- [x] GitHub-hosted CBOMkit Action 실행 및 artifact 회수
- [x] CBOMkit public Git scan, API, DB, compliance 검증
- [x] schema 14/14, semantic 13/13, 링크·크기·민감정보·독립 staged tree 검증
- [x] 원격 증거 후속 커밋 push 및 remote hash 최종 대조
- [x] `RESULTS_OVERVIEW.md` 작성·커밋·push
- [x] 실제 ML-KEM-768 코드·CBOM·Quantum Safe Viewer 결과 생성
- [ ] 격리된 quantum-safe GitHub Action 재실행 성공 및 원격 artifact 회수

## 산출물 위치

- [한눈에 보는 결과 요약](RESULTS_OVERVIEW.md)
- [통합 기능 명세서](CBOM_%ED%86%B5%ED%95%A9_%EA%B8%B0%EB%8A%A5_%EB%AA%85%EC%84%B8%EC%84%9C.md)
- [상세 실행 원장](CBOM_LAB_PLAN.md)
- [Ground truth](ground-truth.md)
- [캡처 설명서](evidence/CAPTURE_MANIFEST.md)
- [GitHub Action 원본 증거](results/action/github/)
- [CBOMkit Git scan 결과](results/cbomkit/git-scan-cbom.json)
- [Quantum-safe Viewer 입력 CBOM](results/quantum-safe/action/cbom.json)

## 다음 재개 지점

1. `CBOM_LAB_PLAN.md`를 처음부터 끝까지 다시 읽는다.
2. `git status`, 민감정보, 파일 크기, Markdown 링크를 검사한다.
3. schema 14건과 semantic positive 13건을 재검증한다.
4. 격리된 quantum-safe workflow를 재실행하고 원격 artifact에서 `ML-KEM-768`과 source evidence를 검증한다.
5. 후속 커밋을 push하고 `git ls-remote origin refs/heads/main`과 로컬 `HEAD`를 대조한다.
