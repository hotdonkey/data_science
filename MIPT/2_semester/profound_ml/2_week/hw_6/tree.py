import numpy as np
from sklearn.base import BaseEstimator


def entropy(y):
    """
    Computes entropy of the provided distribution. Use log(value + eps) for numerical stability

    Parameters
    ----------
    y : np.array of type float with shape (n_objects, n_classes)
        One-hot representation of class labels for corresponding subset

    Returns
    -------
    float
        Entropy of the provided subset
    """
    EPS = 0.0005

    # YOUR CODE HERE
    if len(y) == 0:
        return 0

    _, probs = np.unique(y, return_counts=True)
    probs = probs/len(y)
    entropy = -np.sum(probs*np.log2(probs+EPS))

    return entropy


def gini(y):
    """
    Computes the Gini impurity of the provided distribution

    Parameters
    ----------
    y : np.array of type float with shape (n_objects, n_classes)
        One-hot representation of class labels for corresponding subset

    Returns
    -------
    float
        Gini impurity of the provided subset
    """

    # YOUR CODE HERE
    if len(y) <= 1:
        return 0

    _, probs = np.unique(y, return_counts=True)
    probs = probs/len(y)
    gini = 1 - np.sum(probs**2)

    return gini


def variance(y):
    """
    Computes the variance the provided target values subset

    Parameters
    ----------
    y : np.array of type float with shape (n_objects, 1)
        Target values vector

    Returns
    -------
    float
        Variance of the provided target vector
    """

    # YOUR CODE HERE

    return np.var(y)


def mad_median(y):
    """
    Computes the mean absolute deviation from the median in the
    provided target values subset

    Parameters
    ----------
    y : np.array of type float with shape (n_objects, 1)
        Target values vector

    Returns
    -------
    float
        Mean absolute deviation from the median in the provided vector
    """

    # YOUR CODE HERE

    return np.median(y)


def one_hot_encode(n_classes, y):
    y_one_hot = np.zeros((len(y), n_classes), dtype=float)
    y_one_hot[np.arange(len(y)), y.astype(int)[:, 0]] = 1.
    return y_one_hot


def one_hot_decode(y_one_hot):
    return y_one_hot.argmax(axis=1)[:, None]


class Node:
    """
    This class is provided "as is" and it is not mandatory to it use in your code.
    """

    def __init__(self, feature_index, threshold, proba=0):
        self.feature_index = feature_index
        self.value = threshold
        self.proba = proba
        self.left_child = None
        self.right_child = None


class DecisionTree(BaseEstimator):
    all_criterions = {
        'gini': (gini, True),  # (criterion, classification flag)
        'entropy': (entropy, True),
        'variance': (variance, False),
        'mad_median': (mad_median, False)
    }

    def __init__(self, n_classes=None, max_depth=np.inf, min_samples_split=2,
                 criterion_name='gini', debug=False):

        assert criterion_name in self.all_criterions.keys(
        ), 'Criterion name must be on of the following: {}'.format(self.all_criterions.keys())

        self.n_classes = n_classes
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion_name = criterion_name

        self.depth = 0
        self.root = None  # Use the Node class to initialize it later
        self.debug = debug

    def make_split(self, feature_index, threshold, X_subset, y_subset):
        """
        Makes split of the provided data subset and target values using provided feature and threshold

        Parameters
        ----------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels for corresponding subset

        Returns
        -------
        (X_left, y_left) : tuple of np.arrays of same type as input X_subset and y_subset
            Part of the providev subset where selected feature x^j < threshold
        (X_right, y_right) : tuple of np.arrays of same type as input X_subset and y_subset
            Part of the providev subset where selected feature x^j >= threshold
        """

        # YOUR CODE HERE
        left_mask = X_subset[:, feature_index] < threshold
        right_mask = X_subset[:, feature_index] >= threshold

        # Разделяем данные с использованием масок
        X_left = X_subset[left_mask]
        y_left = y_subset[left_mask]

        X_right = X_subset[right_mask]
        y_right = y_subset[right_mask]

        return (X_left, y_left), (X_right, y_right)

    def make_split_only_y(self, feature_index, threshold, X_subset, y_subset):
        """
        Split only target values into two subsets with specified feature and threshold

        Parameters
        ----------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels for corresponding subset

        Returns
        -------
        y_left : np.array of type float with shape (n_objects_left, n_classes) in classification 
                   (n_objects, 1) in regression 
            Part of the provided subset where selected feature x^j < threshold

        y_right : np.array of type float with shape (n_objects_right, n_classes) in classification 
                   (n_objects, 1) in regression 
            Part of the provided subset where selected feature x^j >= threshold
        """

        # YOUR CODE HERE
        left_mask = X_subset[:, feature_index] < threshold
        right_mask = X_subset[:, feature_index] >= threshold

        # Разделяем данные с использованием масок

        y_left = y_subset[left_mask]

        y_right = y_subset[right_mask]

        return y_left, y_right

    def choose_best_split(self, X_subset, y_subset):
        """
        Greedily select the best feature and best threshold w.r.t. selected criterion

        Parameters
        ----------
        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels or target values for corresponding subset

        Returns
        -------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        """
        # YOUR CODE HERE
        n_samples, n_features = X_subset.shape
        best_gain = -np.inf
        best_feature = None
        best_threshold = None

        # Текущее значение критерия (до разделения)
        current_criterion_value = self.criterion(y_subset)

        for feature_idx in range(n_features):
            feature_values = X_subset[:, feature_idx]
            thresholds = np.unique(feature_values)

            for threshold in thresholds:
                # Разделяем данные
                left_mask = X_subset[:, feature_idx] <= threshold
                right_mask = X_subset[:, feature_idx] > threshold

                # Проверяем, что разделение не пустое
                if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
                    continue

                # Вычисляем критерий для левого и правого подмножеств
                y_left = y_subset[left_mask]
                y_right = y_subset[right_mask]

                criterion_left = self.criterion(y_left)
                criterion_right = self.criterion(y_right)

                # Вычисляем взвешенное значение критерия после разделения
                n_left = len(y_left)
                n_right = len(y_right)
                weighted_criterion = (
                    n_left / n_samples) * criterion_left + (n_right / n_samples) * criterion_right

                # Вычисляем информационный выигрыш
                gain = current_criterion_value - weighted_criterion

                # Если текущее разделение лучше, обновляем лучшие параметры
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_idx
                    best_threshold = threshold

        return best_feature, best_threshold

    def make_tree(self, X_subset, y_subset):
        """
        Recursively builds the tree

        Parameters
        ----------
        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels or target values for corresponding subset

        Returns
        -------
        root_node : Node class instance
            Node of the root of the fitted tree
        """

        # YOUR CODE HERE

        n_samples, n_features = X_subset.shape

        # Проверять условия прекращения
        if (self.depth >= self.max_depth) or (n_samples < self.min_samples_split) or np.unique(y_subset, return_counts=True)[1].size == 1:
            # Если одно из условий выполнено, возвращаем узел с вероятностями
            proba = np.sum(y_subset, axis=0) / n_samples
            return Node(None, None, proba)

        best_feature, best_threshold = self.choose_best_split(
            X_subset, y_subset)

        # Если нет лучшего разделения
        if best_feature is None or best_threshold is None:
            proba = np.sum(y_subset, axis=0) / n_samples
            return Node(None, None, proba)

        # Создаём узел с найденными параметрами
        node = Node(best_feature, best_threshold)

        # Разделяем данные
        (X_left, y_left), (X_right, y_right) = self.make_split(
            best_feature, best_threshold, X_subset, y_subset)
        
        # Увеличиваем глубину
        self.depth += 1

        # Рекурсивно строим левое и правое поддеревья
        node.left_child = self.make_tree(X_left, y_left, depth + 1)
        node.right_child = self.make_tree(X_right, y_right, depth + 1)

        return node

    def fit(self, X, y):
        """
        Fit the model from scratch using the provided data

        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data to train on

        y : np.array of type int with shape (n_objects, 1) in classification 
                   of type float with shape (n_objects, 1) in regression 
            Column vector of class labels in classification or target values in regression

        """
        assert len(y.shape) == 2 and len(y) == len(X), 'Wrong y shape'
        self.criterion, self.classification = self.all_criterions[self.criterion_name]
        if self.classification:
            if self.n_classes is None:
                self.n_classes = len(np.unique(y))
            y = one_hot_encode(self.n_classes, y)

        self.root = self.make_tree(X, y)

    def predict(self, X):
        """
        Predict the target value or class label  the model from scratch using the provided data

        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data the predictions should be provided for

        Returns
        -------
        y_predicted : np.array of type int with shape (n_objects, 1) in classification 
                   (n_objects, 1) in regression 
            Column vector of class labels in classification or target values in regression

        """

        # YOUR CODE HERE
        
        y_predicted = np.zeros((X.shape[0], 1))

        for i in range(X.shape[0]):
            node = self.root
            while node.left_child is not None:  # Пока узел не листовой
                if X[i, node.feature_index] < node.value:
                    node = node.left_child
                else:
                    node = node.right_child
            y_predicted[i] = node.proba.argmax()

        return y_predicted

    def predict_proba(self, X):
        """
        Only for classification
        Predict the class probabilities using the provided data

        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data the predictions should be provided for

        Returns
        -------
        y_predicted_probs : np.array of type float with shape (n_objects, n_classes)
            Probabilities of each class for the provided objects

        """
        assert self.classification, 'Available only for classification problem'

        # YOUR CODE HERE
        y_predicted_probs = np.zeros((X.shape[0], self.n_classes))

        for i in range(X.shape[0]):
            node = self.root
            while node.left_child is not None:  # Пока узел не листовой
                if X[i, node.feature_index] < node.value:
                    node = node.left_child
                else:
                    node = node.right_child
            y_predicted_probs[i] = node.proba

        return y_predicted_probs
