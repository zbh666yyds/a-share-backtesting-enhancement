# main.py

from backtesting import Backtest

from baostock_data import (
    login_baostock,
    logout_baostock,
    get_a_stock_list,
    get_custom_stock_list,
    safe_get_stock_data
)

from strategies import SmaCrossStrategy
from result_manager import ResultManager


def run_single_backtest(code, start_date, end_date):
    """
    对单只股票进行回测
    """
    data = safe_get_stock_data(
        code=code,
        start_date=start_date,
        end_date=end_date,
        adjustflag="2",
        min_rows=120
    )

    if data.empty:
        return None

    try:
        bt = Backtest(
            data,
            SmaCrossStrategy,
            cash=1000000,
            commission=0.0008,
            exclusive_orders=True
        )

        stats = bt.run()

        result = ResultManager.format_result(stats, code)
        print(f"✅ {code} 回测完成，总收益率：{result.get('总收益率(%)')}")
        return result

    except Exception as e:
        print(f"❌ {code} 回测失败：{e}")
        return None


def run_batch_backtest(
    start_date="2020-01-01",
    end_date="2025-12-31",
    use_custom_list=True,
    limit=30
):
    """
    批量回测函数

    use_custom_list=True:
        使用自定义股票池，速度快，适合调试和展示

    use_custom_list=False:
        使用 baostock 获取 A 股股票池，适合正式跑
    """

    login_baostock()

    try:
        if use_custom_list:
            stock_df = get_custom_stock_list([
                "sh.600519",  # 贵州茅台
                "sh.601995",  # 中金公司
                "sz.300750",  # 宁德时代
                "sh.601138",  # 工业富联
                "sz.000333",  # 美的集团
                "sz.300308",  # 中际旭创
                "sz.002594",  # 比亚迪
                "sh.601899",  # 紫金矿业
                "sh.603345",  # 安井食品
                "sz.300476",  # 胜宏科技
            ])
        else:
            stock_df = get_a_stock_list(limit=limit)

        results = []

        for i, row in stock_df.iterrows():
            code = row["code"]
            print(f"\n正在回测第 {i + 1} 只股票：{code}")

            result = run_single_backtest(code, start_date, end_date)

            if result is not None:
                results.append(result)

        result_df = ResultManager.build_result_table(results)

        if result_df.empty:
            print("❌ 没有得到有效回测结果")
            return

        result_df = ResultManager.sort_results(
            result_df,
            sort_by="总收益率(%)",
            ascending=False,
            top_n=20
        )

        import pandas as pd

        pd.set_option("display.unicode.east_asian_width", True)
        pd.set_option("display.unicode.ambiguous_as_wide", True)
        pd.set_option("display.width", 200)
        pd.set_option("display.max_columns", None)

        result_df = result_df.reset_index(drop=True)

        print("\n========== 回测结果 Top 20 ==========")
        print(result_df.to_string(index=False))

        ResultManager.save_to_excel(result_df, "a_stock_backtest_results.xlsx")

    finally:
        logout_baostock()


if __name__ == "__main__":
    run_batch_backtest(
        start_date="2020-01-01",
        end_date="2025-12-31",
        use_custom_list=True,
        limit=None
    )