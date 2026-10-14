// Arkhaven LAN announcer for a Windows host (run with the bundled Java: `java LanAnnounce.java 25565 Arkhaven`).
// Same protocol as "Open to LAN": multicast 224.0.2.60:4445 every 1.5 s, so the server appears in
// Multiplayer -> LAN and the Arkhaven launcher connects to it automatically.
// Sends on every active IPv4 interface: PCs with VPN/VMware adapters would otherwise announce on the wrong one.
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class LanAnnounce {
    public static void main(String[] args) throws Exception {
        String port = args.length > 0 ? args[0] : "25565";
        String motd = args.length > 1 ? args[1] : "Arkhaven";
        byte[] payload = ("[MOTD]" + motd + "[/MOTD][AD]" + port + "[/AD]").getBytes(StandardCharsets.UTF_8);
        InetSocketAddress group = new InetSocketAddress(InetAddress.getByName("224.0.2.60"), 4445);
        System.out.println("announcing " + motd + " on port " + port);
        while (true) {
            for (NetworkInterface nic : Collections.list(NetworkInterface.getNetworkInterfaces())) {
                try {
                    if (!nic.isUp() || nic.isLoopback() || !nic.supportsMulticast()) continue;
                    boolean v4 = nic.getInterfaceAddresses().stream().anyMatch(a -> a.getAddress() instanceof Inet4Address);
                    if (!v4) continue;
                    try (MulticastSocket s = new MulticastSocket()) {
                        s.setNetworkInterface(nic);
                        s.setTimeToLive(2);
                        s.send(new DatagramPacket(payload, payload.length, group));
                    }
                } catch (Exception ignored) {
                    // interface went down or refuses multicast — skip it this round
                }
            }
            Thread.sleep(1500);
        }
    }
}
