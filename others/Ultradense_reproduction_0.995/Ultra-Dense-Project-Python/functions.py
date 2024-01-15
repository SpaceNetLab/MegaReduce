from global_land_mask import globe
import random
import math



"""
Convert the latitude and longitude coordinates of ground points into three-dimensional Cartesian coordinates
@param points      Latitude and longitude coordinates
@param R           Earth radius
@return            Three-dimensional Cartesian coordinates
"""
def LongitudeAndLatitudeToDescartesPoints(points , R):
    result = []
    a=0
    b=0
    for i in range(len(points)):
        if points[i][0] > 0:
            a = points[i][0]
        else:
            a = points[i][0] + 360

        if points[i][1] > 0:
            b = points[i][1]
        else:
            b = points[i][1] + 360
        temp=[]
        temp.append(R*math.cos(math.radians(a)))
        temp.append(R*math.sin(math.radians(a)))
        temp.append(R*math.sin(math.radians(b)))
        result.append(temp)
    return result






"""
Generate n points on land and convert them into a three-dimensional Cartesian coordinate system and return
@param n    how many points to generate
@param R    Earth radius
@return     Generated coordinate array of n land points (Cartesian coordinate system)
"""
def groundPoint(n , R):
    # The longitude and latitude coordinates of n ground points also need to be converted into three-dimensional Cartesian coordinates.
    points = []
    while len(points) < n:
        longitude = random.uniform(-180, 180)
        latitude = random.uniform(-90, 90)
        if globe.is_land(latitude,longitude):
            points.append([longitude, latitude])
    result = LongitudeAndLatitudeToDescartesPoints(points,R)



    return result




"""
Convert the satellite's right ascension and dimensional coordinates into three-dimensional Cartesian coordinates
@param satellites    Satellite latitude and longitude collection
@param R             Satellite orbit height is equal to the sum of the earth's radius and the satellite's height from the ground
@return              A collection of satellite three-dimensional Cartesian coordinate representations
"""
def LongitudeAndLatitudeToDescartesSatellites(satellites , R):
    result = []
    a = 0
    b = 0
    for i in range(len(satellites)):
        sub1 = []
        for j in range(len(satellites[i])):
            sub2 = []
            if satellites[i][j][0] > 0:
                a = satellites[i][j][0]
            else:
                a = satellites[i][j][0] + 360

            if satellites[i][j][1] > 0:
                b = satellites[i][j][1]
            else:
                b = satellites[i][j][1] + 360

            sub2.append(R * math.cos(math.radians(a)))
            sub2.append(R * math.sin(math.radians(a)))
            sub2.append(R * math.sin(math.radians(b)))
            sub1.append(sub2)
        result.append(sub1)
    return result



"""
Generate m*n satellites and convert them into a three-dimensional Cartesian coordinate system and return
@param m      Number of tracks
@param n      Number of satellites per orbit
@param R      Earth radius
@param h      satellite height from ground
@param i      Orbital inclination
@return       Generated coordinate array of m*n satellites (three-dimensional Cartesian coordinate system)
!!!   i=90° in the current code version
"""
def satellite(m , n , R , h , i):
    satellites = []
    # There are m tracks in total, then the angle between any two adjacent tracks is 360/m
    angle1 = 360.0 / (2 * m) # angle1 represents the angle between any two adjacent tracks
    # There are n satellites in each orbit, then the angle between any adjacent satellites is 360/n
    angle2 = 360.0 / n # angle2 represents the angle between any two adjacent satellites in the same orbit
    for orbit in range(m):
        orbit_sub = []
        for sat in range(n):
            sat_sub = []
            if sat * angle2 < 90:
                sat_sub.append(orbit * angle1)  # Satellite longitude is between [0,180°]
                sat_sub.append(sat * angle2) # Satellite dimension is in northern latitude
            elif sat * angle2 < 270:
                sat_sub.append(orbit * angle1 - 180) # The satellite longitude is between[180°, 360°]
                sat_sub.append(180 - sat * angle2) # Satellite dimensions are in northern or southern latitudes
            else:
                sat_sub.append(orbit * angle1) # Satellite longitude is between[0, 180°]
                sat_sub.append(sat * angle2 - 360) # Satellite dimension is in southern latitude
            orbit_sub.append(sat_sub)
        satellites.append(orbit_sub)
    result = LongitudeAndLatitudeToDescartesSatellites(satellites,R+h)
    return result




"""
Given the coordinates of a ground point and a satellite in the three-dimensional Cartesian system, determine
whether the ground point can see the satellite.
@param sx      Satellite x coordinate
@param sy      Satellite y coordinate
@param sz      Satellite z coordinate
@param px      ground point x coordinate
@param py      ground point y coordinate
@param pz      ground point z coordinate
@param e        The minimum elevation angle at which the satellite can be seen from the ground
@return        Return true to indicate that it can be seen, false to indicate that it cannot be seen.
"""
def judgePointToSatellite(sx , sy , sz , px , py , pz , e):
    A = px * (px - sx) + py * (py - sy) + pz * (pz - sz)
    B = math.sqrt(px * px + py * py + pz * pz)
    C = math.sqrt(math.pow(sx - px, 2) + math.pow(sy - py, 2) + math.pow(sz - pz, 2))
    angle = math.degrees(math.acos(A / (B * C))) # Find angles and convert radians to degrees
    if angle < 90 + e or abs(angle - 90 - e) <= 1e-6:
        return False
    else:
        return True






"""
Using the ground point as the perspective, find the satellites that each ground station can see.
@param satellites        Satellite collection (3D Cartesian coordinates)
@param points            Ground point set (three-dimensional Cartesian coordinates)
@param e                 The minimum elevation angle at which the satellite can be seen from the ground
@return                  Returns whether each ground station can see each satellite. For example: if the p-th
ground point can see the j-th star in the i-th orbit, then [p][i][j]=1, otherwise [p][i ][j]=0
"""
def vision(satellites , points , e):
    # Using the ground station as the perspective, find the satellites that each ground station can see. The result is the 01 matrix.
    points2satellites = []
    for p in range(len(points)):
        vision = []
        for i in range(len(satellites)):
            sub1 = []
            for j in range(len(satellites[i])):
                if judgePointToSatellite(satellites[i][j][0], satellites[i][j][1],
                                          satellites[i][j][2],
                                          points[p][0], points[p][1], points[p][2], e):
                    sub1.append(1)
                else:
                    sub1.append(0)
            vision.append(sub1)
        points2satellites.append(vision)
    return points2satellites










"""
Using satellites as the perspective, find the ground points that each satellite can see.
@param satellites        Satellite collection (3D Cartesian coordinates)
@param points            Ground point set (three-dimensional Cartesian coordinates)
@param e                 The minimum elevation angle at which the satellite can be seen from the ground
@return                  Returns the visibility of each satellite to each base station, 01 matrix
"""
def vision2(satellites, points , e):
    result = []
    for i in range(len(satellites)):
        sub1 = []
        for j in range(len(satellites[i])):
            sub2 = []
            for p in range(len(points)):
                if judgePointToSatellite(satellites[i][j][0], satellites[i][j][1],satellites[i][j][2],
                                          points[p][0], points[p][1], points[p][2], e):
                    sub2.append(1)
                else:
                    sub2.append(0)
            sub1.append(sub2)
        result.append(sub1)
    return result




"""
Kepler's third law determines satellite orbital period
@param R   Satellite orbit radius (satellite height from the ground + radius of the earth)
@return    Satellite orbital period (seconds)
"""
def satellitePeriod(R):
    # The Earth's gravitational constant (unit: m^3/kg*s^2)
    G = 6.67430e-11
    # Mass of the Earth (unit: kg)
    M = 5.97219e24
    # Calculate the orbital period of the satellite (unit: seconds)
    return 2 * math.pi * math.sqrt(math.pow(R, 3) / (G * M))







"""
Convert satellite's three-dimensional Cartesian coordinates to longitude and latitude coordinates
@param satellites    Array storing Cartesian coordinates of satellites
@param R             Satellite flight altitude (radius of the earth + satellite distance from the ground)
@return              Returns the converted latitude and longitude coordinates
"""
def DescartesToLongitudeAndLatitude(satellites , R):
    result = []
    for i in range(len(satellites)):
        sub1 = []
        for j in range(len(satellites[i])):
            sub2 = []
            x = satellites[i][j][0]
            y = satellites[i][j][1]
            z = satellites[i][j][2]
            if abs(math.degrees(math.atan2(y, x)) - 180) < 1e-6:
                sub2.append(-math.degrees(math.atan2(y, x)))
            else:
                sub2.append(math.degrees(math.atan2(y, x)))
            sub2.append(math.degrees(math.asin(z / R)))
            sub1.append(sub2)
        result.append(sub1)
    return result






"""
Find the Cartesian coordinates of a point on the earth and its new three-dimensional coordinates after seconds of the earth's rotation.
@param points      Three-dimensional Cartesian coordinate coefficient set of land points
@param R           Radius of the Earth (meters)
@param seconds     The time difference between the current update time and the last update time (seconds)
@return            The updated three-dimensional Cartesian coordinate coefficient set of the land point
"""
def updatePoints(points , seconds , R):
    # The angle the earth rotates in seconds (radians)
    a = math.pi * seconds / 43200
    for i in range(len(points)):
        # Angle b (radians) between the point before updating and the x-axis
        b = math.atan2(points[i][1], points[i][0])
        # Updated angle c (radians)
        c = b + a
        # The updated x coordinate value of the poin
        points[i][0] = R * math.cos(c)
        # The updated y coordinate value of the point
        points[i][1] = R * math.sin(c)
    return points










"""
Find the new three-dimensional coordinates (Cartesian coordinates) of the satellite after seconds.
@param satellite   Satellite's three-dimensional Cartesian coordinate coefficient set
@param seconds     The time difference between the current update time and the last update time (seconds)
@param R           Satellite orbit radius (i.e. Earth radius + satellite height from the ground)
@return            Updated satellite 3D Cartesian coordinates
"""
def updateSatellites(satellite , seconds ,R):
    # Find the angle the satellite rotates during seconds
    T = satellitePeriod(R) # Satellite orbital motion period
    angle = 360 * seconds / T  # The angle that the satellite rotates along its orbit in seconds
    # Convert the three-dimensional Cartesian coordinate system to longitude and latitude coordinates
    longAndlati = DescartesToLongitudeAndLatitude(satellite,R)
    # Mobile satellite coordinates
    for i in range(len(longAndlati)):
        for j in range(len(longAndlati[i])):
            longitude = longAndlati[i][j][0]
            latitude = longAndlati[i][j][1]
            if (longitude > 0 or abs(longitude - 0) <= 1e-6) and (latitude > 0 or abs(latitude - 0) <= 1e-6):
                if latitude + angle < 90:
                    longAndlati[i][j][1] = latitude + angle
                elif latitude + angle < 270:
                    longAndlati[i][j][0] = longitude - 180
                    longAndlati[i][j][1] = 180 - angle - latitude
                else:
                    longAndlati[i][j][1] = latitude + angle - 360
            elif (longitude < 0 or abs(longitude-0) <= 1e-6) and (latitude > 0 or abs(latitude-0) <= 1e-6):
                if angle < latitude + 90 or abs(angle - latitude - 90) <= 1e-6:
                    longAndlati[i][j][1] = latitude - angle
                elif angle < -latitude+270 or abs(angle+latitude-270) <= 1e-6:
                    longAndlati[i][j][0] = longitude - 180
                    longAndlati[i][j][1] = 180 - angle - latitude
                elif angle < 360 or abs(angle-360) <= 1e-6:
                    longAndlati[i][j][1] = angle + latitude - 360
            elif (longitude < 0 or abs(longitude-0) <= 1e-6) and (latitude < 0 or abs(latitude-0) <= 1e-6):
                if angle < 90 + latitude or abs(angle - 90 - latitude) <= 1e-6:
                    longAndlati[i][j][1] = latitude - angle
                elif angle < latitude+270 or abs(angle-latitude-270) <= 1e-6:
                    longAndlati[i][j][0] = longitude + 180
                    longAndlati[i][j][1] = angle - latitude - 180
                elif angle < 360 or abs(angle-360) <= 1e-6:
                    longAndlati[i][j][1] = latitude - angle + 360
    # Convert the moved latitude and longitude coordinates to Cartesian coordinates
    result = LongitudeAndLatitudeToDescartesSatellites(longAndlati, R)

    return result










"""
The function of this function is to find out how many satellites can be seen by the matrix matrix
@param matrix      Bitmap of all satellites that can be seen from a certain point on the ground, 0 means not visible, 1 means visible
@return            Returns the number of 1's in the matrix
"""
def number_of_point_vision_satellite(matrix):
    sum = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == 1:
                sum += 1
    return sum





"""
The function of this function is to find out how many ground stations can be seen by the j-th satellite in the i-th orbit
@param satellites2points          01 matrix that stores the ground station conditions visible to all satellites
@param i                          i-th orbit
@param j                          j-th satellite
@return                           The total number of ground stations that can be seen by the i-th orbit dij satellite
"""
def number_of_ij_vision_point(satellites2points ,i , j):
    sum = 0
    for k in range(len(satellites2points[i][j])):
        if satellites2points[i][j][k] == 1:
            sum += 1
    return sum


