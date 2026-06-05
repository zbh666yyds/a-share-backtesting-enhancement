# result_manager.py

import pandas as pd


class ResultManager:
    """
    回测结果管理器：
    用于整理、排序、导出多个股票的回测结果
    """

    CORE_MAP = {
        "Return [%]": "总收益率(%)",
        "Buy & Hold Return [%]": "买入持有收益率(%)",
        "Max. Drawdown [%]": "最大回撤(%)",
        "# Trades": "交易次数",
        "Win Rate [%]": "胜率(%)",
        "Sharpe Ratio": "夏普比率",
        "CAGR [%]": "年化收益率(%)",
        "Profit Factor": "盈亏比",
    }

    @staticmethod
    def format_result(stats, code):
        """
        把 backtesting.py 返回的 stats 转成一行 DataFrame
        """
        result = {"股票代码": code}

        for eng_name, cn_name in ResultManager.CORE_MAP.items():
            if eng_name in stats:
                result[cn_name] = stats[eng_name]

        return result

    @staticmethod
    def build_result_table(results):
        """
        把多个股票结果整理成表格
        """
        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)

        # 数值保留两位小数
        for col in df.columns:
            if col != "股票代码":
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

        return df

    @staticmethod
    def sort_results(df, sort_by="总收益率(%)", ascending=False, top_n=20):
        """
        按某个指标排序
        """
        if df.empty:
            return df

        if sort_by not in df.columns:
            print(f"⚠️ 排序字段 {sort_by} 不存在，默认按总收益率排序")
            sort_by = "总收益率(%)"

        df = df.sort_values(by=sort_by, ascending=ascending)

        if top_n is not None:
            df = df.head(top_n)

        return df

    @staticmethod
    def save_to_excel(df, filename="backtest_results.xlsx"):
        """
        保存结果到 Excel
        """
        df.to_excel(filename, index=False)
        print(f"✅ 回测结果已保存到：{filename}")