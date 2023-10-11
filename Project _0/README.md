# Project 0. Find the number

## Table of content
[1. Project description](README.md#Project-description)  
[2. What case are we trying to solve?](README.md#What-case-are-we-trying-to-solve?)  
[3. Short info about the data](README.md#Short-info-about-the-data)  
[4. Work stages](README.md#Work-stages)  
[5. Result](README.md#Result)    
[6. Conclusion](README.md#Conclusion) 

### Project description    
Find a random number that computer will take from the stated range for minimal number of attempts.

:arrow_up:[To the table of content](README.md#Table_of_content)


### What case are we trying to solve?    
We neen to create a programm that will find a random number in the stated range for minimal number of attempts. 
An algorithm for this programm should be logarithmic i.e. the width influence on the step's number should be minimal.

**Task conditions:**  
- The computer takes a number (int) from the range of 1 to 100 and tryes to guess it. Saying guess we mean we need to write a 
programm that will execute the logic using algorithm to find a number from the stated range.
- Algorithm takes in account the information about the position of a guessed number relatively the position of a prediction i.e.
is it higher or lower than the prediction.

**Quality metrics**     
The result will be rated by the average number of steps/attempts of the algorithm 

**What do we practice**     
Learning how to make a decent code

:arrow_up:[To the table of content](README.md#Table_of_content)

### Short info about the data
The data will be generated from the random range via numpy module
  
:arrow_up:[To the table of content](README.md#Table_of_content)


### Work stages 
1. Describing the idea of algorithm that will create the list of numbers with lenght equal to stated range of numbers and 
taking the middle number from it to check is it higher or lower. On the next step we should create the new numbers list with 
borders based on previous step: if the number that we're trying to guess is higher than the prediction then we're changing the lower border of this list with this prediction number, vice versa if the number is lower we're going to change the top border. After thar the algorithm starts from the beggining. Main idea is to reduce the area of possibility where we can find the number by reducing it in half on every step.

2. Creating the infinite loop with the break point (number == prediction) and internal counter that will keep tracking number of itterations.

3. Implementation within the code of task example that creating the test environment which is beyond my current comprehension.

4. Creating readme file with the description of task, steps, etc. Which was the longest and maybe the hardest part because it just won't work properly.

:arrow_up:[To the table of content](README.md#Table_of_content)


### Result:  
As a result we have the programm that is creating a random number secretly for itself and finding it via sophisticated, never seen 
algorithm in short range of attempts, there is a test programm that I've used to check number of attempts on the large scale, with a 
huge succes I must say not for realisation time though.

:arrow_up:[To the table of content](README.md#Table_of_content)


### Conclusion:  
Our algorithm unbound from the number's scale it's a win, but greater number can take a greater time to execute.

:arrow_up:[To the table of content](README.md#Table_of_content)



If the information about this project was useful for You or atleast intersting in some way I would be realy grateful if You'll tag this rep and profile with ⭐️⭐️⭐️. P.S. Hope there's not a lot of mistakes in the description or comms text. CYA.