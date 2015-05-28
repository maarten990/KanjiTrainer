import itertools
import math
import operator

# higher weight = higher importance to history
def exp_moving_avg(history):
     ewma   = history[-1]
     weight = 2/(len(history)+1)
 
     for i in reversed(range(len(history)-1)):
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
    
# test thingamajig    
def main(): 
    history = [1,1,0,0,1,1,0,1,0,1,1,1,1,1,0,0,1,1,1,1]
    print(log_num_done(history))
    print(log_num_missed(history))
    print(percent_correct(history))
    print(exp_moving_avg(history))
    print(streak(history))
    print(top_streak(history))
    
if __name__ == '__main__':
    main()
