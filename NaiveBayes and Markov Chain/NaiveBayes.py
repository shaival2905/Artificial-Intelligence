#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:17:11 2019

@author: shaivalshah
"""

import pandas as pd
import sys

class NaiveBayes:
    def __init__(self, train_data_path, class_column, model_file, result_file):
        self.train_data = pd.read_csv(train_data_path)
        self.class_column = class_column
        self.total_classes = self.train_data[self.class_column].unique()
        self.model_file = model_file
        self.result_file = result_file
    
    # This function returns all the unique value from the column
    def getUniqueValues(self, column_name):
        return self.train_data[column_name].unique()
    
    # This function returns the dictionary contaning value and its frequency in data, of column passed in argument
    def getCountDictOfAttribute(self, column_name):
        temp_df = self.train_data.groupby([self.class_column, column_name]).size().reset_index(level=1)
        count_dict = {
            col_name: dict(group.values)
            for col_name, group in temp_df.groupby(level=0)
        }
        return count_dict
    
    # This function returns the dictionary contaning value and its probability of occurring, of the column passed
    def getProbabilityDict(self, column_name):
        prob_dict = self.getCountDictOfAttribute(column_name)
        total_values = self.train_data[column_name].unique()
        for class_name, value_dict in prob_dict.copy().items():
            total = sum(value_dict.values())
            for value in total_values:
                if value in prob_dict[class_name]:
                    prob_dict[class_name][value] = round(prob_dict[class_name][value] / total, 4)
                else:
                    prob_dict[class_name][value] = 0
        return prob_dict
    
    # This function generates a dictionary of all columns contaning probability dictionary of that column
    def train(self):
        self.conditional_probs = dict()
        for col in set(self.train_data.columns) - {self.class_column}:
            self.conditional_probs[col] = self.getProbabilityDict(col)
        self.outputModelFile()
        
    # To get the probability of the class column
    def getClassProb(self):
        class_prob_dict = dict()
        total_rows = len(self.train_data)
        for class_name in self.total_classes:
            class_prob_dict[class_name] = len(self.train_data[self.train_data[
                self.class_column] == class_name]) / total_rows
        return class_prob_dict
    
    # This function normalize the probability between 0 to 1 
    def normalize(self, fea_class_prob):
        total = sum(fea_class_prob.values())
        for class_name, prob in fea_class_prob.items():
            fea_class_prob[class_name] = prob / total
        return fea_class_prob
    
    # Output the class name which has probability more than 0.5
    def getClass(self, fea_class_prob):
        for class_name, prob in fea_class_prob.items():
            if prob >= 0.5:
                return class_name
    
    # Predict the class from the test data using the condictional probability dictionary
    def predict(self, test_data):
        predicted_values = []
        class_prob_dict = self.getClassProb()
        for i, row in test_data.iterrows():
            fea_class_prob = {
                class_name: 1 for class_name in self.total_classes
            }
            for class_name in self.total_classes:
                for col in set(self.train_data.columns) - {self.class_column}:
                    fea_class_prob[class_name] = fea_class_prob[
                        class_name] * self.conditional_probs[col][class_name][row[col]]
                fea_class_prob[class_name] = fea_class_prob[
                    class_name] * class_prob_dict[class_name]
            fea_class_prob = self.normalize(fea_class_prob)
            predicted_values.append(self.getClass(fea_class_prob))
        return predicted_values
    
    # Outputs the confusion matrix from the predicted value
    def getConfusionMatrix(self, data, predicted_values):
        mat = [[0 for _ in range(len(self.total_classes))] for _ in range(len(self.total_classes))]
        for actual_value, predicted_value in zip(data['class'], predicted_values):
            mat[actual_value][predicted_value] += 1
        self.outputResultFile(data, mat, predicted_values)
        return mat

    # Writes the conditional probabilities in the model file passed
    def outputModelFile(self):
        with open(self.model_file, 'w') as f:
            for col in set(self.train_data.columns) - {self.class_column}:
                f.write("Conditional probability of feature " + col + "\n")
                for feature_value in list(self.conditional_probs[col].values())[0]:
                    for class_name in self.total_classes:
                        f.write('P({} = {} | {} = {}) = {}\t'.format(
                            col, feature_value, self.class_column, class_name,
                            self.conditional_probs[col][class_name]
                            [feature_value]))
                    f.write("\n")
                f.write("\n")
            f.close()
    
    # Writes the confusion matrix and actual vs predicted values in the result file passed
    def outputResultFile(self, data, mat, predicted_values):
        with open(self.result_file, 'w') as f:
            f.write("Confusion Matrix:\n\n")
            f.write("\t\t|\tPredicted_Pos\t|\tPredicted_Neg\t|\n")
            max_len = len(str(max([max(row) for row in mat])))
            for i in range(len(mat)-1, -1, -1):
                f.write("Actual_{}\t".format('Pos' if i == 1 else 'Neg'))
                for j in range(len(mat[0])-1, -1, -1):
                    if i == 1 and j == 1:
                        con_str = 'TP'
                    elif i == 1 and j == 0:
                        con_str = 'FN'
                    elif i == 0 and j == 1:
                        con_str = 'FP'
                    else:
                        con_str = 'TN'
                    f.write(("|\t{0:2} = {1:"+str(max_len+1)+"}\t").format(con_str, mat[i][j]))
                f.write("|\n")
            f.write("\nResult of prediction\n")
            f.write("\nActual\tPredicted\n")
            for actual_value, predicted_value in zip(data['class'], predicted_values):
                f.write("{}\t{}\n".format(actual_value, predicted_value))
            f.close()


if __name__ == "__main__":
    train_data_path = sys.argv[1]
    model_file = sys.argv[3]
    result_file = sys.argv[4]
    model = NaiveBayes(train_data_path, 'class', model_file, result_file)
    model.train()
    test_data_path = sys.argv[2]
    test_data = pd.read_csv(test_data_path)
    predicted_values = model.predict(test_data)
    print("Confusion Matrix", model.getConfusionMatrix(test_data, predicted_values))