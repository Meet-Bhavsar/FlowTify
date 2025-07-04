import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

def calculate_grouped_funnel(funnel_df, funnel_steps, groupby_cols):
    funnel_df = funnel_df[funnel_df['event_name'].isin(funnel_steps)]
    funnel_df = funnel_df.drop_duplicates(subset=['user_id', 'event_name'])

    metadata_cols = ['user_id'] + groupby_cols
    user_meta = funnel_df[metadata_cols].drop_duplicates('user_id').set_index('user_id')

    pivot = funnel_df.pivot(index='user_id', columns='event_name', values='event_timestamp')
    pivot = pivot.reindex(columns=funnel_steps)

    full_df = pivot.join(user_meta)

    grouped_results = []

    for group_values, group_df in full_df.groupby(groupby_cols):
        group_label = dict(zip(groupby_cols, group_values)) if isinstance(group_values, tuple) else {groupby_cols[0]: group_values}
        users_reached = group_df.notnull().sum()

        for i in range(len(funnel_steps) - 1):
            step_from = funnel_steps[i]
            step_to = funnel_steps[i + 1]

            from_count = users_reached[step_from]
            to_count = users_reached[step_to]

            conv = (to_count / from_count) * 100 if from_count > 0 else 0
            drop = 100 - conv

            grouped_results.append({
                'from_step': step_from,
                'to_step': step_to,
                'users_at_from_step': from_count,
                'users_at_to_step': to_count,
                'conversion_rate_%': round(conv, 2),
                'drop_off_rate_%': round(drop, 2),
                **group_label
            })

    return pd.DataFrame(grouped_results)

def analyze_feature_adoption_24h(feature_df):
    feature_df['hours_since_signup'] = (feature_df['usage_timestamp'] - feature_df['signup_date']).dt.total_seconds() / 3600
    first_24h_df = feature_df[feature_df['hours_since_signup'] <= 24]
    total_users = feature_df['user_id'].nunique()

    adoption = first_24h_df.groupby('feature_name')['user_id'].nunique().reset_index()
    adoption.columns = ['feature_name', 'users_used_24h']
    adoption['adoption_rate_%'] = (adoption['users_used_24h'] / total_users * 100).round(2)

    return adoption

def analyze_time_to_first_use(feature_df):
    first_use_df = feature_df.sort_values('usage_timestamp') \
                             .drop_duplicates(subset=['user_id', 'feature_name'], keep='first')
    first_use_df['hours_to_first_use'] = (first_use_df['usage_timestamp'] - first_use_df['signup_date']).dt.total_seconds() / 3600

    ttfu_summary = first_use_df.groupby('feature_name')['hours_to_first_use'].agg(['mean', 'median']).reset_index()
    ttfu_summary.columns = ['feature_name', 'avg_hours_to_first_use', 'median_hours_to_first_use']
    
    return ttfu_summary.round(2)

def correlate_usage_with_retention(feature_df):
    feature_df["usage_date"] = feature_df["usage_timestamp"].dt.date

    summary = feature_df.groupby("user_id").agg(
        unique_features_used=("feature_name", "nunique"),
        active_days=("usage_date", "nunique"),
        total_events=("feature_name", "count")
    ).reset_index()

    summary["retained"] = (summary["active_days"] >= 3).astype(int)
    correlation = summary[["unique_features_used", "total_events", "active_days", "retained"]].corr()

    return summary, correlation["retained"].sort_values(ascending=False)

def run_ab_tests(funnel_df, funnel_steps, group_col='ab_group'):
    funnel_df = funnel_df.copy()

    deduped = funnel_df.drop_duplicates(subset=['user_id', 'event_name'])
    pivot = deduped.pivot(index='user_id', columns='event_name', values='event_timestamp')
    pivot = pivot.reindex(columns=funnel_steps)

    user_groups = funnel_df[['user_id', group_col]].drop_duplicates().set_index('user_id')
    pivot = pivot.join(user_groups)

    results = []

    for i in range(len(funnel_steps) - 1):
        step_from = funnel_steps[i]
        step_to = funnel_steps[i + 1]

        pivot['converted'] = pivot[step_to].notnull()
        pivot['in_step'] = pivot[step_from].notnull()

        for group in pivot[group_col].unique():
            group_df = pivot[pivot[group_col] == group]
            total = group_df['in_step'].sum()
            converted = group_df['converted'].sum()
            conv_rate = (converted / total) * 100 if total > 0 else 0

            results.append({
                'group': group,
                'from_step': step_from,
                'to_step': step_to,
                'users_at_from_step': total,
                'users_converted': converted,
                'conversion_rate_%': round(conv_rate, 2)
            })

        a = pivot[pivot[group_col] == 'A']
        b = pivot[pivot[group_col] == 'B']
        count = [a['converted'].sum(), b['converted'].sum()]
        nobs = [a['in_step'].sum(), b['in_step'].sum()]
        pval = proportions_ztest(count, nobs)[1] if all(n > 0 for n in nobs) else None

        results.append({
            'group': 'z-test',
            'from_step': step_from,
            'to_step': step_to,
            'users_at_from_step': sum(nobs),
            'users_converted': sum(count),
            'conversion_rate_%': None,
            'p_value': round(pval, 4) if pval is not None else None
        })

    return pd.DataFrame(results)

def get_daily_conversion(funnel_df, funnel_steps):
    dedup = funnel_df.drop_duplicates(subset=['user_id', 'event_name'])
    dedup['event_date'] = dedup['event_timestamp'].dt.date

    daily_results = []

    for i in range(len(funnel_steps) - 1):
        step_from = funnel_steps[i]
        step_to = funnel_steps[i + 1]

        df_from = dedup[dedup['event_name'] == step_from]
        df_to = dedup[dedup['event_name'] == step_to]

        for date in sorted(dedup['event_date'].unique()):
            users_from = df_from[df_from['event_date'] == date]['user_id'].nunique()
            users_to = df_to[df_to['event_date'] == date]['user_id'].nunique()

            conv_rate = (users_to / users_from) * 100 if users_from > 0 else 0

            daily_results.append({
                'date': date,
                'from_step': step_from,
                'to_step': step_to,
                'users_from': users_from,
                'users_to': users_to,
                'conversion_rate': round(conv_rate, 2)
            })

    return pd.DataFrame(daily_results)

def detect_anomalies(conversion_df, threshold=12):
    conversion_df = conversion_df.sort_values('date')

    conversion_df['7d_avg'] = (
        conversion_df
        .groupby(['from_step', 'to_step'])['conversion_rate']
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )

    conversion_df['deviation'] = conversion_df['conversion_rate'] - conversion_df['7d_avg']
    conversion_df['anomaly'] = conversion_df['deviation'].abs() > threshold

    conversion_df['flag'] = conversion_df.apply(
        lambda row: 'Spike' if row['deviation'] > threshold else (
            'Drop' if row['deviation'] < -threshold else ''
        ), axis=1
    )

    return conversion_df
