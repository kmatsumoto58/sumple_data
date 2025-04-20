import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="販売データダッシュボード",
    page_icon="📊",
    layout="wide"
)

# アプリケーションのタイトル
st.title("📊 販売データダッシュボード")
st.markdown("このダッシュボードでは、販売データの分析と可視化を行います。")

# サイドバー
st.sidebar.header("データ読み込み")

# ファイルアップロード機能
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロード", type=["csv"])

# デモデータの使用オプション
use_demo_data = st.sidebar.checkbox("デモデータを使用", value=True)

# データの読み込み
@st.cache_data
def load_data():
    try:
        return pd.read_csv('sales_data.csv')
    except:
        st.error("デモデータファイル（sales_data.csv）が見つかりません。")
        return pd.DataFrame()

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif use_demo_data:
    df = load_data()
else:
    st.info("CSVファイルをアップロードするか、デモデータを使用してください。")
    st.stop()

# データの前処理
df['日付'] = pd.to_datetime(df['日付'])
df['月'] = df['日付'].dt.strftime('%Y-%m')

# データフィルタリングオプション
st.sidebar.header("データフィルター")

# 日付範囲フィルター
date_range = st.sidebar.date_input(
    "日付範囲を選択",
    [df['日付'].min(), df['日付'].max()],
    min_value=df['日付'].min(),
    max_value=df['日付'].max()
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['日付'] >= pd.Timestamp(start_date)) & (df['日付'] <= pd.Timestamp(end_date))
    filtered_df = df[mask]
else:
    filtered_df = df

# カテゴリフィルター
all_categories = ['すべて'] + sorted(df['商品カテゴリ'].unique().tolist())
selected_category = st.sidebar.selectbox('商品カテゴリを選択', all_categories)

if selected_category != 'すべて':
    filtered_df = filtered_df[filtered_df['商品カテゴリ'] == selected_category]

# メインコンテンツ
if not filtered_df.empty:
    # データ概要
    st.header("データ概要")
    total_sales = filtered_df['売上高'].sum()
    total_quantity = filtered_df['数量'].sum()
    avg_price = filtered_df['単価'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("総売上高", f"¥{total_sales:,.0f}")
    col2.metric("総販売数量", f"{total_quantity:,}個")
    col3.metric("平均単価", f"¥{avg_price:,.0f}")
    
    # データテーブル（先頭10行を表示）
    with st.expander("データテーブル", expanded=False):
        st.dataframe(filtered_df.head(10))
        
        # CSVのダウンロードボタン
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSVとしてダウンロード",
            data=csv,
            file_name='filtered_sales_data.csv',
            mime='text/csv',
        )
    
    # タブでビジュアライゼーションを分ける
    tab1, tab2, tab3 = st.tabs(["時系列分析", "カテゴリ分析", "商品分析"])
    
    with tab1:
        st.subheader("時系列での売上推移")
        
        # 日次売上データの集計
        daily_sales = filtered_df.groupby('日付')['売上高'].sum().reset_index()
        
        # 折れ線グラフの作成
        fig = px.line(
            daily_sales, 
            x='日付', 
            y='売上高',
            title='日次売上推移',
            labels={'売上高': '売上高 (円)', '日付': '日付'},
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 月次売上データの集計
        monthly_sales = filtered_df.groupby('月')['売上高'].sum().reset_index()
        
        # 棒グラフの作成
        fig = px.bar(
            monthly_sales, 
            x='月', 
            y='売上高',
            title='月次売上推移',
            labels={'売上高': '売上高 (円)', '月': '月'},
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("商品カテゴリ分析")
        
        # カテゴリ別売上の集計
        category_sales = filtered_df.groupby('商品カテゴリ')['売上高'].sum().reset_index()
        category_sales = category_sales.sort_values('売上高', ascending=False)
        
        # 円グラフの作成
        fig = px.pie(
            category_sales, 
            values='売上高', 
            names='商品カテゴリ',
            title='カテゴリ別売上構成比',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # カテゴリ別のヒートマップ
        category_monthly = filtered_df.groupby(['月', '商品カテゴリ'])['売上高'].sum().unstack().fillna(0)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(category_monthly, annot=True, cmap='viridis', fmt='.0f', ax=ax)
        plt.title('月次・カテゴリ別売上ヒートマップ')
        plt.ylabel('月')
        plt.xlabel('商品カテゴリ')
        st.pyplot(fig)
    
    with tab3:
        st.subheader("商品分析")
        
        # カテゴリ選択
        if selected_category == 'すべて':
            category_for_products = st.selectbox('商品を表示するカテゴリを選択', sorted(df['商品カテゴリ'].unique().tolist()))
            product_data = filtered_df[filtered_df['商品カテゴリ'] == category_for_products]
        else:
            product_data = filtered_df
        
        # 商品別売上の集計
        product_sales = product_data.groupby('商品名')['売上高'].sum().reset_index()
        product_sales = product_sales.sort_values('売上高', ascending=False)
        
        # 水平棒グラフの作成
        fig = px.bar(
            product_sales, 
            y='商品名', 
            x='売上高',
            title='商品別売上ランキング',
            labels={'売上高': '売上高 (円)', '商品名': '商品名'},
            orientation='h',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 商品別の平均単価と販売数量の散布図
        product_stats = product_data.groupby('商品名').agg({
            '数量': 'sum',
            '単価': 'mean',
            '売上高': 'sum'
        }).reset_index()
        
        fig = px.scatter(
            product_stats, 
            x='単価', 
            y='数量',
            size='売上高',
            color='商品名',
            title='商品別: 平均単価 vs 販売数量',
            labels={'単価': '平均単価 (円)', '数量': '販売数量 (個)'},
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    # インタラクティブな分析セクション
    st.header("インタラクティブ分析")
    
    # カスタム集計の作成
    st.subheader("カスタム集計")
    
    col1, col2 = st.columns(2)
    groupby_field = col1.selectbox("集計単位", ["日付", "月", "商品カテゴリ", "商品名"])
    agg_field = col2.selectbox("集計項目", ["売上高", "数量", "単価"])
    
    agg_function = st.radio("集計方法", ["合計", "平均", "最大", "最小"], horizontal=True)
    
    agg_map = {
        "合計": "sum",
        "平均": "mean",
        "最大": "max",
        "最小": "min"
    }
    
    # 集計を実行
    custom_agg = filtered_df.groupby(groupby_field)[agg_field].agg(agg_map[agg_function]).reset_index()
    custom_agg = custom_agg.sort_values(agg_field, ascending=False)
    
    # 結果表示
    st.dataframe(custom_agg)
    
    # チャート表示
    chart_type = st.radio("チャートタイプ", ["棒グラフ", "折れ線グラフ", "散布図"], horizontal=True)
    
    if chart_type == "棒グラフ":
        fig = px.bar(
            custom_agg, 
            x=groupby_field, 
            y=agg_field,
            title=f'{groupby_field}別 {agg_field}の{agg_function}',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "折れ線グラフ":
        fig = px.line(
            custom_agg, 
            x=groupby_field, 
            y=agg_field,
            title=f'{groupby_field}別 {agg_field}の{agg_function}',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # 散布図
        if len(custom_agg) <= 1:
            st.warning("散布図の表示には2つ以上のデータポイントが必要です。")
        else:
            fig = px.scatter(
                custom_agg, 
                x=groupby_field, 
                y=agg_field,
                title=f'{groupby_field}別 {agg_field}の{agg_function}',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("選択された条件に一致するデータがありません。フィルター条件を変更してください。")

# フッター
st.markdown("---")
st.markdown("Streamlitで作成した販売データダッシュボード | 2025年")