import torch
import torch.nn as nn
import torch.nn.functional as F


class LaniakeaNNet(nn.Module):
    def __init__(self, game, args):
        super().__init__()

        self.board_x, self.board_y, self.board_z = game.getBoardSize()  # x=8, y=6, z=17
        self.action_size = game.getActionSize()
        self.args = args

        c = args.num_channels  # z. B. 32

        # ──────────────── convolutional trunk ────────────────
        self.conv1 = nn.Conv2d(self.board_z, c, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(c, c, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(c, c, kernel_size=3, stride=1, padding=1)
        self.conv4 = nn.Conv2d(c, c, kernel_size=3, stride=1, padding=1)
        self.conv5 = nn.Conv2d(c, c, kernel_size=3, stride=1, padding=1)
        self.conv6 = nn.Conv2d(c, c, kernel_size=3, stride=1, padding=1)

        self.bn1 = nn.BatchNorm2d(c)
        self.bn2 = nn.BatchNorm2d(c)
        self.bn3 = nn.BatchNorm2d(c)
        self.bn4 = nn.BatchNorm2d(c)
        self.bn5 = nn.BatchNorm2d(c)
        self.bn6 = nn.BatchNorm2d(c)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # ──────────────── dynamische Flatten-Berechnung ────────────────
        with torch.no_grad():
            dummy = torch.zeros(1, self.board_z, self.board_x, self.board_y)  # (B, C, H, W)
            x = self._forward_conv(dummy)
            self.linear_input_size = x.reshape(1, -1).size(1)

        # ──────────────── fully connected head ────────────────
        self.fc1 = nn.Linear(self.linear_input_size, 4096)
        self.fc_bn1 = nn.BatchNorm1d(4096)

        self.fc2 = nn.Linear(4096, 2048)
        self.fc_bn2 = nn.BatchNorm1d(2048)

        self.fc3 = nn.Linear(2048, 1024)
        self.fc_bn3 = nn.BatchNorm1d(1024)

        self.fc4 = nn.Linear(1024, 512)
        self.fc_bn4 = nn.BatchNorm1d(512)

        self.fc_pi = nn.Linear(512, self.action_size)
        self.fc_v = nn.Linear(512, 1)

    def _forward_conv(self, s):
        s = F.relu(self.bn1(self.conv1(s)))
        s = F.relu(self.bn2(self.conv2(s)))
        s = F.relu(self.bn3(self.conv3(s)))
        s = F.relu(self.bn4(self.conv4(s)))
        s = F.relu(self.bn5(self.conv5(s)))
        s = F.relu(self.bn6(self.conv6(s)))
        s = self.pool(s)
        return s

    def forward(self, s):
        # Erwartet (B, 8, 6, 17) oder (B, H, W, C)
        if s.dim() == 4 and s.shape[-1] == self.board_z:
            s = s.permute(0, 3, 1, 2)  # → (B, C, H, W)
        elif s.dim() != 4 or s.shape[1] != self.board_z:
            raise ValueError(f"Expected (B, 8, 6, 17) or (B, 17, 8, 6), got {s.shape}")
        

        s = self._forward_conv(s)
        s = s.reshape(s.size(0), -1)  # statt .view() → robust
        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.args.dropout, training=self.training)
        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.args.dropout, training=self.training)
        s = F.dropout(F.relu(self.fc_bn3(self.fc3(s))), p=self.args.dropout, training=self.training)
        s = F.dropout(F.relu(self.fc_bn4(self.fc4(s))), p=self.args.dropout, training=self.training)

        pi = self.fc_pi(s)
        v = self.fc_v(s)

        return F.log_softmax(pi, dim=1), torch.tanh(v)
