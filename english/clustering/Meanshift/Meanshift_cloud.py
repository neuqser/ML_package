import pandas as pd
from sklearn.model_selection import ParameterGrid,GridSearchCV
from sklearn.base import clone
from sklearn.cluster import MeanShift
from sklearn import metrics
import numpy as np
import joblib
import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import sys

def MSGridsearch(dmodel, data, labels, param_dict):
    """
         dmodel: default model
          data：training data
          labels: real classification
          param_dict: hyperparameter combination dictionary
    """
    output_models = []

    # Create parameter grid
   # Create hyperparameter grid
    param_grid = ParameterGrid(param_dict)

    # change the parameter attributes in dbscan according to the param_grid
        # Modify the corresponding parameters of DBSCAN object according to the grid super parameters, train the model, and get the output data
    for param in param_grid:
        for key, value in param.items():
            setattr(dmodel, key, value)

        dmodel.fit(data)
        model = clone(dmodel)
        output_models.append(model)
    #If you have other data to output, just add it
    return (output_models)


#Evaluation criteria, for testing, not the final modular function block



def get_marks(estimator, data, labels,name=None):
    """           To get the score, there are five kinds of actual classification information that are required to know the data set, and there are three kinds that are not required,
       refer to the readme.txt
       
    :param estimator: model
    :param name: initial method
    :param data: feature data set
    """
    estimator.fit(data.astype(np.float64))
    print(30 * '*', name, 30 * '*')
    print("Model and parameters: ", estimator)
    print("Homogeneity Score         : ", metrics.homogeneity_score(labels, estimator.labels_))
    print("Completeness Score        : ", metrics.completeness_score(labels, estimator.labels_))
    print("V-Measure Score           : ", metrics.v_measure_score(labels, estimator.labels_))
    print("Adjusted Rand Score       : ", metrics.adjusted_rand_score(labels, estimator.labels_))
    print("Adjusted Mutual Info Score: ", metrics.adjusted_mutual_info_score(labels, estimator.labels_))
    print("Calinski Harabasz Score   :   ", metrics.calinski_harabasz_score(data, estimator.labels_))
    print("Silhouette Score          : ", metrics.silhouette_score(data, estimator.labels_))

def read_para(FEATURE_FILE_PATH):
    para = pd.read_excel(FEATURE_FILE_PATH,header=None,dtype='object')
    dic=para.set_index(0).T.to_dict('list')
    for i in dic:
        dic[i]=[x for x in dic[i] if x == x]
    return dic

def plot_learning_curve(model,data,labels,OUTPUT_RESULTS):
    train_sizes, train_scores, test_scores = learning_curve(model, data, labels,
                                                            scoring='adjusted_rand_score', cv=5)
    train_scores_mean = np.mean(train_scores, axis=1)  # To average the training score set by row 
    train_scores_std = np.std(train_scores, axis=1)   #  Calculate the standard deviation of training matrix
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()   # Set the background to gridlines

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std, train_scores_mean + train_scores_std, alpha=0.1,
                     color='r')
    # plt.fill_between(function fills the space of the upper and lower variances of the average model accuracy with colors.。
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std, test_scores_mean + test_scores_std, alpha=0.1,
                     color='g')
    plt.plot(train_sizes, train_scores_mean, 'o-', color='r', label='Training score')
    # Then use plt.plot The () function draws the average of the model accuracy.
    plt.plot(train_sizes, test_scores_mean, 'o-', color='g', label='Cross_validation score')
    plt.legend(loc='best')  # Show legend
    #  plt.show()
    TIMESTAMP = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S").replace("'", "")
    plt.savefig(OUTPUT_RESULTS + "{}.png".format(TIMESTAMP))

def main():
    FEATURE_FILE_PATH = sys.argv[1]
    DATA_FILE_PATH = sys.argv[2]
    OUTPUT_MODEL = sys.argv[3]
    OUTPUT_RESULTS = sys.argv[4]
    df = pd.read_excel(DATA_FILE_PATH)

    data = df.drop('TRUE VALUE', axis=1)
    labels = df['TRUE VALUE']

    # Test unsupervised model
    ms = MeanShift()
    ms_dict =read_para(FEATURE_FILE_PATH)
    output = MSGridsearch(ms, data, labels, ms_dict)

    # The test resylts of meanshift 
    for i in range(len(output)):
        get_marks(output[i], data=data, labels=labels,name="output" + str(i))
    ms_best_model = GridSearchCV(ms, ms_dict, cv=5, scoring='adjusted_rand_score', verbose=1, n_jobs=-1)
    ms_result = ms_best_model.fit(data, labels)
    print(ms_result.best_params_)
    # Save model
    joblib.dump(ms_best_model.best_estimator_, OUTPUT_MODEL+"test.pkl")

    # Save parameters
    TIMESTAMP = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S").replace("'", "")
    result = pd.DataFrame(ms_result.best_params_, index=['value'])
    result.to_csv(OUTPUT_RESULTS + "{}.csv".format(TIMESTAMP), index=None)

    # Draw learning curve
    plot_learning_curve(ms_best_model.best_estimator_,data,labels,OUTPUT_RESULTS)

if __name__ == '__main__':
    main()
