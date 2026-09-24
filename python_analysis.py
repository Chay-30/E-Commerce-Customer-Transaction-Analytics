import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. LOAD DATA
# ============================================================

customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
products = pd.read_csv("products.csv")
orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
order_items = pd.read_csv("order_items.csv")


# ============================================================
# 2. MERGE DATA
# ============================================================

df = (
    orders
    .merge(order_items, on="order_id")
    .merge(products, on="product_id")
    .merge(customers, on="customer_id")
)

df["revenue"] = df["quantity"] * df["unit_price"]


# ============================================================
# 3. BASIC BUSINESS KPIs
# ============================================================

print("\n===== BUSINESS KPIs =====")

print("Total Revenue:", round(df["revenue"].sum(), 2))
print("Total Orders:", df["order_id"].nunique())
print("Total Customers:", df["customer_id"].nunique())
print("Total Units Sold:", df["quantity"].sum())

aov = df["revenue"].sum() / df["order_id"].nunique()
print("Average Order Value:", round(aov, 2))


# ============================================================
# 4. DELIVERED ORDER ANALYSIS
# ============================================================

delivered = df[df["status"] == "Delivered"].copy()

print("\n===== DELIVERED ORDERS =====")

delivered_revenue = delivered["revenue"].sum()
delivered_orders = delivered["order_id"].nunique()
delivered_customers = delivered["customer_id"].nunique()

print("Delivered Revenue:", round(delivered_revenue, 2))
print("Delivered Orders:", delivered_orders)
print("Delivered Customers:", delivered_customers)

delivered_aov = delivered_revenue / delivered_orders
print("Delivered AOV:", round(delivered_aov, 2))


# ============================================================
# 5. ORDER STATUS ANALYSIS
# ============================================================

print("\n===== ORDER STATUS =====")

status_analysis = (
    orders.groupby("status")
    .size()
    .reset_index(name="orders")
)

status_analysis["percentage"] = (
    status_analysis["orders"] /
    status_analysis["orders"].sum() * 100
).round(2)

print(status_analysis)


# ============================================================
# 6. PAYMENT METHOD ANALYSIS
# ============================================================

print("\n===== PAYMENT METHODS =====")

payment_analysis = (
    orders.groupby("payment_method")
    .size()
    .reset_index(name="orders")
    .sort_values("orders", ascending=False)
)

payment_analysis["percentage"] = (
    payment_analysis["orders"] /
    payment_analysis["orders"].sum() * 100
).round(2)

print(payment_analysis)


# ============================================================
# 7. MONTHLY REVENUE
# ============================================================

monthly = (
    delivered
    .groupby(delivered["order_date"].dt.to_period("M"))["revenue"]
    .sum()
)

print("\n===== MONTHLY REVENUE =====")
print(monthly)


plt.figure(figsize=(10, 5))
monthly.plot(kind="line", marker="o")
plt.title("Monthly Revenue - Delivered Orders")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 8. CATEGORY ANALYSIS
# ============================================================

category = (
    delivered
    .groupby("category")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

print("\n===== CATEGORY REVENUE =====")
print(category)


plt.figure(figsize=(9, 5))
category.sort_values().plot(kind="barh")
plt.title("Revenue by Category")
plt.xlabel("Revenue")
plt.ylabel("Category")
plt.tight_layout()
plt.show()


# ============================================================
# 9. TOP 10 PRODUCTS
# ============================================================

top_products = (
    delivered
    .groupby(["product_id", "product_name", "category"])
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("revenue", "sum")
    )
    .reset_index()
    .sort_values("revenue", ascending=False)
    .head(10)
)

print("\n===== TOP 10 PRODUCTS =====")
print(top_products)


# ============================================================
# 10. CITY ANALYSIS
# ============================================================

city_analysis = (
    delivered
    .groupby("city")
    .agg(
        customers=("customer_id", "nunique"),
        orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"),
        revenue=("revenue", "sum")
    )
    .reset_index()
    .sort_values("revenue", ascending=False)
)

print("\n===== CITY ANALYSIS =====")
print(city_analysis)


# ============================================================
# 11. RFM ANALYSIS
# ============================================================

snapshot = delivered["order_date"].max() + pd.Timedelta(days=1)

rfm = (
    delivered
    .groupby("customer_id")
    .agg(
        recency=("order_date", lambda x: (snapshot - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    )
    .reset_index()
)


# RFM scores
rfm["R_score"] = pd.qcut(
    rfm["recency"],
    4,
    labels=[4, 3, 2, 1],
    duplicates="drop"
)

rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    4,
    labels=[1, 2, 3, 4]
)

rfm["M_score"] = pd.qcut(
    rfm["monetary"],
    4,
    labels=[1, 2, 3, 4]
)


rfm["RFM_score"] = (
    rfm["R_score"].astype(int).astype(str)
    + rfm["F_score"].astype(int).astype(str)
    + rfm["M_score"].astype(int).astype(str)
)


# ============================================================
# 12. CUSTOMER SEGMENTATION
# ============================================================

def segment(row):

    if (
        row.R_score >= 4
        and row.F_score >= 4
        and row.M_score >= 4
    ):
        return "Champions"

    elif (
        row.F_score >= 3
        and row.M_score >= 3
    ):
        return "Loyal Customers"

    elif (
        row.R_score >= 3
        and row.F_score >= 2
    ):
        return "Potential Loyalists"

    elif (
        row.R_score <= 2
        and row.M_score >= 3
    ):
        return "At Risk"

    else:
        return "Others"


rfm["segment"] = rfm.apply(segment, axis=1)


print("\n===== RFM SEGMENTS =====")
print(rfm["segment"].value_counts())


# ============================================================
# 13. RFM REVENUE BY SEGMENT
# ============================================================

segment_analysis = (
    rfm
    .groupby("segment")
    .agg(
        customers=("customer_id", "count"),
        revenue=("monetary", "sum"),
        average_customer_value=("monetary", "mean")
    )
    .reset_index()
    .sort_values("revenue", ascending=False)
)

print("\n===== RFM SEGMENT REVENUE =====")
print(segment_analysis)


# ============================================================
# 14. EXPORT ANALYSIS FILES
# ============================================================

rfm.to_csv(
    "rfm_customer_segments.csv",
    index=False
)

top_products.to_csv(
    "top_10_products.csv",
    index=False
)

city_analysis.to_csv(
    "city_analysis.csv",
    index=False
)

segment_analysis.to_csv(
    "rfm_segment_analysis.csv",
    index=False
)

payment_analysis.to_csv(
    "payment_analysis.csv",
    index=False
)

status_analysis.to_csv(
    "status_analysis.csv",
    index=False
)

print("\n===== ANALYSIS COMPLETE =====")
print("Analysis CSV files created successfully.")

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt


# customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
# products = pd.read_csv("products.csv")
# orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
# order_items = pd.read_csv("order_items.csv")

# df = (orders.merge(order_items, on="order_id")
#             .merge(products, on="product_id")
#             .merge(customers, on="customer_id"))

# df["revenue"] = df["quantity"] * df["unit_price"]
# delivered = df[df["status"] == "Delivered"].copy()

# print("Total revenue:", delivered["revenue"].sum())
# print("Orders:", delivered["order_id"].nunique())
# print("Customers:", delivered["customer_id"].nunique())
# print("AOV:", delivered["revenue"].sum() / delivered["order_id"].nunique())

# # Monthly revenue
# monthly = delivered.groupby(delivered["order_date"].dt.to_period("M"))["revenue"].sum()
# monthly.plot(kind="line", title="Monthly Revenue")
# plt.tight_layout()
# plt.show()

# # Category revenue
# category = delivered.groupby("category")["revenue"].sum().sort_values()
# category.plot(kind="barh", title="Revenue by Category")
# plt.tight_layout()
# plt.show()

# # RFM
# snapshot = delivered["order_date"].max() + pd.Timedelta(days=1)
# rfm = delivered.groupby("customer_id").agg(
#     recency=("order_date", lambda x: (snapshot - x.max()).days),
#     frequency=("order_id", "nunique"),
#     monetary=("revenue", "sum")
# ).reset_index()

# rfm["R_score"] = pd.qcut(rfm["recency"], 4, labels=[4,3,2,1], duplicates="drop")
# rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1,2,3,4])
# rfm["M_score"] = pd.qcut(rfm["monetary"], 4, labels=[1,2,3,4])
# rfm["RFM_score"] = (
#     rfm["R_score"].astype(int).astype(str) +
#     rfm["F_score"].astype(int).astype(str) +
#     rfm["M_score"].astype(int).astype(str)
# )

# def segment(row):
#     if row.R_score >= 4 and row.F_score >= 4 and row.M_score >= 4:
#         return "Champions"
#     if row.F_score >= 3 and row.M_score >= 3:
#         return "Loyal Customers"
#     if row.R_score >= 3 and row.F_score >= 2:
#         return "Potential Loyalists"
#     if row.R_score <= 2 and row.M_score >= 3:
#         return "At Risk"
#     return "Others"

# rfm["segment"] = rfm.apply(segment, axis=1)
# print(rfm["segment"].value_counts())
# rfm.to_csv("rfm_customer_segments.csv", index=False)
