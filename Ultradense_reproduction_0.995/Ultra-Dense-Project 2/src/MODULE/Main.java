package MODULE;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

public class Main {

    //Points on land (three-dimensional Cartesian coordinate system, one line represents a point, three numbers represent xyz coordinates)
    public static ArrayList<ArrayList<Double>> points;
    //Satellite (three-dimensional Cartesian coordinate system)
    public static ArrayList<ArrayList<ArrayList<Double>>> satellites;
    //The number of points on the land
    public static int numberOfPoints = 1000;
    //kmin
    public static int kmin = 3;
    //kmax
    public static int kmax = 0;
    //Orbital height (m)
    public static double h = 600000.0;
    //Number of orbits
    public static int m = 50;
    //Number of satellites per orbit
    public static int n = 50;
    //Number of time slices
    public static int timeSlice = 100;
    //Satellite orbit inclination angle (°)
    public static double γ = 90;
    //The minimum elevation angle at which the satellite can be seen from the ground (°)
    public static double e = 0;
    //Satellite surface coverage
    public static double η0 = 0.995;
    //dividing line between high and low latitudes
    public static double bound = 66.5;


    //Radius of the Earth (m)
    public static final double R = 6371000.0;

    public static void main(String[] args) {
        //Generate random points on land
        points = Functions.groundPoint(numberOfPoints,R);
        //Generate satellite in orbit
        satellites = Functions.satellite(m,n,R,h,γ);
        //Find the kmax value
        //getKmax();
        for(int kmin = 3;kmin <=8;kmin++){
            for(int timeslot = 0;timeslot < 60;timeslot++){
                Thread thread = new MyThread(kmin , timeslot);
                thread.setName("Thread   :   kmin=" + kmin + ",timeslot=" + timeslot + "-->   ");
                thread.start();
            }
        }
    }


    /**
     * Find the Kmax value
     */
    public static int getKmax(int kmin){
        double β = Math.toDegrees(Math.asin(1.0*R*Math.sin(Math.toRadians(90+e))/(R+h))); //angle
        double θ = 90 - e - β; //angle
        double d = 2*(R+h)*Math.sin(Math.toRadians(θ));
        return (int)Math.ceil(η0*kmin*2*Math.PI*(R+h)/d);
    }





    /**
     * Constellation deep copy, the resulting copy is used for loop optimization
     * @return      Returns the copy of the constellation
     */
    public static ArrayList<ArrayList<ArrayList<Double>>> copySatellites(){
        ArrayList<ArrayList<ArrayList<Double>>> result = new ArrayList<>();
        for(int i=0;i<satellites.size();i++){
            ArrayList<ArrayList<Double>> sub1 = new ArrayList<>();
            for(int j=0;j<satellites.get(i).size();j++){
                ArrayList<Double> sub2 = new ArrayList<>();
                sub2.add(satellites.get(i).get(j).get(0));
                sub2.add(satellites.get(i).get(j).get(1));
                sub2.add(satellites.get(i).get(j).get(2));
                sub1.add(sub2);
            }
            result.add(sub1);
        }
        return result;
    }



    /**
     * Calculate constellation coverage
     * @param copySatellites    Constellations to be calculated
     * @return                  Return coverage
     */
    public static double coverageRatio(ArrayList<ArrayList<ArrayList<Double>>> copySatellites , int kmin){
        //Traverse every point on the land and calculate how many satellites they are covered by
        ArrayList<ArrayList<ArrayList<Integer>>> points2satellites = Functions.vision(copySatellites , points , e);
        //sum is used to calculate how many points in low latitudes meet kmin and how many points in high latitudes meet kmax
        int sum = 0;
        for(int i=0;i<points2satellites.size();i++){
            //Calculate how many satellites can be seen from the i-th ground point
            int temp = 0; //temp represents how many satellites can be seen from the i-th ground point
            for(int xx=0;xx<points2satellites.get(i).size();xx++){
                for(int yy=0;yy<points2satellites.get(i).get(xx).size();yy++){
                    if(points2satellites.get(i).get(xx).get(yy) == 1)  temp++;
                }
            }
            if(temp >= kmin)  sum++;
        }
        return 1.0*sum/points2satellites.size();
    }

    /**
     *    Constellation optimization
     * @return     Return the optimized constellation
     */
    public static ArrayList<ArrayList<ArrayList<Double>>> algorithm1(int kmin , int timeslot){
        ArrayList<ArrayList<ArrayList<Double>>> satellites = null;
        satellites = copySatellites(); //Copy the constellation, and the optimization of each time slice uses the original constellation optimization.
        System.out.println("current thread : " + Thread.currentThread().getName() + " number of satellites : " + getSum(satellites));
        //Mobile satellites and ground points
        Functions.updatePoints(points, timeSlice*timeslot, R);  //Update points on the ground
        satellites = Functions.updateSatellites(satellites , timeSlice*timeslot , R+h); //Update satellite coordinates
        //Calculate the constellation coverage at the current moment. If it is lower than eta0, it will no longer be optimized, indicating that the initial size of the constellation is too small to achieve the required coverage eta0.
        double ratio_current = coverageRatio(satellites , kmin);
        if(ratio_current < η0){
            return null;
        }
        //Indicates whether there are deleted elements in the following loop. If there are no deleted elements, it means that the current moment has met the requirements and the time slice can be moved.
        boolean have_remove;

        do{
            //Traverse every point on the land and calculate how many satellites they are covered by
            ArrayList<ArrayList<ArrayList<Integer>>> points2satellites = Functions.vision(satellites , points , e);
            ArrayList<ArrayList<ArrayList<Integer>>> satellites2points = Functions.vision2(satellites , points , e);
            //Traverse the ground points that each satellite can see. If all the ground points that a satellite can see are covered by at least kmin (or kmax) satellites, the satellite should be deleted.
            boolean flag = false; //Indicates whether any satellite has been deleted
            //If flag=true, it means that there is a satellite to be deleted, and the satellite to be deleted is located at the index_jth satellite in the index_ith orbit.
            int index_i = -1 , index_j = -1;
            for(int i=0;i<satellites2points.size();i++){
                for(int j=0;j<satellites2points.get(i).size();j++){
                    //Find out how many ground points can be seen by the j-th satellite in orbit i
                    int numberOfIJSatellites = Functions.number_of_ij_vision_point(satellites2points , i , j);
                    //The j-th satellite in orbit i can see how many points on the ground are covered by > kmin (kmax) satellites
                    int numberOfSatelliteKminKmax = 0;
                    for(int k=0;k<satellites2points.get(i).get(j).size();k++){
                        if(satellites2points.get(i).get(j).get(k)==1){
                            //Find how many satellites can be seen from the kth ground point
                            int numberOfKPoint = Functions.number_of_point_vision_satellite(points2satellites.get(k));
                            //Determine conditions based on the latitude of k ground point
                            if(Math.abs(points.get(k).get(2)) < R*bound/90){ //low dimensional area
                                if(numberOfKPoint > kmin)   numberOfSatelliteKminKmax++;
                            }else{ //high latitudes
                                if(numberOfKPoint > getKmax(kmin))   numberOfSatelliteKminKmax++;
                            }
                            if(numberOfSatelliteKminKmax == numberOfIJSatellites)  break;
                        }
                    }
                    if(numberOfSatelliteKminKmax == numberOfIJSatellites && numberOfIJSatellites > 0){
                        flag = true;
                        index_i = i;
                        index_j = j;
                        break;
                    }
                }
                if(flag)  break;
            }
            if(flag){
                //Indicates that a satellite needs to be deleted, and the index_jth satellite located in the index_ith orbit needs to be deleted.
                satellites.get(index_i).remove(index_j);
                have_remove = true;
                if(coverageRatio(satellites , kmin) < η0)  return satellites;
            }else{
                have_remove = false;
            }
            //Delete and re-traverse
        }while(have_remove);

        //If the coverage rate is greater than eta0 after the above loop is executed, continue to randomly delete some points from the constellation so that the coverage rate is equal to eta0
        while(coverageRatio(satellites , kmin) > η0){
            //Traverse points. For ground points that meet kmin requirements, randomly delete some of the satellites and then recalculate the coverage.
            ArrayList<ArrayList<ArrayList<Integer>>> points2satellites = Functions.vision(satellites , points , e);
            for(int tt = 0;tt < points2satellites.size();tt++){
                int row = -1 , col = -1; //The row and column index of the satellite you are looking for
                if(Functions.number_of_point_vision_satellite(points2satellites.get(tt)) >= kmin){
                    //Find one of the satellites visible from point tt
                    for(int row1 = 0;row1 < points2satellites.get(tt).size();row1++){
                        for(int col1 = 0; col1 < points2satellites.get(tt).get(row1).size();col1++){
                            if(points2satellites.get(tt).get(row1).get(col1) == 1){
                                row = row1;
                                col = col1;
                                break;
                            }
                        }
                        if(row > 0)  break;
                    }
                }
                //Delete the satellite in column row, orbit, col1
                if(row > 0){
                    satellites.get(row).remove(col);
                    break;
                }
            }
        }

        double η = coverageRatio(satellites , kmin);
        System.out.println("The final constellation coverage is:" + η);
        saveConstellation(satellites , η , timeslot , kmin);
        System.out.println("Constellation information has been written to the file!");



        return satellites;
    }


    /**
     * Calculate how many satellites are included in the final constellation
     * @param minimized_LEO_constellation          final constellation
     * @return                  Total number of satellites in the constellation
     */
    public static int getSum(ArrayList<ArrayList<ArrayList<Double>>> minimized_LEO_constellation){
        int sum = 0;
        for (ArrayList<ArrayList<Double>> arrayLists : minimized_LEO_constellation) {
            sum += arrayLists.size();
        }
        return sum;
    }


    /**
     * Write the optimized constellation information to a file and save it
     * @param minimized_LEO_constellation       Optimized constellation
     * @param η                                 Final constellation coverage
     */
    public static void saveConstellation(ArrayList<ArrayList<ArrayList<Double>>> minimized_LEO_constellation , double η , int timeslot , int kmin){
        //Convert satellite's three-dimensional Cartesian coordinates to longitude and latitude coordinates
        minimized_LEO_constellation = Functions.DescartesToLongitudeAndLatitude(minimized_LEO_constellation , R+h);
        try {
            BufferedWriter bw = new BufferedWriter(new FileWriter("TEST_Constellation_info(" + "m=" + m + ",n=" + n + ",η0=" + η0 + ",kmin=" + kmin
                    + ",timeslot=" + timeslot + ").txt"));
            bw.write("The constellation coverage is : " + η + "\n");
            for(int i=0;i<minimized_LEO_constellation.size();i++){
                for(int j=0;j<minimized_LEO_constellation.get(i).size();j++){
                    bw.write("The " + j + "-th satellite in the " + i + "-th orbit : \tLongitude : " +
                            minimized_LEO_constellation.get(i).get(j).get(0) + "\tLatitude : " +
                            minimized_LEO_constellation.get(i).get(j).get(1) + "\n");
                }
            }
            bw.flush();
            bw.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
