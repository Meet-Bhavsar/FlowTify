import os
from datetime import datetime

# Create logs directory if not exists
LOG_DIR = "alerts"
os.makedirs(LOG_DIR, exist_ok=True)

def log_to_file(message, prefix="INFO"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(LOG_DIR, f"slack_log_{date_str}.txt")
    
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} [{prefix}] {message}\n")

    print(f"Logged to {log_filename}")


def alert_funnel_drop(conversion_df, threshold=15):
    for _, row in conversion_df.iterrows():
        if row["drop_off_rate_%"] > threshold:
            msg = (
                f"Drop detected: {row['from_step']} → {row['to_step']}\n"
                f"Users at step: {row['users_at_from_step']}, Converted: {row['users_at_to_step']}\n"
                f"Drop-off Rate: {row['drop_off_rate_%']}%"
            )
            log_to_file(msg, prefix="FUNNEL")


def alert_ab_test(ab_test_df, pval_threshold=0.05):
    significant_tests = ab_test_df[
        (ab_test_df['group'] == 'z-test') & 
        (ab_test_df['p_value'] < pval_threshold)
    ]

    for _, row in significant_tests.iterrows():
        msg = (
            f"A/B Test Significant Difference ({row['from_step']} → {row['to_step']}):\n"
            f"p-value = {row['p_value']}"
        )
        log_to_file(msg, prefix="ABTEST")


def alert_anomalies(anomalies_df):
    for _, row in anomalies_df[anomalies_df["anomaly"]].iterrows():
        msg = (
            f"Anomaly Detected on {row['date']} ({row['from_step']} → {row['to_step']}):\n"
            f"Conversion: {row['conversion_rate']}% | 7-day Avg: {row['7d_avg']:.2f}%\n"
            f"Deviation: {row['deviation']:.2f} ({row['flag']})"
        )
        log_to_file(msg, prefix="ANOMALY")
