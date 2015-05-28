import itertools
import math
import operator

# higher weight = higher importance to history
def exp_moving_avg(history):
     ewma   = history[-1] # alternative? 
     ewma   = .33 # P(first problem correct)
     weight = 2/(len(history)+1)
     
     #for i in reversed(range(len(history))):
     for i in range(len(history)):
         ewma = weight * history[i] + (1 - weight) * ewma
     return ewma


def top_streak(history): 
    top_streak = 0
    streak     = 0
    for i in history: 
        if i == 1: 
            streak += 1
        else: 
            if streak > top_streak: 
                top_streak = streak
            streak = 0
    return top_streak
    
def streak(history): 
    streak = 0
    for i in reversed(history): 
        if i == 1: 
            streak += 1
        else: 
            return streak
    return streak
    
def log_num_done(history): 
    return math.log(len(history))
    
def log_num_missed(history): 
    return math.log(len(history) - sum(history)+1)

def percent_correct(history): 
    return sum(history) / len(history)

# return for kanjitrainer.py
def get_all(history): 
    history = history[1:] # quick fix for non-empty initialization
    return [sum(history), len(history), percent_correct(history), exp_moving_avg(history), streak(history), top_streak(history)]
    
def predict(history):
    # parameters fairly random - obviously not good. 
    INTERCEPT       = -1.2229719
    INTERCEPT       = -0.5
    EWMA            = 0.8393673
    STREAK          = 0.0153545
    LOG_NUM_DONE    = 0.4135883
    LOG_NUM_MISSED  = -0.5677724
    PERCENT_CORRECT = 0.6284309
    # higher importance to streak and lower to ewma seems to generate better results
    #STREAK          = EWMA
    #EWMA            = 0.015
    
    
    # get features
    lnd            = log_num_done(history)
    lnm            = log_num_missed(history)
    perc_cor       = percent_correct(history)
    ewma           = exp_moving_avg(history)
    current_streak = streak(history)
    highest_streak = top_streak(history)
    
    # combine features with associated weights
    weighted_features = [
                (ewma, EWMA),
                (current_streak, STREAK),
                (lnd, LOG_NUM_DONE),
                (lnm, LOG_NUM_MISSED),
                (perc_cor, PERCENT_CORRECT),
            ]
    # logistc regression
    X, weight_vector = zip(*weighted_features)
    dot_product      = sum( weight_vector[i]*X[i] for i in range(len(X)))
    z                = dot_product + INTERCEPT
    prediction       = 1.0 / (1.0 + math.exp(-z))
    print(prediction)
    return prediction
    
# higher value for exponent = longer history allowed. 
def is_struggling(history, exponent, min_acc, min_attempts): 
    current_acc = predict(history)
    if len(history) < min_attempts: 
        return False
    if current_acc > min_acc: 
        return False
    value = (len(history) ** exponent) * (min_acc - currenct_acc)    
    return value > 20.0
    
# test thingamajig    
def main(): 
    history = [1,1,0,0,1,1,0,1,0,1,1,1,1,1,0,0,1,1,1,1]
    history = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    history = [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1]
    history = [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0]
    history = [1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1]
    print(exp_moving_avg(history))
    print(predict(history))
    print('----')
    predict([1])
    predict([1,1])
    predict([1,1,1])
    predict([1,1,1,1])
    predict([1,1,1,1,1])
    
if __name__ == '__main__':
    main()
