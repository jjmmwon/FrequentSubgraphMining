import enum
import os
import glob
import json
import argparse

import snap
import numpy as np

class FSM:
    def __init__(self, graph_title, min_support=8):
        self.graph_title = graph_title
        self.min_support = min_support
        self.path = f'/home/myeongwon/mw_dir/FSM/result/{self.graph_title}/graph/'
        self.graph_set = []
        self.CAM_set = []
        self.FS_set = None

    def load_graphs(self):
        # graph를 snap.py에서 제공하는 graph 형식으로 load
        graph_path = self.path + '*.graph'
        graph_files = glob.glob(graph_path)
        graph_files.sort()
        for graph_file in graph_files:
            FIn = snap.TFIn(graph_file)
            graph = snap.TUNGraph.Load(FIn)
            self.graph_set.append(graph)
        
        #Canonical Adjacency Matrix (CAM) 형식으로 저장된 txt 파일 load
        CAM_path = self.path + '*.txt'
        CAM_files = glob.glob(CAM_path)
        CAM_files.sort()
        for CAM_file in CAM_files:
            file = open(CAM_file, "r")
            CAM = file.readline()
            self.CAM_set.append(CAM)
        

    def candidate_gen(self, k):
        # level-wise 방식으로 후보군 생성
        candidate_list = []
        if k == 2:
            for g in self.graph_set:
                for edge in g.Edges():
                    if {edge.GetSrcNId(), edge.GetDstNId()} not in candidate_list:
                        candidate_list.append({edge.GetSrcNId(), edge.GetDstNId()})
            return candidate_list
        
        # (k-1)번째 셋에서 k-2의 구조가 겹치는 것을 합쳐서 k번쨰 셋 생성
        for i in range(len(self.FS_set[k-1])):
            for j in range(i,len(self.FS_set[k-1])):
                candidate = self.FS_set[k-1][i] | self.FS_set[k-1][j]
                if len(candidate) == k:
                    candidate_list.append(candidate)
                    
        return candidate_list

    def subgraph_isomorphism(self, subgraph_CAM, idx):
        #subgraph의 CAM에서 edge와 그래프들의 edge를 비교하는 방법으로 isomorphism 탐색
        occurrence_cnt = 10
        for i in range(len(self.CAM_set)):
            if idx == i :
                continue

            for j in range(len(subgraph_CAM)):
                if subgraph_CAM[i] == "1":
                    if self.CAM_set[i][j] != "1":
                        occurrence_cnt -= 1
                        break;
        
        return occurrence_cnt

    

    def save_FS(self):
        # Frequent subgraph 저장
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
        self.load_graphs()

        self.FS_set = [[] for _ in range(self.graph_set[0].GetNodes()) ]
        self.FS_set[1].extend(range(self.graph_set[0].GetNodes()))
        
        k=2
        cnt =0
        while len(self.FS_set[k-1]) != 0 and k < self.graph_set[0].GetNodes():  # (k-1)번째 셋이 비었거나 k가 전체 노드의 개수보다 크면 종료
            candidate_list = self.candidate_gen(k)  # 후보군 생성

            # 후보 마다 frequent subgraph counting 후 FS_set에 저장
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

def argparsing():
    parser = argparse.ArgumentParser(description="Frequent Subgraph Mining")
    parser.add_argument('--data_title', '-d', help="graph data title for FSM")
    parser.add_argument('--min_support', '-s', help="min_support for FSM")

    args = parser.parse_args()
    return args


def main():
    args = argparsing()
    fsm = FSM(args.data_title, args.min_support)
    fsm.run()

if __name__== "__main__":
    main()

