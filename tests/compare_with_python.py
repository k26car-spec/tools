#!/usr/bin/env python3
"""回歸測試：用真實瀏覽器跑 tools/master-txt.html，確認產出沒有變。

比對方式是雜湊而不是檔案內容——來源檔與產出檔都含完整商品主檔與零售價，
不適合放進這個公開 repo，所以 expected.json 只存 SHA-256。

用法:
    python3 tests/compare_with_python.py
    python3 tests/compare_with_python.py --source-dir ~/Desktop/主檔來源
    python3 tests/compare_with_python.py --update      # 規則刻意改動後，重新寫入雜湊

需要:
    pip3 install playwright && python3 -m playwright install chromium

來源檔預設找 ~/Downloads。找不到的案例會跳過並在最後列出，不算失敗，
因為這些檔案不在 repo 裡，別台電腦上不一定有。
"""
import argparse
import hashlib
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "master-txt.html"
EXPECTED = pathlib.Path(__file__).resolve().parent / "expected.json"


def run_case(browser, source: pathlib.Path, drop_void: bool, outdir: pathlib.Path):
    """在瀏覽器裡跑一次轉檔，回傳 {'13': path, '12': path} 與摘要文字。"""
    page = browser.new_page(accept_downloads=True)
    js_errors = []
    page.on("pageerror", lambda e: js_errors.append(str(e)))
    try:
        page.goto(TOOL.as_uri())
        page.set_input_files("#srcFile", str(source))
        page.set_checked("#dropVoid", drop_void)
        page.click("#runBtn")
        page.wait_for_selector("#resultArea .result-box", timeout=180000)
        page.wait_for_function(
            "() => !document.getElementById('runBtn').disabled", timeout=180000)

        err = page.query_selector("#resultArea .result-box.err")
        if err:
            raise AssertionError("工具報錯：" + err.inner_text().strip())

        summary = page.inner_text("#resultArea .result-box.ok")
        files = {}
        for link in page.query_selector_all("#resultArea a.download-link"):
            label = link.inner_text()
            with page.expect_download() as dl:
                link.click()
            download = dl.value
            dest = outdir / download.suggested_filename
            download.save_as(dest)
            files["12" if "12" in label else "13"] = dest

        if js_errors:
            raise AssertionError("頁面有 JS 錯誤：" + "; ".join(js_errors[:3]))
        return files, summary
    finally:
        page.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default="~/Downloads",
                    help="來源 Excel 放哪，預設 ~/Downloads")
    ap.add_argument("--update", action="store_true",
                    help="把目前產出的雜湊寫回 expected.json（規則刻意改動後才用）")
    args = ap.parse_args()

    if not TOOL.exists():
        sys.exit(f"找不到 {TOOL}")
    spec = json.loads(EXPECTED.read_text(encoding="utf-8"))
    src_dir = pathlib.Path(args.source_dir).expanduser()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("需要 playwright：pip3 install playwright && python3 -m playwright install chromium")

    failures, skipped, checked = [], [], 0
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="master-txt-test-"))

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for case in spec["cases"]:
            source = src_dir / case["source"]
            if not source.exists():
                skipped.append(case["source"])
                continue
            print(f"\n########## {case['source']} ##########")
            print(f"  {case['note']}")
            try:
                files, summary = run_case(browser, source, case["dropVoid"], tmp)
            except Exception as exc:
                failures.append(f"{case['source']}：{exc}")
                print(f"  ✗ {exc}")
                continue
            for line in summary.splitlines():
                print("  | " + line)

            for digits, want in case["expect"].items():
                got = files.get(digits)
                if got is None:
                    failures.append(f"{case['source']} {digits}碼：沒有產生下載連結")
                    continue
                data = got.read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                nlines = data.count(b"\r\n")
                checked += 1
                if args.update:
                    want.update(sha256=digest, bytes=len(data), lines=nlines)
                    print(f"  ↻ {digits} 碼版雜湊已更新 {digest[:16]}…")
                elif digest == want["sha256"]:
                    print(f"  ✓ {digits} 碼版相同（{len(data)} bytes、{nlines} 行）")
                else:
                    failures.append(
                        f"{case['source']} {digits}碼：產出變了\n"
                        f"      預期 {want['sha256']} / {want['bytes']} bytes / {want['lines']} 行\n"
                        f"      實際 {digest} / {len(data)} bytes / {nlines} 行")
                    print(f"  ✗ {digits} 碼版雜湊不符")
        browser.close()

    print("\n" + "=" * 62)
    if skipped:
        print(f"跳過 {len(skipped)} 個案例（本機找不到來源檔）：")
        for s in skipped:
            print("  - " + s)
        print(f"  來源檔不在 repo 裡。若放在別的資料夾，用 --source-dir 指定。")
    if args.update:
        EXPECTED.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nexpected.json 已更新（{checked} 筆雜湊）。請確認改動是刻意的再 commit。")
        return
    if failures:
        print(f"\n失敗 {len(failures)} 項：")
        for f in failures:
            print("  ✗ " + f)
        print("\n產出變了代表 master-txt.html 的行為被改動。若是刻意改規則，"
              "確認新產出正確後跑 --update 重新寫入雜湊。")
        sys.exit(1)
    if checked == 0:
        print("\n沒有任何案例可以驗（來源檔都找不到）。用 --source-dir 指定正確路徑。")
        sys.exit(2)
    print(f"\n全部通過：{checked} 份產出與基準雜湊相同")


if __name__ == "__main__":
    main()
