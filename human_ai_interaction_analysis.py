"""
Human-AI Interaction Latent Trust Score Prediction
CRISP-DM Regression & Feature Selection Pipeline
Author: 7115056187
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import statsmodels.api as sm

warnings.filterwarnings("ignore")

# =========================================================
# 1. 基本設定
# =========================================================
RANDOM_STATE = 42
TARGET = "latent_trust_score"
DATA_PATH = Path("data/Human-AI Interaction.csv")
OUTPUT_DIR = Path("results_hai")
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# =========================================================
# 2. Data Understanding & Preparation
# =========================================================
df = pd.read_csv(DATA_PATH)

print("=" * 65)
print("Human-AI Interaction：Latent Trust Score Prediction")
print("=" * 65)
print(f"原始資料筆數：{len(df):,}")
print(f"欄位數：{df.shape[1]}")
print(f"缺失值總數：{df.isnull().sum().sum()}")

# 處理缺失值 (數值以中位數填補，類別以眾數填補)
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

for c in num_cols:
    df[c] = df[c].fillna(df[c].median())

for c in cat_cols:
    df[c] = df[c].fillna(df[c].mode()[0])

# 類別編碼
ordinal_maps = {
    "education_level": {"High School": 1, "Bachelor": 2, "Master": 3, "PhD": 4},
    "prior_ai_exposure": {"Low": 1, "Medium": 2, "High": 3},
    "ui_complexity": {"Low": 1, "Medium": 2, "High": 3},
    "task_risk": {"Low": 1, "Medium": 2, "High": 3},
    "domain": {"E-commerce": 1, "Education": 2, "Transportation": 3, "Healthcare": 4, "Finance": 5},
    "cultural_factor": {"Western": 1, "Asian": 2, "Middle Eastern": 3, "African": 4}
}

for col, mapping in ordinal_maps.items():
    if col in df.columns:
        df[col] = df[col].map(mapping).fillna(2)

feature_cols = [c for c in df.columns if c != TARGET]
X = df[feature_cols]
y = df[TARGET]

print(f"輸入特徵數：{len(feature_cols)}")
print("特徵清單：", feature_cols)
print("\n目標變數描述：")
print(y.describe())

# 切分資料 (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=RANDOM_STATE
)

print(f"\n訓練集：{len(X_train):,} 筆")
print(f"測試集：{len(X_test):,} 筆")

# =========================================================
# 3. EDA 視覺化
# =========================================================
# 圖 1：目標變數分布
plt.figure()
sns.histplot(y, bins=35, kde=True, color="#4f46e5")
plt.title("Distribution of Latent Trust Score")
plt.xlabel("Latent Trust Score (0-100)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_target_distribution.png", dpi=200)
plt.close()

# 圖 2：特徵相關性熱圖
corr = df[feature_cols + [TARGET]].corr(numeric_only=True)
plt.figure(figsize=(15, 12))
sns.heatmap(corr, cmap="coolwarm", center=0, annot=False)
plt.title("Human-AI Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_correlation_heatmap.png", dpi=200)
plt.close()

# =========================================================
# 4. Feature Selection：Forward Selection (前向逐步選擇)
# =========================================================
X_fs_train, X_fs_val, y_fs_train, y_fs_val = train_test_split(
    X_train, y_train,
    test_size=0.2,
    random_state=RANDOM_STATE
)

remaining = list(feature_cols)
selected = []
selection_history = []
N_FEATURES = min(10, len(remaining))

for step in range(N_FEATURES):
    candidates = []
    for feature in remaining:
        curr = selected + [feature]
        model = LinearRegression()
        model.fit(X_fs_train[curr], y_fs_train)
        pred = model.predict(X_fs_val[curr])
        score = r2_score(y_fs_val, pred)
        candidates.append((score, feature))

    candidates.sort(reverse=True)
    score, best_feature = candidates[0]
    selected.append(best_feature)
    remaining.remove(best_feature)

    selection_history.append({
        "Step": step + 1,
        "Feature": best_feature,
        "Validation_R2": score
    })
    print(f"HAI Forward Selection 第 {step + 1} 步：{best_feature}, Validation R² = {score:.6f}")

pd.DataFrame(selection_history).to_csv(
    OUTPUT_DIR / "feature_selection_history.csv",
    index=False
)
print("\n選出的 10 個核心特徵：", selected)

# =========================================================
# 5. Modeling：模型評估比較
# =========================================================
models = {
    "Multiple Linear Regression": LinearRegression(),
    "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    "Lasso": make_pipeline(StandardScaler(), Lasso(alpha=0.005, max_iter=5000))
}

results = []
predictions = {}

for name, model in models.items():
    model.fit(X_train[selected], y_train)
    pred = model.predict(X_test[selected])
    predictions[name] = pred

    results.append({
        "Model": name,
        "R2": r2_score(y_test, pred),
        "MAE": mean_absolute_error(y_test, pred),
        "RMSE": np.sqrt(mean_squared_error(y_test, pred))
    })

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_DIR / "model_evaluation.csv", index=False)
print("\n模型評估結果：")
print(results_df.to_string(index=False))

best_name = results_df.loc[results_df["R2"].idxmax(), "Model"]
best_pred = predictions[best_name]

# =========================================================
# 6. Evaluation：實際值 vs 預測值 & 殘差診斷
# =========================================================
rng = np.random.default_rng(RANDOM_STATE)
plot_n = min(2000, len(y_test))
plot_idx = rng.choice(len(y_test), size=plot_n, replace=False)

actual_plot = y_test.iloc[plot_idx].to_numpy()
pred_plot = best_pred[plot_idx]

# 圖 3：Actual vs Predicted
plt.figure()
plt.scatter(actual_plot, pred_plot, alpha=0.4, s=14, color="#6366f1")
low = min(actual_plot.min(), pred_plot.min())
high = max(actual_plot.max(), pred_plot.max())
plt.plot([low, high], [low, high], "r--", label="Perfect Prediction")
plt.xlabel("Actual Latent Trust Score")
plt.ylabel("Predicted Latent Trust Score")
plt.title(f"Actual vs Predicted: {best_name}")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_actual_vs_predicted.png", dpi=200)
plt.close()

# 圖 4：Residual Plot
residuals = y_test.to_numpy() - best_pred
plt.figure()
plt.scatter(best_pred[plot_idx], residuals[plot_idx], alpha=0.4, s=14, color="#0ea5e9")
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Predicted Latent Trust Score")
plt.ylabel("Residual")
plt.title("Residual Plot (Latent Trust Score)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_residual_plot.png", dpi=200)
plt.close()

# =========================================================
# 7. 95% Prediction Interval
# =========================================================
X_train_const = sm.add_constant(X_train[selected], has_constant="add")
ols_model = sm.OLS(y_train, X_train_const).fit()

interval_n = min(500, len(X_test))
interval_idx = rng.choice(len(X_test), size=interval_n, replace=False)
X_interval = X_test.iloc[interval_idx][selected]
X_interval_const = sm.add_constant(X_interval, has_constant="add")

interval_res = ols_model.get_prediction(X_interval_const).summary_frame(alpha=0.05)

interval_df = pd.DataFrame({
    "Actual": y_test.iloc[interval_idx].to_numpy(),
    "Predicted": interval_res["mean"].to_numpy(),
    "Lower_95_PI": interval_res["obs_ci_lower"].to_numpy(),
    "Upper_95_PI": interval_res["obs_ci_upper"].to_numpy()
}).sort_values("Predicted").reset_index(drop=True)

interval_df.to_csv(OUTPUT_DIR / "prediction_intervals.csv", index=False)

# 計算覆蓋率
coverage = ((interval_df["Actual"] >= interval_df["Lower_95_PI"]) & 
            (interval_df["Actual"] <= interval_df["Upper_95_PI"])).mean()
avg_width = (interval_df["Upper_95_PI"] - interval_df["Lower_95_PI"]).mean()

print(f"\n95% 預測區間覆蓋率：{coverage * 100:.2f}% (涵蓋 {int(coverage*len(interval_df))}/{len(interval_df)})")
print(f"平均區間寬度：{avg_width:.4f}")

# 圖 5：95% 預測區間圖
show = interval_df.iloc[:100]
plt.figure(figsize=(12, 6))
x_axis = np.arange(len(show))

plt.fill_between(
    x_axis,
    show["Lower_95_PI"].to_numpy(),
    show["Upper_95_PI"].to_numpy(),
    alpha=0.25,
    color="#38bdf8",
    label="95% Prediction Interval"
)
plt.plot(x_axis, show["Predicted"].to_numpy(), color="#0284c7", label="OLS Predicted", linewidth=1.5)
plt.scatter(x_axis, show["Actual"].to_numpy(), s=12, color="#f43f5e", alpha=0.7, label="Actual")
plt.xlabel("Test Observation (sorted by predicted trust)")
plt.ylabel("Latent Trust Score")
plt.title("OLS Prediction with 95% Prediction Intervals (HAI Trust)")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_prediction_interval.png", dpi=200)
plt.close()

print("\nOLS 模型統計摘要：")
print(ols_model.summary())
print("\n完成！所有輸出檔案已寫入 results_hai/ 資料夾。")
