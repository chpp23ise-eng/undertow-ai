import pandas as pd


df = pd.read_csv("data/revenue_events.csv")

print("Total events:", len(df))
print()

print("Events by type:")
print(df["event_type"].value_counts())
print()

print("Events by bank:")
print(df["bank"].value_counts())
print()

print("Events by error:")
print(df["error_code"].value_counts())
print()

print("Top bank + error combinations:")
print(
    df.groupby(["bank", "error_code"])
    .size()
    .sort_values(ascending=False)
    .head(10)
)