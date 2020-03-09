# Bitcoin Bubble Index

### What's this?

This project provides a visualization analysis tool for price bubble of Bitcoin, including basic price information, 60-days accumulative increase, hot keywords index, and bubble index. We accumulated the original data (`2010/07/17` - `2020/03/09`) and put them into `/original_data` folder, and we visualize our analysis result using [echarts][1].

### Datasets

We provide the following dataset:

 - *price.txt:* The bitcoin price in USD per day. 
 - *sentaddr.txt:* Number of unique active addresses per day. 
 - *transaction.txt:* Number of transactions in BTC blockchain per day. 
 - *difficulty.txt:* Average mining difficulty per day. 
 - *gtrend.txt:* Google Trends to "Bitcoin".
 - *tweets.txt:* Tweets per day #Bitcoin.

You can get the lastest data from [bitinfocharts.com][2]

### How to use

Open `index.html` in your browser directly and you will see the following page:

<img src="https://github.com/aksnzhy/bitcoin-bubble-index/blob/master/index.png" width = "800"/>

In `original_data` folder, you can run the command:

```
python process_data.py
```

to get the analysis result, which will be stored in `data.json`.


  [1]: https://github.com/apache/incubator-echarts
  [2]: https://bitinfocharts.com/comparison/bitcoin-transactions.html