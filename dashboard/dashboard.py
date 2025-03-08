import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from babel.numbers import format_currency
sns.set(style='dark')
st.set_page_config(layout="wide")

def create_yearly_orders_df(df):
    yearly_orders_df = df.resample(rule='Y', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    
    yearly_orders_df.index = yearly_orders_df.index.strftime('%Y')

    yearly_orders_df = yearly_orders_df.reset_index()
    yearly_orders_df.rename(columns={"order_id": "order_count", "price": "revenue"}, inplace=True)
    
    return yearly_orders_df

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",  
        "price": "sum"  
    })

    monthly_orders_df = monthly_orders_df.reset_index()

    monthly_orders_df["year"] = monthly_orders_df["order_purchase_timestamp"].dt.year
    monthly_orders_df["month"] = monthly_orders_df["order_purchase_timestamp"].dt.strftime('%b')  

    monthly_orders_df["order_purchase_timestamp"] = monthly_orders_df["order_purchase_timestamp"].dt.strftime('%Y-%m')
    monthly_orders_df.rename(columns={"order_id": "order_count", "price": "revenue"}, inplace=True)

    return monthly_orders_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df

def create_bypayment_df(df):
    bypayment_df = df.groupby(by="payment_type").customer_id.nunique().reset_index()
    bypayment_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bypayment_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").order_item_id.sum().sort_values(ascending=False).reset_index()
    
    sum_order_items_df["product_category_name_english"] = sum_order_items_df["product_category_name_english"].apply(lambda x: x.replace("_", " ").title())
    
    return sum_order_items_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    rfm_df["customer_label"] = [f"USER_{i:03}" for i in range(1, len(rfm_df) + 1)]
    
    return rfm_df

#Membaca Data
file_path = os.path.join(os.path.dirname(__file__), "all_data.csv")
all_df = pd.read_csv(file_path)

datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "shipping_limit_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


#Membuat DataFrame
yearly_orders_df = create_yearly_orders_df(all_df)
monthly_orders_df = create_monthly_orders_df(all_df)
sum_order_items_df = create_sum_order_items_df(all_df)
bystate_df = create_bystate_df(all_df)
bycity_df = create_bycity_df(all_df)
bypayment_df = create_bypayment_df(all_df)
rfm_df = create_rfm_df(all_df)


#VISUALISASI DASHBOARD
st.header('📊 Public E-Commerce Dashboard 🛍️')
st.subheader('🔎 Insights & Analytics for Better Decisions')
st.markdown('---') 

# SECTION: Yearly Orders & Revenue
st.header("📆 Yearly Performance Summary")

col1, col2 = st.columns(2)

# Yearly Orders
with col1:
    st.subheader("📦 Yearly Orders")

    total_orders = yearly_orders_df["order_count"].sum()
    st.metric(label="Total Orders", value=f"{total_orders:,}")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(yearly_orders_df["order_purchase_timestamp"], yearly_orders_df["order_count"], 
            marker='o', linewidth=2, color="#72BCD4", label="Order Count")

    for i, txt in enumerate(yearly_orders_df["order_count"]):
        ax.text(yearly_orders_df["order_purchase_timestamp"][i], yearly_orders_df["order_count"][i], 
                str(txt), ha="center", va="bottom", fontsize=10, color="#72BCD4")

    ax.set_title("Number of Orders per Year", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Order Count")
    ax.set_xticks(yearly_orders_df["order_purchase_timestamp"])
    ax.set_xticklabels(yearly_orders_df["order_purchase_timestamp"], rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)

# Yearly Revenue
with col2:
    st.subheader("💰 Yearly Revenue")
    total_revenue = yearly_orders_df["revenue"].sum()
    st.metric(label="Total Revenue", value=f"USD$ {total_revenue:,}")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(yearly_orders_df["order_purchase_timestamp"], yearly_orders_df["revenue"], 
            marker='s', linewidth=2, color="#FF5733", label="Revenue")

    for i, txt in enumerate(yearly_orders_df["revenue"]):
        ax.text(yearly_orders_df["order_purchase_timestamp"][i], yearly_orders_df["revenue"][i], 
                f"{txt:,.0f}", ha="center", va="bottom", fontsize=10, color="#FF5733")

    ax.set_title("Revenue per Year", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Revenue (USD$)")
    ax.set_xticks(yearly_orders_df["order_purchase_timestamp"])
    ax.set_xticklabels(yearly_orders_df["order_purchase_timestamp"], rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---") 

# SECTION: Monthly Orders & Revenue
col1, col2 = st.columns([1, 1]) 

with col1:
    st.markdown("## 📊 Monthly Performance Summary")

with col2:
    selected_metric = st.selectbox("Pilih Metrik:", ["Order Count", "Revenue"], index=0)
    selected_year = st.selectbox("Pilih Tahun:", ["All", 2016, 2017, 2018], index=0)

# Filter Data
if selected_year != "All":
    filtered_df = monthly_orders_df[monthly_orders_df["year"] == selected_year]
else:
    filtered_df = monthly_orders_df.groupby("month").sum().reset_index()

metric_column = "order_count" if selected_metric == "Order Count" else "revenue"

# Visualisasi data
fig, ax = plt.subplots(figsize=(6, 3))  
fig.tight_layout()
ax.plot(
    filtered_df["month"], 
    filtered_df[metric_column], 
    marker='o' if metric_column == "order_count" else 's', 
    linestyle='-', 
    color="blue" if metric_column == "order_count" else "red"
)

ax.set_title(f"Monthly {selected_metric} Trend ({selected_year})", fontsize=14)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel(selected_metric, fontsize=12)
ax.set_xticks(filtered_df["month"])
ax.set_xticklabels(filtered_df["month"], rotation=45)
ax.grid(True)

with st.container():
    st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---") 

# SECTION: Segmentasi Pelanggan
st.markdown("## 📊 Customer Segmentation")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🏛 Top 10 States by Number of Customers")

    bystate_df = bystate_df.sort_values(by="customer_count", ascending=False).head(10)

    highlight_color = "#2A9D8F"
    default_color = "#D3D3D3"
    colors = [highlight_color] + [default_color] * (len(bystate_df) - 1)

    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x="customer_count", y="customer_state", data=bystate_df, palette=colors, ax=ax)

    for index, value in enumerate(bystate_df["customer_count"]):
        ax.text(value + 50, index, str(value), va="center", fontsize=10, color="black")

    ax.set_title("Top 10 States by Number of Customers", fontsize=14, fontweight="bold")
    ax.set_xlabel("Number of Customers", fontsize=12)
    ax.set_ylabel("State", fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    st.pyplot(fig)

with col2:
    st.markdown("### 🏙 Top 10 Cities by Number of Customers")

    bycity_df = bycity_df.sort_values(by="customer_count", ascending=False).head(10)

    highlight_color = "#8E44AD"
    default_color = "#BEBEBE"
    colors = [highlight_color] + [default_color] * (len(bycity_df) - 1)

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x="customer_count", y="customer_city", data=bycity_df, palette=colors, ax=ax)

    for index, value in enumerate(bycity_df["customer_count"]):
        ax.text(value + 50, index, str(value), va="center", fontsize=10, color="black")

    ax.set_title("Top 10 Cities by Number of Customers", fontsize=14, fontweight="bold")
    ax.set_xlabel("Number of Customers", fontsize=12)
    ax.set_ylabel("City", fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)

# Segmentasi pelanggan by payment method
st.markdown("### 💳 Payment Methods Distribution")

col_left, col_middle, col_right = st.columns([1, 2, 1])

with col_middle:
    payment_counts_percentage = all_df["payment_type"].value_counts(normalize=True) * 100
    labels = [label.replace("_", " ").title() for label in payment_counts_percentage.index]
    colors = ["#72BCD4", "#FFC300", "#FF5733", "#C70039"]

    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(payment_counts_percentage, labels=labels, autopct='%1.1f%%',
           colors=colors, startangle=140, wedgeprops={'edgecolor': 'black'})

    ax.set_title("Distribution of Payment Methods", fontsize=14, fontweight="bold")

    st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---") 


#SECTION: Kategori Produk paling diminati dan paling jarang diminati
st.markdown("## 🏆 Best & Worst Performing Product Categories")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 🔵 Best Performing Product Categories")
    top_categories = sum_order_items_df.head(8)
    top_categories = top_categories.squeeze()
    top_colors = sns.color_palette("Blues_r", len(top_categories))
    
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(
        x="order_item_id",
        y="product_category_name_english",
        data=top_categories,
        hue=top_categories.index,
        palette=top_colors,
        legend=False,
        ax=ax
    )

    for index, value in enumerate(top_categories.order_item_id):
        ax.text(value + 5, index, str(value), va="center", fontsize=10, color="black")

    ax.set_xlabel("Number of Orders", fontsize=10)
    ax.set_ylabel(None)
    ax.set_title("Top Product Categories", fontsize=12, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    st.pyplot(fig)

with col2:
    st.markdown("#### 🟠 Worst Performing Product Categories")
    bottom_categories = sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(8)
    bottom_categories = bottom_categories.squeeze()
    bottom_colors = sns.color_palette("Oranges", len(bottom_categories))
    
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(
        x="order_item_id",
        y="product_category_name_english",
        data=bottom_categories,
        hue=bottom_categories.index,
        palette=bottom_colors,
        legend=False,
        ax=ax
    )

    for index, value in enumerate(bottom_categories.order_item_id):
        ax.text(value + 2, index, str(value), va="center", fontsize=10, color="black")

    ax.invert_xaxis()
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.set_xlabel("Number of Orders", fontsize=10)
    ax.set_ylabel(None)
    ax.set_title("Least Popular Product Categories", fontsize=12, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---") 

#SECTION: RFM Analysis
st.markdown("## 💡 RFM Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "USD$", locale='es_CO')
    st.metric("Average Monetary", value=avg_monetary)

recency_colors = sns.color_palette("Blues_r", 5)
frequency_colors = sns.color_palette("Greens", 5)
monetary_colors = sns.color_palette("Oranges", 5)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))

# Plot Recency
sns.barplot(y="recency", x="customer_label",
            data=rfm_df.sort_values(by="recency", ascending=True).head(5),
            palette=recency_colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer", fontsize=25)
ax[0].set_title("By Recency (days)", loc="center", fontsize=35, fontweight="bold")
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis='x', labelsize=20, rotation=45)

# Plot Frequency
sns.barplot(y="frequency", x="customer_label",
            data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
            palette=frequency_colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer", fontsize=25)
ax[1].set_title("By Frequency", loc="center", fontsize=35, fontweight="bold")
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=20, rotation=45)

# Plot Monetary
sns.barplot(y="monetary", x="customer_label",
            data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
            palette=monetary_colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer", fontsize=25)
ax[2].set_title("By Monetary", loc="center", fontsize=35, fontweight="bold")
ax[2].tick_params(axis='y', labelsize=25)
ax[2].tick_params(axis='x', labelsize=20, rotation=45)

plt.tight_layout()
st.pyplot(fig)


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---") 

st.caption('Copyright (c) Muhammad Awwal Aryananta - 2025')