#### In this code we want to implement the bollinger band + rsi + candlestick strategy

### buy when :
1. If rsi < oversell level 
2. If price < lower band 
3. Then if we had a candle whose close price was higher than the open price and higher than the lower band

### sell when :
1. If rsi > overbuy level 
2. If price > higher band 
3. Then if we had a candle whose close price was lower than the open price and lower than the higher band

### SL when :

Previous n candles swing (high swing for short positions / low swing for longpositions)

### TP when :
* Mehtod 1  : based on risk to rivard
* Method 2  : middle line of bollinger band