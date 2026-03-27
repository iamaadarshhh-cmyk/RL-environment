class Environment:
    def __init__(self):
        self.state = 0

    def reset(self):
        self.state = 0
        return {"observation": self.state, "reward": 0, "done": False}

    def step(self, action):
        if action == "right":
            self.state += 1
        else:
            self.state -= 1

        reward = 1 if self.state == 5 else -0.1
        done = self.state == 5

        return {"observation": self.state, "reward": reward, "done": done}