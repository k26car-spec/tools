# 回歸測試

確認 `tools/master-txt.html` 改動之後，產出的主檔 TXT 沒有變。

```bash
pip3 install playwright && python3 -m playwright install chromium
python3 tests/compare_with_python.py
```

## 為什麼只存雜湊

來源 Excel 與產出的 TXT 都是完整商品主檔，含品名與零售價，**不放進這個公開 repo**。
`expected.json` 只存每份產出的 SHA-256、位元組數與行數，行為一變雜湊就不同，照樣抓得到走鐘。

來源檔預設找 `~/Downloads`，放別的地方用 `--source-dir` 指定。找不到的案例會跳過不算失敗，
因為別台電腦上不一定有這些檔案。

## 基準怎麼來的

`expected.json` 的雜湊取自 `~/.claude/skills/converse-master-txt/scripts/excel_to_master_txt.py`
產出、且已經實際交付使用過的檔案。建立當時用 Playwright 驗過網頁工具的產出與該腳本
**逐位元組完全相同**（五份來源檔，涵蓋兩種版面、混季節、作廢條碼、贈品）。

## 刻意改規則的時候

產出本來就該變。確認新產出正確之後：

```bash
python3 tests/compare_with_python.py --update
```

這會把新雜湊寫回 `expected.json`。**先確認改動是對的再 commit**，否則等於把錯誤當成新基準。

## 涵蓋的情境

| 來源檔 | 驗什麼 |
|---|---|
| `CS_HO26貨品資料_20261001.xlsx` | erp-raw 單季（冬→20264），條碼全 12 碼 |
| `CS_FA26+HO26貨品資料.xlsx` | 混季節（秋+冬各自套前綴）、DEL 作廢條碼、被 Excel 吃掉開頭 0 的 11 碼條碼 |
| `Converse_FA26產品主檔20260921更新.xlsx` | 條碼欄存成文字、贈品列（大類 99） |
| `Z & F品主檔.xlsx` | 小檔案 |
| `CS_FA26貨品資料_加工轉txt.xlsx` | preprocessed 版面 |
