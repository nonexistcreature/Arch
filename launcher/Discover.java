// Arkhaven LAN discovery (runs as a Prism pre-launch step with the bundled Java: `java Discover.java <instanceDir>`).
// Listens up to 4 s for the server's LAN announcement (224.0.2.60:4445, same as "Open to LAN").
// If found, writes the address into servers.dat (first entry "Arkhaven") and into instance.cfg
// (JoinServerOnLaunchAddress), so the game connects to it. If nothing is heard, the configured address stays.
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.regex.*;

public class Discover {
    public static void main(String[] args) throws Exception {
        Path inst = Paths.get(args.length > 0 ? args[0] : ".");
        // server on this same PC: localhost beats whatever adapter (VMware, ZeroTier...) the announcement came from
        String found = portOpen("127.0.0.1", 25565) ? "localhost" : listen(4000);
        if (found == null) {
            System.out.println("[Arkhaven] LAN server not heard; using the configured address");
            return;
        }
        System.out.println("[Arkhaven] LAN server found at " + found);
        // Prism instance dir (has .minecraft/) or a plain game folder (install-to-launcher.ps1)
        Path mc = Files.isDirectory(inst.resolve(".minecraft")) ? inst.resolve(".minecraft") : inst;
        writeServersDat(mc.resolve("servers.dat"), found);
        Path cfg = inst.resolve("instance.cfg");
        if (Files.exists(cfg)) {
            String t = Files.readString(cfg, StandardCharsets.UTF_8);
            t = t.replaceAll("(?m)^JoinServerOnLaunchAddress=.*$", "JoinServerOnLaunchAddress=" + Matcher.quoteReplacement(found));
            Files.writeString(cfg, t, StandardCharsets.UTF_8);
        }
    }

    static String listen(int ms) {
        try (MulticastSocket s = new MulticastSocket(4445)) {
            InetSocketAddress group = new InetSocketAddress(InetAddress.getByName("224.0.2.60"), 4445);
            // join on every IPv4 interface: home Wi-Fi/Ethernet and the ZeroTier virtual adapter alike
            int joined = 0;
            for (NetworkInterface nic : java.util.Collections.list(NetworkInterface.getNetworkInterfaces())) {
                try {
                    if (!nic.isUp() || nic.isLoopback() || !nic.supportsMulticast()) continue;
                    if (nic.getInterfaceAddresses().stream().noneMatch(a -> a.getAddress() instanceof Inet4Address)) continue;
                    s.joinGroup(group, nic);
                    joined++;
                } catch (IOException ignored) {
                    // adapter refuses multicast — skip it
                }
            }
            if (joined == 0) s.joinGroup(group, null);
            s.setSoTimeout(ms);
            byte[] buf = new byte[1024];
            long end = System.currentTimeMillis() + ms;
            while (System.currentTimeMillis() < end) {
                DatagramPacket p = new DatagramPacket(buf, buf.length);
                try { s.receive(p); } catch (SocketTimeoutException e) { return null; }
                String msg = new String(p.getData(), 0, p.getLength(), StandardCharsets.UTF_8);
                Matcher m = Pattern.compile("\\[MOTD\\](.*?)\\[/MOTD\\]\\[AD\\](\\d+)\\[/AD\\]").matcher(msg);
                if (m.find() && m.group(1).contains("Arkhaven")) {
                    String port = m.group(2);
                    String host = p.getAddress().getHostAddress();
                    return port.equals("25565") ? host : host + ":" + port;
                }
            }
        } catch (IOException e) {
            System.out.println("[Arkhaven] discovery failed: " + e);
        }
        return null;
    }

    static boolean portOpen(String host, int port) {
        try (Socket s = new Socket()) {
            s.connect(new InetSocketAddress(host, port), 300);
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    // Minimal NBT writer: { servers: [ { ip, name, hidden:0b } ] }
    static void writeServersDat(Path file, String ip) throws IOException {
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        DataOutputStream o = new DataOutputStream(bo);
        o.writeByte(10); o.writeUTF("");
        o.writeByte(9); o.writeUTF("servers"); o.writeByte(10); o.writeInt(1);
        o.writeByte(8); o.writeUTF("ip"); o.writeUTF(ip);
        o.writeByte(8); o.writeUTF("name"); o.writeUTF("Arkhaven");
        o.writeByte(1); o.writeUTF("hidden"); o.writeByte(0);
        o.writeByte(0); // end server compound
        o.writeByte(0); // end root
        Files.createDirectories(file.getParent());
        Files.write(file, bo.toByteArray());
    }
}
