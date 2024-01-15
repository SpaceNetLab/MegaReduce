import global_variables as gv
import functions as fun
import math



"""
Find the Kmax value
"""
def getKmax(kmin):
    β = math.degrees(math.asin(1.0 * gv.R * math.sin(math.radians(90 + gv.e)) / (gv.R + gv.h))) # angle
    θ = 90 - gv.e - β # angle
    d = 2 * (gv.R + gv.h) * math.sin(math.radians(θ))
    return int(math.ceil(gv.η0 * kmin * 2 * math.pi * (gv.R + gv.h) / d))



"""
Constellation deep copy, the resulting copy is used for loop optimization
"""
def copySatellites():
    result = []
    for i in range(len(gv.satellites)):
        sub1 = []
        for j in range(len(gv.satellites[i])):
            sub2 = []
            sub2.append(gv.satellites[i][j][0])
            sub2.append(gv.satellites[i][j][1])
            sub2.append(gv.satellites[i][j][2])
            sub1.append(sub2)
        result.append(sub1)
    return result




"""
Calculate constellation coverage
@param copySatellites    Constellations to be calculated
@return                  Return coverage
"""
def coverageRatio(copySatellites , kmin):
    # Traverse every point on the land and calculate how many satellites they are covered by
    points2satellites = fun.vision(copySatellites , gv.points , gv.e)
    # sum is used to calculate how many points in low latitudes meet kmin and how many points in high latitudes meet kmax
    sum = 0
    for i in range(len(points2satellites)):
        # Calculate how many satellites can be seen from the i-th ground point
        temp = 0 # temp represents how many satellites can be seen from the i-th ground point
        for xx in range(len(points2satellites[i])):
            for yy in range(len(points2satellites[i][xx])):
                if points2satellites[i][xx][yy] == 1:
                    temp += 1
        if temp >= kmin:
            sum += 1
    return 1.0 * sum / len(points2satellites)





"""
Calculate how many satellites are included in the final constellation
@param minimized_LEO_constellation          final constellation
@return                  Total number of satellites in the constellation
"""
def getSum(minimized_LEO_constellation):
    sum = 0
    for arrayLists in minimized_LEO_constellation:
        sum += len(arrayLists)

    return sum





def saveConstellation(minimized_LEO_constellation , η , timeslot , kmin):
    # Convert satellite's three-dimensional Cartesian coordinates to longitude and latitude coordinates
    minimized_LEO_constellation = fun.DescartesToLongitudeAndLatitude(minimized_LEO_constellation, gv.R + gv.h)
    file_name = ("TEST_Constellation_info(" + "m=" + str(gv.m) + ",n=" + str(gv.n) + ",η0=" + str(gv.η0) + ",kmin=" + str(kmin) +
                 ",timeslot=" + str(timeslot) + ").txt")
    with open(file_name, 'w') as f:
        f.write("The constellation coverage is : " + str(η) + "\n")
        for i in range(len(minimized_LEO_constellation)):
            for j in range(len(minimized_LEO_constellation[i])):
                f.write("The " + str(j) + "-th satellite in the " + str(i) + "-th orbit : \tLongitude : " +
                            str(minimized_LEO_constellation[i][j][0]) + "\tLatitude : " +
                            str(minimized_LEO_constellation[i][j][1]) + "\n")








"""
Constellation optimization
@return     Return the optimized constellation
"""
def algorithm1(kmin , timeslot):
    # Copy the constellation, and the optimization of each time slice uses the original constellation optimization
    satellites = copySatellites()

    print(" number of satellites : " + str(getSum(satellites)))

    # Mobile satellites and ground points
    fun.updatePoints(gv.points, gv.timeSlice*timeslot, gv.R) # Update points on the ground
    satellites = fun.updateSatellites(satellites , gv.timeSlice*timeslot , gv.R+gv.h) # Update satellite coordinates
    # Calculate the constellation coverage at the current moment. If it is lower than eta0, it will no longer be optimized, indicating that the initial size of the constellation is too small to achieve the required coverage eta0.
    ratio_current = coverageRatio(satellites, kmin)
    if ratio_current < gv.η0:
        return None
    # Indicates whether there are deleted elements in the following loop. If there are no deleted elements, it means that the current moment has met the requirements and the time slice can be moved.
    while True:
        # Traverse every point on the land and calculate how many satellites they are covered by
        points2satellites = fun.vision(satellites , gv.points , gv.e)
        satellites2points = fun.vision2(satellites , gv.points , gv.e)
        # Traverse the ground points that each satellite can see. If all the ground points that a satellite can see are covered by at least kmin (or kmax) satellites, the satellite should be deleted.
        flag = False # Indicates whether any satellite has been deleted
        # If flag=true, it means that there is a satellite to be deleted, and the satellite to be deleted is located at the index_jth satellite in the index_ith orbit.
        index_i = -1
        index_j = -1
        for i in range(len(satellites2points)):
            for j in range(len(satellites2points[i])):
                # Find out how many ground points can be seen by the j-th satellite in orbit i
                numberOfIJSatellites = fun.number_of_ij_vision_point(satellites2points, i, j)
                # The j-th satellite in orbit i can see how many points on the ground are covered by > kmin (kmax) satellites
                numberOfSatelliteKminKmax = 0
                for k in range(len(satellites2points[i][j])):
                    if satellites2points[i][j][k] == 1:
                        # Find how many satellites can be seen from the kth ground point
                        numberOfKPoint = fun.number_of_point_vision_satellite(points2satellites[k])
                        # Determine conditions based on the latitude of k ground point
                        if abs(gv.points[k][2]) < gv.R * gv.bound / 90:  # low dimensional area
                            if numberOfKPoint > kmin:
                                numberOfSatelliteKminKmax += 1
                        else:
                            if numberOfKPoint > getKmax(kmin):
                                numberOfSatelliteKminKmax += 1
                        if numberOfSatelliteKminKmax == numberOfIJSatellites:
                            break
                if numberOfSatelliteKminKmax == numberOfIJSatellites and numberOfIJSatellites > 0:
                    flag = True
                    index_i = i
                    index_j = j
                    break
            if flag:
                break
        if flag:
            # Indicates that a satellite needs to be deleted, and the index_jth satellite located in the index_ith orbit needs to be deleted.
            temp_list = satellites[index_i]
            del temp_list[index_j]
            have_remove = True
            print("The constellation has " +  str(getSum(satellites)) + " satellite, and the " + str(index_j + 1) + "-th satellite in the " + \
                  str(1 + index_i) + "-th orbit has been deleted. There are " + str(len(satellites[index_i])) + \
                  " satellites left in the orbit, and the constellation coverage is " + str(coverageRatio(satellites, kmin)))
            if coverageRatio(satellites, kmin) < gv.η0:
                return satellites
        else:
            have_remove = False
            print("The constellation has " +  str(getSum(satellites)) + " satellite, and no satellites were deleted in this cycle")

        if not have_remove:
            break

    # If the coverage rate is greater than eta0 after the above loop is executed, continue to randomly delete some points from the constellation so that the coverage rate is equal to eta0
    while coverageRatio(satellites, kmin) > gv.η0:
        # Traverse points. For ground points that meet kmin requirements, randomly delete some of the satellites and then recalculate the coverage.
        points2satellites = fun.vision(satellites , gv.points , gv.e)
        for tt in range(len(points2satellites)):
            # The row and column index of the satellite you are looking for
            row = -1
            col = -1
            if fun.number_of_point_vision_satellite(points2satellites[tt]) >= kmin:
                # Find one of the satellites visible from point tt
                for row1 in range(len(points2satellites[tt])):
                    for col1 in range(len(points2satellites[tt][row1])):
                        if points2satellites[tt][row1][col1] == 1:
                            row = row1
                            col = col1
                            break
                    if row > 0:
                        break
            # Delete the satellite in column row, orbit, col1
            if row > 0:
                temp_list = satellites[row]
                del temp_list[col]

                print("The constellation has " + str(getSum(satellites)) + " satellite, and the " + str(col + 1) + "-th satellite in the " + \
                      str(1 + row) + "-th orbit has been deleted. There are " + str(len(satellites[row])) + \
                      " satellites left in the orbit, and the constellation coverage is " + str(coverageRatio(satellites, kmin)))
                break

    η = coverageRatio(satellites, kmin)
    print("The final constellation coverage is:" + str(η))
    saveConstellation(satellites, η, timeslot, kmin)
    print("Constellation information has been written to the file!")

    return satellites









if __name__ == '__main__':
    # Generate random points on land
    gv.points = fun.groundPoint(gv.numberOfPoints,gv.R)
    # Generate satellite in orbit
    gv.satellites = fun.satellite(gv.m, gv.n, gv.R, gv.h, gv.γ)

    algorithm1(8, 0)

