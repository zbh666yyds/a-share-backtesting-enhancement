# baostock_data.py

import baostock as bs
import pandas as pd
import time


def login_baostock():
    """
    登录 baostock 系统
    """
    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError(f"baostock 登录失败：{lg.error_msg}")
    print("✅ baostock 登录成功")


def logout_baostock():
    """
    登出 baostock 系统
    """
    bs.logout()
    print("✅ baostock 已登出")


def get_a_stock_list(limit=None):
    """
    获取当前正常上市的 A 股股票列表

    参数：
        limit: 限制股票数量，调试时可以先设置为 20 或 50

    返回：
        DataFrame，包含 code, code_name 等字段
    """
    rs = bs.query_stock_basic()

    data_list = []
    while rs.next():
        row = rs.get_row_data()
        data_list.append(row)

    df = pd.DataFrame(data_list, columns=rs.fields)

    # 只保留正常上市股票
    df = df[df["status"] == "1"]

    # 只保留股票，排除指数等
    # baostock 中 type=1 一般表示股票
    df = df[df["type"] == "1"]

    # 只保留沪深 A 股，排除 B 股等
    df = df[df["code"].str.startswith(("sh.6", "sz.0", "sz.3"))]

    df = df.reset_index(drop=True)

    if limit is not None:
        df = df.head(limit)

    print(f"✅ 获取 A 股股票数量：{len(df)}")
    return df


def get_stock_data(code, start_date="2023-01-01", end_date="2024-12-31", adjustflag="2"):
    """
    下载单只 A 股历史行情数据，并转换成 backtesting.py 需要的格式

    参数：
        code: 股票代码，例如 'sh.600000'、'sz.000001'
        start_date: 开始日期
        end_date: 结束日期
        adjustflag:
            1：后复权
            2：前复权
            3：不复权

    返回：
        DataFrame，字段包括 Open, High, Low, Close, Volume
    """
    fields = "date,code,open,high,low,close,volume,amount,turn,pctChg"

    rs = bs.query_history_k_data_plus(
        code,
        fields,
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag=adjustflag
    )

    if rs.error_code != "0":
        print(f"❌ {code} 数据下载失败：{rs.error_msg}")
        return pd.DataFrame()

    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())

    df = pd.DataFrame(data_list, columns=rs.fields)

    if df.empty:
        return df

    # 转换数据类型
    numeric_cols = ["open", "high", "low", "close", "volume", "amount", "turn", "pctChg"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 日期转换
    df["date"] = pd.to_datetime(df["date"])

    # 删除缺失值
    df = df.dropna()

    # backtesting.py 需要这些列名
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })

    df = df.set_index("date")

    # 只保留 backtesting.py 需要的字段
    df = df[["Open", "High", "Low", "Close", "Volume"]]

    return df


def get_custom_stock_list(codes):
    """
    自定义股票列表，例如：
    ['sh.600519', 'sz.000858', 'sz.300750']
    """
    return pd.DataFrame({"code": codes})


def safe_get_stock_data(code, start_date, end_date, adjustflag="2", min_rows=120):
    """
    更安全的数据下载函数：
    - 下载失败返回空 DataFrame
    - 数据太少返回空 DataFrame
    - 自动稍微暂停，避免请求过快
    """
    try:
        df = get_stock_data(code, start_date, end_date, adjustflag)
        time.sleep(0.2)

        if df.empty:
            print(f"⚠️ {code} 无数据，已跳过")
            return pd.DataFrame()

        if len(df) < min_rows:
            print(f"⚠️ {code} 数据不足 {min_rows} 行，已跳过")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"❌ {code} 处理失败：{e}")
        return pd.DataFrame()