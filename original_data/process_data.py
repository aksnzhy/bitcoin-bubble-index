import collections
import datetime
import json
import math

def get_bubble_index(price,
                     growth_60_day,
                     hot_keywords,
                     difficulty_value,
                     sentaddr_value,
                     trascation_value):
    """Calculate bitcoin bubble index

    Parameters
    ----------
    price : float
        bitcoin price, USD
    growth_60_day : float
        60 days accumulative increase
    hot_keywords : float
        google trend and twitter index
    difficulty_value : float
       average minining difficulty per day
    sentaddr_value : float
        number of unique active address per day
    transcation_value : float
        median transaction value, USD
        
    Returns
    -------
    float
        bubble index
    """
    bubble_index_0 = 5000 * price  / (sentaddr_value + difficulty_value / 10000000 + trascation_value)
    bubble_index_1 = growth_60_day * math.pi + hot_keywords / math.pi
    return bubble_index_0 + bubble_index_1 / 10.0 - 30.0

def get_hot_value(gtread_value, tweets_value):
    """Callculate key-words hot value in google trend and tweets.

    Parameters
    ----------
    gtread : float
        google trend index
    tweets_value : float
        twitter trend index

    Returns
    -------
    float
        hot value
    """
    return math.sqrt(tweets_value) + gtread_value * 6.27

def get_day(start_date, gap_day):
    """Given a start date and day gap, return the target date.

    Forexample, the start_date is '2017/01/01' and gap_day is 1, the
    target date is '2017/01/02'.

    Parameters
    ----------
    start_date : str
        string of start date, e.g, '2017/01/01'
    gap_day : int
        gap of day

    Returns
    -------
    str
        string of target date
    """
    tmp = datetime.datetime.strptime(start_date, '%Y/%m/%d')
    target_date = (tmp + datetime.timedelta(days=gap_day)).strftime('%Y/%m/%d')
    return target_date

def read_datafile(filename):
    """Read txt data file by given the filename.

    Parameters
    ----------
    filename : str
        name of data file

    Returns
    -------
    list
        a list of string that contains the datetime (key) and data (value), e.g.
        '2010/07/26:181.543' or '2010/12/07:5.25E-5'
    """
    result = []

    file = open(filename, "r")
    txt_data = file.read()
    index = 0
    key = ''
    value = ''
    for data in txt_data.split(','):
        if index % 2 == 0:
            key = data.translate(None, '[new Date("")')
        else:
            value = data.translate(None, ']')
            result.append(key+":"+value)
        index += 1

    return result

def add_missing_data(start_date, end_date, init_value, scale_factor):
    """Add missing data to a time window [start_date, end_date).

    Here we use a linear scale factor to scale up the missing data.

    Parameters
    ----------
    start_date : str
        string of start date, e.g., '2010/07/17'
    end_date: str
        string of end date, e.g., '2014/04/09'
    init_value : float
        initialize data
    scale_factor : float
        linear scale factor
    """
    result = []
    index = 0
    while True:
        date = get_day(start_date, index)
        if date == end_date:
            break
        init_value += init_value*scale_factor
        result.append(date+':'+str(init_value))
        index += 1

    return result

def process_data():
    """Convert original data to json file
    """
    # Bitcoin price in USD
    price = read_datafile('price.txt')
    # Difficulty index for bitcoin minining
    difficulty = read_datafile('difficulty.txt')
    # Google trend index
    gtread = read_datafile('gtrend.txt')
    # Number of active address 
    sentaddr = read_datafile('sentaddr.txt')
    # Number of transacation per day
    trascation = read_datafile('transcation.txt')
    # Number of tweets per day
    # Tweets file lacks of the data before the date '2014/04/09', 
    # so we mamuannly add missing data from 2010/07/17.
    tweets = add_missing_data(
        start_date='2010/07/17', 
        end_date='2014/04/09', 
        init_value=300, 
        scale_factor=0.002);
    tweets += read_datafile('tweets.txt')

    json_data = {}
    json_data['date'] = []
    json_data['price'] = []
    json_data['growth_60_day'] = []
    json_data['hot'] = []
    json_data['bubble'] = []

    # Get Date, Price, and 60_day_growth
    last_price = 0.0
    accumulate_60 = 0.0
    my_q = queue = collections.deque()
    for data in price:
        key, value = data.split(':')
        json_data['date'].append(key)
        json_data['price'].append('%0.2f'%float(value))
        if last_price == 0.0:
            last_price = float(value)
        if len(my_q) >= 60:
            accumulate_60 -= my_q.popleft()
        day_growth = (float(value) - last_price) / last_price
        accumulate_60 += day_growth
        my_q.append(day_growth)
        last_price = float(value)
        json_data['growth_60_day'].append(int(accumulate_60*100))

    # Get keywords Hot value
    for i in range(len(gtread)):
        gtrend_key, gtread_value = gtread[i].split(':')
        assert gtrend_key == json_data['date'][i]
        tweets_key, tweets_value = tweets[i].split(':')
        assert tweets_key == json_data['date'][i]
        gtread_value = 0.0 if gtread_value == 'null' else float(gtread_value)
        tweets_value = 0.0 if tweets_value == 'null' else float(tweets_value)
        hot_value = get_hot_value(gtread_value, tweets_value)
        json_data['hot'].append(int(hot_value))

    assert len(json_data['hot']) == len(json_data['price'])

    # Get bubble index
    for i in range(len(price)):
        difficulty_key, difficulty_value = difficulty[i].split(':')
        assert difficulty_key == json_data['date'][i]
        sentaddr_key, sentaddr_value = sentaddr[i].split(':')
        assert sentaddr_key == json_data['date'][i]
        trascation_key, trascation_value = trascation[i].split(':')
        assert trascation_key == json_data['date'][i]

        difficulty_value = 0.0 if difficulty_value == 'null' else float(difficulty_value)
        sentaddr_value = 0.0 if sentaddr_value == 'null' else float(sentaddr_value)
        trascation_value = 0.0 if trascation_value == 'null' else float(trascation_value)

        bubble_index = get_bubble_index(
            float(json_data['price'][i]),
            float(json_data['growth_60_day'][i]),
            float(json_data['hot'][i]),
            float(difficulty_value),
            float(sentaddr_value),
            float(trascation_value))

        json_data['bubble'].append(int(bubble_index))

    assert len(json_data['bubble']) == len(json_data['price'])

    # Write json data to file
    file = open('../data.json', "w")
    file.write("data = '")
    file.write(json.dumps(json_data))
    file.write("'")
    file.close()

if __name__ == '__main__':
    process_data()