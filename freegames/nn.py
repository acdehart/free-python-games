import numpy as np
import nnfs
from nnfs.datasets import spiral_data, vertical_data


class nn:
    class Layer_Dense:

        def __init__(self, n_inputs, n_neurons):
            self.weights = 0.01 * np.random.randn(n_inputs, n_neurons)
            self.biases = np.zeros((1, n_neurons))

        def forward(self, inputs):
            self.inputs = inputs
            self.output = np.dot(inputs, self.weights) + self.biases

        def backward(self, dvalues):
            # Gradients on params
            self.dweights = np.dot(self.inputs.T, dvalues)
            self.dbiases = np.sum(dvalues, axis=0, keepdims=True)
            # Gradient on values
            self.dinputs = np.dot(dvalues, self.weights.T)

    class Activation_ReLU:
        def forward(self, inputs):
            self.inputs = inputs
            self.output = np.maximum(0, inputs)

        def backward(self, dvalues):
            self.dinputs = dvalues.copy()
            self.dinputs[self.inputs <= 0] = 0

    class Activation_Softmax:

        def forward(self, inputs):
            self.inputs = inputs
            exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
            probabilities = exp_values / np.sum(exp_values, axis=1, keepdims=True)
            self.output = probabilities

        def backward(self, dvalues):
            self.dinputs = np.empty_like(dvalues)
            for index, (single_output, single_dvalues) in enumerate(zip(self.output, dvalues)):
                single_output = single_output.reshape(-1, 1)
                jacobian_matrix = np.diagflat(single_output) - np.dot(single_output, single_output.T)
                self.dinputs[index] = np.dot(jacobian_matrix, single_dvalues)

    class Loss:
        def calculate(self, output, y):
            sample_losses = self.forward(output, y)
            data_loss = np.mean(sample_losses)
            return data_loss

    class Loss_CategoricalCrossentropy(Loss):

        def forward(self, y_pred, y_true):
            samples = len(y_pred)
            y_pred_clipped = np.clip(y_pred, 1e-7, 1 - 1e-7)

            if len(y_true.shape) == 1:
                correct_confidences = y_pred_clipped[
                    range(samples),
                    y_true
                ]

            elif len(y_true.shape) == 2:
                correct_confidences = np.sum(
                    y_pred_clipped * y_true,
                    axis=1
                )

            negative_log_likelihoods = -np.log(correct_confidences)
            return negative_log_likelihoods

        def backward(self, dvalues, y_true):
            samples = len(dvalues)
            labels = len(dvalues[0])

            if len(y_true.shape) == 1:
                y_true = np.eye(labels)[y_true]

            self.dinputs = -y_true / dvalues
            self.dinputs = self.dinputs / samples

    class Activation_Softmax_Loss_CategoricalCrossentropy():
        def __init__(self):
            self.activation = nn.Activation_Softmax()
            self.loss = nn.Loss_CategoricalCrossentropy()

        def forward(self, inputs, y_true):
            self.activation.forward(inputs)
            self.output = self.activation.output
            return self.loss.calculate(self.output, y_true)

        def backward(self, dvalues, y_true):
            samples = len(dvalues)

            if len(y_true.shape) == 2:
                y_true = np.argmax(y_true, axis=1)

            self.dinputs = dvalues.copy()
            self.dinputs[range(samples), y_true] -= 1

            self.dinputs = self.dinputs / samples

    # SGD optimizer
    class Optimizer_SGD:
        # Initialize optimizer - set settings,
        # learning rate of 1. is default for this optimizer
        def __init__(self, learning_rate=1., decay=0., momentum=0.):
            self.learning_rate = learning_rate
            self.current_learning_rate = learning_rate
            self.decay = decay
            self.iterations = 0
            self.momentum = momentum

        # Call once before any parameter updates
        def pre_update_params(self):
            if self.decay:
                self.current_learning_rate = self.learning_rate * \
                                             (1. / (1. + self.decay * self.iterations))

        # Update parameters
        def update_params(self, layer):

            # If we use momentum
            if self.momentum:
                # If layer does not contain momentum arrays, create them
                # filled with zeros
                if not hasattr(layer, 'weight_momentums'):
                    layer.weight_momentums = np.zeros_like(layer.weights)
                    # If there is no momentum array for weights
                    # The array doesn't exist for biases yet either.
                    layer.bias_momentums = np.zeros_like(layer.biases)
                # Build weight updates with momentum - take previous
                # updates multiplied by retain factor and update with
                # current gradients
                weight_updates = \
                    self.momentum * layer.weight_momentums - \
                    self.current_learning_rate * layer.dweights
                layer.weight_momentums = weight_updates
                # Build bias updates
                bias_updates = \
                    self.momentum * layer.bias_momentums - \
                    self.current_learning_rate * layer.dbiases
                layer.bias_momentums = bias_updates


            # Vanilla SGD updates (as before momentum update)
            else:
                weight_updates = -self.current_learning_rate * \
                                 layer.dweights
                bias_updates = -self.current_learning_rate * \
                               layer.dbiases
            # Update weights and biases using either
            # vanilla or momentum updates
            layer.weights += weight_updates
            layer.biases += bias_updates

        # Call once after any parameter updates
        def post_update_params(self):
            self.iterations += 1


def main():
    # Create dataset
    X, y = spiral_data(samples=100, classes=3)
    # Create Dense layer with 2 input features and 64 output values
    dense1 = nn.Layer_Dense(2, 64)
    # Create ReLU activation (to be used with Dense layer):
    activation1 = nn.Activation_ReLU()
    # Create second Dense layer with 64 input features (as we take output
    # of previous layer here) and 3 output values (output values)
    dense2 = nn.Layer_Dense(64, 3)
    # Create Softmax classifier's combined loss and activation
    loss_activation = nn.Activation_Softmax_Loss_CategoricalCrossentropy()
    # Create optimizer
    optimizer = nn.Optimizer_SGD(decay=1e-3, momentum=0.9)
    # Train in loop
    for epoch in range(10001):
        # Perform a forward pass of our training data through this layer
        dense1.forward(X)
        # Perform a forward pass through activation function
        # takes the output of first dense layer here
        activation1.forward(dense1.output)
        # Perform a forward pass through second Dense layer
        # takes outputs of activation function of first layer as inputs
        dense2.forward(activation1.output)
        # Perform a forward pass through the activation/loss function
        # takes the output of second dense layer here and returns loss
        loss = loss_activation.forward(dense2.output, y)
        # Calculate accuracy from output of activation2 and targets
        # calculate values along first axis
        predictions = np.argmax(loss_activation.output, axis=1)
        # if len(y.shape) == 2:
        #     y = np.argmax(y, axis=1)
        accuracy = np.mean(predictions == y)
        if not epoch % 100:
            print(f'epoch: {epoch}, ' +
                  f'acc: {accuracy:.3f}, ' +
                  f'loss: {loss:.3f}, ' +
                  f'lr: {optimizer.current_learning_rate}')

        # Backward pass
        loss_activation.backward(loss_activation.output, y)
        dense2.backward(loss_activation.dinputs)
        activation1.backward(dense2.dinputs)
        dense1.backward(activation1.dinputs)
        # Update weights and biases
        optimizer.pre_update_params()
        optimizer.update_params(dense1)
        optimizer.update_params(dense2)
        optimizer.post_update_params()


def check_combo_method():
    softmax_outputs = np.array([[0.7, 0.1, 0.2],
                                [0.1, 0.5, 0.4],
                                [0.02, 0.9, 0.08]])
    class_targets = np.array([0, 1, 1])

    softmax_loss = nn.Activation_Softmax_Loss_CategoricalCrossentropy()
    softmax_loss.backward(softmax_outputs, class_targets)
    dvalues1 = softmax_loss.dinputs

    activation = nn.Activation_Softmax()
    activation.output = softmax_outputs
    loss = nn.Loss_CategoricalCrossentropy()
    loss.backward(softmax_outputs, class_targets)
    activation.backward(loss.dinputs)
    dvalues2 = activation.dinputs

    print('Gradients: combined loss and activation:')
    print(dvalues1)
    print('Gradients: separate loss and activation:')
    print(dvalues2)


if __name__ == '__main__':
    main()