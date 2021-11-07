import torch
from torch.autograd import Variable
import numpy as np
import matplotlib.pyplot as plt
class linearRegression(torch.nn.Module):
    def __init__(self, inputSize, outputSize):
        super(linearRegression, self).__init__()
        self.linear = torch.nn.Linear(inputSize, outputSize)

    def forward(self, x):
        out = self.linear(x)
        return out

def main():
    # create dummy data for training

    x_values = []
    y_values = []
    fi = open("user_1_video_3.txt",'r')
    prev = -1
    for line in fi.readlines():
        data = line.split(",")
        x_values.append(float(data[0]))
        data[1] = float(data[1])
        print(prev)
        if prev!= -1 and prev > data[1]:
            y_values.append(data[1]+360)
            prev = data[1] + 360
        else:
            y_values.append(data[1])
        if float(data[0]) > 200:
            break
    x_train = np.array(x_values, dtype=np.float32)
    x_train = x_train.reshape(-1, 1)

    y_train = np.array(y_values, dtype=np.float32)
    y_train = y_train.reshape(-1, 1)

    print(x_values)
    print(y_values)


    inputDim = 1        # takes variable 'x' 
    outputDim = 1       # takes variable 'y'
    learningRate = .1
    epochs = 100

    model = linearRegression(inputDim, outputDim)
    ##### For GPU #######
    if torch.cuda.is_available():
        model.cuda()

    criterion = torch.nn.MSELoss() 
    optimizer = torch.optim.Adam(model.parameters(), lr=learningRate)

    for epoch in range(epochs):
        # Converting inputs and labels to Variable
        if torch.cuda.is_available():
            inputs = Variable(torch.from_numpy(x_train).cuda())
            labels = Variable(torch.from_numpy(y_train).cuda())
        else:
            inputs = Variable(torch.from_numpy(x_train))
            labels = Variable(torch.from_numpy(y_train))

        # Clear gradient buffers because we don't want any gradient from previous epoch to carry forward, dont want to cummulate gradients
        optimizer.zero_grad()

        # get output from the model, given the inputs
        outputs = model(inputs)

        # get loss for the predicted output
        loss = criterion(outputs, labels)
        #print(loss)
        # get gradients w.r.t to parameters
        loss.backward()

        # update parameters
        optimizer.step()

        print('epoch {}, loss {}'.format(epoch, loss.item()))

    with torch.no_grad(): # we don't need gradients in the testing phase
        if torch.cuda.is_available():
            predicted = model(Variable(torch.from_numpy(x_train).cuda())).cpu().data.numpy()
        else:
            predicted = model(Variable(torch.from_numpy(x_train))).data.numpy()
        print(predicted)

    plt.clf()
    plt.plot(x_train, y_train, 'go', label='True data', alpha=0.5)
    plt.plot(x_train, predicted, '--', label='Predictions', alpha=0.5)
    plt.legend(loc='best')
    plt.show()




if __name__ == "__main__":
    main()