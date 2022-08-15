import enum
import os
import glob
import json

import snap
import numpy as np

class FSM:
    def __init__(self, graph_title, min_support=8):
        self.graph_title = graph_title
        self.min_support = min_support
        self.path = f'/home/myeongwon/mw_dir/FSM/result/{self.graph_title}/graph/'
        self.graph_set = []
        self.FS_set = None

    def load_graphSet(self):
        path = self.path + '*.graph'
        graph_files = glob.glob(path)
        for graph_file in graph_files:
            FIn = snap.TFIn(graph_file)
            graph = snap.TUNGraph.Load(FIn)
            self.graph_set.append(graph)

    def candidate_gen(self, k):
        candidate_list = []
        if k == 2:
            for g in self.graph_set:
                for edge in g.Edges():
                    if {edge.GetSrcNId(), edge.GetDstNId()} not in candidate_list:
                        candidate_list.append({edge.GetSrcNId(), edge.GetDstNId()})
            return candidate_list
        
        for i in range(len(self.FS_set[k-1])):
            for j in range(i,len(self.FS_set[k-1])):
                candidate = self.FS_set[k-1][i] | self.FS_set[k-1][j]
                if len(candidate) == k:
                    candidate_list.append(candidate)
                    
        return candidate_list

    def subgraph_isomorphism(self):
        pass

    def save_FS(self):
        json_out = {}
        fsm_dict = {}
        for i, fsm in enumerate(self.FS_set):
            if i<=1:
                continue
            print(self.FS_set)
            fsm_cpy = [tuple(s) for s in fsm]
            fsm_dict[i] = fsm_cpy
            
        json_out["title"] = self.graph_title
        json_out["FSM"] = fsm_dict

        json_path = self.path + f'{self.graph_title}_FSM.json'
        with open(json_path, 'w') as outfile:
            json.dump(json_out, outfile)



    def run(self):
        self.load_graphSet()
        self.FS_set = [[] for _ in range(self.graph_set[0].GetNodes()) ]
        self.FS_set[1].extend(range(self.graph_set[0].GetNodes()))
        
        k=2
        cnt =0
        while len(self.FS_set[k-1]) != 0 and k < self.graph_set[0].GetNodes():
            candidate_list = self.candidate_gen(k)
            for candidate in candidate_list:
                gCount = 10
                clist = list(candidate)
                for g in self.graph_set:
                    sub_g = g.GetSubGraph(clist)
                    if len(clist) != sub_g.GetNodes():
                        gCount -= 1
                        cnt += 1
                        print(cnt)
                    if gCount < 8:
                        break
                if gCount < 8:
                    break
                self.FS_set[k].append(candidate)
            k += 1
            print(k)
            print(len(self.FS_set[k-1]))
        self.save_FS()

        print(self.FS_set)


def main():
    fsm = FSM("Iris")
    fsm.run()

if __name__== "__main__":
    main()

