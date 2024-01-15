package MODULE;

public class MyThread extends Thread{

    public int kmin;
    public int timeslot;

    public MyThread(int kmin , int timeslot) {
        this.kmin  = kmin;
        this.timeslot  = timeslot;
    }

    @Override
    public void run() {
        Main.algorithm1(kmin , timeslot);
    }


}
