The python scripts requires python version 3.5 and above
Both file uses standard python packages except numpy and pandas
If numpy or pandas is not installed there is requirements.txt file which can be used to install both packages
The command for that is: pip install -r requirements.txt

For NaiveBayes.py

Command: python NaiveBayes.py train_data test_data model_file.txt result_file.txt

It will generate 2 files:
	model_file.txt will have all probabilities of values of each attribute
	result_file.txt will contain confusion matrix and actual vs predicted values


For MarkovChain.py

Command:
	python MarkovChain.py aut_dir prob_file.txt result_file.txt
				
					OR
	
	For bonus:
	python MarkovChain.py aut_dir1 aut_dir2 prob1.txt prob2.txt result_file.txt

There is only single file which can handle both commands
The normal one will generate 2 files:
	prob_file.txt will have all probabilities of unigram, bigram and trigram
	result_file.txt will have 10 sentences of at-most length 20 words