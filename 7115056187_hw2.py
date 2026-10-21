
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
TARGET = "FloodProbability"
DATA_PATH = Path("data/train.csv")
OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# =========================================================
# 2. Data Understanding：讀取及檢查資料
# =========================================================
df = pd.read_csv(DATA_PATH)

print("=" * 65)
print("HW2：Flood Probability Prediction")
print("=" * 65)

print(f"資料筆數：{len(df):,}")
print(f"欄位數：{df.shape[1]}")
print(f"缺失值總數：{df.isnull().sum().sum()}")

# id 為識別碼，不作為預測特徵
feature_cols = [
    col for col in df.columns
    if col not in [TARGET, "id"]
]

X = df[feature_cols]
y = df[TARGET]

print(f"實際輸入特徵數：{len(feature_cols)}")
print("特徵名稱：", feature_cols)
print("\n目標變數描述：")
print(y.describe())

# =========================================================
# 3. Data Preparation：切分資料
# =========================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=RANDOM_STATE
)

print(f"\n訓練集：{len(X_train):,} 筆")
print(f"測試集：{len(X_test):,} 筆")

# =========================================================
# 4. EDA：目標分布與相關係數
# =========================================================
plt.figure()
sns.histplot(y, bins=40, kde=True)
plt.title("Distribution of FloodProbability")
plt.xlabel("FloodProbability")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_target_distribution.png", dpi=200)
plt.close()

corr = df[feature_cols + [TARGET]].corr(numeric_only=True)

plt.figure(figsize=(15, 12))
sns.heatmap(corr, cmap="coolwarm", center=0)
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_correlation_heatmap.png", dpi=200)
plt.close()

# =========================================================
# 5. Feature Selection：Forward Selection
#    使用訓練集子樣本進行特徵選擇，避免計算成本過高
# =========================================================
selection_size = min(50000, len(X_train))

X_fs, _, y_fs, _ = train_test_split(
    X_train,
    y_train,
    train_size=selection_size,
    random_state=RANDOM_STATE
)

remaining = list(feature_cols)
selected = []
selection_history = []

# 每次加入一個能讓驗證集 R² 提升最多的特徵
X_fs_train, X_fs_val, y_fs_train, y_fs_val = train_test_split(
    X_fs, y_fs,
    test_size=0.2,
    random_state=RANDOM_STATE
)

best_score = -np.inf

# 最多選 10 個特徵；可依作業需要調整
N_FEATURES = min(10, len(remaining))

for step in range(N_FEATURES):
    candidates = []

    for feature in remaining:
        current_features = selected + [feature]

        model = LinearRegression()
        model.fit(X_fs_train[current_features], y_fs_train)

        pred = model.predict(X_fs_val[current_features])
        score = r2_score(y_fs_val, pred)

        candidates.append((score, feature))

    candidates.sort(reverse=True)
    score, best_feature = candidates[0]

    selected.append(best_feature)
    remaining.remove(best_feature)
    best_score = score

    selection_history.append({
        "Step": step + 1,
        "Feature": best_feature,
        "Validation_R2": score
    })

    print(
        f"Forward Selection 第 {step + 1} 步："
        f"{best_feature}, Validation R² = {score:.6f}"
    )

pd.DataFrame(selection_history).to_csv(
    OUTPUT_DIR / "feature_selection_history.csv",
    index=False
)

print("\n選出的特徵：")
print(selected)

# =========================================================
# 6. Modeling：比較不同模型
# =========================================================
models = {
    "Multiple Linear Regression": LinearRegression(),
    "Ridge": make_pipeline(
        StandardScaler(),
        Ridge(alpha=1.0)
    ),
    "Lasso": make_pipeline(
        StandardScaler(),
        Lasso(alpha=0.001, max_iter=5000)
    )
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

# 以測試集 R² 最高者作為主要展示模型
best_name = results_df.loc[results_df["R2"].idxmax(), "Model"]
best_pred = predictions[best_name]

print(f"\n主要展示模型：{best_name}")

# =========================================================
# 7. Evaluation：實際值 vs 預測值
# =========================================================
# 抽樣繪圖，避免圖檔過大
rng = np.random.default_rng(RANDOM_STATE)
plot_n = min(3000, len(y_test))
plot_idx = rng.choice(len(y_test), size=plot_n, replace=False)

actual_plot = y_test.iloc[plot_idx].to_numpy()
pred_plot = best_pred[plot_idx]

plt.figure()
plt.scatter(actual_plot, pred_plot, alpha=0.35, s=12)

low = min(actual_plot.min(), pred_plot.min())
high = max(actual_plot.max(), pred_plot.max())
plt.plot([low, high], [low, high], "r--", label="Perfect Prediction")

plt.xlabel("Actual FloodProbability")
plt.ylabel("Predicted FloodProbability")
plt.title(f"Actual vs Predicted: {best_name}")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_actual_vs_predicted.png", dpi=200)
plt.close()

# =========================================================
# 8. Residual Analysis：殘差分析
# =========================================================
residuals = y_test.to_numpy() - best_pred

plt.figure()
plt.scatter(best_pred[plot_idx], residuals[plot_idx], alpha=0.35, s=12)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Predicted FloodProbability")
plt.ylabel("Residual")
plt.title("Residual Plot")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_residual_plot.png", dpi=200)
plt.close()

# =========================================================
# 9. 95% Prediction Interval：預測區間
#    使用訓練集中的隨機子樣本建立統計 OLS 模型。
#    區間圖使用該 OLS 模型的預測值，確保區間與模型一致。
# =========================================================
ols_size = min(50000, len(X_train))

X_ols = X_train[selected].sample(
    n=ols_size,
    random_state=RANDOM_STATE
)
y_ols = y_train.loc[X_ols.index]

X_ols_const = sm.add_constant(X_ols, has_constant="add")
ols_model = sm.OLS(y_ols, X_ols_const).fit()

interval_n = min(500, len(X_test))
interval_idx = rng.choice(len(X_test), size=interval_n, replace=False)

X_interval = X_test.iloc[interval_idx][selected]
X_interval_const = sm.add_constant(
    X_interval, has_constant="add"
)

interval_result = ols_model.get_prediction(
    X_interval_const
).summary_frame(alpha=0.05)

interval_df = pd.DataFrame({
    "Actual": y_test.iloc[interval_idx].to_numpy(),
    "Predicted": interval_result["mean"].to_numpy(),
    "Lower_95_PI": interval_result["obs_ci_lower"].to_numpy(),
    "Upper_95_PI": interval_result["obs_ci_upper"].to_numpy()
}).sort_values("Predicted").reset_index(drop=True)

interval_df.to_csv(
    OUTPUT_DIR / "prediction_intervals.csv",
    index=False
)

# 顯示前 100 筆，避免圖表過度擁擠
show = interval_df.iloc[:100]

plt.figure(figsize=(12, 6))
x_axis = np.arange(len(show))

plt.fill_between(
    x_axis,
    show["Lower_95_PI"].to_numpy(),
    show["Upper_95_PI"].to_numpy(),
    alpha=0.2,
    label="95% Prediction Interval"
)
plt.plot(
    x_axis,
    show["Predicted"].to_numpy(),
    label="OLS Predicted",
    linewidth=1.5
)
plt.scatter(
    x_axis,
    show["Actual"].to_numpy(),
    s=12,
    alpha=0.65,
    label="Actual"
)

plt.xlabel("Test Observation (sorted by prediction)")
plt.ylabel("FloodProbability")
plt.title("OLS Prediction with 95% Prediction Intervals")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_prediction_interval.png", dpi=200)
plt.close()

print("\nOLS 模型摘要：")
print(ols_model.summary())

print("\n所有分析完成！輸出檔案位於 results/ 資料夾。")
