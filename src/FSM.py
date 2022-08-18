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
        self.adjList_set = []
        
        self.candidate = []
        self.prev_candidate = None
        self.visit = []
        
        self.FS_set = []
        self.node_len = None
        self.data_len = None
        

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

        self.data_len = len(CAM_files)
    
    def adjList_gen(self):
        # Adjacency List 생성
        for g in self.graph_set:
            adjList = [[] for _ in range(self.node_len)]
            for edge in g.Edges():
                adjList[edge.GetSrcNId()].append(edge.GetDstNId())
                adjList[edge.GetDstNId()].append(edge.GetSrcNId())
            self.adjList_set.append(adjList)

    def candidate_gen(self):
        while False in self.visit:
            if not self.candidate:
                for i, n in enumerate(self.visit):
                    if not n:
                        self.candidate = [i]
                        self.visit[i] = True
                        break

            for node in self.candidate:
                for adj_list in self.adjList_set:
                    for adj_node in adj_list[node]:
                        if  not self.visit[adj_node]:
                            self.candidate.insert(0,adj_node)
                            self.visit[adj_node] = True
                            return False    # candidate가 생성되면 return
            
            if self.prev_candidate:  # 방문하지 않은 인접한 node가 없으면 이전 frequent subgraph 저장
                self.FS_set.append(self.prev_candidate)
                self.prev_candidate = []

            self.candidate = [] # 후보 초기화
        return True # 더이상 candidate가 없으면 True return

        

    def subgraph_isomorphism(self, sub_g): 
        #subgraph의 edge를 반복하며 각 graph에 존재하는지 각 graph의 CAM을 통해 확인한다.
        occurrence_cnt = self.data_len
        idx_list = [i for i,c in enumerate(self.CAM_set[0]) if c == "$"]    # CAM을 통해 edge의 존재를 찾기위해 필요한 list

        # ex) subgraph의 edge가 (3,4)인 경우 검색하는 graph의 CAM에서 3번째 $에서 5번쨰 떨어진 값이 1이면 그 graph에 edge가 존재한다는 것을 알 수 있다.
        for edge in sub_g.Edges():
            if edge.GetSrcNId() < edge.GetDstNId(): 
                for cam in self.CAM_set:
                    if cam[idx_list[edge.GetDstNId()-1]+edge.GetSrcNId()+1] != "1":
                        occurrence_cnt -= 1
                        if occurrence_cnt < self.min_support:
                            return False
            else:
                for cam in self.CAM_set:
                    if cam[idx_list[edge.GetSrcNId()-1]+edge.GetDstNId()+1] != "1":
                        occurrence_cnt -= 1
                        if occurrence_cnt < self.min_support:
                            return False
        return True


    def save_FS(self):
        # Frequent subgraph 저장
        json_out = {}        
            
        json_out["Data"] = self.graph_title
        json_out["FSM"] = self.FS_set

        json_path = self.path + f'{self.graph_title}_FSM.json'
        with open(json_path, 'w') as outfile:
            json.dump(json_out, outfile)


    def is_graph(self, sub_g):
        # sub_g로 생성된 것이 그래프인지 확인한다. node에 연결된 edge가 없으면 graph가 아닌 것으로 판단한다.
        for node in sub_g.Nodes():
            if node.GetOutDeg() == 0:
                return False
        return True


    def run(self):
        self.load_graphs()
        self.node_len = self.graph_set[0].GetNodes()    # 그래프 노드 개수
        self.adjList_gen()
        self.FS_set = []
        self.visit = [False for _ in range(self.node_len)]
       
        while False in self.visit:
            if self.candidate_gen():
                break

            for g in self.graph_set:
                sub_g = g.GetSubGraph(self.candidate)
                if not self.is_graph(sub_g):
                    continue
                if self.subgraph_isomorphism(sub_g):
                    self.prev_candidate = self.candidate.copy()
                    break
            if self.prev_candidate != self.candidate:
                self.candidate = []
                if self.prev_candidate:
                    self.FS_set.append(self.prev_candidate)
                    self.prev_candidate = []          

        self.save_FS()
        print(self.FS_set)




def argparsing():
    parser = argparse.ArgumentParser(description="Frequent Subgraph Mining")
    parser.add_argument('--data_title', '-d', help="graph data title for FSM")
    parser.add_argument('--min_support', '-s', type = int, action = 'store', default = 8, help="min_support for FSM")

    args = parser.parse_args()
    return args


def main():
    args = argparsing()
    fsm = FSM(args.data_title, args.min_support)
    fsm.run()

if __name__== "__main__":
    main()

