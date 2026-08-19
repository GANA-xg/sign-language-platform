class MovementTracker:

    def __init__(self):

        self.positions = []

        self.current_action = None

        self.display_frames = 0

        self.cooldown = 0

    def update(self, x, y):

        # -----------------------------
        # Show previous detected action
        # -----------------------------
        if self.display_frames > 0:
            self.display_frames -= 1
            return self.current_action

        # -----------------------------
        # Cooldown
        # -----------------------------
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # -----------------------------
        # Store palm center
        # -----------------------------
        self.positions.append((x, y))

        if len(self.positions) > 10:
            self.positions.pop(0)

        if len(self.positions) < 10:
            return None

        # -----------------------------
        # Average first 3 points
        # -----------------------------
        first = self.positions[:3]

        start_x = sum(p[0] for p in first) / 3
        start_y = sum(p[1] for p in first) / 3

        # -----------------------------
        # Average last 3 points
        # -----------------------------
        last = self.positions[-3:]

        end_x = sum(p[0] for p in last) / 3
        end_y = sum(p[1] for p in last) / 3

        dx = end_x - start_x
        dy = end_y - start_y

        print(f"dx={dx:.3f}, dy={dy:.3f}")


        # -----------------------------
        # Ignore tiny movement
        # -----------------------------
        if abs(dx) < 0.03 and abs(dy) < 0.03:
            return None

        # -----------------------------
        # Horizontal movement
        # -----------------------------
        if abs(dx) > abs(dy):

            if dx > 0.03:
                self.current_action = "HELLO"

            elif dx < -0.03:
                self.current_action = "BYE"

            else:
                return None

        # -----------------------------
        # Vertical movement
        # -----------------------------
        else:

            if dy > 0.03:
                self.current_action = "YES"

            else:
                return None

        # -----------------------------
        # Reset tracker
        # -----------------------------
        self.positions.clear()

        # Show action for ~1.5 seconds
        self.display_frames = 45

        # Ignore new gesture for ~0.8 second
        self.cooldown = 25

        return self.current_action