package com.remote.tap;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.os.Handler;
import android.os.Looper;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Listens on 127.0.0.1:9931 (reachable via adb forward). Protocol: one line
 * per connection, "x y" in display pixels; replies "OK" or "ERR:<reason>".
 * Taps are performed through the accessibility gesture API, which needs no
 * INJECT_EVENTS permission (MIUI blocks plain `input tap`).
 */
public class TapService extends AccessibilityService {
    private static final int PORT = 9931;
    private final Handler main = new Handler(Looper.getMainLooper());

    @Override
    protected void onServiceConnected() {
        listen();
    }

    private void listen() {
        new Thread(() -> {
            try {
                ServerSocket ss = new ServerSocket(PORT, 50, InetAddress.getByName("127.0.0.1"));
                while (true) {
                    Socket s = ss.accept();
                    handle(s);
                }
            } catch (Exception e) {
                try { Thread.sleep(2000); } catch (InterruptedException ie) { }
                main.post(() -> listen());
            }
        }).start();
    }

    private void handle(Socket s) {
        try (Socket sock = s) {
            BufferedReader r = new BufferedReader(new InputStreamReader(sock.getInputStream()));
            String line = r.readLine();
            String resp = "ERR:bad-request";
            if (line != null) {
                String[] p = line.trim().split("[ ,]+");
                if (p.length >= 2) {
                    try {
                        tap(Float.parseFloat(p[0]), Float.parseFloat(p[1]));
                        resp = "OK";
                    } catch (Throwable t) {
                        resp = "ERR:" + t;
                    }
                }
            }
            OutputStream os = sock.getOutputStream();
            os.write((resp + "\n").getBytes());
            os.flush();
        } catch (Exception ignored) {
        }
    }

    private void tap(float x, float y) {
        Path path = new Path();
        path.moveTo(x, y);
        GestureDescription.Builder b = new GestureDescription.Builder();
        b.addStroke(new GestureDescription.StrokeDescription(path, 0, 60));
        dispatchGesture(b.build(), null, null);
    }

    @Override
    public void onAccessibilityEvent(android.view.accessibility.AccessibilityEvent e) {
    }

    @Override
    public void onInterrupt() {
    }
}
