import java.lang.reflect.Method;

public class Main {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.out.println("USAGE: Main <socket> <cmd>");
            return;
        }
        String socket = args[0];
        String cmd = args[1];
        Class<?> cls = Class.forName("vendor.sprd.hardware.log.V1_0.ILogControl");
        Method getService = cls.getMethod("getService", boolean.class);
        Object svc = getService.invoke(null, Boolean.FALSE);
        System.out.println("SVC=" + svc);
        Method sendCmd = cls.getMethod("sendCmd", String.class, String.class);
        Object ret = sendCmd.invoke(svc, socket, cmd);
        System.out.println("RET=" + ret);
    }
}