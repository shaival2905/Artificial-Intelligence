%---------------------Utility Funtions Block Starts------------------------

% Max funtion to get maximum value between two
max(X,Y, Max):-
  X > Y, !,
  Max = X;
  Max = Y.

% Min function to get minimum value between two
min(X, Y, Min):-
  X < Y, !,
  Min = X;
  Min = Y.

% Addition function
add(X, Y, Add):-
  Add is X+Y.

% Subtraction function
sub(X, Y, Sub):-
  Sub is X-Y.

%----------------------Utility Funtions Block Ends-------------------------

%-----------------------Early Finish Block Starts--------------------------
/*
This block gives early finish time of task specified
The logic is
To compute the early finish of the current task we need to compute early finish
of the prerequisite task
So first find all the prerequisite tasks of the current task and put them in list
Now computeEF iterate to the list of tasks recursively calling earlyFinish each
time for each task.
After getting early finish time of all prerequisite task max of that time is
selected and value is returned is the early finish time of
later task
Base case is when it reaches to the first task and again computeEF is called it has
no prerequisite so time of finish is given 0
Then duration of current task is added and value returned
*/
computeEF([], MaxTime, MaxTime).

computeEF([H|T], PrevMaxTime, MaxTime):-
  earlyFinish(H, Time),
  max(Time, PrevMaxTime, NextMaxTime),
  computeEF(T, NextMaxTime, MaxTime).

earlyFinish(Task, Time):-
  findall(Taskp, prerequisite(Task,Taskp), Tps),
  computeEF(Tps, 0, Timep),
  duration(Task, X),
  add(Timep, X, Time),!.

%------------------------Early Finish Block Ends---------------------------

%-------------------------Late Start Block Ends----------------------------

/*
Here first, case 1 is checked and if the task specified is last task which is no
prerequisite of any other task then case 1 conditions are further checked.
So it calls case 1 of computeLS which first finds all the tasks given and find
the list of tasks which are at last.
Then max early finish time among those last tasks is returned
Using the value returned from case 1 of computeLS
Here 2 cases are used because we need to find the max early finish time of last
tasks and minimum value from the list containing late start of prerequisite tasks.
Finding last task is done just to optimize so only early finish of those tasks is
computed.
*/

% Checks if the task is last task that is this task is no prerequisite of any other task
checkLastTask(Task):-
  findall(Taskn, prerequisite(Taskn,Task), []).

% Find all tasks which are last that is these tasks are no prerequisite of any other task
findLastTasks([], []).

findLastTasks([H|T], [H|Y]):-
  checkLastTask(H),
  findLastTasks(T, Y).

findLastTasks([_|T], Y):-
  findLastTasks(T, Y).

getMaxEF([], MaxTime, MaxTime).

getMaxEF([H|T], PrevMaxTime, MaxTime):-
  earlyFinish(H, Time),
  max(Time, PrevMaxTime, NextMaxTime),
  getMaxEF(T, NextMaxTime, MaxTime).

% case 1
computeLS([], MinTime):-
  findall(Task, duration(Task, _), Tasks),
  findLastTasks(Tasks, LTasks),
  getMaxEF(LTasks, 0, MinTime).

% case 2
computeLS([], MinTime, MinTime).

computeLS([H|T], PrevMinTime, MinTime):-
  lateStart(H, Time),
  min(Time, PrevMinTime, NextMinTime),
  computeLS(T, NextMinTime, MinTime).

% case 1
lateStart(Task, Time):-
  findall(Taskn, prerequisite(Taskn,Task), []),
  computeLS([], Timen),
  duration(Task, X),
  sub(Timen, X, Time),!.

% case 2
lateStart(Task, Time):-
  findall(Taskn, prerequisite(Taskn,Task), Tns),
  computeLS(Tns, 10000000, Timen),
  duration(Task, X),
  sub(Timen, X, Time).

%-------------------------Late Start Block Starts---------------------------

%-----------------------Critical Path Block Starts--------------------------
/*
This block computes critical path of the node specified
To get path query criticalPath(<task>, <Path>)
Here the logic is:
1) compute value which is equal to earlyFinish - duration
2) Then pass it to prerequisite tasks
3) Select that prerequisite node which has earlyFinish equal to the value passed before
4) Repeat step 2 to 3 untill we get value equal to 0 in step 2, that is where we reach first task
5) Backtrack the result to the main function.
*/

computePath([], 0, Path, Path).

computePath([H|_], ES, PathTemp, Path):-
  earlyFinish(H, ES),
  duration(H, T),
  sub(ES, T, ESh),
  computeCriticalPath(H, ESh, [H|PathTemp], Path).

computePath([_|T], ES, PathTemp, Path):-
  computePath(T, ES, PathTemp, Path).

computeCriticalPath(Task, ES, PathTemp, Path):-
  findall(Taskp, prerequisite(Task,Taskp), Tps),
  computePath(Tps, ES, PathTemp, Path),!.

criticalPath(Task, Path):-
  earlyFinish(Task, Time),
  duration(Task, T),
  sub(Time, T, ES),
  computeCriticalPath(Task, ES, [], Path).

%-----------------------Critical Path Block Ends--------------------------

%-------------------------Max Slack Block Ends----------------------------
/*
This blocks gives answer of the query maxSlack
The logic is first find all the tasks then find the max slack time and task which
has the max slack time.
*/
% returns the max slack time and task which has max slack time
maxTimeNode(Time1, Task1, Time2, Task2, MaxTime, MaxTask):-
  Time1 > Time2, !,
  MaxTime = Time1, MaxTask = Task1;
  MaxTime = Time2, MaxTask = Task2.

findMaxSlack([], MS, MT, MS, MT).

findMaxSlack([H|T], PrevMS, PrevMT, MS, MT):-
  findSlack(H, Time),
  maxTimeNode(Time, H, PrevMS, PrevMT, NextMS, NextMT),
  findMaxSlack(T, NextMS, NextMT, MS, MT),!.

findMaxSlack([_|T], PrevMS, PrevMT, MS, MT):-
  findMaxSlack(T, PrevMS, PrevMT, MS, MT).

findSlack(Task, Time):-
  earlyFinish(Task, EF),
  lateStart(Task, LS),
  duration(Task, D),
  Time is LS-EF+D.

% To get the first element from the list for initial value
getFirst([H|_], H).

maxSlack(Task, Time):-
  findall(T, duration(T, _), Tasks),
  getFirst(Tasks, FN),
  findMaxSlack(Tasks, 0, FN, MS, MT),
  Time is MS,
  Task = MT.

%-------------------------Max Slack Block Ends----------------------------
