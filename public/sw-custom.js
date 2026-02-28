// Custom service worker additions for CertDuo
// This file is merged with the generated service worker by @ducanh2912/next-pwa

// Handle push notifications
self.addEventListener("push", (event) => {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch {
    data = { title: "CertDuo", body: event.data.text() };
  }

  const options = {
    body: data.body || "Time to learn!",
    icon: "/icons/icon-192.png",
    badge: "/icons/icon-192.png",
    data: { url: data.url || "/dashboard" },
    actions: [
      { action: "open", title: "Start Learning" },
      { action: "dismiss", title: "Later" },
    ],
    tag: "certduo-reminder",
    renotify: true,
  };

  event.waitUntil(self.registration.showNotification(data.title || "CertDuo", options));
});

// Handle notification clicks
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "dismiss") return;

  const url = event.notification.data?.url || "/dashboard";

  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && "focus" in client) {
            client.focus();
            client.navigate(url);
            return;
          }
        }
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});
