import torch
import numpy as np
import time


class MacroPlacer:
    def __init__(self):
        self.gap = 0.05

    def place(self, benchmark, plc=None) -> torch.Tensor:
        start_ts = time.time()
        W, H = benchmark.canvas_width, benchmark.canvas_height
        sizes = benchmark.macro_sizes.float()
        pos = benchmark.macro_positions.clone().float()
        movable_mask = benchmark.get_movable_mask() & benchmark.get_hard_macro_mask()
        movable_idx = torch.where(movable_mask)[0].tolist()

        movable_idx.sort(key=lambda i: sizes[i, 1].item(), reverse=True)

        # Track which macros land on which shelf for horizontal spread
        shelves = []       # {'y', 'h', 'curr_x', 'index', 'members': [idx,...]}
        final_pos = pos.clone()
        current_y = 0.0

        for idx in movable_idx:
            mw = sizes[idx, 0].item() + self.gap
            mh = sizes[idx, 1].item() + self.gap
            placed = False

            for shelf in shelves:
                if mw <= (W - shelf['curr_x']) and mh <= shelf['h']:
                    si = shelf['index']
                    if si % 2 == 0:
                        final_pos[idx, 0] = shelf['curr_x'] + mw / 2
                    else:
                        final_pos[idx, 0] = W - shelf['curr_x'] - mw / 2
                    final_pos[idx, 1] = shelf['y'] + mh / 2
                    shelf['curr_x'] += mw
                    shelf['members'].append(idx)
                    placed = True
                    break

            if not placed:
                if current_y + mh <= H:
                    si = len(shelves)
                    if si % 2 == 0:
                        final_pos[idx, 0] = mw / 2
                    else:
                        final_pos[idx, 0] = W - mw / 2
                    final_pos[idx, 1] = current_y + mh / 2
                    shelves.append({
                        'y': current_y, 'h': mh,
                        'curr_x': mw, 'index': si,
                        'members': [idx]
                    })
                    current_y += mh
                else:
                    final_pos[idx, 0] = W - mw / 2
                    final_pos[idx, 1] = H - mh / 2

        # ----------------------------------------------------------------
        # VERTICAL SPREAD
        # Scale y positions so packed region fills full canvas height.
        # ----------------------------------------------------------------
        if 0 < current_y < H:
            scale = H / current_y
            for idx in movable_idx:
                mh = sizes[idx, 1].item() + self.gap
                new_y = final_pos[idx, 1].item() * scale
                new_y = max(mh / 2, min(H - mh / 2, new_y))
                final_pos[idx, 1] = new_y

        # ----------------------------------------------------------------
        # HORIZONTAL SPREAD (per shelf)
        # Each shelf uses only `shelf['curr_x']` of W. Scale each macro's
        # x position so the shelf fills the full canvas width.
        # Boustrophedon direction is preserved — even shelves scale from
        # left, odd shelves scale from right.
        # ----------------------------------------------------------------
        for shelf in shelves:
            members = shelf['members']
            used_x = shelf['curr_x']
            if used_x <= 0 or used_x >= W or len(members) < 2:
                continue
            scale = W / used_x
            si = shelf['index']
            for idx in members:
                mw = sizes[idx, 0].item() + self.gap
                cx = final_pos[idx, 0].item()
                if si % 2 == 0:
                    # left-to-right shelf: scale from left edge
                    new_x = cx * scale
                else:
                    # right-to-left shelf: scale from right edge
                    dist_from_right = W - cx
                    new_x = W - dist_from_right * scale
                new_x = max(mw / 2, min(W - mw / 2, new_x))
                final_pos[idx, 0] = new_x

        return final_pos