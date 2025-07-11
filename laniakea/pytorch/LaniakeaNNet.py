import torch
import torch.nn as nn
import torch.nn.functional as F


class LaniakeaNNet(nn.Module):
    def __init__(self, game, args):
        super().__init__()

        self.board_x, self.board_y, self.board_z = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        c = args.num_channels  # usually 32

        # ──────────────────────────────────── convolutional trunk ─
        self.conv1 = nn.Conv3d(1, c, 3, stride=1, padding=1)
        self.conv2 = nn.Conv3d(c, c, 3, stride=1, padding=1)
        self.conv3 = nn.Conv3d(c, c, 3, stride=1, padding=0)
        self.conv4 = nn.Conv3d(c, c, 3, stride=1, padding=0)

        self.bn1 = nn.BatchNorm3d(c)
        self.bn2 = nn.BatchNorm3d(c)
        self.bn3 = nn.BatchNorm3d(c)
        self.bn4 = nn.BatchNorm3d(c)

        # Pooling nach convs zum Speicher sparen
        self.pool = nn.MaxPool3d(kernel_size=2, stride=2)

        # Dynamische Berechnung der Flatten-Dimension
        with torch.no_grad():
            dummy = torch.zeros(1, 1, self.board_x, self.board_y, self.board_z)
            x = self._forward_conv(dummy)
            self.linear_input_size = x.view(1, -1).size(1)

        # ──────────────────────────────────── fully connected ─
        self.fc1 = nn.Linear(self.linear_input_size, 128)
        self.fc_bn1 = nn.BatchNorm1d(128)

        self.fc2 = nn.Linear(128, 64)
        self.fc_bn2 = nn.BatchNorm1d(64)

        self.fc_pi = nn.Linear(64, self.action_size)
        self.fc_v = nn.Linear(64, 1)

    def _forward_conv(self, s):
        s = F.relu(self.bn1(self.conv1(s)))
        s = F.relu(self.bn2(self.conv2(s)))
        s = F.relu(self.bn3(self.conv3(s)))
        s = F.relu(self.bn4(self.conv4(s)))
        s = self.pool(s)
        return s

    def forward(self, s):
        if s.dim() == 4:
            s = s.unsqueeze(1)  # (B, 1, x, y, z)
        elif s.dim() != 5:
            raise ValueError(f"Expected 4D or 5D tensor, got {s.shape}")

        s = self._forward_conv(s)
        s = s.view(s.size(0), -1)

        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.args.dropout, training=self.training)
        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.args.dropout, training=self.training)

        pi = self.fc_pi(s)
        v = self.fc_v(s)

        return F.log_softmax(pi, dim=1), torch.tanh(v)
