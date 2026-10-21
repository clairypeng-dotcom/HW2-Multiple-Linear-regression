# HW2: Multiple Linear Regression & CRISP-DM Analytics Platform
> **學生編號 (Student ID)**: `7115056187`  
> **課程作業**: 資料探勘作業二 (HW2 - Multiple Linear Regression)  
> **GitHub Repository**: [https://github.com/clairypeng-dotcom/HW2-Multiple-Linear-regression.git](https://github.com/clairypeng-dotcom/HW2-Multiple-Linear-regression.git)
https://clairypeng-dotcom.github.io/HW2-Multiple-Linear-regression/
>
> <img width="909" height="471" alt="截圖 2026-10-21 下午6 43 59" src="https://github.com/user-attachments/assets/bb2048b8-5876-4922-8ada-34d4147d9472" />
<img width="1440" height="823" alt="截圖 2026-10-21 下午5 39 49" src="https://github.com/user-attachments/assets/e52b29c5-8311-4d1f-97df-6f017cb0672b" />

---

## 📌 專案簡介 (Overview)

本專案遵循國際資料探勘標準方法論 **CRISP-DM (Cross-Industry Standard Process for Data Mining)**，落實六大階段（商業理解、資料理解、資料準備、建模技術、模型評估、部署應用），實作多元線性迴歸 (Multiple Linear Regression)、L2 正則化 Ridge、L1 正則化 Lasso、逐步前向特徵選擇 (Forward Selection) 及 95% 預測區間 (Prediction Intervals) 分析。

同時，本專案打造了一個現代化、高質感的**多主題互動式分析網頁平台**，內建即時 OLS 迴歸推論引擎，支援切換與分析：
1. 🌊 **洪水機率預測 (Flood Probability Prediction)**：Kaggle S4E5 合成資料集 (111.8 萬筆)
2. 🤖 **人機互動信任度分析 (Human-AI Interaction Trust)**：10,100 筆人機互動實證資料集
3. 🌐 **自訂資料集即時分析 (Custom Dataset URL / Upload)**：支援任意公開 CSV 網址輸入（預設 50 Startups 範例）或檔案上傳，純前端即時計算迴歸參數。

---

## 🚀 網頁平台啟動方式 (Web Application Quickstart)

本專案以純原生技術建構（HTML5 + CSS3 + Vanilla JavaScript + Chart.js + PapaParse），無需編譯或安裝龐大前端框架：

```bash
# 啟動本機 HTTP 伺服器
python3 -m http.server 8088

# 在瀏覽器開啟平台
open http://localhost:8088/
```

---

## 🔬 核心分析主題與評估指標比較

| 分析主題 | 🌊 洪水機率預測 (Flood) | 🤖 人機互動信任度 (HAI) | 🌐 自訂資料集分析 (50 Startups 範例) |
| :--- | :--- | :--- | :--- |
| **資料來源** | Kaggle S4E5 Dataset | Human-AI Interaction Dataset | Avik-Jain 100-Days-Of-ML-Code |
| **資料筆數** | 1,117,957 筆 (80/20 切分) | 10,100 筆 (80/20 切分) | 50 筆 (80/20 切分) |
| **輸入特徵數** | 20 個環境/水文/政策特徵 | 20 個人機介面/演算法/認知特徵 | 3 個財務投入指標 |
| **預測目標變數** | `FloodProbability` (0.00 ~ 1.00) | `latent_trust_score` (0 ~ 100 分) | `Profit` (營業淨利潤, 美元 $) |
| **測試集 $R^2$** | **0.373864** | **0.661662** | **0.903726** |
| **測試集 MAE** | 0.032578 | 4.097399 | 6,979.29 美元 |
| **測試集 RMSE** | 0.040342 | 5.166084 | 9,067.47 美元 |
| **95% 預測區間覆蓋率** | **95.6%** (478 / 500 命中) | **93.0%** (465 / 500 命中) | **100.0%** (10 / 10 命中) |
| **平均區間寬度** | 0.1580 | 20.1072 分 | 40,463 美元 |

---

## 📁 檔案結構 (Repository Structure)

```text
.
├── index.html                   # 網頁平台主結構 (支援下拉選單切換多資料集)
├── style.css                    # 現代化深色/淺色玻璃擬態設計系統
├── app.js                       # 前端互動邏輯、Chart.js 與即時 OLS 迴歸引擎
├── data.js                      # 儲存 Flood、HAI、50 Startups 結構化資料
├── 7115056187_hw2.py            # 洪水機率預測 Python 完整分析腳本
├── human_ai_interaction_analysis.py # 人機互動信任度 Python 完整分析腳本
├── requirements.txt             # Python 依賴清單
├── .gitignore                   # Git 忽略設定
├── data/                        # 資料集目錄
│   ├── 50_Startups.csv
│   └── Human-AI Interaction.csv
├── results/                     # 洪水機率預測成果圖表與報表
│   ├── 01_target_distribution.png
│   ├── 02_correlation_heatmap.png
│   ├── 03_actual_vs_predicted.png
│   ├── 04_residual_plot.png
│   ├── 05_prediction_interval.png
│   ├── model_evaluation.csv
│   ├── feature_selection_history.csv
│   └── prediction_intervals.csv
├── results_hai/                 # 人機互動信任度成果圖表與報表
│   ├── 01_target_distribution.png
│   ├── 02_correlation_heatmap.png
│   ├── 03_actual_vs_predicted.png
│   ├── 04_residual_plot.png
│   ├── 05_prediction_interval.png
│   ├── model_evaluation.csv
│   ├── feature_selection_history.csv
│   └── prediction_intervals.csv
├── results_startups/            # 50 Startups 獲利預測成果圖表與報表
└── 7115056187_HW2_Flood_Probability_Report_EDITABLE_WITH_FIGURES.pdf # 完整作業報告書
```

---

## 🛠️ Python 本地分析腳本執行方式

```bash
# 安裝依賴環境
pip install -r requirements.txt

# 執行洪水機率預測管線
python 7115056187_hw2.py

# 執行人機互動信任度分析管線
python human_ai_interaction_analysis.py
```

---

## 📜 授權與維護
- **開發者**: 7115056187
- **專案原始碼儲存庫**: [GitHub: clairypeng-dotcom/HW2-Multiple-Linear-regression](https://github.com/clairypeng-dotcom/HW2-Multiple-Linear-regression)
