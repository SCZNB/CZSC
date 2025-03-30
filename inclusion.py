#这个文件夹是为了处理包含问题

# ------------------------------第一二步开始：初步分型，包含关系处理------------------------------

# 第一步：初步判断顶底分型，只储存最近的分型信息用作包含判断的条件
# 第二步：根据初步顶底分型判断，更改

# The columns of the data are in order: close, high, low, open, volume
# 先判断顶底分型，然后导出处理了包含关系后的数据
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

def candle_plot(df,ticker):
    # Convert the 'Datetime' column to datetime
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    #Plot candle stick of original data
    mpf.plot(data=df,
             type='candle',
             volume=True,
             style='charles',
             title=f'Original Candlestick Chart({ticker})',
    )



def inclusion_process(df, ticker):
    clean_df = df.copy().reset_index()
    clean_df['TS'] = clean_df['Datetime']
    clean_df['TE'] = clean_df['Datetime']

    # 预处理：确保前两根K线无包含关系
    while len(clean_df) >= 2:
        current = clean_df.iloc[0]
        next_ = clean_df.iloc[1]

        if (current['High'] >= next_['High'] and current['Low'] <= next_['Low']) or \
                (next_['High'] >= current['High'] and next_['Low'] <= current['Low']):
            clean_df = clean_df.iloc[1:].reset_index(drop=True)
        else:
            break

    # 主处理循环
    i = 0
    while i < len(clean_df) - 2:
        current = clean_df.iloc[i]
        next_ = clean_df.iloc[i + 1]
        further = clean_df.iloc[i + 2]

        # 判断包含关系
        is_contained = (next_['High'] >= further['High'] and next_['Low'] <= further['Low']) or \
                       (further['High'] >= next_['High'] and further['Low'] <= next_['Low'])

        if is_contained:
            # 方向判断
            if i > 0:
                prev_k = clean_df.iloc[i - 1]
                direction = 'up' if prev_k['High'] < current['High'] else 'down'
            else:
                direction = 'up' if current['High'] < next_['High'] else 'down'

            # 记录初始时间范围
            start_time = next_['TS']
            end_time = further['TE']

            # 创建合并后的K线（关键修改：TS取最早，TE取最晚）
            merged = {
                'Datetime': further['Datetime'],  # 使用最后一根的时间作为显示时间
                'Open': next_['Open'],
                'High': max(next_['High'], further['High']) if direction == 'up' else min(next_['High'],
                                                                                          further['High']),
                'Low': max(next_['Low'], further['Low']) if direction == 'up' else min(next_['Low'], further['Low']),
                'Close': further['Close'],
                'Volume': next_['Volume'] + further['Volume'],
                'TS': start_time,
                'TE': end_time
            }

            # 使用i+1.5插入
            clean_df.loc[i + 1.5] = merged  # 在i+1和i+2之间插入
            clean_df = clean_df.sort_index().reset_index(drop=True)

            # 删除原K线
            clean_df.drop([i + 2, i + 3], inplace=True)  # 原i+1变为i+1，原i+2变为i+3
            clean_df.reset_index(drop=True, inplace=True)

            print(f"合并 {merged['TS']} 至 {merged['TE']} 的K线")
            # 不增加i，继续检查
        else:
            i += 1

    # 时区处理
    clean_df['TS'] = pd.to_datetime(clean_df['TS']).dt.tz_localize(None)
    clean_df['TE'] = pd.to_datetime(clean_df['TE']).dt.tz_localize(None)
    clean_df['Datetime'] = pd.to_datetime(clean_df['Datetime']).dt.tz_localize(None)
    clean_df.set_index('Datetime', inplace=True)
    print(clean_df)

    # 结果保存和绘图
    clean_df.to_csv('inclusion_processed_V1.csv', index=True)
    mpf.plot(clean_df, type='candle', volume=True, style='charles',
             title=f'Processed Klines ({ticker})')

    return clean_df