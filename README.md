# A-share Backtesting Enhancement

This project is an enhancement based on the open-source Python library `backtesting.py`.

Original project: https://github.com/kernc/backtesting.py

## Main Features

* Use `baostock` to download A-share daily stock data
* Support custom stock list and automatic A-share stock pool
* Implement a simple moving average crossover strategy
* Run batch backtests on multiple stocks
* Sort backtest results by return, Sharpe ratio, drawdown, etc.
* Export results to Excel

## Files

* `main.py`: main program
* `baostock_data.py`: A-share data download and preprocessing
* `strategies.py`: trading strategy
* `result_manager.py`: result formatting and export

## How to Run

Install dependencies:

```bash
pip install baostock pandas openpyxl backtesting
```

Run the project:

```bash
python3 main.py
```

## Strategy

The default strategy is a moving average crossover strategy:

* Buy when the short-term moving average crosses above the long-term moving average
* Sell when the long-term moving average crosses above the short-term moving average

## Output

The program exports the backtest results to:

```text
a_stock_backtest_results.xlsx
```
