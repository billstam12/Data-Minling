import pandas as pd 
from ast import literal_eval
from collections import Counter
import dtw
import numpy as np 
import gmplot
from math import radians, cos, sin, asin, sqrt
import time

AVG_EARTH_RADIUS = 6371 #km

train_set = pd.read_csv('datasets/train_set.csv', 
						converters = {"Trajectory": literal_eval})
						

test_set = pd.read_csv('datasets/test_set_a2.csv', sep =";", converters = {"Trajectory": literal_eval})
						
def haversine(lon1,lat1,lon2,lat2):
	
		
	lon1, lat1, lon2, lat2, = map(radians, (lon1, lat1, lon2, lat2))
	
	#calculate haversine distance
	
	lon = lon2 - lon1
	lat = lat2 - lat1
	
	d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lon * 0.5) ** 2
	h = 2* AVG_EARTH_RADIUS * asin(sqrt(d))
	
	return h

#Dynamic lcs implementation
def lcs(search , target):
    
	m = len(search)
	n = len(target)
	
	
	L = [[None]*(n+1) for i in xrange(m+1)]
	
	for i in range(m+1):
		for j in range(n+1):
			x = haversine(search[i-1][1], search[i-1][2], target[j-1][1], target[j-1][2]) 
			if i == 0 or j == 0:
				L[i][j] = 0
			elif x <= 0.2:
				L[i][j] = L[i-1][j-1]+1
			else:
				L[i][j] = max(L[i-1][j] , L[i][j-1])
	cp = common_path(L,target)
	ls = [L[m][n], cp]
	return ls

#To find a common path, traverse the L matrix but in reverse this time.
def common_path(L,target):
    cp = []
    i=len(L)-1
    j=len(L[len(L)-1])-1
    while(True):
        if(j == 0 and i == 0): 
            break;
        if(j!=0 and L[i][j] == L[i][j-1]) :
            j=j-1
            continue
        elif(i!=0 and L[i][j] == L[i-1][j]):
            i=i-1
            continue
        else:
            cp.insert(0, target[j-1])
            i=i-1
            j=j-1
    return cp
	
train_traj = train_set['Trajectory']
train_traj = np.array(train_traj)
test_traj = test_set['Trajectory']

# Here we iterate through each instance of the table and
# for each of the elements in every row we remove the time element
# thus we keep only the coordinates.

start_of_run = time.time()
index = 1
for traj in test_traj:
	matching = []
	num = 0
	traj = np.array(traj)
	lats = []
	lons = []
	
	#Get coordinates
	for item in traj:
		lons.append(item[1])
		lats.append(item[2])
	
	# PLOT THE TEST ROUTE
	gmap = gmplot.GoogleMapPlotter(lats[int(len(lats)/2)], lons[int(len(lons)/2)], 11)
	gmap.plot(lats, lons, 'cornflowerblue', edge_width=5)
	gmap.draw("results2_2/Test_Route_"+str(index)+".html")
	
	#Calculate lcss and create matching list
	start_time = time.time()
	for j in train_traj:
		mt = lcs(traj,j)		
		matching.append([mt,num])
		#print cp
		num = num + 1	#This counts the position of the neighbor
	matching = sorted(matching, key = lambda x:x[0], reverse=True)

	# MATCHING = [ #points, {shortest_path}, index]
	elapsed_time = time.time() - start_time
	
	for k in range(5):
		#print matching[k];
		lats = []
		lons = []
		
		#Calculate coordinates of nearest neighbors and plot them too
		for l in train_traj[matching[k][1]]:
			lons.append(l[1])
			lats.append(l[2])
		
		#Common subsequence plot
		common_lats = []
		common_lons = []
		for i in matching[k][0][1]:
			common_lons.append(i[1])
			common_lats.append(i[2])
		
		gmap = gmplot.GoogleMapPlotter(lats[int(len(lats)/2)], lons[int(len(lons)/2)], 11)
		gmap.plot(lats, lons, 'cornflowerblue', edge_width=5)
		gmap.plot(common_lats, common_lons, 'red', edge_width=5)
		gmap.draw("results2_2/Neighbor_"+str(matching[k][1])+".html")
	
	print matching[0][0][0],matching[1][0][0],matching[2][0][0],matching[3][0][0],matching[4][0][0]
	fl = open('results2_2/final/final_'+str(index)+'.html','w')
	message = """
	<!DOCTYPE html>
	<html>
		<body>
			<table>
				<tr>
					<td><iframe src = "../Test_Route_"""+str(index)+""".html"></iframe></td>
					<td><iframe src = "../Neighbor_"""+str(matching[0][1])+""".html"></iframe></td>
					<td><iframe src = "../Neighbor_"""+str(matching[1][1])+""".html"></iframe></td>
				</tr>
				<tr>
					<td>Test Trip """+str(index)+"""</td>
					<td>Neighbor 1</td>
					<td>Neighbor 2</td>
				</tr>
				<tr>
					<td>Dt= """+str(elapsed_time)+"""sec</td>
					<td>JP_ID: """+str(train_set['journeyPatternId'][matching[0][1]])+"""</td>
					<td>JP_ID: """+str(train_set['journeyPatternId'][matching[1][1]])+"""</td>
				</tr>
				<tr>
					<td></td>
					<td>Matching Points:  """+str(matching[0][0][0])+"""</td>
					<td>Matching Points:  """+str(matching[1][0][0])+"""</td>
				</tr>
				<tr>
					<td><iframe src = "../Neighbor_"""+str(matching[2][1])+""".html"></iframe></td>
					<td><iframe src = "../Neighbor_"""+str(matching[3][1])+""".html"></iframe></td>
					<td><iframe src = "../Neighbor_"""+str(matching[4][1])+""".html"></iframe></td>
				</tr>
				<tr>
					<td>Neighbor 3</td>
					<td>Neighbor 4</td>
					<td>Neighbor 5</td>
				</tr>
				<tr>
					<td>JP_ID: """+str(train_set['journeyPatternId'][matching[2][1]])+"""</td>
					<td>JP_ID: """+str(train_set['journeyPatternId'][matching[3][1]])+"""</td>
					<td>JP_ID: """+str(train_set['journeyPatternId'][matching[4][1]])+"""</td>
				</tr>
				<tr>
					<td>Matching Points:  """+str(matching[2][0][0])+"""</td>
					<td>Matching Points:  """+str(matching[3][0][0])+"""</td>
					<td>Matching Points:  """+str(matching[4][0][0])+"""</td>
				</tr>
			</table>
		</body>
	</html>
	"""
	fl.write(message)
	fl.close()
	index+=1

total_time = time.time() - start_of_run
print total_time