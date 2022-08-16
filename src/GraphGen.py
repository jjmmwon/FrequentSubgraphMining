import glob
from ipaddress import NetmaskValueError
from operator import ne
import os
import numpy as np
import pandas as pd
import snap
import argparse

class GraphGenerator:
    def __init__(self, data_title, k=5):
        self.data_title = data_title
        self.path = f'/home/myeongwon/mw_dir/FSM/result/{data_title}/'
        self.k = k
        self.graph = None
        self.current_file = None
        self.dist_mtrx = None
        self.CAM = None

    def distant_matrix(self, data): # generate distant matrix 
        M = data.shape[0]
        self.dist_mtrx = np.empty((M,M))

        for i in range(M):
            for j in range(i, M):
                if i==j:
                    self.dist_mtrx[i,j] =0
                    continue
                x1, y1, x2, y2 = data[i,0], data[i,1], data[j,0], data[j,1]
                self.dist_mtrx[i,j] = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
                self.dist_mtrx[j,i] = self.dist_mtrx[i,j]
        

    def make_graph(self):   # make graph with k neighbors per each point
        self.graph = snap.TUNGraph.New()
        self.CAM = ""
        for i in range(self.dist_mtrx.shape[0]):
            self.graph.AddNode(i)
            self.CAM += "0"*i + "$"
        idx_list = [i for i,c in enumerate(self.CAM) if c == "$"]
        

        idx = 0
        for row in self.dist_mtrx:
            nearest_neighbor = row.argsort()
            for i in range(1,self.k+1):
                self.graph.AddEdge(int(idx), int(nearest_neighbor[i]))
                if int(idx) < int(nearest_neighbor[i]):
                    self.CAM = self.CAM[:idx_list[int(nearest_neighbor[i])-1]+int(idx)+1] + "1" + self.CAM[idx_list[int(nearest_neighbor[i])-1]+int(idx)+2:]
                else:
                    self.CAM = self.CAM[:idx_list[int(idx)-1]+int(nearest_neighbor[i])+1] + "1" + self.CAM[idx_list[int(idx)-1]+int(nearest_neighbor[i])+2:]
            idx += 1
        

    def save_graph(self):   # save graph file using snap lib
        dir_path = self.path + 'graph'
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        graph_title = self.current_file[len(self.path):-4]

        # FOut = snap.TFOut(f'{dir_path}/{graph_title}.graph')
        # self.graph.Save(FOut)
        # FOut.Flush()

        CAM_file = open(f'{dir_path}/{graph_title}.txt', "w")
        CAM_file.write(self.CAM)
        CAM_file.close()


    def save_graphViz(self):
        dir_path = self.path + 'graphViz'
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        graph_title = self.current_file[len(self.path):-4]

        labels = {}
        for NI in self.graph.Nodes():
            labels[NI.GetId()] = str(NI.GetId())
        self.graph.DrawGViz(snap.gvlDot, f'{dir_path}/{graph_title}.png', " ", labels)



    def run(self):
        path = self.path + '*.npy'
        npy_files = glob.glob(path)
        for npy_file in npy_files:
            self.current_file = npy_file
            data = np.load(self.current_file)

            self.distant_matrix(data)
            self.make_graph()
            self.save_graph()
            #self.save_graphViz()

def argparsing():
    parser = argparse.ArgumentParser(description="Make kNN Graph from MDP data")
    parser.add_argument('--data_title', '-d', help="MDP data title for making graph")
    parser.add_argument('--neighbors', '-k', type = int, action = 'store', default = 5, help="Number of neighbor for graph")

    args = parser.parse_args()
    return args

def main():
    args = argparsing()

    gmaker = GraphGenerator(args.data_title, args.neighbors)
    gmaker.run()

if __name__== "__main__":
    main()
