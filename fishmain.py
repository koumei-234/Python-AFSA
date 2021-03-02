import random, math
from cfish import *
#from scipy.spatial import distance
import copy
import argparse
import json
import pprint
import numpy as np
import pandas as pd
import os
import datetime
# from bayes_opt import BayesianOptimization

from collections import OrderedDict

import GPy
import GPyOpt
from GPyOpt.methods import BayesianOptimization

path = os.path.dirname(os.path.abspath(__file__))

def do(dim=2,population=10,trytimes=3,Visual=0.2,step=0.3,i=0,iteration=10):
	StoreBest=[]
	GroupFish=[]
	#魚の初期条件
	initialize(dim, population, GroupFish)

	B=getBestFish(GroupFish)
	StoreBest.append(copy.deepcopy(B))

	#繰り返し
	while i< iteration:
		j=0
		while j<population:
			k=0
			while k<trytimes:	
				temp_Position=makeTemp(GroupFish[j], Visual)
				if GroupFish[j].fitness<temp_Position.fitness:
					prey(GroupFish[j], temp_Position, B, dim, step, population, Visual, GroupFish, j)
					break
				k=k+1
			moveRandomly(GroupFish[j], Visual)
			j=j+1
			#leapFish(GroupFish)
		i=i+1
		B=getBestFish(GroupFish)
		StoreBest.append(copy.deepcopy(B))

	return getBestFish(StoreBest),[dim,population,trytimes,Visual,step,i,iteration]

def do_b(dim=2,population=10,trytimes=3,Visual=0.2,step=0.3,i=0,iteration=50):
	population =  int(dim[0][1])
	trytimes =  int(dim[0][2])
	Visual =  dim[0][3]
	step = dim[0][4]
	dim = int(dim[0][0])
	StoreBest=[]
	GroupFish=[]

	
	#魚の初期条件
	initialize(dim, population, GroupFish)

	B=getBestFish(GroupFish)
	StoreBest.append(copy.deepcopy(B))

	#繰り返し
	while i< iteration:
		j=0
		while j<population:
			k=0
			while k<trytimes:	
				temp_Position=makeTemp(GroupFish[j], Visual)
				if GroupFish[j].fitness<temp_Position.fitness:
					prey(GroupFish[j], temp_Position, B, dim, step, population, Visual, GroupFish, j)
					break
				k=k+1
			moveRandomly(GroupFish[j], Visual)
			j=j+1
			#leapFish(GroupFish)
		i=i+1
		B=getBestFish(GroupFish)
		StoreBest.append(copy.deepcopy(B))
	
	return getBestFish(StoreBest).fitness

bounds = [
    {'name': 'dim', 'type': 'discrete', 'domain': tuple([i for i in range(1,11)])}, 
    {'name': 'population', 'type': 'discrete', 'domain': tuple([i for i in range(1,11)])}, 
    {'name': 'trytimes', 'type': 'discrete', 'domain': tuple([i for i in range(1,11)])}, 
    {'name': 'Visual', 'type': 'continuous', 'domain': (0.1, 1.0)}, 
    {'name': 'step', 'type': 'continuous', 'domain': (0.1, 1.0)}, 
]

pbounds = {
    					"dim" :(1.0,10.0),
						"population" : (1.0,10.0),
						"trytimes" : (1.0,10.0),
						"Visual" : (0.1,1.0),
						"step" : (0.1,1.0)
					}

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='ASFAを実行するためのスクリプト')
	parser.add_argument('-j', '--json',default=0,help='jsonファイルで設定されたパラメータを読み込む')
	parser.add_argument('-r', '--rand',default=0,help='ランダムモードにして、パラメータをランダムに設定する')
	parser.add_argument('-i', '--iter',default=None,help='イテレーションを強制的に変える')
	parser.add_argument('-b', '--byth',default=None,help='byth推定を行う')

	args = parser.parse_args()
	

	np.random.seed(int(args.rand))
	
	rand = np.random.randint(0, 100, 10)
	print(rand)
	
	
	if args.json!=0:
		try:
			with open(args.json) as f:
				df = json.load(f)
			pprint.pprint(df, width=40)
			if args.iter == None:
				iter = df["params"]["iter"]
			else:
				iter = int(args.iter)
	
			BE,val = do(dim=df["algo"]["dim"],population=df["algo"]["population"],trytimes=df["algo"]["trytimes"],Visual=df["fish"]["visual"],step=df["fish"]["step"],i=df["params"]["i"],iteration=iter)
			
		# except expression as identifier:
		except FileNotFoundError:
			print("ファイルが見つかりませんでした。")
			BE,val = do()
	elif args.rand != 0 and args.json == 0:
		arr = np.random.random_sample(3)
		if args.iter == None:
			iter = 10
		else:
			iter = int(args.iter)
		BE,val = do(dim=rand[0],population=rand[1],trytimes=rand[2],Visual=arr[0],step=arr[1],i=0,iteration=iter)
	
	elif args.byth != 0:
		
		# optimizer = BayesianOptimization(f=do_b, pbounds=pbounds)
		# optimizer.maximize(init_points=3, n_iter=10)
		optimizer = BayesianOptimization(f=do_b, domain=bounds, model_type='GP', acquisition_type='EI')
		optimizer.run_optimization(max_iter=100)
		maxd = optimizer.x_opt
		d = {"algo":{"dim":maxd[0],"population":maxd[1],"trytimes":maxd[2]},"fish": {"visual":maxd[3], "step":maxd[4]}, "params": {"i":0,"iter":100}}
		with open('/Users/ystk/Documents/AFSA/best_pram.json', 'w') as f:
			json.dump(d, f, indent=4)
		quit()
		# BE,val = do(dim=maxd["dim"],population=maxd["population"],trytimes=maxd["trytimes"],Visual=maxd["visual"],step=maxd["step"],i=0,iteration=iter)



	key=["dim","population","trytimes","Visual","step","i","iteration"]
	dict1=dict(zip(key,val))
	dt_now = datetime.datetime.now()
	d={"socore":BE.fitness,"time":dt_now.strftime('%Y-%m-%d %H:%M:%S')}
	dict1.update(d)
	dfd = pd.DataFrame(dict1.values(), index=dict1.keys()).T
	dfd=dfd.set_index("time")
	
	try:
		df_r = pd.read_csv(path+'/result.csv')
		df_r=df_r.set_index("time")
		
	except FileNotFoundError:
		print("csvファイルを作成します")
	try:
		dfd = df_r.append(dfd)
		dfd.to_csv(path+'/result.csv')
	except NameError:
		dfd.to_csv(path+'/result.csv')
	print(dfd.tail())
