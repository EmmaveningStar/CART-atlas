# CAR-T Atlas

繁體中文 CAR-T 知識與研究網站。白底、青綠與深藍的響應式設計，無須 npm、API key 或外部資料庫。

## 功能

- 原理、典型自體療程、細胞來源、靶點、研發方向與安全風險。
- 已上市產品搜尋、靶點篩選與詳細資料。
- 美國、歐盟、日本、台灣、中國、英國核准矩陣；每個狀態連回來源。
- 研究中用途獨立呈現，顯示 NCT、期別、招募狀態與來源更新日期。
- 新聞分類：核准消息、研究文獻、試驗更新、待核對來源異動。

## 目前資料範圍與限制

首版人工核對日期 2026-11-05，收錄美國／歐盟7項主要產品及中國納基奧侖賽示例，不是完整全球產品或管線清單。日本部分產品與台灣 Kymriah 已核對；其他未核對欄位明示「待查證」。核准、商業供應與保險給付是不同概念。適應症摘要以美國為主，中國產品以中國公告為主；不跨地區套用。歷史消息依原始日期顯示，不假裝是今日新聞。

## 放到 GitHub 並啟用網站

1. 新建 GitHub repository，預設分支使用 `main`。
2. 上傳本壓縮包解壓後的全部內容，包括 `.github/workflows/`。不要只上傳 ZIP；iPhone 若不便上傳隱藏資料夾，可交給 Codex 從這個專案推送。
3. 在 Settings → Pages → Build and deployment → Source 選 **GitHub Actions**。
4. 在 Actions 啟用 workflows；執行 **Deploy GitHub Pages**。
5. 執行一次 **Daily CAR-T intelligence**，檢查各來源成功後，頁面會顯示真實更新狀態。

若儲存庫政策限制 Actions 寫入或禁止直接推送 main，需由擁有者調整權限或改用審閱 PR 流程。此專案未建立你的 GitHub 儲存庫，排程在上傳並啟用前不會運行。另提供的預覽網站是初始資料展示，不會隨 GitHub 排程自動同步；日後應以 GitHub Pages 作為更新站點。

## 每日更新

`.github/workflows/daily-update.yml` 在 UTC 00:20（台灣08:20）排程，GitHub 可能延遲；公開儲存庫長期無活動時排程可能被停用。可隨時手動執行。

- ClinicalTrials.gov API v2：搜尋 CAR-T / CAR T / chimeric antigen receptor T，完整翻頁（保護上限10,000筆），儲存研究登錄快照並記錄近30日異動。搜尋結果可能含關聯研究，並非每項都代表未上市新產品。
- PubMed E-utilities：匯入最近30天新收錄資料，最新100篇；保留原文標題，日期為 PubMed 收錄日。不自動產生未經查證的繁中療效摘要。
- FDA / EMA 等：監測收錄來源頁面的主要文字雜湊；初次建立基線不發布假異動；變化只建立「待核對」消息。
- `products.json` 不被自動腳本改寫。新增產品、新適應症或撤銷核准須人工核對後提交。
- 成功來源即使其他來源失敗仍會保留；失敗來源不清空既有資料。`health.json` 記錄嘗試、完整成功及來源結果。workflow 出現部分失敗時仍提交狀態，並標示失敗供查修。
- `pages.yml` 透過 `workflow_run` 部署資料更新，避免 GITHUB_TOKEN 的 push 不觸發新 workflow 問題。

這是版本化 JSON 資料庫，適合唯讀知識站。`dist/data/news.json` 保留最近600筆，完整變更可追溯 Git 歷史；沒有使用者登入或私人病人資料。

## 本機預覽與檢查

```sh
python3 -m http.server 8000 --directory dist
python3 scripts/validate.py
python3 scripts/test_update.py
node --check dist/app.js
# 真實網路抓取（會更新 dist/data）
python3 scripts/update_data.py
```

檔案不要直接以 file:// 開啟，因為瀏覽器會限制 JSON fetch。

## 人工核對流程

先讀來源異動 → 查主管機關正式核准／仿單 → 修改產品地區狀態、適應症和 verifiedAt → 新增已核對新聞（使用事件日期）→ 提交 Git。不要把送件、受理、正面意見、試驗完成或優先資格當成核准。資料結構以 `dist/data/products.json` 為例。

## 主要資料與技術來源

- [NCI CAR-T 原理](https://www.cancer.gov/about-cancer/treatment/research/car-t-cells)
- [FDA 已核准細胞與基因治療](https://www.fda.gov/vaccines-blood-biologics/cellular-gene-therapy-products/approved-cellular-and-gene-therapy-products)
- [EMA 產品資料](https://www.ema.europa.eu/en/medicines)
- [PMDA 再生醫療產品審查](https://www.pmda.go.jp/english/review-services/reviews/approved-information/0004.html)
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

此站提供教育資訊；特定療法的臨床使用以當地最新核准仿單與專業團隊評估為準。
