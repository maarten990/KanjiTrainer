import itertools
import math
import operator

# higher weight = higher importance to history
def exp_moving_avg(history):
     ewma   = history[-1] # alternative? 
     ewma   = .33 # P(first problem correct)
     weight = 2/(len(history)+1)
     
     for i in reversed(range(len(history))):
         ewma = weight * history[i] + (1 - weight) * ewma
     return ewma


def top_streak(history): 
    top_streak = 0
    streak = 0
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

def get_all(history): 
    history = history[1:] # quick fix for non-empty initialization
    return [sum(history), len(history), percent_correct(history), exp_moving_avg(history), streak(history), top_streak(history)]
    
def predict(history):
    # parameters from Khan Academy - obviously not good. 
    INTERCEPT       = -1.2229719
    EWMA            = 0.8393673
    STREAK          = 0.0153545
    LOG_NUM_DONE    = 0.4135883
    LOG_NUM_MISSED  = -0.5677724
    PERCENT_CORRECT = 0.6284309
    
    lnd            = log_num_done(history)
    lnm            = log_num_missed(history)
    perc_cor       = percent_correct(history)
    ewma           = exp_moving_avg(history)
    current_streak = streak(history)
    highest_streak = top_streak(history)
    
    weighted_features = [
                (ewma, EWMA),
                (current_streak, STREAK),
                (lnd, LOG_NUM_DONE),
                (lnm, LOG_NUM_MISSED),
                (perc_cor, PERCENT_CORRECT),
            ]
    X, weight_vector = zip(*weighted_features)
    dot_product      = sum( weight_vector[i]*X[i] for i in range(len(X)))
    z                = dot_product + INTERCEPT
    prediction       = 1.0 / (1.0 + math.exp(-z))
    return prediction
    
# test thingamajig    
def main(): 
    history = [1,1,0,0,1,1,0,1,0,1,1,1,1,1,0,0,1,1,1,1]
    history = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    history = [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1]
    history = [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0]
    history = [1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1]
    print(exp_moving_avg(history))
    print(predict(history))
    
if __name__ == '__main__':
    main()
