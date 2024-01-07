package MODULE;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Function class, including various public function modules
 */
public class Functions {
    /**
     *  Kepler's third law determines satellite orbital period
     * @param R   Satellite orbit radius (satellite height from the ground + radius of the earth)
     * @return    Satellite orbital period (seconds)
     */
    public static double satellitePeriod(double R){
        //The Earth's gravitational constant (unit: m^3/kg*s^2)
        double G = 6.67430e-11;
        //Mass of the Earth (unit: kg)
        double M = 5.97219e24;
        //Calculate the orbital period of the satellite (unit: seconds)
        return 2 * Math.PI * Math.sqrt(Math.pow(R, 3) / (G * M));
    }




    /**
     * Generate n points on land and convert them into a three-dimensional Cartesian coordinate system and return
     * @param n    how many points to generate
     * @param R    Earth radius
     * @return     Generated coordinate array of n land points (Cartesian coordinate system)
     */
    public static ArrayList<ArrayList<Double>> groundPoint(int n , double R){
        //The longitude and latitude coordinates of n ground points also need to be converted into three-dimensional Cartesian coordinates.
        ArrayList<ArrayList<Double>>  points = new ArrayList<>();
        /*
        Runtime runtime = Runtime.getRuntime();
        try {
            Process process = runtime.exec("python src/MODULE/points.py");
        } catch (IOException e) {
            e.printStackTrace();
        }
         */
        //read file
        try {
            BufferedReader br = new BufferedReader(new FileReader("points.txt"));
            String s;
            for(int i=0;i<n;i++){
                s = br.readLine();
                String[] t = s.split("\\s+");
                double longitude = Double.parseDouble(t[0]);
                double latitude = Double.parseDouble(t[1]);
                ArrayList<Double> temp = new ArrayList<>();
                temp.add(longitude);
                temp.add(latitude);
                points.add(temp);
            }
            br.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        ArrayList<ArrayList<Double>> result = LongitudeAndLatitudeToDescartesPoints(points,R);
        return result;
    }

    /**
     * Generate m*n satellites and convert them into a three-dimensional Cartesian coordinate system and return
     * @param m      Number of tracks
     * @param n      Number of satellites per orbit
     * @param R      Earth radius
     * @param h      satellite height from ground
     * @param i      Orbital inclination
     * @return       Generated coordinate array of m*n satellites (three-dimensional Cartesian coordinate system)
     *
     *  !!!   i=90° in the current code version
     */
    public static ArrayList<ArrayList<ArrayList<Double>>> satellite(int m , int n , double R , double h , double i){
        ArrayList<ArrayList<ArrayList<Double>>> satellites = new ArrayList<>();
        //There are m tracks in total, then the angle between any two adjacent tracks is 360/m
        double angle1 = 360.0/(2*m); //angle1 represents the angle between any two adjacent tracks
        //There are n satellites in each orbit, then the angle between any adjacent satellites is 360/n
        double angle2 = 360.0/n; //angle2 represents the angle between any two adjacent satellites in the same orbit
        for(int orbit=0;orbit<m;orbit++){
            ArrayList<ArrayList<Double>> orbit_sub = new ArrayList<>();
            for(int sat=0;sat<n;sat++){
                ArrayList<Double> sat_sub = new ArrayList<>();
                if(sat * angle2 < 90){
                    sat_sub.add(orbit * angle1); //Satellite longitude is between [0,180°]
                    sat_sub.add(sat * angle2);   //Satellite dimension is in northern latitude

                }else if(sat * angle2 < 270){
                    sat_sub.add(orbit * angle1 - 180);  //The satellite longitude is between [180°, 360°]
                    sat_sub.add(180 - sat * angle2);    //Satellite dimensions are in northern or southern latitudes
                }else{
                    sat_sub.add(orbit * angle1);  //Satellite longitude is between [0,180°]
                    sat_sub.add(sat * angle2 - 360);  //Satellite dimension is in southern latitude
                }
                orbit_sub.add(sat_sub);
            }
            satellites.add(orbit_sub);
        }
        ArrayList<ArrayList<ArrayList<Double>>> result = LongitudeAndLatitudeToDescartesSatellites(satellites,R+h);
        return result;
    }


    /**
     * Convert the latitude and longitude coordinates of ground points into three-dimensional Cartesian coordinates
     * @param points      Latitude and longitude coordinates
     * @param R           Earth radius
     * @return            Three-dimensional Cartesian coordinates
     */
    private static ArrayList<ArrayList<Double>> LongitudeAndLatitudeToDescartesPoints(ArrayList<ArrayList<Double>> points , double R){
        ArrayList<ArrayList<Double>> result = new ArrayList<>();
        double a,b;
        for(int i=0;i<points.size();i++){
            if(points.get(i).get(0) > 0) a = points.get(i).get(0);
            else a = points.get(i).get(0) + 360;
            if(points.get(i).get(1) > 0) b = points.get(i).get(1);
            else b = points.get(i).get(1) + 360;
            ArrayList<Double> temp = new ArrayList<>();
            temp.add(R*Math.cos(Math.toRadians(a)));
            temp.add(R*Math.sin(Math.toRadians(a)));
            temp.add(R*Math.sin(Math.toRadians(b)));
            result.add(temp);
        }
        return result;
    }


    /**
     *  Convert the satellite's right ascension and dimensional coordinates into three-dimensional Cartesian coordinates
     * @param satellites    Satellite latitude and longitude collection
     * @param R             Satellite orbit height is equal to the sum of the earth's radius and the satellite's height from the ground
     * @return              A collection of satellite three-dimensional Cartesian coordinate representations
     */
    private static ArrayList<ArrayList<ArrayList<Double>>> LongitudeAndLatitudeToDescartesSatellites(ArrayList<ArrayList<ArrayList<Double>>> satellites , double R){
        ArrayList<ArrayList<ArrayList<Double>>> result = new ArrayList<>();
        double a,b;
        for(int i=0;i<satellites.size();i++){
            ArrayList<ArrayList<Double>> sub1 = new ArrayList<>();
            for(int j=0;j<satellites.get(i).size();j++){
                ArrayList<Double> sub2 = new ArrayList<>();
                if(satellites.get(i).get(j).get(0) > 0) a = satellites.get(i).get(j).get(0);
                else a = satellites.get(i).get(j).get(0) + 360;
                if(satellites.get(i).get(j).get(1) > 0) b = satellites.get(i).get(j).get(1);
                else b = satellites.get(i).get(j).get(1) + 360;
                sub2.add(R*Math.cos(Math.toRadians(a)));
                sub2.add(R*Math.sin(Math.toRadians(a)));
                sub2.add(R*Math.sin(Math.toRadians(b)));
                sub1.add(sub2);
            }
            result.add(sub1);
        }
        return result;
    }


    /**
     * Find the Cartesian coordinates of a point on the earth and its new three-dimensional coordinates after seconds of the earth's rotation.
     * @param points      Three-dimensional Cartesian coordinate coefficient set of land points
     * @param R           Radius of the Earth (meters)
     * @param seconds     The time difference between the current update time and the last update time (seconds)
     * @return            The updated three-dimensional Cartesian coordinate coefficient set of the land point
     */
    public static ArrayList<ArrayList<Double>> updatePoints(ArrayList<ArrayList<Double>> points , double seconds , double R){
        //The angle the earth rotates in seconds (radians)
        double a = Math.PI*seconds/43200;
        for(int i=0;i<points.size();i++){
            //Angle b (radians) between the point before updating and the x-axis
            double b = Math.atan2(points.get(i).get(1),points.get(i).get(0));
            //Updated angle c (radians)
            double c = b + a;
            //The updated x coordinate value of the point
            points.get(i).set(0 , R*Math.cos(c));
            //points[i][0] = R*Math.cos(c);
            //The updated y coordinate value of the point
            points.get(i).set(1 , R*Math.sin(c));
            //points[i][1] = R*Math.sin(c);
        }
        return points;
    }


    /**
     * Find the new three-dimensional coordinates (Cartesian coordinates) of the satellite after seconds.
     * @param satellite   Satellite's three-dimensional Cartesian coordinate coefficient set
     * @param seconds     The time difference between the current update time and the last update time (seconds)
     * @param R           Satellite orbit radius (i.e. Earth radius + satellite height from the ground)
     * @return            Updated satellite 3D Cartesian coordinates
     */
    public static ArrayList<ArrayList<ArrayList<Double>>> updateSatellites(ArrayList<ArrayList<ArrayList<Double>>> satellite , double seconds , double R){
        //Find the angle the satellite rotates during seconds
        double T = satellitePeriod(R); //Satellite orbital motion period
        double angle = 360*seconds / T; //The angle that the satellite rotates along its orbit in seconds
        //Convert the three-dimensional Cartesian coordinate system to longitude and latitude coordinates
        ArrayList<ArrayList<ArrayList<Double>>> longAndlati = DescartesToLongitudeAndLatitude(satellite,R);
        //Mobile satellite coordinates
        for(int i=0;i< longAndlati.size();i++){
            for(int j=0;j< longAndlati.get(i).size();j++){
                double longitude = longAndlati.get(i).get(j).get(0);
                double latitude = longAndlati.get(i).get(j).get(1);
                if((longitude > 0 || Math.abs(longitude-0)<=1e-6) && (latitude > 0 || Math.abs(latitude-0)<=1e-6)){
                    if(latitude+angle < 90){
                        longAndlati.get(i).get(j).set(1 , latitude + angle);
                    }else if(latitude + angle < 270){
                        longAndlati.get(i).get(j).set(0 , longitude - 180);
                        longAndlati.get(i).get(j).set(1 , 180-angle-latitude);
                    }else{
                        longAndlati.get(i).get(j).set(1 , latitude + angle - 360);
                    }
                }else if((longitude < 0 || Math.abs(longitude-0)<=1e-6) && (latitude > 0 || Math.abs(latitude-0)<=1e-6)){
                    if(angle < latitude+90 || Math.abs(angle-latitude-90)<=1e-6){
                        longAndlati.get(i).get(j).set(1 , latitude - angle);
                    }else if(angle < latitude+270 || Math.abs(angle-latitude-270)<=1e-6){
                        longAndlati.get(i).get(j).set(0 , longitude + 180);
                        longAndlati.get(i).get(j).set(1 , angle-latitude-180);
                    }else if(angle < 360 || Math.abs(angle-360)<=1e-6){
                        longAndlati.get(i).get(j).set(1 , latitude-angle+360);
                    }
                }else if((longitude > 0 || Math.abs(longitude-0)<=1e-6) && (latitude < 0 || Math.abs(latitude-0)<=1e-6)){
                    if(angle < -latitude+90 || Math.abs(angle+latitude-90)<=1e-6){
                        longAndlati.get(i).get(j).set(1 , latitude + angle);
                    }else if(angle < -latitude+270 || Math.abs(angle+latitude-270)<=1e-6){
                        longAndlati.get(i).get(j).set(0 , longitude - 180);
                        longAndlati.get(i).get(j).set(1 , 180-angle-latitude);
                    }else if(angle < 360 || Math.abs(angle-360)<=1e-6){
                        longAndlati.get(i).get(j).set(1 , angle+latitude-360);
                    }
                }else if((longitude < 0 || Math.abs(longitude-0)<=1e-6) && (latitude < 0 || Math.abs(latitude-0)<=1e-6)){
                    if(angle < 90+latitude || Math.abs(angle-90-latitude)<=1e-6){
                        longAndlati.get(i).get(j).set(1 , latitude - angle);
                    }else if(angle < latitude+270 || Math.abs(angle-latitude-270)<=1e-6){
                        longAndlati.get(i).get(j).set(0 , longitude + 180);
                        longAndlati.get(i).get(j).set(1 , angle-latitude-180);
                    }else if(angle < 360 || Math.abs(angle-360)<=1e-6){
                        longAndlati.get(i).get(j).set(1 , latitude - angle + 360);
                    }
                }
            }
        }

        //Convert the moved latitude and longitude coordinates to Cartesian coordinates
        ArrayList<ArrayList<ArrayList<Double>>> result = LongitudeAndLatitudeToDescartesSatellites(longAndlati , R);
        return result;
    }

    /**
     * Convert satellite's three-dimensional Cartesian coordinates to longitude and latitude coordinates
     * @param satellites    Array storing Cartesian coordinates of satellites
     * @param R             Satellite flight altitude (radius of the earth + satellite distance from the ground)
     * @return              Returns the converted latitude and longitude coordinates
     */
    public static ArrayList<ArrayList<ArrayList<Double>>> DescartesToLongitudeAndLatitude(ArrayList<ArrayList<ArrayList<Double>>> satellites , double R){
        ArrayList<ArrayList<ArrayList<Double>>> result = new ArrayList<>();
        for(int i=0;i<satellites.size();i++){
            ArrayList<ArrayList<Double>> sub1 = new ArrayList<>();
            for(int j=0;j<satellites.get(i).size();j++){
                ArrayList<Double> sub2 = new ArrayList<>();
                double x = satellites.get(i).get(j).get(0);
                double y = satellites.get(i).get(j).get(1);
                double z = satellites.get(i).get(j).get(2);
                if(Math.abs(Math.toDegrees(Math.atan2(y,x)) -180)<1e-6){
                    sub2.add(-Math.toDegrees(Math.atan2(y,x)));
                }else{
                    sub2.add(Math.toDegrees(Math.atan2(y,x)));
                }
                sub2.add(Math.toDegrees(Math.asin(z/R)));
                sub1.add(sub2);
            }
            result.add(sub1);
        }
        return result;
    }


    /**
     * Using the ground point as the perspective, find the satellites that each ground station can see.
     * @param satellites        Satellite collection (3D Cartesian coordinates)
     * @param points            Ground point set (three-dimensional Cartesian coordinates)
     * @param e                 The minimum elevation angle at which the satellite can be seen from the ground
     * @return                  Returns whether each ground station can see each satellite. For example: if the p-th
     *  ground point can see the j-th star in the i-th orbit, then [p][i][j]=1, otherwise [p][i ][j]=0
     */
    public static ArrayList<ArrayList<ArrayList<Integer>>> vision(ArrayList<ArrayList<ArrayList<Double>>> satellites ,
                                                                  ArrayList<ArrayList<Double>> points , double e){
        //Using the ground station as the perspective, find the satellites that each ground station can see. The result is the 01 matrix.
        ArrayList<ArrayList<ArrayList<Integer>>> points2satellites = new ArrayList<>();
        for(int p=0;p<points.size();p++){
            ArrayList<ArrayList<Integer>> vision = new ArrayList<>();
            for(int i=0;i<satellites.size();i++){
                ArrayList<Integer> sub1 = new ArrayList<>();
                for(int j=0;j<satellites.get(i).size();j++){
                    if(judgePointToSatellite(satellites.get(i).get(j).get(0) , satellites.get(i).get(j).get(1) , satellites.get(i).get(j).get(2) ,
                            points.get(p).get(0) , points.get(p).get(1) , points.get(p).get(2) , e)){
                        sub1.add(1);
                    }else{
                        sub1.add(0);
                    }
                }
                vision.add(sub1);
            }
            points2satellites.add(vision);
        }
        return points2satellites;
    }



    /**
     * Using satellites as the perspective, find the ground points that each satellite can see.
     * @param satellites        Satellite collection (3D Cartesian coordinates)
     * @param points            Ground point set (three-dimensional Cartesian coordinates)
     * @param e                 The minimum elevation angle at which the satellite can be seen from the ground
     * @return                  Returns the visibility of each satellite to each base station, 01 matrix
     */
    public static ArrayList<ArrayList<ArrayList<Integer>>> vision2(ArrayList<ArrayList<ArrayList<Double>>> satellites ,
                                                                  ArrayList<ArrayList<Double>> points , double e){
        ArrayList<ArrayList<ArrayList<Integer>>> result = new ArrayList<>();
        for(int i=0;i<satellites.size();i++){
            ArrayList<ArrayList<Integer>> sub1 = new ArrayList<>();
            for(int j=0;j<satellites.get(i).size();j++){
                ArrayList<Integer> sub2 = new ArrayList<>();
                for(int p=0;p<points.size();p++){
                    if(judgePointToSatellite(satellites.get(i).get(j).get(0) , satellites.get(i).get(j).get(1) , satellites.get(i).get(j).get(2) ,
                            points.get(p).get(0) , points.get(p).get(1) , points.get(p).get(2) , e)){
                        sub2.add(1);
                    }else{
                        sub2.add(0);
                    }
                }
                sub1.add(sub2);
            }
            result.add(sub1);
        }
        return result;
    }




    /**
     * Given the coordinates of a ground point and a satellite in the three-dimensional Cartesian system, determine
     * whether the ground point can see the satellite.
     * @param sx      Satellite x coordinate
     * @param sy      Satellite y coordinate
     * @param sz      Satellite z coordinate
     * @param px      ground point x coordinate
     * @param py      ground point y coordinate
     * @param pz      ground point z coordinate
     * @param e        The minimum elevation angle at which the satellite can be seen from the ground
     * @return        Return true to indicate that it can be seen, false to indicate that it cannot be seen.
     *
     */
    private static boolean judgePointToSatellite(double sx , double sy , double sz , double px , double py , double pz , double e){
        double A = px*(px-sx)+py*(py-sy)+pz*(pz-sz);
        double B = Math.sqrt(px*px+py*py+pz*pz);
        double C = Math.sqrt(Math.pow(sx-px , 2) + Math.pow(sy-py , 2) + Math.pow(sz-pz , 2));
        double angle = Math.toDegrees(Math.acos(A/(B*C))); //Find angles and convert radians to degrees
        if(angle < 90 + e || Math.abs(angle - 90 - e) <= 1e-6)  return false;
        else return true;
    }


    /**
     * The function of this function is to find out how many satellites can be seen by the matrix matrix
     * @param matrix      Bitmap of all satellites that can be seen from a certain point on the ground, 0 means not visible, 1 means visible
     * @return            Returns the number of 1's in the matrix
     */
    public static int number_of_point_vision_satellite(ArrayList<ArrayList<Integer>> matrix){
        int sum=0;
        for(int i=0;i<matrix.size();i++){
            for(int j=0;j<matrix.get(i).size();j++){
                if(matrix.get(i).get(j) == 1) sum++;
            }
        }
        return sum;
    }

    /**
     * The function of this function is to find out how many ground stations can be seen by the j-th satellite in the i-th orbit
     * @param satellites2points          01 matrix that stores the ground station conditions visible to all satellites
     * @param i                          i-th orbit
     * @param j                          j-th satellite
     * @return                           The total number of ground stations that can be seen by the i-th orbit dij satellite
     */
    public static int number_of_ij_vision_point(ArrayList<ArrayList<ArrayList<Integer>>> satellites2points , int i , int j){
        int sum = 0;
        for(int k = 0;k < satellites2points.get(i).get(j).size();k++){
            if(satellites2points.get(i).get(j).get(k) == 1) sum++;
        }
        return sum;
    }


}
