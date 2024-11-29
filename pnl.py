import pandas as pd

# Load the data from CSV file
data = pd.read_csv('trades.csv')

# Filter buy and sell trades
buy_trades = data[data['type'] == 'buy']
sell_trades = data[data['type'] == 'sell']

# Calculate total cost for buy trades and total revenue for sell trades
total_buy_cost = buy_trades['cost'].sum() + buy_trades['fee'].sum()
total_sell_revenue = sell_trades['cost'].sum() - sell_trades['fee'].sum()

# Calculate profitability
total_profit = total_sell_revenue - total_buy_cost

# Calculate average profit per trade
num_trades = len(data)
average_profit_per_trade = total_profit / num_trades

# Display the results
print("Total Buy Cost: $", round(total_buy_cost, 2))
print("Total Sell Revenue: $", round(total_sell_revenue, 2))
print("Total Profit: $", round(total_profit, 2))
print("Average Profit per Trade: $", round(average_profit_per_trade, 2))

# Fee impact
total_fees = data['fee'].sum()
print("Total Fees Paid: $", round(total_fees, 2))
