import numpy as np

def random_predict(number:int=np.random.randint(1, 101)) -> int:
    """Prediction of the random number from the range 
       (adjustable can be replaced by user iput) via algorithm
       that will keep attempts number in the stable range below 10
       (main goal is to keep avg attemts on the lvl of 7).

       Args:
       number (int, random): Number which we are trying to find.

       Returns:
       int: Number of attempts
    """
    count = 0
    upper = 101                                             #upper border of the generated list
    lower = 1                                               #lower border of the generated list
    number_range = [x for x in range(lower,upper)]          #generated searching list
    
    while True:
        count += 1
        predict_number = number_range[round(len(number_range)/2)-1]
        
        if predict_number > number:                          #First check
            upper = predict_number+1                         #if number is in the lower range
            number_range = [x for x in range(lower,upper)]   #cutting off upper range and searching in
            #print(predict_number)                           #the lower range
        
        elif predict_number < number:                        #Second check
            lower = predict_number                           #if number is in the higher range
            upper += 1                                       #cutting off lower range
            number_range = [x for x in range(lower,upper)]   #and proceed searching
            #print(predict_number)
        
        else:                                                #Final result
            break
                    
    return count

def score_game(random_predict) -> int:
    """Calculation of the average number of attempts that
       needed to find our number 

       Args:
       random_predict ([type]): prediction function from abowe

       Returns:
       int: avg numbers of attempts
    """
    count_ls = []
    #np.random.seed(1)                                        #fixing seed (dunno what it is realy >.<)
    random_array = np.random.randint(1, 101, size=(1000))     #ammount of cycles to find the number in the stated range

    for number in random_array:
        count_ls.append(random_predict(number))

    score = int(np.mean(count_ls))
    print(f"It takes: {score} attempts to find the number in average")
    return score


if __name__ == "__main__":
    # RUN
    score_game(random_predict)

random_predict()