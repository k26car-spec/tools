# 營運工具中心

離線的 Excel 工具集，全部在瀏覽器本機處理，資料不會上傳。

- `index.html`：工具首頁，用 iframe 載入下面幾個工具。
- `tools/shipment-merge.html`：福城出貨 → 京虹格式合併，把「銷售訂單分析報表」跟「銷售出入庫明細表」合併成京虹固定格式。
- `tools/order-image.html`：訂單本補圖，依型號把「電子檔」的圖片比對貼到「手本」對應欄位。
- `tools/shipment-pivot.html`：出貨明細樞紐分析，上傳「銷售出/入庫明細表」，依客戶、銷售出貨單號自動加總出貨數量與出貨金額，並把結果存進下載檔案的「工作表1」分頁。
- `tools/master-txt.html`：貨品資料轉福城主檔 TXT，上傳 Converse 貨品資料 Excel，產出 212 字元固定寬度的主檔文字檔，條碼 13 碼與 12 碼各一版。

## 測試

`tools/master-txt.html` 有回歸測試，改動後確認產出沒變：

```bash
python3 tests/compare_with_python.py
```

細節見 [tests/README.md](tests/README.md)。

## 使用方式

下載這個 repo（或直接開 GitHub Pages 網址），用瀏覽器打開 `index.html` 即可，不需要安裝任何東西。
