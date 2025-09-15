class HermiteCurve:
    def __init__(self):
        self.t = 0.0
        self.n = 0
        self.step = 0.0
        self.poss = [None]
        self.dirs = [None]
        self.next_pos = np.empty(3)
        self.active = False
        self.path3D = Node()
        self.hermite_matrix = np.array([[ 2,-2, 1, 1],
                                        [-3, 3,-2,-1],
                                        [ 0, 0, 1, 0],
                                        [ 1, 0, 0, 0]])

    def hermite_point(self, pos1, dir1, pos2, dir2):
        pos_matrix = np.vstack([pos1, pos2, dir1, dir2])

        t_arr = np.array([self.t**3, self.t**2, self.t, 1], dtype=np.float32)

        return t_arr @ self.hermite_matrix @ pos_matrix
    
    def start(self, pos, dir):
        if len(self.poss) > 1:
            self.active = True
            difference = np.linalg.norm(self.poss[1] - pos)
            factor = np.log(difference)
            if difference > 3: 
                self.step = 1 / (40 * factor)
                self.dirs[0] = dir * 5 * factor
            else:
                self.step = 1/20
                self.dirs[0] = dir
            self.poss[0] = pos
            self.t += self.step
            self.next_pos = self.hermite_point(self.poss[0], self.dirs[0], self.poss[1], self.dirs[1])

    def end(self):
        self.active = False
        self.t = 0.0
        self.n = 0
        
        global phi, theta
        final_dir = self.dirs[-1]
        phi = np.arcsin(final_dir[1]/np.linalg.norm(final_dir))
        if final_dir[2] == 0:
            theta = -(np.pi/2)*(final_dir[0]/abs(final_dir[0]))
        else:
            theta = np.arctan(final_dir[0]/final_dir[2])
            if final_dir[2] > 0:
                theta += np.pi

    def next_curve_position(self):
        self.t += self.step

        if self.t >= 1:
            self.t -= 1
            self.n += 1
            if self.n == len(self.poss)-1:
                self.end()
                return self.poss[-1]
            else:
                difference = np.linalg.norm(self.poss[self.n+1] - self.poss[self.n])
                if difference > 2:
                    self.step = 1 / (40 * np.log(difference))
                else:
                    self.step = 1/20
                
        return self.hermite_point(self.poss[self.n], self.dirs[self.n], self.poss[self.n+1], self.dirs[self.n+1])

    def update_pos(self):
        newPos = np.array(self.next_pos)
        self.next_pos = self.next_curve_position()

        newDir = self.next_pos - newPos
        newDir = newDir / np.linalg.norm(newDir)

        return newPos, newDir
    
    def new_point(self, pos, dir): #añadir punto a la lista y gpu shape del caminio
        if len(self.poss) == 1:
            self.dirs += [np.array(dir) * 5]
        else:
            norm = np.linalg.norm(pos - self.poss[-1])
            if norm > 3:
                self.dirs += [np.array(dir) * 5 * np.log(norm)]
            elif norm > 0.5:
                self.dirs[-1] = self.dirs[-1]/np.linalg.norm(self.dirs[-1]) 
                self.dirs += [np.array(dir)]
            else:
                return
        self.poss += [np.array(pos)]
        self.path3D.children.append(create_checkpoint(pos, dir))