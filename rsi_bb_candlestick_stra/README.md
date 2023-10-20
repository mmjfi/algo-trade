#### In this code we want to implement the bollinger band + rsi + candlestick strategy

### buy when :
1. if rsi < oversell level 
2. if price < lower band 
3. then if we had a candle whose close price was higher than the open price and higher than the lower band

### sell when :
1. if rsi > overbuy level 
2. if price > higher band 
3. then if we had a candle whose close price was lower than the open price and lower than the higher band

### SL when :

previous n candles swing (high swing for short positions / low swing for longpositions)

### TP when :
* Mehtode 1  : based on risk to rivard
* Methode 2  : middle line of bollinger band