import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ランダムなデータを作成
np.random.seed(42)  # 再現性のために乱数シードを固定

# 日付の範囲を作成
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(100)]

# 商品カテゴリと商品名
categories = ['電子機器', '衣類', '食品', '書籍', '家具']
products = {
    '電子機器': ['スマートフォン', 'ノートPC', 'タブレット', 'イヤホン', 'スマートウォッチ'],
    '衣類': ['Tシャツ', 'ジーンズ', 'スニーカー', 'ジャケット', 'セーター'],
    '食品': ['チョコレート', 'コーヒー', 'パスタ', 'スナック菓子', '果物'],
    '書籍': ['小説', '参考書', '雑誌', 'コミック', '自己啓発'],
    '家具': ['椅子', 'テーブル', '照明', 'ソファ', 'ベッド']
}

# データフレームの作成
data = []
for date in dates:
    # この日の売上件数をランダムに決定（5〜15件）
    num_sales = np.random.randint(5, 16)
    
    for _ in range(num_sales):
        category = np.random.choice(categories)
        product = np.random.choice(products[category])
        quantity = np.random.randint(1, 11)  # 1〜10個
        
        # カテゴリによって単価の範囲を変える
        if category == '電子機器':
            price = np.random.randint(10000, 100001)
        elif category == '家具':
            price = np.random.randint(5000, 50001)
        elif category == '衣類':
            price = np.random.randint(2000, 15001)
        elif category == '書籍':
            price = np.random.randint(500, 5001)
        else:  # 食品
            price = np.random.randint(100, 2001)
        
        # 売上を計算
        sales = quantity * price
        
        data.append([date.strftime('%Y-%m-%d'), category, product, quantity, price, sales])

# データフレームの作成と保存
df = pd.DataFrame(data, columns=['日付', '商品カテゴリ', '商品名', '数量', '単価', '売上高'])
df.to_csv('sales_data.csv', index=False, encoding='utf-8')

print("サンプルデータを作成し、sales_data.csvに保存しました。")