import os
import sys
import time
from typing import List, Tuple

import numpy as np
from tqdm import tqdm

sys.path.append("../../")
from utils import AverageMeter, dotdict  # noqa: E402
from NeuralNet import NeuralNet        # noqa: E402

import torch
import torch.optim as optim

# Import the 3‑D network – adjust the path to your project layout
from .LaniakeaNNet import LaniakeaNNet as onnet  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────────
# Hyper‑parameters (tweak as desired)
# ──────────────────────────────────────────────────────────────────────────────
args = dotdict(
    {
        "lr": 0.001,
        "dropout": 0.3,
<<<<<<< Updated upstream
        "epochs": 10,
        "batch_size": 64,
=======
        "epochs": 16,
        "batch_size": 512,
>>>>>>> Stashed changes
        "cuda": torch.cuda.is_available(),
        "num_channels": 512,
    }
)


class NNetWrapper(NeuralNet):
    """Thin convenience wrapper around :class:`Game3DNNet`.

    * Handles batching, loss functions, checkpointing.
    * Converts numpy boards ⇄ torch tensors.
    * Expects *volumetric* game boards with shape ``(x, y, z)``.
    """

    def __init__(self, game):
        super().__init__(game)

        # Instantiate the underlying 3‑D network
        self.nnet = onnet(game, args)

        # Board geometry and action size
        self.board_x, self.board_y, self.board_z = game.getBoardSize()
        self.action_size = game.getActionSize()

        if args.cuda:
            self.nnet.cuda()

    # ─────────────────────────────────────────────────────────────────── train ──
    def train(self, examples: List[Tuple[np.ndarray, np.ndarray, float]]):
        """`examples` is a list of *(board, pi, v)* tuples."""
        optimizer = optim.Adam(self.nnet.parameters(), lr=args.lr)

        for epoch in range(args.epochs):
            print(f"EPOCH ::: {epoch + 1}")
            self.nnet.train()
            pi_losses, v_losses = AverageMeter(), AverageMeter()

            batch_count = len(examples) // args.batch_size
            for _ in tqdm(range(batch_count), desc="Training Net"):
                ids = np.random.randint(len(examples), size=args.batch_size)
                boards, pis, vs = zip(*[examples[i] for i in ids])

                # -------- convert to torch tensors ---------------------------
                boards = torch.FloatTensor(np.array(boards).astype(np.float32))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float32))


                # Ensure 4‑D shape (B, x, y, z) – the net will unsqueeze chan dim
                boards_t = boards.reshape(-1, self.board_x, self.board_y, self.board_z)


                if args.cuda:
                    boards_t, pis_t, vs_t = boards_t.contiguous().cuda(), target_pis.contiguous().cuda(), target_vs.contiguous().cuda()

                # ---------- forward / backward ------------------------------
                out_pi, out_v = self.nnet(boards_t)
                l_pi = self.loss_pi(pis_t, out_pi)
                l_v  = self.loss_v(vs_t, out_v)
                loss = l_pi + l_v

                pi_losses.update(l_pi.item(), boards_t.size(0))
                v_losses.update(l_v.item(), boards_t.size(0))

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            print(f"pi_loss: {pi_losses.avg:.4f} | v_loss: {v_losses.avg:.4f}\n")

    # ───────────────────────────────────────────────────────────────── predict ──
    def predict(self, board: np.ndarray):
        """Predict *(policy, value)* for a single board.

        Parameters
        ----------
        board : np.ndarray
            Shape ``(x, y, z)``.
        """
        board_t = torch.tensor(board, dtype=torch.float32).view(
            1, self.board_x, self.board_y, self.board_z
        )  # channel dim will be added in net

        if args.cuda:
            board_t = board_t.cuda()

        self.nnet.eval()
        with torch.no_grad():
            pi, v = self.nnet(board_t)

        return torch.exp(pi)[0].cpu().numpy(), v[0].cpu().numpy()

    # ────────────────────────────────────────────────────── loss definitions ──
    @staticmethod
    def loss_pi(targets: torch.Tensor, outputs: torch.Tensor) -> torch.Tensor:
        return -torch.sum(targets * outputs) / targets.size(0)

    @staticmethod
    def loss_v(targets: torch.Tensor, outputs: torch.Tensor) -> torch.Tensor:
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size(0)

    # ───────────────────────────────────────────────────────── checkpointing ──
    def save_checkpoint(self, folder: str = "checkpoint", filename: str = "checkpoint.pth.tar"):
        os.makedirs(folder, exist_ok=True)
        torch.save({"state_dict": self.nnet.state_dict()}, os.path.join(folder, filename))

    def load_checkpoint(self, folder: str = "checkpoint", filename: str = "checkpoint.pth.tar"):
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No model in path {path}")
        map_loc = None if args.cuda else "cpu"
        chkpt = torch.load(path, map_location=map_loc)
        self.nnet.load_state_dict(chkpt["state_dict"])