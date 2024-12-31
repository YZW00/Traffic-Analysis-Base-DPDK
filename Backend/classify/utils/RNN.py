from torch import nn

class RNN(nn.Module):
    def __init__(self, max_payload_length, num_classes):
        super(RNN, self).__init__()
        self.embedding = nn.Embedding(max_payload_length, 256)
        self.rnn = nn.LSTM(input_size = 256, hidden_size = 256, num_layers = 1, bidirectional = True)#, dropout = 0.25,
        self.classifier = nn.Sequential(
            nn.Linear(256*2*1, num_classes),
            nn.Softmax(dim = -1)
        )

    def forward(self, X):
        X = self.embedding(X.transpose(0,1))
        _, (h_n, c_n) = self.rnn(X)
        h_n = h_n.transpose(0, 1).reshape(X.shape[1], -1)
        return self.classifier(h_n)